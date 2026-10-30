"""
Build quiz.html (interactive) and quiz.md (GitHub-friendly) from quiz.json.

    python tools/build_quiz.py 1-agentic-architecture/1-1-agentic-loops
"""
import html
import json
import pathlib
import sys

LETTERS = "ABCDEFGH"

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root {
  --bg: #fdfbf2; --card: #ffffff; --ink: #1f2a44; --muted: #5b6577; --line: #d9dde6;
  --accent: #1f3a8a; --ok: #1d7a46; --ok-bg: #e4f5ea; --bad: #b3261e; --bad-bg: #fbe9e7;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #14171f; --card: #1c212c; --ink: #e8ebf2; --muted: #9aa4b8; --line: #323a4b;
    --accent: #8fa8ff; --ok: #6fd39a; --ok-bg: #173325; --bad: #ff9b92; --bad-bg: #3a1c19;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 17px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 720px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 1.6rem; line-height: 1.25; margin: 0 0 4px; }
.intro { color: var(--muted); margin: 0 0 16px; }
.bar { position: sticky; top: 0; z-index: 2; display: flex; gap: 12px; align-items: center;
  justify-content: space-between; padding: 10px 14px; margin: 0 -2px 16px; background: var(--card);
  border: 1px solid var(--line); border-radius: 12px; }
.bar button { font: inherit; font-size: .9rem; padding: 4px 12px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--line); background: transparent; color: var(--ink); }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px 18px 14px; margin: 0 0 16px; }
.q-head { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; font-size: .85rem; color: var(--muted); }
.pill { border: 1px solid var(--line); border-radius: 999px; padding: 0 10px; }
.pill.bonus { color: var(--accent); border-color: var(--accent); }
.prompt { margin: 0 0 12px; font-weight: 600; }
.opts { display: grid; gap: 8px; padding: 0; margin: 0; list-style: none; }
.opt { width: 100%; text-align: left; font: inherit; color: var(--ink); background: transparent;
  border: 1.5px solid var(--line); border-radius: 10px; padding: 10px 12px; cursor: pointer;
  display: flex; gap: 10px; }
.opt:hover:not(:disabled) { border-color: var(--accent); }
.opt:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.opt .k { font-weight: 700; color: var(--muted); min-width: 1.2em; }
.opt:disabled { cursor: default; }
.opt.correct { border-color: var(--ok); background: var(--ok-bg); }
.opt.wrong { border-color: var(--bad); background: var(--bad-bg); }
.fb { margin: 12px 0 2px; padding: 10px 12px; border-radius: 10px; background: var(--bg); border-left: 4px solid var(--accent); }
.fb strong.ok { color: var(--ok); } .fb strong.no { color: var(--bad); }
.result { text-align: center; padding: 20px; border: 2px dashed var(--accent); border-radius: 14px; }
.result .big { font-size: 2rem; font-weight: 700; }
[hidden] { display: none !important; }
</style>
</head>
<body>
<main>
  <h1 id="title"></h1>
  <p class="intro" id="intro"></p>
  <div class="bar" aria-live="polite">
    <span id="score"></span>
    <button id="reset" type="button">Start over</button>
  </div>
  <div id="list"></div>
  <div class="result" id="result" hidden>
    <div class="big" id="final"></div>
    <p id="verdict"></p>
  </div>
</main>
<script>
const DATA = __DATA__;
const LETTERS = "ABCDEFGH";
const $ = (id) => document.getElementById(id);
let answered = 0, correct = 0;

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

function updateScore() {
  const total = DATA.questions.length;
  $("score").textContent = `Answered ${answered} of ${total}  ·  Correct ${correct}`;
  if (answered === total) {
    const pct = Math.round((correct / total) * 100);
    $("final").textContent = `${correct} / ${total}  (${pct}%)`;
    $("verdict").textContent = pct >= 80
      ? "Strong. Move on to the next topic, or re-read the notes for anything you missed."
      : "Re-read the notes and the explanations for the ones you missed, then try again.";
    $("result").hidden = false;
  } else {
    $("result").hidden = true;
  }
}

function build() {
  answered = 0; correct = 0;
  $("title").textContent = DATA.title;
  $("intro").textContent = DATA.intro;
  const list = $("list");
  list.replaceChildren();

  DATA.questions.forEach((q, qi) => {
    const card = el("section", "card");
    const head = el("div", "q-head");
    head.append(el("span", "", `Question ${qi + 1}`),
      el("span", "pill" + (q.tag === "bonus" ? " bonus" : ""), q.tag === "bonus" ? "Beyond the exam key" : "Exam topic"));
    card.append(head, el("p", "prompt", q.prompt));

    const ul = el("ul", "opts");
    const buttons = [];
    const fb = el("div", "fb");
    fb.hidden = true;
    fb.setAttribute("role", "status");

    q.options.forEach((text, oi) => {
      const li = el("li");
      const b = el("button", "opt");
      b.type = "button";
      b.append(el("span", "k", LETTERS[oi]), el("span", "", text));
      b.addEventListener("click", () => {
        buttons.forEach((x) => (x.disabled = true));
        const right = oi === q.answer;
        buttons[q.answer].classList.add("correct");
        if (!right) b.classList.add("wrong");
        const label = el("strong", right ? "ok" : "no", right ? "Correct. " : `Not quite. The answer is ${LETTERS[q.answer]}. `);
        fb.replaceChildren(label, document.createTextNode(q.explanation));
        fb.hidden = false;
        answered += 1; if (right) correct += 1;
        updateScore();
      });
      buttons.push(b);
      li.append(b);
      ul.append(li);
    });
    card.append(ul, fb);
    list.append(card);
  });
  updateScore();
}

$("reset").addEventListener("click", () => { build(); window.scrollTo({ top: 0 }); });
build();
</script>
</body>
</html>
"""


def build_md(data):
    out = [f"# {data['title']}", "", data["intro"].replace("Pick an answer to see why it is right or wrong.",
           "Click **Show answer** under each question to check yourself."), ""]
    out.append("> Prefer clicking? Open [`quiz.html`](quiz.html) in a browser for the interactive version "
               "(GitHub does not run it in the file preview, so download the file or use GitHub Pages).")
    out.append("")
    for i, q in enumerate(data["questions"], 1):
        tag = " *(bonus: beyond the exam key)*" if q["tag"] == "bonus" else ""
        out.append(f"### Q{i}.{tag}")
        out.append("")
        out.append(q["prompt"])
        out.append("")
        for oi, text in enumerate(q["options"]):
            out.append(f"- **{LETTERS[oi]}.** {text}")
        out.append("")
        out.append("<details>")
        out.append("<summary>Show answer</summary>")
        out.append("")
        out.append(f"**{LETTERS[q['answer']]}.** {q['options'][q['answer']]}")
        out.append("")
        out.append(q["explanation"])
        out.append("")
        out.append("</details>")
        out.append("")
    return "\n".join(out)


def main():
    folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    data = json.loads((folder / "quiz.json").read_text(encoding="utf-8"))

    for n, q in enumerate(data["questions"], 1):
        assert 0 <= q["answer"] < len(q["options"]), f"Q{n}: answer index out of range"
        assert len(q["options"]) >= 2, f"Q{n}: needs at least 2 options"

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = HTML_TEMPLATE.replace("__TITLE__", html.escape(data["title"])).replace("__DATA__", payload)
    (folder / "quiz.html").write_text(page, encoding="utf-8")
    (folder / "quiz.md").write_text(build_md(data), encoding="utf-8")
    print(f"built {len(data['questions'])} questions -> quiz.html, quiz.md")


if __name__ == "__main__":
    main()
