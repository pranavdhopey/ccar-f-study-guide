"""
Example 2: watch the conversation history grow.

Covers: "append tool results to the conversation history". The API remembers nothing,
        so every request carries the WHOLE history. This script prints it each round.

Scenario: a glazier's support agent. To find a fitting date it must
    1. look up the order (this returns a fitter_id), THEN
    2. check that fitter's diary (needs the fitter_id from step 1).
Step 2 depends on step 1, so Claude cannot do them at the same time.

    python 02_watch_the_history.py
"""
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

tools = [
    {
        "name": "lookup_order",
        "description": "Look up an order by its id. Returns the customer, item and the fitter_id.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "check_diary",
        "description": "Get a fitter's next free fitting slot. Needs the fitter_id from lookup_order.",
        "input_schema": {
            "type": "object",
            "properties": {"fitter_id": {"type": "string"}},
            "required": ["fitter_id"],
        },
    },
]


def run_tool(name, args):
    if name == "lookup_order":
        return {"customer": "Priya", "item": "double-glazed window", "fitter_id": "F-7"}
    if name == "check_diary":
        return {"fitter_id": args["fitter_id"], "next_free_slot": "Tuesday 4 Nov, 9:00"}


def show_history(messages):
    """Print one line per message so you can SEE what is being sent to Claude."""
    print(f"  --- history sent next: {len(messages)} message(s) ---")
    for i, m in enumerate(messages):
        parts = []
        content = m["content"]
        if isinstance(content, str):
            parts.append(f'text: "{content[:60]}"')
        else:
            for b in content:
                kind = b["type"] if isinstance(b, dict) else b.type
                if kind == "text":
                    text = b["text"] if isinstance(b, dict) else b.text
                    parts.append(f'text: "{text[:50]}"')
                elif kind == "tool_use":
                    parts.append(f"tool_use: {b.name}({b.input})")
                elif kind == "tool_result":
                    parts.append(f"tool_result: {b['content']}")
        print(f"  [{i}] {m['role']:<9} " + "  +  ".join(parts))


messages = [{"role": "user", "content": "Hi, it's Priya. When is the fitting for order W-1042?"}]
round_no = 0

while True:
    round_no += 1
    print(f"\n=== Round {round_no}: sending {len(messages)} message(s) ===")
    response = client.messages.create(model=MODEL, max_tokens=1024, tools=tools, messages=messages)
    print("stop_reason:", response.stop_reason)

    if response.stop_reason == "end_turn":
        print("\nFinal answer:", "".join(b.text for b in response.content if b.type == "text"))
        break
    if response.stop_reason != "tool_use":
        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

    messages.append({"role": "assistant", "content": response.content})   # +1: what Claude asked for
    results = []
    for block in response.content:
        if block.type == "tool_use":
            output = run_tool(block.name, block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
    messages.append({"role": "user", "content": results})                  # +1: what the tool returned
    show_history(messages)
