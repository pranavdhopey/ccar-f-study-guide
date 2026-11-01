# 1.2 Multi-Agent Orchestration: practice questions

Exam-style questions for CCAR-F Task 1.2. Click **Show answer** under each question to check yourself.

> Prefer clicking? Open [`quiz.html`](quiz.html) in a browser for the interactive version (GitHub does not run it in the file preview, so download the file or use GitHub Pages).

### Q1.

Which multi-agent architecture does the exam test?

- **A.** A peer-to-peer mesh where subagents message each other directly
- **B.** Hub-and-spoke: a coordinator at the centre with subagents as the spokes
- **C.** A single agent with no subagents
- **D.** A chain where each subagent calls the next one

<details>
<summary>Show answer</summary>

**B.** Hub-and-spoke: a coordinator at the centre with subagents as the spokes

The exam tests one pattern: hub-and-spoke. The coordinator receives the task, splits it up, delegates, aggregates, and routes all information.

</details>

### Q2.

A synthesis subagent needs what the web search subagent found. What is the right way to get it there?

- **A.** The synthesis subagent reads the web search subagent's conversation history
- **B.** The coordinator sets up a memory the two subagents share automatically
- **C.** The web search subagent returns its findings to the coordinator, which includes them in the synthesis subagent's prompt
- **D.** The web search subagent calls the synthesis subagent directly to save a step

<details>
<summary>Show answer</summary>

**C.** The web search subagent returns its findings to the coordinator, which includes them in the synthesis subagent's prompt

All communication routes through the coordinator, and a subagent only knows what is in its prompt. Example 2 pastes both sets of findings into the synthesis task.

</details>

### Q3.

A coordinator has had a twenty-turn conversation with the user and now starts a new subagent. What does the subagent know about those twenty turns?

- **A.** Only what the coordinator writes into the subagent's prompt
- **B.** All of it: subagents inherit the coordinator's conversation history
- **C.** The coordinator's system prompt, but nothing else
- **D.** The last five messages, automatically

<details>
<summary>Show answer</summary>

**A.** Only what the coordinator writes into the subagent's prompt

Subagents do not inherit history. They have no access to the coordinator's system prompt (unless it is included), earlier messages, other subagents' results, or shared memory.

</details>

### Q4.

A multi-agent system writes a report on "risks facing a coastal town". It covers flooding and erosion in depth and every subagent did its assigned job well, but the report says nothing about tourism decline or an ageing population. Where is the root cause?

- **A.** The synthesis subagent should have invented the missing sections
- **B.** The web search subagent's queries were too narrow
- **C.** The subagents needed a larger context window
- **D.** The coordinator's decomposition never assigned those topics to any subagent

<details>
<summary>Show answer</summary>

**D.** The coordinator's decomposition never assigned those topics to any subagent

A subtopic nobody is assigned never gets researched. When whole topics are missing (scope), suspect the decomposition first. Better queries or a smarter synthesis step cannot add an area that no subagent was given.

</details>

### Q5.

A teammate proposes letting subagents message each other directly to save time. Why does the exam treat this as the wrong answer?

- **A.** Subagents cannot produce text that another agent can read
- **B.** It bypasses the coordinator, losing observability, consistent error handling and controlled information flow
- **C.** It is slower in every case, which is its only drawback
- **D.** It requires every subagent to use the same model

<details>
<summary>Show answer</summary>

**B.** It bypasses the coordinator, losing observability, consistent error handling and controlled information flow

Even when offered as an efficiency gain, direct inter-subagent communication gives up the three benefits of a single hub.

</details>

### Q6.

A subagent returns an incomplete answer for its task. What should you check first?

- **A.** Whether the subagent's model is too small
- **B.** Whether the synthesis subagent hid the missing part
- **C.** Whether the coordinator gave it the right input, meaning the full context in its prompt
- **D.** Whether the user's question was too long

<details>
<summary>Show answer</summary>

**C.** Whether the coordinator gave it the right input, meaning the full context in its prompt

Blame the origin, not the output. Subagents start blank, so incomplete output often traces back to what the coordinator did or did not pass in.

</details>

### Q7.

A user asks, "What time does the council recycling centre open?" How should a well-designed coordinator handle it?

- **A.** Invoke only the subagent(s) the question needs, here just web search
- **B.** Run the full pipeline anyway so every query is handled the same way
- **C.** Run every subagent in parallel and keep whichever answers first
- **D.** Have the synthesis subagent answer from its own knowledge without searching

<details>
<summary>Show answer</summary>

**A.** Invoke only the subagent(s) the question needs, here just web search

Dynamic subagent selection: analyse what the query needs and invoke only those subagents. A simple factual question needs only web search.

</details>

### Q8.

To cut costs, a team runs every query through all subagents and caches the unused results. Why does caching not fix the problem?

- **A.** Caching cannot be used with subagents
- **B.** Cached results are always out of date
- **C.** Unused results always make the final answer worse
- **D.** Invoking unneeded subagents still adds latency and API overhead, so the coordinator should choose subagents per query

<details>
<summary>Show answer</summary>

**D.** Invoking unneeded subagents still adds latency and API overhead, so the coordinator should choose subagents per query

The cost is incurred when the unneeded subagents run, cached or not. Select the subagents each query actually needs.

</details>

### Q9.

Two subagents keep searching the same sources and return duplicate findings. Which coordinator responsibility addresses this?

- **A.** Iterative refinement: re-run both until their results differ
- **B.** Research scope partitioning: give each subagent distinct subtopics or source types
- **C.** Dynamic selection: drop one of them for every query
- **D.** Communication routing: let them compare notes directly

<details>
<summary>Show answer</summary>

**B.** Research scope partitioning: give each subagent distinct subtopics or source types

Partition the scope so no two subagents cover the same ground. In example 4, one subagent covers the web and the other covers internal documents.

</details>

### Q10.

A synthesis draft has no section on insurance costs, though the topic needs one. What does a good coordinator do?

- **A.** Accept the draft and add a disclaimer
- **B.** Ask the synthesis subagent to guess the insurance figures
- **C.** Re-delegate a targeted search for insurance costs, then synthesise again and re-check coverage
- **D.** Restart all the research from the original question

<details>
<summary>Show answer</summary>

**C.** Re-delegate a targeted search for insurance costs, then synthesise again and re-check coverage

That is the iterative refinement loop: evaluate the output for gaps, re-delegate with targeted queries, and re-run synthesis until coverage is sufficient.

</details>

### Q11.

Which of these is NOT a benefit of routing all subagent communication through one coordinator?

- **A.** Subagents automatically share each other's memory
- **B.** Every message can be logged and monitored in one place
- **C.** Errors are handled with one consistent recovery policy
- **D.** The coordinator controls what context each subagent receives

<details>
<summary>Show answer</summary>

**A.** Subagents automatically share each other's memory

The benefits are observability, consistent error handling and controlled information flow. Subagents do not share memory: the coordinator passes context explicitly.

</details>

### Q12.

A subagent fails partway through its task. In hub-and-spoke, who decides how to recover (retry, re-delegate, or carry on without it)?

- **A.** The failed subagent, by calling another subagent itself
- **B.** The user, in every case
- **C.** The next subagent in the chain
- **D.** The coordinator, applying a consistent recovery policy

<details>
<summary>Show answer</summary>

**D.** The coordinator, applying a consistent recovery policy

Handling errors is one of the coordinator's responsibilities, which is what makes recovery consistent across subagents.

</details>

### Q13.

A web search subagent is invoked twice in one run, and the second invocation needs to know what the first one found. What must the coordinator do?

- **A.** Nothing: subagents share memory between invocations
- **B.** Include the first invocation's findings in the second invocation's prompt
- **C.** Nothing: the API remembers earlier calls
- **D.** Rename the subagent so it is recognised the second time

<details>
<summary>Show answer</summary>

**B.** Include the first invocation's findings in the second invocation's prompt

Subagents do not share memory between invocations. A second invocation knows nothing about the first unless the coordinator passes it along. Example 1, run C, shows this.

</details>

### Q14.

A report has a section on geothermal energy that is shallow, while the solar section is detailed. The coordinator assigned both subtopics. What should you suspect first?

- **A.** A missing subtopic in the decomposition
- **B.** The solar subagent using up the shared memory
- **C.** What that subagent was told and given: its prompt, tools and context for geothermal
- **D.** The report's formatting

<details>
<summary>Show answer</summary>

**C.** What that subagent was told and given: its prompt, tools and context for geothermal

The subtopic was assigned, so decomposition is not the problem. A thin section is a depth problem: look at that subagent's instructions, tools and context. A missing section is a scope problem and points to the decomposition.

</details>

### Q15.

An iterative refinement loop re-delegates to fill coverage gaps. How should it end?

- **A.** When coverage is sufficient, with a maximum number of rounds as a safety bound
- **B.** After exactly one round, always
- **C.** Only when it reaches the maximum number of rounds
- **D.** When the synthesis subagent writes "done"

<details>
<summary>Show answer</summary>

**A.** When coverage is sufficient, with a maximum number of rounds as a safety bound

Like the loop in 1.1, it should end on its real signal (sufficient coverage), with a maximum round count as a backup. Example 4 stops at 3 refinements with a warning.

</details>

### Q16. *(bonus: beyond the exam key)*

A study note says subagents can never spawn other subagents. According to the lesson's current-state note, how accurate is that?

- **A.** Fully accurate in every Claude product
- **B.** Wrong: subagents can spawn an unlimited number of layers
- **C.** Accurate, but only for web search subagents
- **D.** A simplification for the exam: in Claude Code a subagent can spawn subagents, up to three layers below the main conversation

<details>
<summary>Show answer</summary>

**D.** A simplification for the exam: in Claude Code a subagent can spawn subagents, up to three layers below the main conversation

The lesson notes this as the current state (checked October 2026). The exam still keys hub-and-spoke, so answer exam questions with the coordinator at the centre.

</details>
