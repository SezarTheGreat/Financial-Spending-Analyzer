/**
 * Gemini Native Function Calling Tool Definitions
 * FinWise Mutual Fund AI Advisor (Groww G.1 Architecture)
 */

export interface ToolDefinition {
  functionDeclarations: Array<{
    name: string;
    description: string;
    parameters: {
      type: string;
      properties: Record<string, any>;
      required?: string[];
    };
  }>;
}

export const MUTUAL_FUND_TOOLS: ToolDefinition = {
  functionDeclarations: [
    {
      name: "get_fund_metadata_and_nav",
      description:
        "Fetches official scheme master details from Supabase fund_master: current NAV, nav_date, Total Expense Ratio (TER), AUM in Crores, category, sub-category, and benchmark index.",
      parameters: {
        type: "OBJECT",
        properties: {
          scheme_name: {
            type: "STRING",
            description: "The name or search keyword of the mutual fund scheme (e.g., 'Parag Parikh Flexi Cap', 'Bandhan Small Cap').",
          },
          amfi_code: {
            type: "STRING",
            description: "Optional 6-digit AMFI scheme code if known (e.g., '122639').",
          },
        },
        required: ["scheme_name"],
      },
    },
    {
      name: "get_portfolio_and_sector_exposure",
      description:
        "Retrieves asset allocation breakdown (Equity %, Debt %, Cash %), top 10 company holdings, and concentration weights for a mutual fund scheme.",
      parameters: {
        type: "OBJECT",
        properties: {
          amfi_code: {
            type: "STRING",
            description: "6-digit AMFI code or scheme identifier.",
          },
          scheme_name: {
            type: "STRING",
            description: "Scheme name if AMFI code is not directly available.",
          },
        },
        required: ["scheme_name"],
      },
    },
    {
      name: "execute_quant_performance_audit",
      description:
        "Executes deterministic zero-hallucination quant calculations via Python Quant Engine: 1Y/3Y/5Y CAGR, rolling returns, Sharpe ratio, Sortino ratio, Beta vs Nifty 50, Maximum Drawdown, and 4-tier Form Classification (In-Form, On-Track, Off-Track, Out-of-Form).",
      parameters: {
        type: "OBJECT",
        properties: {
          amfi_code: {
            type: "STRING",
            description: "6-digit AMFI code of the fund.",
          },
          scheme_name: {
            type: "STRING",
            description: "Full scheme name.",
          },
          risk_profile: {
            type: "STRING",
            description: "Investor risk tolerance: 'Conservative', 'Moderate', or 'Aggressive'.",
          },
        },
        required: ["scheme_name"],
      },
    },
    {
      name: "search_fund_documents",
      description:
        "Executes hybrid vector similarity search (pgvector HNSW) over Scheme Information Documents (SID), Key Information Memorandums (KIM), factsheets, exit load rules, and SEBI regulations.",
      parameters: {
        type: "OBJECT",
        properties: {
          query: {
            type: "STRING",
            description: "Natural language query regarding tax rules, exit loads, fund objectives, or lock-in periods.",
          },
          amfi_code: {
            type: "STRING",
            description: "Optional AMFI code to restrict document search to a specific scheme.",
          },
          document_type: {
            type: "STRING",
            description: "Optional filter: 'SID', 'KIM', 'FACTSHEET', or 'REGULATION'.",
          },
        },
        required: ["query"],
      },
    },
  ],
};
