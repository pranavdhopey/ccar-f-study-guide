"""
Example 3: break the loop on purpose.

Covers: why stop_reason is THE signal, why tool results must be appended, and why an
        iteration cap is a safety net, never the primary stop.

Same question, same tools as example 2. Four loops: three broken, one correct.

    python 03_break_it.py            # run all four
    python 03_break_it.py text       # anti-pattern 3: "text means finished"
    python 03_break_it.py noappend   # forgot to append tool results
    python 03_break_it.py cap        # a cap used as the main stopping rule
    python 03_break_it.py fixed      # the correct loop

NOTE: the system prompt asks Claude to write a sentence before each tool call. That makes
the "text first" bug happen every time instead of only sometimes. Real Claude often does
this on its own, which is exactly why the bug shows up unpredictably in production.
"""
import sys

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
SYSTEM = "Before every tool call, write one short sentence saying what you are about to do."
QUESTION = "Hi, it's Priya. When is the fitting for order W-1042?"

tools = [
    {
        "name": "lookup_order",
        "description": "Look up an order by its id. Returns the customer, item and the fitter_id.",
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
    },
    {
        "name": "check_diary",
        "description": "Get a fitter's next free fitting slot. Needs the fitter_id from lookup_order.",
        "input_schema": {"type": "object", "properties": {"fitter_id": {"type": "string"}}, "required": ["fitter_id"]},
    },
]


def run_tool(name, args):
    if name == "lookup_order":
        return {"customer": "Priya", "item": "double-glazed window", "fitter_id": "F-7"}
    if name == "check_diary":
        return {"fitter_id": args["fitter_id"], "next_free_slot": "Tuesday 4 Nov, 9:00"}


def ask(messages):
    return client.messages.create(
        model=MODEL, max_tokens=1024, system=SYSTEM, tools=tools, messages=messages
    )


def text_of(response):
    return "".join(b.text for b in response.content if b.type == "text")


def run_tools_and_append(messages, response):
    """The correct step 3: append Claude's request, run the tools, append the results."""
    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:
        if block.type == "tool_use":
            out = run_tool(block.name, block.input)
            print(f"    ran {block.name}({block.input})")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(out)})
    messages.append({"role": "user", "content": results})


# ---------------------------------------------------------------- BROKEN 1
def broken_text_check():
    """Anti-pattern 3: 'if the first block is text, Claude must be finished'."""
    messages = [{"role": "user", "content": QUESTION}]
    response = ask(messages)
    print("    stop_reason was:", response.stop_reason)
    if response.content[0].type == "text":  # <-- the bug
        return text_of(response)
    return "(never gets here)"


# ---------------------------------------------------------------- BROKEN 2
def broken_no_append(max_rounds=4):
    """Tool results never reach Claude, so every round looks exactly like round 1."""
    messages = [{"role": "user", "content": QUESTION}]
    for n in range(1, max_rounds + 1):
        response = ask(messages)
        asked = [f"{b.name}({b.input})" for b in response.content if b.type == "tool_use"]
        print(f"    round {n}: stop_reason={response.stop_reason}, Claude asks for {asked}")
        if response.stop_reason == "end_turn":
            return text_of(response)
        for b in response.content:          # we run the tool...
            if b.type == "tool_use":
                run_tool(b.name, b.input)
        # ...but forget to append the assistant message and the tool_result.  <-- the bug
    return f"(gave up after {max_rounds} rounds: Claude kept asking for the same thing)"


# ---------------------------------------------------------------- BROKEN 3
def broken_cap_as_primary(cap=2):
    """A cap as the main stopping rule cuts off work that needs more rounds."""
    messages = [{"role": "user", "content": QUESTION}]
    response = None
    for n in range(1, cap + 1):
        response = ask(messages)
        print(f"    round {n}: stop_reason={response.stop_reason}")
        if response.stop_reason != "tool_use":
            return text_of(response)
        run_tools_and_append(messages, response)
    return f"(cut off by the cap of {cap}. Task needed one more round. No answer for the customer.)"


# ---------------------------------------------------------------- CORRECT
def fixed_loop(max_iterations=20):
    messages = [{"role": "user", "content": QUESTION}]
    for n in range(1, max_iterations + 1):   # the cap is only a backup
        response = ask(messages)
        print(f"    round {n}: stop_reason={response.stop_reason}")
        if response.stop_reason == "end_turn":
            return text_of(response)
        if response.stop_reason != "tool_use":
            raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")
        run_tools_and_append(messages, response)
    return "(hit the safety cap: investigate)"


DEMOS = {
    "text": ("BROKEN 1: 'text first means finished' (anti-pattern 3)", broken_text_check),
    "noappend": ("BROKEN 2: tool results never appended", broken_no_append),
    "cap": ("BROKEN 3: iteration cap as the primary stop (anti-pattern 2)", broken_cap_as_primary),
    "fixed": ("CORRECT: stop_reason decides, cap is only a backup", fixed_loop),
}

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(DEMOS)
    for key in chosen:
        title, fn = DEMOS[key]
        print(f"\n##### {title}")
        print("  RESULT:", fn())
