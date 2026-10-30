# 1.1 Agentic Loops: practice questions

Exam-style questions for CCAR-F Task 1.1. Click **Show answer** under each question to check yourself.

> Prefer clicking? Open [`quiz.html`](quiz.html) in a browser for the interactive version (GitHub does not run it in the file preview, so download the file or use GitHub Pages).

### Q1.

In an agentic loop, Claude decides it needs your lookup_order tool. Who actually runs that function?

- **A.** Claude, on Anthropic's servers, before it replies
- **B.** Claude, but only when tool_choice is set to "any"
- **C.** The Messages API, automatically, using the tool definition
- **D.** Your code, after Claude's response asks for the call

<details>
<summary>Show answer</summary>

**D.** Your code, after Claude's response asks for the call

Claude never runs a tool you define. Its response asks for the call (stop_reason "tool_use"), your code runs the function and sends the result back.

</details>

### Q2.

Which description best matches the agentic loop?

- **A.** A prompting technique that tells Claude to think step by step
- **B.** A retry mechanism that resends a request when the API fails
- **C.** Deterministic control flow in your code that sends requests, runs the tools Claude asks for, and repeats until Claude is finished
- **D.** A single chat turn in which Claude answers one question

<details>
<summary>Show answer</summary>

**C.** Deterministic control flow in your code that sends requests, runs the tools Claude asks for, and repeats until Claude is finished

The loop is ordinary code you write. It is not a prompt trick, a retry loop or a chatbot turn.

</details>

### Q3.

Your loop gets a response with stop_reason "tool_use". What should it do next?

- **A.** Run the requested tool(s), append the results to the conversation history, and send the updated conversation back to Claude
- **B.** Wait until stop_reason is "end_turn" before running anything
- **C.** Return the text to the user, because Claude has answered
- **D.** Start a new conversation containing only the tool result

<details>
<summary>Show answer</summary>

**A.** Run the requested tool(s), append the results to the conversation history, and send the updated conversation back to Claude

Step 3 of the lifecycle: execute the tools, append the results as a new message, send the whole conversation again. Starting fresh would lose the context Claude needs.

</details>

### Q4.

A bakery's support agent answers "Where is my cake order?" Claude's response contains a text block ("Let me check your order") followed by a tool_use block for track_order. The developer's code checks response.content[0].type == "text" and returns, so the customer gets only "Let me check your order". What is the root cause?

- **A.** Claude should be prompted never to write text before a tool call
- **B.** The code treats the presence of text as completion, but Claude can return text alongside tool_use blocks. It should check stop_reason instead
- **C.** The track_order tool definition is missing a description
- **D.** max_tokens is too low, so the response was cut off

<details>
<summary>Show answer</summary>

**B.** The code treats the presence of text as completion, but Claude can return text alongside tool_use blocks. It should check stop_reason instead

This is anti-pattern 3. Text presence says nothing about whether the agent is finished. Fix: continue on "tool_use", stop on "end_turn", whatever content types the response holds.

</details>

### Q5.

A developer ends the loop when Claude's text contains "task complete" or "I'm done". Why is this unreliable?

- **A.** Natural language is ambiguous. Claude might say it finished one step while intending to continue, so the phrase does not reliably mean the whole task is done
- **B.** Claude never writes phrases like that
- **C.** Checking text is much slower than checking stop_reason
- **D.** The check is case-sensitive, so it misses some replies

<details>
<summary>Show answer</summary>

**A.** Natural language is ambiguous. Claude might say it finished one step while intending to continue, so the phrase does not reliably mean the whole task is done

Anti-pattern 1. stop_reason exists to remove exactly this ambiguity: it is deterministic and unambiguous.

</details>

### Q6.

An agent's loop stops after 10 iterations. Tasks that need 12 iterations are cut off, while simple tasks finish in 3 and still run extra loops. What is the best fix?

- **A.** Raise the cap to 15 and keep it as the main stopping rule
- **B.** Remove the stop_reason check and rely on the cap alone
- **C.** Ask Claude to reply "DONE" so the code can stop on that word
- **D.** Make stop_reason the primary control, and keep a cap only as a safety net against runaway agents

<details>
<summary>Show answer</summary>

**D.** Make stop_reason the primary control, and keep a cap only as a safety net against runaway agents

Anti-pattern 2. A fixed cap either cuts off useful work or wastes iterations. Claude signals completion through stop_reason. A generous cap (e.g. 20) is fine as a backup, never as the primary mechanism.

</details>

### Q7.

To save tokens, a developer sends each next request WITHOUT the tool results from the previous step. What happens?

- **A.** Claude remembers the results from the earlier call on the server
- **B.** The API fills in the missing results from its cache
- **C.** The loop finishes faster and the final answer is the same
- **D.** Claude never sees what the tool returned, because the Messages API keeps no server-side memory of the turn, so it has nothing new to reason about

<details>
<summary>Show answer</summary>

**D.** Claude never sees what the tool returned, because the Messages API keeps no server-side memory of the turn, so it has nothing new to reason about

Every request must carry the full history, including tool results. Dropping them leaves the model blind to what the tool returned.

</details>

### Q8.

A tool returns a very large JSON blob and token costs are climbing. What is the right way to reduce them?

- **A.** Shrink what the tool returns, for example by returning only the fields Claude needs
- **B.** Replace the whole history with a short summary on every round
- **C.** Drop the tool result and let Claude guess
- **D.** Lower the iteration cap to 2

<details>
<summary>Show answer</summary>

**A.** Shrink what the tool returns, for example by returning only the fields Claude needs

Keep appending each tool result to the history, but make the results smaller at the source. Summarising away or dropping the history breaks the loop.

</details>

### Q9.

A customer asks for their fitting date. The agent must call lookup_order, then check_diary, and then reply. With a correct loop, what is the minimum number of Messages API requests sent to Claude?

- **A.** 1
- **B.** 2
- **C.** 3
- **D.** 4

<details>
<summary>Show answer</summary>

**C.** 3

Request 1 returns tool_use (lookup_order). Request 2, with that result, returns tool_use (check_diary). Request 3, with both results, returns end_turn with the reply.

</details>

### Q10.

A store's refund policy says any refund over $500 must have manager approval, with no exceptions. Where should that rule be enforced?

- **A.** In the system prompt, asking Claude to always remember it
- **B.** In the tool description only
- **C.** In code that enforces it programmatically, whatever Claude decides (covered in Task 1.4)
- **D.** Nowhere special: model-driven tool selection will handle it

<details>
<summary>Show answer</summary>

**C.** In code that enforces it programmatically, whatever Claude decides (covered in Task 1.4)

Model-driven selection is the default because it flexes. The exception is business logic that demands deterministic compliance (money, security, regulations), which programmatic enforcement overrides.

</details>

### Q11. *(bonus: beyond the exam key)*

Beyond the two exam values: a production loop receives stop_reason "refusal". What is the right way to think about it?

- **A.** Treat it as "tool_use" and run the tools
- **B.** It is a normal HTTP 200 response in which Claude declined to respond, so it is not finished normally and should be handled explicitly rather than assumed to be tool_use or end_turn
- **C.** It is an API error, so retry the same request until it succeeds
- **D.** Treat it exactly like "end_turn" and show the output

<details>
<summary>Show answer</summary>

**B.** It is a normal HTTP 200 response in which Claude declined to respond, so it is not finished normally and should be handled explicitly rather than assumed to be tool_use or end_turn

Current API docs list pause_turn, max_tokens, stop_sequence, refusal and model_context_window_exceeded as well. Treat any value other than end_turn as "not finished, check why". This is beyond what the exam guide v1.0 keys, so it is a bonus question.

</details>
