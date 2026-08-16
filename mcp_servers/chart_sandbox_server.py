"""
FinWise MCP Server: Chart Sandbox Server
Model Context Protocol (MCP) Server for deterministic headless SVG financial chart rendering.
Generates responsive SVGs for asset allocations, rolling CAGR curves, and historical drawdowns.
"""
import sys
import json
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_chart_sandbox")

def render_asset_allocation_donut(
    equity_pct: float,
    debt_pct: float,
    commodities_pct: float,
    cash_pct: float,
    width: int = 400,
    height: int = 240
) -> str:
    """
    Renders a clean SVG Donut Chart for portfolio asset allocation.
    """
    total = max(1.0, equity_pct + debt_pct + commodities_pct + cash_pct)
    e = (equity_pct / total) * 100.0
    d = (debt_pct / total) * 100.0
    co = (commodities_pct / total) * 100.0
    ca = (cash_pct / total) * 100.0

    slices = [
        {"name": "Equity", "pct": e, "color": "#4F46E5"},
        {"name": "Debt", "pct": d, "color": "#059669"},
        {"name": "Commodities", "pct": co, "color": "#D97706"},
        {"name": "Cash/Liquid", "pct": ca, "color": "#0284C7"}
    ]

    cx, cy = 110, 120
    radius = 75
    inner_radius = 45

    def get_coords(pct_offset, rad):
        angle = (pct_offset / 100.0) * 2 * math.pi - math.pi / 2
        return cx + rad * math.cos(angle), cy + rad * math.sin(angle)

    accum = 0.0
    paths = []
    for s in slices:
        if s["pct"] <= 0.01:
            continue
        start_pct = accum
        end_pct = accum + s["pct"]
        accum = end_pct

        x1, y1 = get_coords(start_pct, radius)
        x2, y2 = get_coords(end_pct, radius)
        x3, y3 = get_coords(end_pct, inner_radius)
        x4, y4 = get_coords(start_pct, inner_radius)

        large_arc = 1 if s["pct"] > 50 else 0
        path_d = f"M {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large_arc} 1 {x2:.2f} {y2:.2f} L {x3:.2f} {y3:.2f} A {inner_radius} {inner_radius} 0 {large_arc} 0 {x4:.2f} {y4:.2f} Z"
        paths.append(f'<path d="{path_d}" fill="{s["color"]}" stroke="#FFFFFF" stroke-width="2" />')

    legend_items = []
    ly = 55
    for s in slices:
        legend_items.append(f'''
        <g transform="translate(230, {ly})">
            <rect width="12" height="12" rx="3" fill="{s["color"]}" />
            <text x="20" y="10" font-size="11" font-weight="600" fill="#374151">{s["name"]}</text>
            <text x="140" y="10" font-size="11" font-weight="700" fill="#111827" text-anchor="end">{s["pct"]:.1f}%</text>
        </g>
        ''')
        ly += 32

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="font-family:system-ui, -apple-system, sans-serif;">
        <rect width="{width}" height="{height}" fill="#FAFAFA" rx="12" />
        <g>{''.join(paths)}</g>
        <circle cx="{cx}" cy="{cy}" r="{inner_radius - 2}" fill="#FFFFFF" />
        <text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="11" font-weight="600" fill="#6B7280">Equity</text>
        <text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="14" font-weight="800" fill="#111827">{e:.1f}%</text>
        <g>{''.join(legend_items)}</g>
    </svg>'''
    return svg

def render_rolling_return_comparison(
    scheme_name: str,
    scheme_cagr_1y: float,
    benchmark_cagr_1y: float,
    scheme_cagr_3y: float,
    benchmark_cagr_3y: float
) -> str:
    """
    Renders an SVG bar comparison chart of 1Y/3Y CAGR vs benchmark.
    """
    w, h = 480, 220
    alpha_1y = scheme_cagr_1y - benchmark_cagr_1y
    alpha_3y = scheme_cagr_3y - benchmark_cagr_3y

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="{h}" style="font-family:system-ui, -apple-system, sans-serif;">
        <rect width="{w}" height="{h}" fill="#FAFAFA" rx="12" />
        <text x="24" y="28" font-size="12" font-weight="700" fill="#111827">{scheme_name[:38]}</text>
        <text x="24" y="44" font-size="10" font-weight="500" fill="#6B7280">1Y &amp; 3Y Rolling CAGR vs Category Benchmark</text>
        
        <!-- 1Y Horizon -->
        <g transform="translate(24, 70)">
            <text x="0" y="14" font-size="11" font-weight="600" fill="#374151">1-Year Horizon</text>
            <rect x="110" y="2" width="{max(10, scheme_cagr_1y * 6):.1f}" height="16" rx="4" fill="#4F46E5" />
            <text x="{115 + max(10, scheme_cagr_1y * 6)}" y="14" font-size="10" font-weight="700" fill="#4F46E5">Fund: {scheme_cagr_1y:.1f}%</text>
            
            <rect x="110" y="24" width="{max(10, benchmark_cagr_1y * 6):.1f}" height="16" rx="4" fill="#9CA3AF" />
            <text x="{115 + max(10, benchmark_cagr_1y * 6)}" y="36" font-size="10" font-weight="600" fill="#6B7280">Bench: {benchmark_cagr_1y:.1f}%</text>
            
            <text x="430" y="24" text-anchor="end" font-size="11" font-weight="800" fill="{'#059669' if alpha_1y >= 0 else '#DC2626'}">Alpha: {'+' if alpha_1y >= 0 else ''}{alpha_1y:.2f}%</text>
        </g>

        <!-- 3Y Horizon -->
        <g transform="translate(24, 140)">
            <text x="0" y="14" font-size="11" font-weight="600" fill="#374151">3-Year Horizon</text>
            <rect x="110" y="2" width="{max(10, scheme_cagr_3y * 6):.1f}" height="16" rx="4" fill="#059669" />
            <text x="{115 + max(10, scheme_cagr_3y * 6)}" y="14" font-size="10" font-weight="700" fill="#059669">Fund: {scheme_cagr_3y:.1f}%</text>
            
            <rect x="110" y="24" width="{max(10, benchmark_cagr_3y * 6):.1f}" height="16" rx="4" fill="#9CA3AF" />
            <text x="{115 + max(10, benchmark_cagr_3y * 6)}" y="36" font-size="10" font-weight="600" fill="#6B7280">Bench: {benchmark_cagr_3y:.1f}%</text>
            
            <text x="430" y="24" text-anchor="end" font-size="11" font-weight="800" fill="{'#059669' if alpha_3y >= 0 else '#DC2626'}">Alpha: {'+' if alpha_3y >= 0 else ''}{alpha_3y:.2f}%</text>
        </g>
    </svg>'''
    return svg

def handle_mcp_rpc(request_json: Dict[str, Any]) -> Dict[str, Any]:
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
                        "name": "render_asset_allocation_donut",
                        "description": "Renders a responsive SVG Donut Chart representing Equity, Debt, Commodities, and Cash percentages.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "equity_pct": {"type": "number"},
                                "debt_pct": {"type": "number"},
                                "commodities_pct": {"type": "number"},
                                "cash_pct": {"type": "number"}
                            },
                            "required": ["equity_pct", "debt_pct", "commodities_pct", "cash_pct"]
                        }
                    },
                    {
                        "name": "render_rolling_return_comparison",
                        "description": "Renders an SVG comparison bar chart of fund 1Y and 3Y rolling returns vs category benchmark.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "scheme_name": {"type": "string"},
                                "scheme_cagr_1y": {"type": "number"},
                                "benchmark_cagr_1y": {"type": "number"},
                                "scheme_cagr_3y": {"type": "number"},
                                "benchmark_cagr_3y": {"type": "number"}
                            },
                            "required": ["scheme_name", "scheme_cagr_1y", "benchmark_cagr_1y", "scheme_cagr_3y", "benchmark_cagr_3y"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "render_asset_allocation_donut":
            svg = render_asset_allocation_donut(
                args.get("equity_pct", 60.0),
                args.get("debt_pct", 30.0),
                args.get("commodities_pct", 10.0),
                args.get("cash_pct", 0.0)
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": svg}]}
            }
        elif tool_name == "render_rolling_return_comparison":
            svg = render_rolling_return_comparison(
                args.get("scheme_name", "Mutual Fund Scheme"),
                args.get("scheme_cagr_1y", 18.0),
                args.get("benchmark_cagr_1y", 15.0),
                args.get("scheme_cagr_3y", 16.5),
                args.get("benchmark_cagr_3y", 14.0)
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": svg}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool '{tool_name}'"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Unsupported method '{method}'"}}

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
        logger.info("FinWise Chart Sandbox MCP Server initialized.")
