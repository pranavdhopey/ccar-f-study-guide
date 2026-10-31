"""
Example 5: a realistic agent. Find idle VMs and estimate the monthly saving.

Covers everything so far, plus the two things real agents hit constantly:
  * PARALLEL tool calls: one reply from Claude can hold several tool_use blocks.
    Run them all, and send ALL the results back in ONE user message.
  * TOOL ERRORS: if a tool fails, send the error back as a tool_result with
    is_error=True so Claude can adapt, instead of crashing the loop.

All data here is made up and the prices are illustrative, not real cloud prices.

    python 05_cloud_ops_agent.py
"""
import ast
import logging
import operator

import anthropic

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("agent")

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
MAX_ITERATIONS = 20  # safety net only

PROMPT = (
    "In project 'demo-prod', find the VMs with average CPU under 5%. "
    "Look up the monthly cost of each idle VM's machine type, then use the calculator "
    "to add them up and tell me how much we could save per month. "
    "If a price is unavailable, say which VM and leave it out of the total."
)

tools = [
    {
        "name": "list_instances",
        "description": "List VM instances in a project with their machine type and average CPU percent.",
        "input_schema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]},
    },
    {
        "name": "get_monthly_cost",
        "description": "Get the monthly cost in USD of one machine type.",
        "input_schema": {"type": "object", "properties": {"machine_type": {"type": "string"}}, "required": ["machine_type"]},
    },
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression such as '283 + 49'.",
        "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
    },
]

PRICES = {"e2-standard-2": 49, "e2-standard-4": 98, "n2-standard-8": 283}  # made up


def list_instances(project):
    return [
        {"name": "web-1", "machine_type": "e2-standard-4", "avg_cpu_pct": 62},
        {"name": "batch-7", "machine_type": "n2-standard-8", "avg_cpu_pct": 3},
        {"name": "dev-box", "machine_type": "e2-standard-2", "avg_cpu_pct": 2},
        {"name": "legacy-db", "machine_type": "custom-96-ultramem", "avg_cpu_pct": 1},
    ]


def get_monthly_cost(machine_type):
    return PRICES[machine_type]  # raises KeyError for an unknown type, on purpose


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    raise ValueError("unsupported expression")


def calculator(expression):
    return _eval(ast.parse(expression, mode="eval").body)


TOOLS = {"list_instances": list_instances, "get_monthly_cost": get_monthly_cost, "calculator": calculator}


def run_agent(prompt):
    messages = [{"role": "user", "content": prompt}]

    for n in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(model=MODEL, max_tokens=1024, tools=tools, messages=messages)
        calls = [b for b in response.content if b.type == "tool_use"]
        log.info("round %d: stop_reason=%s, tool calls this round: %d", n, response.stop_reason, len(calls))

        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason != "tool_use":
            raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

        messages.append({"role": "assistant", "content": response.content})

        results = []                      # ONE list, one tool_result per tool_use, matched by id
        for block in calls:
            try:
                output = TOOLS[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
                log.info("   %s(%s) -> %s", block.name, block.input, output)
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": msg, "is_error": True})
                log.info("   %s(%s) FAILED -> %s", block.name, block.input, msg)

        messages.append({"role": "user", "content": results})   # all results in ONE message

    log.warning("Hit MAX_ITERATIONS (%d). Investigate.", MAX_ITERATIONS)
    return None


if __name__ == "__main__":
    print(run_agent(PROMPT))
