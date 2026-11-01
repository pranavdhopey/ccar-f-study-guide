"""
Helpers shared by the 1.2 examples. Read topic 1.1 first.

run_agent() is the agentic loop from topic 1.1, wrapped in a function.

A "subagent" in these examples is nothing magic: it is run_agent() (or ask()) called with
its OWN system prompt, its OWN task and its OWN brand-new messages list. That is exactly
why a subagent knows nothing the coordinator does not put in its task.
"""
import json
import logging
import re

import anthropic

MODEL = "claude-sonnet-5-5"
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment
log = logging.getLogger("agent_kit")

# Handy for the examples: how much work did a run cause?
STATS = {"api_calls": 0, "subagent_runs": 0}


def text_of(response):
    """Join ALL text blocks (never assume the text is in content[0])."""
    return "".join(block.text for block in response.content if block.type == "text")


def ask(system, prompt, max_tokens=1024, subagent=False):
    """One request, one answer. No tools, no loop. Use subagent=True for a subagent run."""
    STATS["api_calls"] += 1
    if subagent:
        STATS["subagent_runs"] += 1
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],  # a fresh list: just this one task
    )
    return text_of(response)


def run_agent(system, task, tools=None, impls=None, max_iterations=20):
    """The 1.1 loop as a function: a subagent that can use tools. Returns its final text."""
    STATS["subagent_runs"] += 1
    messages = [{"role": "user", "content": task}]  # a fresh list: just this one task

    for _ in range(max_iterations):  # the cap is only a safety net
        kwargs = dict(model=MODEL, max_tokens=2048, system=system, messages=messages)
        if tools:
            kwargs["tools"] = tools
        response = client.messages.create(**kwargs)
        STATS["api_calls"] += 1

        if response.stop_reason == "end_turn":
            return text_of(response)
        if response.stop_reason != "tool_use":
            raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

        messages.append({"role": "assistant", "content": response.content})
        results = []  # one tool_result per tool_use (Claude may ask for several at once)
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = impls[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
            except Exception as e:  # report the failure to Claude instead of crashing
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": f"{type(e).__name__}: {e}", "is_error": True})
        messages.append({"role": "user", "content": results})

    log.warning("Subagent hit its safety cap of %d iterations.", max_iterations)
    return "(no result: the subagent hit its safety cap)"


def parse_json(text):
    """Pull the first JSON value out of a reply (handles ```json fences and chatter around it)."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1)
    starts = [i for i in (text.find("["), text.find("{")) if i != -1]
    if not starts:
        raise ValueError(f"No JSON found in: {text[:80]!r}")
    return json.JSONDecoder().raw_decode(text[min(starts):])[0]
