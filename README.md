# CCAR-F Study Guide

Plain-language notes, runnable examples and practice questions for the **Claude Certified Architect – Foundations (CCAR-F)** exam, one topic at a time.

> **Unofficial.** This is a personal study guide. It is not affiliated with or endorsed by Anthropic. Notes are written in my own words, based on the lessons at [claudecertificationguide.com](https://claudecertificationguide.com/learn) and Anthropic's public documentation. Check the official exam guide for what is actually tested.

## How each topic is laid out

Every topic folder has the same files, so you always know where to look:

| File | Purpose |
|---|---|
| `README.md` | The explanation, in simple words |
| `notes.png`, `notes-2.png` | Handwritten-style summary pages |
| `examples/` | Small runnable examples, numbered in the order to run them (where the topic has them) |
| `quiz.html` / `quiz.md` | Exam-style practice questions: interactive, or click-to-reveal |

## Progress

| Domain | Topics | Done |
|---|---|---|
| [1. Agentic Architecture & Orchestration](1-agentic-architecture/) | 7 | 2 of 7 |
| 2. Tool Design & MCP Integration | | not started |
| 3. Claude Code Configuration & Workflows | | not started |
| 4. Prompt Engineering & Structured Output | | not started |
| 5. Context Management & Reliability | | not started |

**Start here:** [1.1 Agentic Loops](1-agentic-architecture/1-1-agentic-loops/)

## Repo layout

```
assets/fonts/        handwriting fonts shared by all notes (SIL Open Font License)
tools/               render_notes.py (notes.html -> notes.png), build_quiz.py (quiz.json -> quiz files)
1-agentic-architecture/
  1-1-agentic-loops/ ...one folder per topic, same files in each
```

## Running the examples

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"     # never commit your key
python 1-agentic-architecture/1-1-agentic-loops/examples/01_minimal_loop.py
```

## Adding a new topic

1. Copy a finished topic folder (e.g. `1-1-agentic-loops`) to the new topic's name and replace its contents.
2. Edit `quiz.json`, then run `python tools/build_quiz.py <topic-folder>`.
3. Edit `notes.html`, then run `python tools/render_notes.py <topic-folder>` (needs `pip install playwright && playwright install chromium`).
4. Update the status table in the domain README and the progress table above.

## License

Code is MIT licensed (see `LICENSE`). The handwriting fonts in `assets/fonts/` keep their own licenses.
