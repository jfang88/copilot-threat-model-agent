"""Rebuild the agent pack from source.

Generates TM-03 and TM-04 from the generator script and the example model, runs the
generator on the example, and converts all knowledge files to .docx for upload to Copilot.

Usage (from repo root):  python tools/build_knowledge.py
Requires: Python 3.9+, pandas + openpyxl (for the register), pandoc (for .docx).
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "knowledge" / "src"
OUT = ROOT / "knowledge"
EX = ROOT / "examples"
GEN = ROOT / "generator" / "tm_generator.py"

sys.path.insert(0, str(GEN.parent))
import tm_generator as g  # noqa: E402

model = json.loads((EX / "example_model.json").read_text(encoding="utf-8"))
script = GEN.read_text(encoding="utf-8")

# 1. Example outputs
warns = g.validate(model)
assert not warns, warns
ix = g.index(model)
g.drawio(model, str(EX / "example_threat_model.drawio"), ix)
g.register(model, str(EX / "example_threat_model_register.xlsx"), ix)
g.threatdragon(model, str(EX / "example_threatdragon.json"), ix)
g.deck(model, str(EX / "example_deck.pptx"), ix)
_imgs = []
import os, tempfile, zipfile
with tempfile.TemporaryDirectory() as _d:
    _cwd = os.getcwd(); os.chdir(_d)
    try:
        _imgs = g.pngs(model, "example", ix)
        with zipfile.ZipFile(EX / "example_diagrams_png.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for f in _imgs: z.write(f)
        g.embed_images(str(EX / "example_threat_model_register.xlsx"), [os.path.join(_d, f) for f in _imgs], ix)
    finally:
        os.chdir(_cwd)
order = sorted(model["diagrams"], key=lambda d: (d.get("level", 0), d["id"]))
mers = {d["id"]: g.mermaid(model, d["id"], ix) for d in order}
mers.update({a["id"]: g.mermaid_attack(model, a["id"], ix) for a in model.get("attack_paths", [])})
(EX / "example_dfd.mmd").write_text("\n\n".join(f"%% {k}\n{v}" for k, v in mers.items()) + "\n", encoding="utf-8")

# 2. TM-03
(SRC / "TM-03_Generator_and_Schema.md").write_text(f"""---
title: "TM-03 Generator Script and JSON Model Schema"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v2.3"
---

# TM-03 What the generator does

tm_generator.py turns one JSON threat model (all levels) into outputs that always agree with each other:

- <system>.drawio - one page per diagram (L0, L1-P#, L2-P#.#). Decomposed processes are double ellipses marked ⊞ and link to their child page; context elements are grey and link back to the page that defines them; every page has a Back link. Hover any element, flow or threat badge for its document references and threats.
- <system>_register.xlsx - one workbook for all levels: Read me, Threats (Problem, Solution and Document reference grouped together, with Refines / Refined by / Related / Arch. improvement / Open questions cross references as clickable links), Arch improvements, Open questions, Elements & flows, Diagrams, Documents.
- <system>_model.json - the model, so the run can be repeated or updated later.
- <system>_threatdragon.json - OWASP Threat Dragon v2 model: one Threat Dragon diagram per level, trust boundary boxes, actors/processes/stores/flows, and every threat on its element or flow with severity, STRIDE type, mitigation, score, and the T# ID, references and cross references in its title and description. Context elements are marked out of scope. Open it in Threat Dragon (web or desktop) with Open an existing threat model.
- <system>_report.md - the full Markdown report: scope, decomposition map, every diagram as Mermaid with its threat table, threat and LINDDUN summary, attack paths (Mermaid + step tables), review, improvements, questions. It is also printed between REPORT_START and REPORT_END; the agent pastes it into the chat unchanged.
- <system>_deck.pptx - PowerPoint deck built from native, editable shapes (needs python-pptx): executive summary, decomposition map, one DFD slide per diagram with glued connectors, threat tables, attack path chain slides, improvements, questions, legend. Action titles and a source line on every slide.
- <system>_diagrams_png.zip - one PNG per DFD and per attack path (needs matplotlib); the same images are embedded in a "Diagram images" sheet of the workbook (needs Pillow).
- draw.io and the workbook also include the attack paths: one draw.io page per path (each step links to the DFD page of its threat) and an "Attack paths" sheet; the Threats sheet has an "Attack paths" column.
If an optional library is missing the generator prints "SKIPPED <output>: <reason>" and still produces everything else.

It validates first and stops with MODEL INVALID on errors: duplicate IDs; broken references; child IDs not prefixed with the parent; a parent flow that is not in the parent diagram; threats whose target is not an own element or flow of their diagram; likelihood or impact outside 1-5; severity that does not match likelihood x impact; threats, improvements or questions without refs; refs to unknown documents; refines that does not point to a higher-level threat.

It prints WARNING for: an attack path that no improvement breaks; Critical threats but no attack paths; a Critical/High threat not addressed by any improvement; a Critical/High threat on a decomposed element not refined in the child; a gap threat without a question; a diagram over 20 elements; a child diagram with fewer than 3 own elements; an element without refs.

# TM-03 How the agent runs it

1. Load the script with the STEP 0 loader in the agent instructions (copy in agent/tm_loader.py). It looks for an attached tm_generator.txt first; if there is none, it extracts the script from the code block at the end of this file (TM-03 docx) when code interpreter can see the knowledge files. If neither is found it raises FileNotFoundError and the agent asks the user to attach tm_generator.txt. Never retype or rewrite the script.
2. Build MODEL in parts to keep each step short, for example:

```python
MODEL = {{"title": "Threat model - <system>", "documents": [...], "diagrams": [], "threats": [], "recommendations": [], "questions": []}}
MODEL["diagrams"].append({{...L0...}})
MODEL["threats"] += [{{...}}, ...]
MODEL["diagrams"].append({{...L1-P3...}})
```

3. run(MODEL, "<system_name>"). Fix every MODEL INVALID error and rerun. Fix each WARNING or explain it in the review.
4. Paste the report between REPORT_START and REPORT_END into the chat unchanged (all Mermaid blocks included), then offer every file listed after FILES: for download.

# TM-03 JSON model schema

```
{{
  "title": "Threat model - <system name>",
  "documents": [ {{"id": "DOC1", "name": "file name", "version": "0.9", "date": "2026-10-02", "pages": 24}} ],
  "summary": "3-5 sentence system summary", "frameworks_applied": "which frameworks and why",
  "assumptions": ["..."], "review": ["coverage result", "cross-level pattern", "..."],
  "diagrams": [
    {{"id": "L0", "level": 0, "title": "System context", "refs": [...], "stop_reason": "what was decomposed and why / why not",
     "boundaries": [ {{"id": "TB1", "name": "Internet"}} ],
     "elements": [ {{"id": "P3", "type": "external|process|store", "name": "...", "boundary": "TB3", "refs": [...], "assumed": false}} ],
     "flows": [ {{"id": "F6", "from": "P3", "to": "E3", "label": "data, protocol, authN", "refs": [...], "assumed": false}} ]}},
    {{"id": "L1-P3", "level": 1, "parent": "P3", "title": "Summariser Agent", "refs": [...], "stop_reason": "...",
     "boundaries": [...],
     "elements": [ {{"id": "E3", "type": "external", "name": "Hosted LLM API", "boundary": "TB5", "context": true}},
                   {{"id": "P3.1", "type": "process", "name": "Text Extractor", "boundary": "TB3", "refs": [...]}} ],
     "flows": [ {{"id": "P3.F6", "from": "P3.3", "to": "E3", "label": "...", "parent": "F6", "refs": [...]}} ]}}
  ],
  "threats": [
    {{"id": "T14", "diagram": "L1-P3", "target": "P3.2", "severity": "Critical|High|Medium|Low", "likelihood": 1-5, "impact": 1-5,
     "stride": "S|T|R|I|D|E", "frameworks": "LLM01:2026; ASI01", "title": "problem (under 12 words)", "description": "problem detail",
     "control": "solution", "refs": [ {{"doc": "DOC1", "section": "4.3", "page": 11, "loc": "Table 4", "quote": "<= 15 words"}} ],
     "refines": "T2", "related": ["T16"], "status": "Open", "owner": ""}}
  ],
  "recommendations": [
    {{"id": "R1", "priority": "P1|P2|P3", "title": "...", "description": "...", "threats": ["T2", "T15"], "refs": [...], "effort": "S|M|L"}}
  ],
  "questions": [
    {{"id": "Q1", "question": "...", "threats": ["T9"], "refs": [...], "ask": "role who should answer"}}
  ],
  "attack_paths": [
    {{"id": "AP1", "title": "...", "actor": "External attacker with a customer account", "entry": "E1",
     "objective": "business impact at the end", "likelihood": 1-5, "impact": 1-5, "severity": "Critical|High|Medium|Low",
     "steps": [ {{"threat": "T4", "action": "what the attacker does at this step"}}, {{"threat": "T14", "action": "..."}} ]}}
  ]
}}
```

Field rules:

- Diagram IDs: L0, then L1-<parent>, L2-<parent>. A child diagram has level = parent's level + 1 and parent = an own element of the level above.
- Own element and flow IDs in a child diagram start with the parent ID and a dot (P3.1, P3.D1, P3.F1).
- Context elements reuse the ID, type and name of an element defined in another diagram and set "context": true; they carry no threats.
- Element and flow IDs are unique across the model; boundary IDs are unique within a diagram.
- A threat's target must be an own element or flow of its diagram.
- refines points to a threat in a higher-level diagram; related lists any other threats. "Refined by", "Addressed by" (improvements) and "Open questions" are derived by the generator - do not add them to the model.
- attack_paths: entry must be an own external entity (E#); at least two steps; each step's threat must exist (any level); severity must match likelihood x impact. "Broken by" per step is derived from the improvements that address the step's threat.
- Boundaries are drawn left to right in the order listed: most untrusted first, build and admin planes last. More than four elements in a boundary wrap into extra columns.

# TM-03 Script: tm_generator.py

```python
{script}```
""", encoding="utf-8")

# 3. TM-04 - the example output is exactly what the generator's report produces (what the agent pastes into chat)
report = re.sub(r"^(#+) ", r"#\1 ", g.report_md(model, ix), flags=re.M)
report = report.split("\n", 2)[2]  # drop the report's own title line
spec = (EX / "example_spec.md").read_text(encoding="utf-8").split("\n", 2)[2]
(EX / "example_report.md").write_text(g.report_md(model, ix), encoding="utf-8")
(SRC / "TM-04_Worked_Example.md").write_text(f"""---
title: "TM-04 Worked Example (gold standard output)"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v2.3"
---

# TM-04 How to use this example

This is the target structure, depth and referencing for every answer. The system and documents are fictional. Reuse the structure, ID scheme, decomposition decisions, attack path style, reference style and wording; do not copy its threats into other models unless the documents support them.

The output section below is exactly the report that tm_generator.py prints between REPORT_START and REPORT_END (and saves as <system>_report.md). The agent pastes that report into the chat unchanged, including every Mermaid block, and then lists the downloadable files.

# TM-04 Example input documents

{spec}
# TM-04 Example output (the report)

{report}
# TM-04 Example downloads

example.drawio (4 DFD pages + 3 attack path pages), example_deck.pptx (editable deck), example_register.xlsx (all levels, attack paths, embedded images), example_diagrams_png.zip, example_report.md, example_model.json, example_threatdragon.json.

# TM-04 Example JSON model (input to tm_generator.py)

```json
{json.dumps(model, indent=1, ensure_ascii=False)}
```
""", encoding="utf-8")

# 4. Word versions for Copilot upload + script copy for attaching in chat
for md in sorted(SRC.glob("TM-0*.md")):
    docx = OUT / (md.stem + ".docx")
    subprocess.run(["pandoc", str(md), "-o", str(docx), "--no-highlight"], check=True)
shutil.copyfile(GEN, ROOT / "agent" / "tm_generator.txt")
(EX / "example_model.json").write_text(json.dumps(model, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Built:", ", ".join(p.name for p in sorted(OUT.glob("*.docx"))))
