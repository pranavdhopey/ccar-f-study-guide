"""
Example 1: the minimal agentic loop.

Covers: the loop lifecycle (send, check stop_reason, run tools, append, repeat),
        handling "tool_use" and "end_turn".

    pip install anthropic
    export ANTHROPIC_API_KEY="your-key"
    python 01_minimal_loop.py
"""
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment
MODEL = "claude-sonnet-5-5"

# 1. Tell Claude which tools exist. Claude only ASKS for them; our code runs them.
tools = [
    {
        "name": "get_price",
        "description": "Get the price of one item from the menu.",
        "input_schema": {
            "type": "object",
            "properties": {"item": {"type": "string"}},
            "required": ["item"],
        },
    },
    {
        "name": "multiply",
        "description": "Multiply two numbers.",
        "input_schema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
]


def run_tool(name, args):
    if name == "get_price":
        return {"pizza": 12, "coffee": 3}.get(args["item"].lower(), "not on the menu")
    if name == "multiply":
        return args["a"] * args["b"]


def final_text(response):
    # Join ALL text blocks. Do not assume the text is in content[0].
    return "".join(block.text for block in response.content if block.type == "text")


# 2. The loop
messages = [{"role": "user", "content": "How much do 3 pizzas cost?"}]

while True:  # no cap here on purpose, to keep this minimal. Example 4 adds the safety net.
    response = client.messages.create(
        model=MODEL, max_tokens=1024, tools=tools, messages=messages
    )
    print("stop_reason:", response.stop_reason)

    if response.stop_reason == "end_turn":  # Claude is finished
        print(final_text(response))
        break

    if response.stop_reason != "tool_use":
        # max_tokens, refusal, pause_turn ... = NOT finished normally.
        # Do not guess. Stop and look at what happened.
        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

    # stop_reason == "tool_use": run the tools, hand the results back, go round again
    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:
        if block.type == "tool_use":
            output = run_tool(block.name, block.input)
            print(f"  ran {block.name}({block.input}) -> {output}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
    messages.append({"role": "user", "content": results})
