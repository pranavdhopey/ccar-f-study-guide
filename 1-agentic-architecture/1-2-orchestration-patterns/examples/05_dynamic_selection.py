"""
Example 5: invoke only the subagents a query needs.

Covers: dynamic subagent selection. A simple factual question should NOT run the whole
pipeline. Running unneeded subagents adds latency and API cost, even if you cache what
they return.

    python 05_dynamic_selection.py            # the coordinator picks subagents per query
    python 05_dynamic_selection.py --naive    # always run all three, for comparison
"""
import sys

from agent_kit import STATS, ask, parse_json, run_agent

SIMPLE = "What are the opening hours of the council recycling centre?"
BROAD = "Write a short report on what is driving our costs this year."

# ------------------------------------------------------------------ stub tools (made-up data)
WEB_TOOLS = [{
    "name": "web_search", "description": "Search the web. Returns a short text result.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]
INVOICE_TOOLS = [{
    "name": "read_invoices",
    "description": "Read the café's invoices for one category: ingredients, energy, staff or rent.",
    "input_schema": {"type": "object", "properties": {"category": {"type": "string"}}, "required": ["category"]},
}]


def web_search(query):
    if "recycling" in query.lower():
        return "Council recycling centre: Mon-Sat 8:00-18:00, Sun 10:00-16:00. (made-up demo data)"
    return "Dairy up 6%, gas up sharply, minimum wage up in April. (made-up demo data)"


def read_invoices(category):
    return {"ingredients": "up 7%", "energy": "gas up 18%", "staff": "wages up 5%", "rent": "unchanged"}.get(
        category.lower(), "none")


# ------------------------------------------------------------------ the subagents
def run_web(query, findings):
    findings["web"] = run_agent(
        "You are the web search subagent. Use web_search and answer briefly.",
        f"Query: {query}", WEB_TOOLS, {"web_search": web_search})


def run_documents(query, findings):
    findings["documents"] = run_agent(
        "You are the invoice analyst subagent. Call read_invoices for ingredients, energy, staff and "
        "rent, then report one short line each.",
        f"Query: {query}", INVOICE_TOOLS, {"read_invoices": read_invoices})


def run_synthesis(query, findings):
    joined = "\n\n".join(f"[{k}]\n{v}" for k, v in findings.items())
    findings["synthesis"] = run_agent(
        "You are the synthesis subagent. Write a short report using ONLY the findings in your task.",
        f"Query: {query}\n\nFINDINGS:\n{joined}")


SUBAGENTS = {"web_search": run_web, "document_analysis": run_documents, "synthesis": run_synthesis}

ROUTER_SYSTEM = (
    "You are the research coordinator. You choose which subagents to invoke for a query.\n"
    "Available subagents:\n"
    "- web_search: finds public information on the web\n"
    "- document_analysis: reads the café's own invoices\n"
    "- synthesis: combines findings from the other subagents into a report. Only useful when there "
    "are findings to combine.\n"
    "Invoke ONLY the subagents the query needs. A simple factual question needs only web_search.\n"
    "Return ONLY a JSON list of subagent names, in the order to run them."
)


def plan_for(query, naive):
    if naive:
        return list(SUBAGENTS)
    plan = parse_json(ask(ROUTER_SYSTEM, f"Query: {query}"))
    unknown = [p for p in plan if p not in SUBAGENTS]
    if unknown:  # never trust the plan blindly
        print(f"  (plan named unknown subagents {unknown}; falling back to the full pipeline)")
        return list(SUBAGENTS)
    return plan


def answer(query, naive):
    calls_before = STATS["api_calls"]
    plan = plan_for(query, naive)
    findings = {}
    for name in plan:
        SUBAGENTS[name](query, findings)
    final = findings.get("synthesis") or list(findings.values())[-1]
    return plan, final, STATS["api_calls"] - calls_before


if __name__ == "__main__":
    naive = "--naive" in sys.argv
    print("MODE:", "naive (always the full pipeline)" if naive else "dynamic selection")
    for label, query in (("SIMPLE", SIMPLE), ("BROAD", BROAD)):
        plan, final, calls = answer(query, naive)
        print(f"\n[{label}] {query}")
        print(f"  subagents invoked: {plan}  ({len(plan)} of 3)")
        print(f"  API calls used:    {calls}")
        print("  answer:", final.strip().replace("\n", "\n         "))
