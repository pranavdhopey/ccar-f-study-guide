"""
Example 2: hub-and-spoke. Every message goes through the coordinator.

Covers: centralised communication routing (observability), explicit context passing.

The coordinator sends work to three subagents and prints every hop. Notice that the
web search subagent's findings reach the synthesis subagent ONLY because the coordinator
pastes them into the synthesis prompt. Subagents never talk to each other.

    python 02_hub_and_spoke.py
"""
from agent_kit import STATS, run_agent

QUESTION = "What is driving the rising costs at Harbour Café this year?"

# ------------------------------------------------------------------ stub tools (made-up data)
SEARCH_TOOLS = [{
    "name": "search_news",
    "description": "Search recent news. Returns short text snippets.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]
INVOICE_TOOLS = [{
    "name": "read_invoices",
    "description": "Read the café's own invoices for one category: ingredients, energy, staff or rent.",
    "input_schema": {"type": "object", "properties": {"category": {"type": "string"}}, "required": ["category"]},
}]


def search_news(query):
    return ("Dairy wholesale prices rose about 6% this year. Natural gas prices for small businesses "
            "rose sharply in spring. The minimum wage went up in April. (made-up demo data)")


def read_invoices(category):
    data = {
        "ingredients": "Milk and coffee beans: spend up 7% year on year.",
        "energy": "Gas bill up 18% since March; electricity up 4%.",
        "staff": "Wages up 5% after the April minimum wage change.",
        "rent": "Rent unchanged this year.",
    }
    return data.get(category.lower(), "No invoices for that category.")


# ------------------------------------------------------------------ the hop log
LOG = []


def hop(sender, receiver, note):
    LOG.append((sender, receiver))
    print(f"  {sender:<14} -> {receiver:<14} {note}")


# ------------------------------------------------------------------ three subagents
def web_search_subagent(task):
    return run_agent(
        "You are the web search subagent. Use search_news to find facts for your task. "
        "Reply with 3 short bullet points.",
        task, SEARCH_TOOLS, {"search_news": search_news},
    )


def invoice_subagent(task):
    return run_agent(
        "You are the invoice analyst subagent. Use read_invoices for each category your task "
        "needs. Reply with one short line per category.",
        task, INVOICE_TOOLS, {"read_invoices": read_invoices},
    )


def synthesis_subagent(task):
    return run_agent(
        "You are the synthesis subagent. Use ONLY the findings in your task. Rank the cost "
        "drivers from biggest to smallest in 5 lines or fewer.",
        task,
    )


# ------------------------------------------------------------------ the coordinator (the hub)
def coordinator(question):
    hop("user", "coordinator", "question")

    hop("coordinator", "web_search", "task + the research question")
    web = web_search_subagent(
        f"Research question: {question}\nFind news that explains cost changes for cafés."
    )
    hop("web_search", "coordinator", "findings")

    hop("coordinator", "invoices", "task + the research question")
    inv = invoice_subagent(
        f"Research question: {question}\nCheck the categories: ingredients, energy, staff, rent."
    )
    hop("invoices", "coordinator", "findings")

    # Isolation: the synthesis subagent has seen NOTHING so far. The coordinator must hand it
    # everything it needs, by pasting both sets of findings into the prompt.
    hop("coordinator", "synthesis", "task + BOTH sets of findings pasted in")
    answer = synthesis_subagent(
        f"Research question: {question}\n\nNEWS FINDINGS:\n{web}\n\nINVOICE FINDINGS:\n{inv}"
    )
    hop("synthesis", "coordinator", "ranked drivers")

    hop("coordinator", "user", "final answer")
    return answer


if __name__ == "__main__":
    print("Message flow:")
    answer = coordinator(QUESTION)
    print("\nAnswer:\n" + answer)

    bypass = [h for h in LOG if "coordinator" not in h]
    print(f"\nHops that bypass the coordinator: {len(bypass)}   (hub-and-spoke means this is always 0)")
    print(f"Subagent runs: {STATS['subagent_runs']}, API calls: {STATS['api_calls']}")
