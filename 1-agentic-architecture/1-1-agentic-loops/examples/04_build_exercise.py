"""
Example 4: the guide's Build Exercise, step by step.

The exercise ("Build a Multi-Tool Agent Loop") has six steps. Each one is marked
STEP 1 ... STEP 6 below so you can find it.

    python 04_build_exercise.py                       # normal run
    python 04_build_exercise.py --runaway --cap 5     # a search that never succeeds: watch the cap fire
"""
import argparse
import ast
import logging
import operator

import anthropic

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("agent")

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

parser = argparse.ArgumentParser()
parser.add_argument("--runaway", action="store_true", help="web_search never finds anything")
parser.add_argument("--cap", type=int, default=20, help="safety cap (the exercise uses 20)")
args = parser.parse_args()

# STEP 6 (part 1): a safety cap constant. NOT the main stopping mechanism.
MAX_ITERATIONS = args.cap

# STEP 5: a prompt that needs a search FIRST, then a calculation using what the search found.
# (Glasshouse Bakery is made up, so Claude cannot know the numbers. It has to search.)
PROMPT = (
    "Search for the price of a Glasshouse Bakery cake and its delivery fee. "
    "Then use the calculator tool to work out the total cost of 3 cakes with one delivery."
)

# STEP 1: two tools with JSON Schema input_schema (name, description, parameters)
tools = [
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression such as '3 * 18.5 + 4.25'.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "e.g. '3 * 18.5 + 4.25'"}},
            "required": ["expression"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the web and return a short text result.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression):
    return round(_eval(ast.parse(expression, mode="eval").body), 4)


def web_search(query):
    """A stub. No internet: returns canned text."""
    if args.runaway:
        return "No results found. Try a different query."
    if "glasshouse" in query.lower():
        return "Glasshouse Bakery: a celebration cake costs $18.50. Delivery is $4.25 per order."
    return "No results found."


TOOLS = {"calculator": calculator, "web_search": web_search}


def run_agent(prompt):
    messages = [{"role": "user", "content": prompt}]
    iterations = 0                                           # STEP 6 (part 2): a counter

    # STEP 2: the loop. Call the API, then inspect stop_reason.
    while iterations < MAX_ITERATIONS:
        iterations += 1
        response = client.messages.create(
            model=MODEL, max_tokens=1024, tools=tools, messages=messages
        )
        log.info("round %d: stop_reason=%s", iterations, response.stop_reason)

        # STEP 4: end_turn means Claude is finished. Return the final text.
        if response.stop_reason == "end_turn":
            log.info("finished in %d round(s) (cap was %d)", iterations, MAX_ITERATIONS)
            return "".join(b.text for b in response.content if b.type == "text")

        if response.stop_reason != "tool_use":
            raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

        # STEP 3: tool_use. Extract the tool_use block(s), run them, and append
        #         BOTH Claude's reply and a user message holding the tool_result(s).
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = TOOLS[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
            except Exception as e:     # tell Claude what went wrong instead of crashing
                output = f"error: {e}"
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output, "is_error": True})
            log.info("   ran %s(%s) -> %s", block.name, block.input, output)
        messages.append({"role": "user", "content": results})

    # STEP 6 (part 3): reached only if the cap ran out. Log a warning.
    log.warning("Hit MAX_ITERATIONS (%d). The agent may be stuck in a runaway loop. Investigate.", MAX_ITERATIONS)
    return None


if __name__ == "__main__":
    print("Prompt:", PROMPT, "\n")
    print("\nFinal answer:", run_agent(PROMPT))
