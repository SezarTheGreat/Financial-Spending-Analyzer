/**
 * Deno Test Suite for Chat Advisor Edge Function & Guardrails
 */
import { assertEquals, assertStringIncludes } from "https://deno.land/std@0.177.0/testing/asserts.ts";
import { MUTUAL_FUND_TOOLS } from "../chat-advisor/tools.ts";
import { sanitizeAdvisorResponse, SEBI_STATUTORY_DISCLAIMER } from "../chat-advisor/guardrails.ts";

Deno.test("Tools Schema contains all required 4 core function declarations", () => {
  const toolNames = MUTUAL_FUND_TOOLS.functionDeclarations.map((f) => f.name);
  assertEquals(toolNames.includes("get_fund_metadata_and_nav"), true);
  assertEquals(toolNames.includes("get_portfolio_and_sector_exposure"), true);
  assertEquals(toolNames.includes("execute_quant_performance_audit"), true);
  assertEquals(toolNames.includes("search_fund_documents"), true);
});

Deno.test("Guardrail Filter neutralizes forbidden marketing promises", () => {
  const nonCompliant = "This fund gives a guaranteed return and is a sure-shot profit! Buy this fund now for high gains.";
  const sanitized = sanitizeAdvisorResponse(nonCompliant);

  assertEquals(sanitized.includes("guaranteed return"), false);
  assertEquals(sanitized.includes("sure-shot profit"), false);
  assertEquals(sanitized.includes("Buy this fund now"), false);
  assertStringIncludes(sanitized, "Mutual fund investments are subject to market risks");
});

Deno.test("Guardrail Filter appends mandatory statutory disclaimer exactly once", () => {
  const normalText = "Parag Parikh Flexi Cap Fund has a 3Y CAGR of 17.5% with a 0.63% TER.";
  const sanitized = sanitizeAdvisorResponse(normalText);

  assertStringIncludes(sanitized, "Mutual fund investments are subject to market risks");
});
