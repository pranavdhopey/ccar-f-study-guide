"""
Example 4: the guide's Build Exercise, "Build a Hub-and-Spoke Research Coordinator".

The exercise has six steps. Each is marked STEP 1 ... STEP 6 below.

    python 04_build_exercise.py

The search and document data are made up. The search stub deliberately returns only an
OVERVIEW for a quick search, and concrete FIGURES only when the query asks for them. The
internal documents hold figures for four technologies and nothing for tidal or fusion.
So after the first pass, tidal and fusion are only "partially covered", and the
refinement loop (STEP 5) has real work to do.
"""
import json

from agent_kit import STATS, ask, parse_json, run_agent

TOPIC = "renewable energy technologies"
GOAL = f"Write a balanced overview of {TOPIC}."
EXPECTED = ["solar", "wind", "geothermal", "tidal", "biomass", "fusion"]  # used in STEP 6
MAX_REFINEMENTS = 3  # safety bound for the loop in STEP 5

# ------------------------------------------------------------------ stub tools (made-up demo data)
OVERVIEW = {
    "solar": "Solar panels turn sunlight into electricity.",
    "wind": "Wind turbines turn moving air into electricity.",
    "geothermal": "Geothermal plants use heat from underground rock and water.",
    "tidal": "Tidal energy uses the movement of ocean tides to spin turbines.",
    "biomass": "Biomass burns or ferments plant and waste material for energy.",
    "fusion": "Fusion would make power by merging light atoms, as the sun does.",
}
FIGURES = {
    "solar": "Typical utility solar cost: about 40 per MWh. Capacity factor around 25%.",
    "wind": "Onshore wind: about 35 per MWh. Capacity factor around 35%.",
    "geothermal": "Geothermal: about 70 per MWh. Capacity factor above 70%.",
    "tidal": "Tidal stream pilots: about 200 per MWh. Capacity factor around 40%.",
    "biomass": "Biomass: about 90 per MWh. Capacity factor around 60%.",
    "fusion": "Fusion: no commercial plant yet. Experimental costs are in the billions.",
}
DOCS = {k: FIGURES[k] for k in ("solar", "wind", "geothermal", "biomass")}  # nothing on tidal or fusion


def web_search(query):
    q = query.lower()
    key = next((k for k in OVERVIEW if k in q), None)
    if key is None:
        return "No results."
    asks_for_figures = any(w in q for w in ("cost", "capacity", "figure", "number"))
    return FIGURES[key] if asks_for_figures else OVERVIEW[key]


def read_document(subject):
    key = next((k for k in DOCS if k in subject.lower()), None)
    return DOCS[key] if key else "No internal document found for that subject."


WEB_TOOLS = [{
    "name": "web_search", "description": "Search the web. Returns a short text result.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]
DOC_TOOLS = [{
    "name": "read_document", "description": "Read the internal document about one subject.",
    "input_schema": {"type": "object", "properties": {"subject": {"type": "string"}}, "required": ["subject"]},
}]

# ================================================================== STEP 1: the coordinator
# A system prompt that defines its role as the orchestrating hub. It never researches itself.
COORDINATOR_SYSTEM = (
    "You are the research coordinator, the hub of a multi-agent system. You decompose topics, "
    "delegate to subagents, check coverage and decide what to research next. You never research directly."
)


# ================================================================== STEP 2: decomposition (5+ subtopics)
def decompose(topic):
    reply = ask(
        COORDINATOR_SYSTEM,
        f"Topic: {topic}\nSplit it into subtopics that together cover the WHOLE topic, including "
        "emerging technologies and not only the best-known ones.\n"
        "Return ONLY a JSON list of 5 to 8 short subtopic names.",
    )
    subtopics = parse_json(reply)
    assert len(subtopics) >= 5, f"Decomposition too narrow: {subtopics}"
    return subtopics


# ================================================================== STEP 3: two subagents, explicit context
def web_search_subagent(subtopics, instructions):
    task = (
        f"Research goal: {GOAL}\n"
        "You cover the WEB only. A colleague covers the internal documents, so do not look there.\n"
        f"Subtopics assigned to you: {json.dumps(subtopics)}\n"
        f"Instructions: {instructions}\n"
        "Report as one line per subtopic: '<subtopic>: <findings>'."
    )
    return run_agent(
        "You are the web search subagent. Use the web_search tool.",
        task, WEB_TOOLS, {"web_search": web_search},
    )


def document_subagent(subtopics):
    task = (
        f"Research goal: {GOAL}\n"
        "You cover the INTERNAL DOCUMENTS only. A colleague covers the web, so do not guess "
        "from general knowledge.\n"
        f"Subtopics assigned to you: {json.dumps(subtopics)}\n"
        "Call read_document for each one. Report as one line per subtopic: "
        "'<subtopic>: <figures>' or '<subtopic>: no document'."
    )
    return run_agent(
        "You are the document analysis subagent. Use the read_document tool.",
        task, DOC_TOOLS, {"read_document": read_document},
    )


# ================================================================== STEP 4: aggregate + coverage evaluation
def aggregate(findings):
    return "\n\n".join(f"[{source}]\n{text}" for source, text in findings)


def evaluate_coverage(subtopics, findings):
    reply = ask(
        COORDINATOR_SYSTEM,
        f"Subtopics: {json.dumps(subtopics)}\n\nFindings so far:\n{aggregate(findings)}\n\n"
        "Rate each subtopic: 'well covered' (explains how it works AND gives a concrete cost or "
        "capacity figure), 'partially covered', or 'missing'.\n"
        "Return ONLY a JSON object mapping each subtopic to its rating.",
    )
    return parse_json(reply)


def show(coverage, title):
    print(f"\n{title}")
    for subtopic, rating in coverage.items():
        print(f"  {subtopic:<28} {rating}")


def synthesis_subagent(findings):
    # Isolation again: the synthesis subagent gets everything pasted into its task.
    return run_agent(
        "You are the synthesis subagent. Write a clear report with one short section per subtopic, "
        "using ONLY the findings in your task.",
        f"Goal: {GOAL}\n\nFINDINGS:\n{aggregate(findings)}",
    )


def research(topic):
    subtopics = decompose(topic)
    print("Subtopics:", subtopics)

    # first pass: the two subagents run once each
    findings = [
        ("web, first pass", web_search_subagent(subtopics, "Run exactly one quick overview search per subtopic.")),
        ("documents, first pass", document_subagent(subtopics)),
    ]
    coverage = evaluate_coverage(subtopics, findings)          # STEP 4
    show(coverage, "Coverage after the first pass:")

    # ============================================================== STEP 5: iterative refinement loop
    for round_no in range(1, MAX_REFINEMENTS + 1):
        gaps = [s for s, rating in coverage.items() if rating != "well covered"]
        if not gaps:
            break                                              # coverage is sufficient
        print(f"\nRefinement {round_no}: re-delegating {gaps}")
        findings.append((
            f"web, refinement {round_no}",
            web_search_subagent(gaps, "Earlier results lacked concrete cost or capacity figures "
                                      "for these subtopics. Search specifically for those figures."),
        ))
        coverage = evaluate_coverage(subtopics, findings)
        show(coverage, f"Coverage after refinement {round_no}:")
    else:
        if any(r != "well covered" for r in coverage.values()):
            print(f"\nWARNING: still gaps after {MAX_REFINEMENTS} refinements. Stopping at the safety bound.")

    return subtopics, coverage, synthesis_subagent(findings)


if __name__ == "__main__":
    subtopics, coverage, report = research(TOPIC)
    print("\n================ REPORT ================\n" + report)

    # ============================================================ STEP 6: verify all six types
    text = (report + " " + " ".join(subtopics)).lower()
    missing = [e for e in EXPECTED if e not in text]
    print("\nCheck against the six expected technologies:")
    for e in EXPECTED:
        print(f"  {e:<11} {'covered' if e not in missing else 'MISSING'}")
    if missing:
        print(f"\n{', '.join(missing)} missing. If the subtopic was never assigned, the root cause is "
              "the coordinator's DECOMPOSITION, not the subagents. Fix the decomposition prompt.")
    else:
        well = sum(1 for r in coverage.values() if r == "well covered")
        print(f"\nAll six covered. Coverage: {well} of {len(coverage)} subtopics rated well covered.")
    print(f"Subagent runs: {STATS['subagent_runs']}, API calls: {STATS['api_calls']}")
