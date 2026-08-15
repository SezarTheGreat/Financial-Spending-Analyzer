/**
 * SEBI Regulatory Guardrails & Response Sanitization Filter
 * Strictly prevents non-compliant financial advice, guaranteed return promises, or speculative buy calls.
 */

export const SEBI_STATUTORY_DISCLAIMER =
  "\n\n---\n*Mutual fund investments are subject to market risks. Read all scheme-related documents carefully before investing.*";

export const SYSTEM_ADVISOR_PROMPT = `You are FinWise AI, an institutional Indian Mutual Fund research and analytical engine modeled after Groww G.1.

CORE PRINCIPLES & CONSTRAINTS:
1. ZERO-HALLUCINATION: Never invent or guess NAVs, returns, expense ratios, or risk ratios. Always invoke tool calling to fetch verified mathematical figures from the Quant Engine or Supabase Fund Master.
2. STRICT ANALYTICAL NEUTRALITY: You are strictly a research analyst, NOT a registered investment advisor (RIA). Never issue directional buy/sell commands, guarantee future profits, or predict specific target prices.
3. COMPARATIVE LANGUAGE: Use objective metrics (e.g., "Scheme A delivers a 3Y Sharpe Ratio of 1.42 with 18.2% max drawdown compared to Scheme B's 1.15 Sharpe").
4. 4-TIER FORM CLASSIFICATION: When reviewing funds, quote their deterministic form tier:
   - 🟢 In-Form: Top-quartile alpha generator over rolling horizons.
   - 🟡 On-Track: Steady performer meeting or tracking category benchmark.
   - 🟠 Off-Track: Trailing benchmark; cooling short-term momentum.
   - 🔴 Out-of-Form: Chronic laggard underperforming benchmark.
5. TAXATION RULES (AY 2025-26):
   - Equity Funds (>65% Indian Equities): STCG (held <12 months) = 20%, LTCG (held >=12 months) = 12.5% on gains exceeding ₹1.25 Lakh per financial year.
   - Specified Debt Funds (<=35% Equity bought on/after 1 Apr 2023): Taxed at applicable slab rate.
6. MANDATORY DISCLAIMER: Every final synthesis response MUST conclude with the statutory SEBI disclaimer.`;

const FORBIDDEN_PHRASE_PATTERNS = [
  /\b(?:guaranteed|assured|risk-free|100%\s*safe)\s*(?:return|gain|profit|yield)s?\b/gi,
  /\b(?:sure-shot|guaranteed)\s*(?:profit|wealth|winner)s?\b/gi,
  /\b(?:buy|invest\s+in)\s+this\s+fund\s+now\b/gi,
  /\b(?:target\s+price|price\s+target)\s*(?:of|is|at)?\s*₹?\d+/gi,
  /\byou\s+must\s+immediately\s+(?:buy|sell)\b/gi,
  /\bpromise\s+(?:a|to\s+deliver)\s+\d+%\s*returns?\b/gi,
];

/**
 * Scans output and replaces forbidden marketing/advisory promises with compliant analytical phrasing.
 */
export function sanitizeAdvisorResponse(rawText: string): string {
  let cleaned = rawText;

  for (const pattern of FORBIDDEN_PHRASE_PATTERNS) {
    cleaned = cleaned.replace(pattern, (match) => {
      if (/guaranteed|assured|risk-free/i.test(match)) {
        return "market-linked historical performance";
      }
      if (/buy this fund/i.test(match)) {
        return "evaluate this fund based on your risk tolerance";
      }
      return "projected historical variance";
    });
  }

  // Ensure mandatory statutory disclaimer is present exactly once
  const disclaimerClean = SEBI_STATUTORY_DISCLAIMER.trim();
  if (!cleaned.includes("Mutual fund investments are subject to market risks")) {
    cleaned += "\n\n" + disclaimerClean;
  }

  return cleaned;
}
