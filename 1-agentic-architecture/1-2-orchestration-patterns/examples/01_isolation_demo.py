"""
Example 1: subagents start with a blank slate.

Covers: ISOLATION. A subagent does not inherit the coordinator's conversation, its system
prompt, other subagents' results, or any shared memory. It knows only what is in its prompt.

    pip install anthropic
    export ANTHROPIC_API_KEY="your-key"
    python 01_isolation_demo.py

The subagent's system prompt tells it to use ONLY what the task contains and to say so if
something is missing. That keeps the demo honest: without it, a model may simply guess.
"""
from agent_kit import ask

SUBAGENT_SYSTEM = (
    "You are a subagent. Use ONLY the information given in your task. "
    "If the task does not contain what you need, say so plainly instead of guessing."
)

# The COORDINATOR knows this fact. Subagents do not, unless it is put in their prompt.
FACT = "Harbour Café's gas bill rose 18% in March."
print("The coordinator knows:", FACT)

print("\n--- Run A: the coordinator forgets to pass the fact on ---")
a = ask(
    SUBAGENT_SYSTEM,
    "Write one sentence about how Harbour Café's gas bill changed in March.",
    subagent=True,
)
print("subagent says:", a)

print("\n--- Run B: the coordinator puts the fact in the subagent's prompt ---")
b = ask(
    SUBAGENT_SYSTEM,
    f"Background: {FACT}\n\nWrite one sentence about how Harbour Café's gas bill changed in March.",
    subagent=True,
)
print("subagent says:", b)

print("\n--- Run C: a NEW invocation. Does it remember run B? (no shared memory between runs) ---")
c = ask(
    SUBAGENT_SYSTEM,
    "By how much did Harbour Café's gas bill rise in March?",
    subagent=True,
)
print("subagent says:", c)

print("\nTakeaway: every subagent request holds ONE message, the task you wrote.")
print("If the output is missing something, check what you PUT IN the prompt before blaming the subagent.")
