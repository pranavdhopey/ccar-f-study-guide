"""
Example 3: blame the origin. Narrow decomposition makes gaps that no subagent can fix.

Covers: why a subtopic nobody is assigned never gets researched, and how to trace an
incomplete report back to the coordinator's decomposition.

Same question, two coordinators:
  narrow  - splits it into only two subtopics (ingredients and rent)
  broad   - asks Claude to split it so the WHOLE topic is covered

Every subagent does its assigned job perfectly in both runs.

    python 03_decomposition.py            # both
    python 03_decomposition.py narrow
    python 03_decomposition.py broad
"""
import sys

from agent_kit import ask, parse_json, run_agent

QUESTION = "What drives the costs at Harbour Café?"

# Areas a complete report should mention, and words that show a subtopic or report covers them.
AREAS = {
    "ingredients": ["ingredient", "food", "milk", "supply", "supplies"],
    "rent": ["rent", "lease", "premises"],
    "staff": ["staff", "wage", "labour", "labor", "payroll"],
    "energy": ["energy", "gas", "electric", "utilit"],
    "equipment": ["equipment", "machine", "maintenance"],
    "insurance": ["insurance"],
}

# ------------------------------------------------------------------ stub tool (made-up data)
COST_DATA = {
    "ingredients": "Milk and coffee beans are the biggest line: up 7% year on year.",
    "rent": "Rent is fixed by the lease and unchanged this year.",
    "staff": "Wages rose 5% after the April minimum wage change.",
    "energy": "The gas bill is up 18% since March.",
    "equipment": "The espresso machine needed a 900 repair this spring.",
    "insurance": "Insurance renewed at about 10% higher.",
}
TOOLS = [{
    "name": "lookup_costs",
    "description": "Look up what the café's records say about one cost subtopic.",
    "input_schema": {"type": "object", "properties": {"subtopic": {"type": "string"}}, "required": ["subtopic"]},
}]


def area_of(text):
    t = text.lower()
    return next((a for a, words in AREAS.items() if any(w in t for w in words)), None)


def lookup_costs(subtopic):
    return COST_DATA.get(area_of(subtopic), "No data for that subtopic.")


# ------------------------------------------------------------------ the two coordinators' decompositions
def decompose_narrow(question):
    return ["ingredient costs", "rent"]


def decompose_broad(question):
    reply = ask(
        "You are the research coordinator. You split research questions into subtopics.",
        f"Question: {question}\n"
        "Split it into subtopics that together cover the WHOLE question, not just the obvious "
        "parts. Think about ingredients, people, premises, energy, equipment and fees.\n"
        "Return ONLY a JSON list of 6 to 8 short subtopic names.",
    )
    return parse_json(reply)


# ------------------------------------------------------------------ subagents
def research_subagent(subtopic):
    return run_agent(
        "You are a research subagent. Research ONLY the subtopic you are given, using "
        "lookup_costs. Reply in one or two sentences.",
        f"Research goal: {QUESTION}\nYour subtopic: {subtopic}",
        TOOLS, {"lookup_costs": lookup_costs},
    )


def synthesis_subagent(findings):
    joined = "\n".join(f"- {t}: {f}" for t, f in findings.items())
    return run_agent(
        "You are the synthesis subagent. Write a short report using ONLY the findings in your task. "
        "Do not add costs that are not in the findings.",
        f"Question: {QUESTION}\n\nFINDINGS:\n{joined}",
    )


# ------------------------------------------------------------------ run + diagnose
def run(label, decompose):
    print(f"\n######## {label} coordinator ########")
    subtopics = decompose(QUESTION)
    print("Subtopics assigned:", subtopics)

    findings = {s: research_subagent(s) for s in subtopics}
    report = synthesis_subagent(findings)
    print("\nReport:\n" + report)

    print("\nCoverage check (simple keyword match):")
    missing = []
    for area, words in AREAS.items():
        assigned = any(w in s.lower() for s in subtopics for w in words)
        in_report = any(w in report.lower() for w in words)
        print(f"  {area:<12} assigned to a subagent: {'yes' if assigned else 'NO ':<3}  in report: {'yes' if in_report else 'no'}")
        if not assigned:
            missing.append(area)

    if missing:
        print(f"\nDIAGNOSIS: {', '.join(missing)} were never assigned to any subagent.")
        print("Every subagent did its job. The root cause is the coordinator's DECOMPOSITION.")
        print("Better search queries or a smarter synthesis step could not have fixed this.")
    else:
        print("\nEvery area was assigned, so every area had a subagent to research it.")


if __name__ == "__main__":
    modes = sys.argv[1:] or ["narrow", "broad"]
    if "narrow" in modes:
        run("NARROW", decompose_narrow)
    if "broad" in modes:
        run("BROAD", decompose_broad)
