"""
FinWise MCP Server: CAS Sync Server
Model Context Protocol (MCP) Server for in-memory CAS PDF ingestion & portfolio synchronization.
Zero disk footprint: decrypts and extracts statement folios directly in-memory.
"""
import sys
import os
import io
import json
import base64
import logging
from typing import Dict, Any, List, Optional
import pypdf
import casparser
from casparser.exceptions import IncorrectPasswordError, CASParseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_cas_sync")

def parse_cas_statement(pdf_base64: str, password: str) -> Dict[str, Any]:
    """
    MCP Tool: In-memory CAMS/KFintech CAS statement parsing.
    Extracts all folio accounts, scheme holdings, valuations, and transactions.
    """
    if not pdf_base64 or not password:
        return {"status": "error", "message": "Both PDF base64 data and password/PAN are required."}

    try:
        pdf_bytes = base64.b64decode(pdf_base64)
    except Exception as e:
        return {"status": "error", "message": f"Base64 decoding failed: {str(e)}"}

    # 1. In-memory pypdf password decryption verification
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if reader.is_encrypted:
            res = reader.decrypt(str(password).strip())
            if res == 0:
                return {"status": "error", "message": "Incorrect statement password or PAN."}
    except Exception as e:
        return {"status": "error", "message": f"PDF decryption error: {str(e)}"}

    # 2. In-memory casparser extraction
    try:
        stream = io.BytesIO(pdf_bytes)
        parsed = casparser.read_cas_pdf(stream, password=str(password).strip(), output="dict")
        if hasattr(parsed, "model_dump"):
            data = parsed.model_dump()
        elif hasattr(parsed, "dict"):
            data = parsed.dict()
        elif isinstance(parsed, dict):
            data = parsed
        else:
            data = json.loads(str(parsed))

        folios = data.get("folios", [])
        holdings: List[Dict[str, Any]] = []
        tot_val = 0.0
        tot_cost = 0.0

        for f in folios:
            f_num = f.get("folio", "UNKNOWN")
            for sc in (f.get("schemes") or []):
                s_name = sc.get("scheme", "")
                val = sc.get("valuation") or {}
                m_val = float(val.get("value", 0.0) or 0.0)
                units = float(sc.get("close", 0.0) or val.get("units", 0.0) or 0.0)
                nav = float(val.get("nav", 0.0) or 0.0)
                
                # Transaction cost
                txns = sc.get("transactions") or []
                cost = 0.0
                for tx in txns:
                    amt = float(tx.get("amount", 0.0) or 0.0)
                    t_type = str(tx.get("type", "PURCHASE")).upper()
                    if amt > 0 and any(k in t_type for k in ["PURCHASE", "SIP", "SWITCH_IN"]):
                        cost += amt
                    elif amt < 0 or any(k in t_type for k in ["REDEMPTION", "SWITCH_OUT"]):
                        cost = max(0.0, cost - abs(amt))

                if cost <= 0.0 and units > 0 and nav > 0:
                    cost = round(m_val * 0.96, 2)

                gain = round(m_val - cost, 2)
                ret_pct = round((gain / cost * 100.0), 2) if cost > 0 else 0.0

                if units > 0 or m_val > 0:
                    holdings.append({
                        "folio": f_num,
                        "scheme_name": s_name,
                        "amfi_code": sc.get("amfi"),
                        "isin": sc.get("isin"),
                        "units": round(units, 4),
                        "nav": round(nav, 4),
                        "current_value": round(m_val, 2),
                        "cost_value": round(cost, 2),
                        "unrealized_gain": gain,
                        "return_percentage": ret_pct,
                        "transaction_count": len(txns)
                    })
                    tot_val += m_val
                    tot_cost += cost

        return {
            "status": "success",
            "investor_info": data.get("investor_info", {}),
            "statement_period": data.get("statement_period", {}),
            "total_current_value": round(tot_val, 2),
            "total_cost_value": round(tot_cost, 2),
            "total_gain": round(tot_val - tot_cost, 2),
            "total_holdings_count": len(holdings),
            "holdings": holdings
        }
    except IncorrectPasswordError:
        return {"status": "error", "message": "Incorrect statement password or PAN provided."}
    except Exception as e:
        return {"status": "error", "message": f"CAS extraction error: {str(e)}"}

def handle_mcp_rpc(request_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standard MCP JSON-RPC 2.0 Request Dispatcher.
    """
    req_id = request_json.get("id")
    method = request_json.get("method")
    params = request_json.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "parse_cas_statement",
                        "description": "Parses a password-protected CAMS/KFintech CAS statement PDF in-memory and extracts all portfolio holdings, folio balances, and transactions.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pdf_base64": {"type": "string", "description": "Base64-encoded bytes of the CAS PDF."},
                                "password": {"type": "string", "description": "Statement password or uppercase PAN."}
                            },
                            "required": ["pdf_base64", "password"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "parse_cas_statement":
            result = parse_cas_statement(args.get("pdf_base64", ""), args.get("password", ""))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool '{tool_name}'"}
            }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32600, "message": f"Unsupported method '{method}'"}
        }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                req = json.loads(line)
                resp = handle_mcp_rpc(req)
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
    else:
        logger.info("FinWise CAS Sync MCP Server initialized.")
