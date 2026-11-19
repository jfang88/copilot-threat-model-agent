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
order = sorted(model["diagrams"], key=lambda d: (d.get("level", 0), d["id"]))
mers = {d["id"]: g.mermaid(model, d["id"], ix) for d in order}
(EX / "example_dfd.mmd").write_text("\n\n".join(f"%% {k}\n{v}" for k, v in mers.items()) + "\n", encoding="utf-8")

# 2. TM-03
(SRC / "TM-03_Generator_and_Schema.md").write_text(f"""---
title: "TM-03 Generator Script and JSON Model Schema"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v2.0"
---

# TM-03 What the generator does

tm_generator.py turns one JSON threat model (all levels) into outputs that always agree with each other:

- <system>.drawio - one page per diagram (L0, L1-P#, L2-P#.#). Decomposed processes are double ellipses marked ⊞ and link to their child page; context elements are grey and link back to the page that defines them; every page has a Back link. Hover any element, flow or threat badge for its document references and threats.
- <system>_register.xlsx - one workbook for all levels: Read me, Threats (Problem, Solution and Document reference grouped together, with Refines / Refined by / Related / Arch. improvement / Open questions cross references as clickable links), Arch improvements, Open questions, Elements & flows, Diagrams, Documents.
- <system>_model.json - the model, so the run can be repeated or updated later.
- Mermaid text for each diagram, printed between "MERMAID_START <diagram>: <title>" and "MERMAID_END".

It validates first and stops with MODEL INVALID on errors: duplicate IDs; broken references; child IDs not prefixed with the parent; a parent flow that is not in the parent diagram; threats whose target is not an own element or flow of their diagram; likelihood or impact outside 1-5; severity that does not match likelihood x impact; threats, improvements or questions without refs; refs to unknown documents; refines that does not point to a higher-level threat.

It prints WARNING for: a Critical/High threat not addressed by any improvement; a Critical/High threat on a decomposed element not refined in the child; a gap threat without a question; a diagram over 20 elements; a child diagram with fewer than 3 own elements; an element without refs.

# TM-03 How the agent runs it

1. If tm_generator.txt is attached to the chat, load it in code interpreter without retyping:

```python
import glob
p = [f for d in ('/mnt/data', '.', '/mnt', '/tmp', '/home') for f in glob.glob(d + '/**/tm_generator*.txt', recursive=True)][0]
exec(open(p).read())
```

   Otherwise copy the script at the end of this file exactly. Do not rewrite, shorten or restructure it.
2. Build MODEL in parts to keep each step short, for example:

```python
MODEL = {{"title": "Threat model - <system>", "documents": [...], "diagrams": [], "threats": [], "recommendations": [], "questions": []}}
MODEL["diagrams"].append({{...L0...}})
MODEL["threats"] += [{{...}}, ...]
MODEL["diagrams"].append({{...L1-P3...}})
```

3. run(MODEL, "<system_name>"). Fix every MODEL INVALID error and rerun. Fix each WARNING or explain it in the review.
4. Provide the .drawio, .xlsx and _model.json files for download and paste each Mermaid block unchanged.

# TM-03 JSON model schema

```
{{
  "title": "Threat model - <system name>",
  "documents": [ {{"id": "DOC1", "name": "file name", "version": "0.9", "date": "2026-10-02", "pages": 24}} ],
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
- Boundaries are drawn left to right in the order listed: most untrusted first, build and admin planes last. More than four elements in a boundary wrap into extra columns.

# TM-03 Script: tm_generator.py

```python
{script}```
""", encoding="utf-8")

# 3. TM-04
def tree(gid, depth=0):
    d = ix["diag"][gid]
    line = f"{'    ' * depth}- {gid} {d['title']}" + (f" (decomposes {d['parent']})" if d.get("parent") else "") + \
        f" [{g.ref_text(d.get('refs'))}]: {d.get('stop_reason', '')}"
    kids = [c for c in order if c.get("parent") and ix["home"].get(c["parent"]) == gid]
    return "\n".join([line] + [tree(c["id"], depth + 1) for c in kids])

tb = g.tables(model, ix)
counts = "\n".join(f"| {d[0]} | {d[1]} | {d[6]} | {d[7]} | {d[8]} | {d[9]} |" for d in tb["Diagrams"][1])
by_id = {t["id"]: t for t in model["threats"]}
hi = "\n".join(
    f"| {r[0]} | {r[1]} | {r[3]} | {r[4]} | {r[5]} | {r[7]} | {r[9]} | {r[16] or '-'} / {r[17] or '-'} |"
    for r in tb["Threats"][1] if r[4] in ("Critical", "High"))
recs = "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[4]} | {r[7]} |" for r in tb["Arch improvements"][1])
qs = "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[4]} |" for r in tb["Open questions"][1])
docs = "\n".join(f"| {d['id']} | {d['name']} | {d['version']} | {d['pages']} |" for d in model["documents"])
diag_md = "\n\n".join(
    f"## {d['id']} {d['title']}" + (f" - decomposes {d['parent']}" if d.get("parent") else "") +
    f" [{g.ref_text(d.get('refs'))}]\n\n```mermaid\n{mers[d['id']]}\n```" for d in order)
spec = (EX / "example_spec.md").read_text(encoding="utf-8").split("\n", 2)[2]
(SRC / "TM-04_Worked_Example.md").write_text(f"""---
title: "TM-04 Worked Example (gold standard output)"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v2.0"
---

# TM-04 How to use this example

This is the target structure, depth and referencing for every answer. The system and documents are fictional. Reuse the structure, ID scheme, decomposition decisions, reference style and wording; do not copy its threats into other models unless the documents support them.

# TM-04 Example input documents

{spec}
# TM-04 Example output

## 1. Scope

| Doc | Document | Version | Pages |
|---|---|---|---|
{docs}

System: customers upload documents through an Internet-facing gateway; an AI agent summarises them using a third-party hosted LLM, a vector index and two database tools, and staff approve summaries in a review portal. Build and deployment use GitHub Actions on shared self-hosted runners to AKS.

Frameworks applied: STRIDE per element (always); LINDDUN (customer personal data); OWASP Top 10:2025 (web services); API Security 2023 (gateway APIs); LLM 2026 and Agentic 2026 (summariser agent, tools, memory, vector index); CI/CD Top 10 (DOC2 pipeline).

Assumptions: F10 Review Portal to Case DB connection is not described in DOC1 and is modelled as assumed.

## 2. Decomposition map

{tree("L0")}

## 3. Diagrams

Legend: rectangle = external entity, circle = process, double circle ⊞ = decomposed (see child diagram), cylinder = data store, grey dashed = context from another level, red dashed box = trust boundary, dashed line = assumed, hexagon = Critical/High threat, ⚠T# on an arrow = threat on that flow.

{diag_md}

## 4. Threat summary

| Diagram | Level | Critical | High | Medium | Low |
|---|---|---|---|---|---|
{counts}

| ID | Diagram | Target | Severity | Problem | Solution | Ref | Refines / Refined by |
|---|---|---|---|---|---|---|---|
{hi}

## 5. Review findings

- Coverage: every Critical/High threat on a decomposed element is refined in its child (T2 by T14 and T15; T7 by T21 and T24; T15 by T26-T28). All Critical and High threats are addressed by an improvement. All gap threats (T9, T10, T13) have questions. Generator warnings: none.
- Cross-level pattern 1 - untrusted content reaches privileged components: crafted uploads (T4) reach parsers that share a container with the orchestrator (T16), are mixed into the prompt (T14) and can drive write tools (T26). One structural change (R1 + R2) addresses the chain.
- Cross-level pattern 2 - static, over-privileged credentials: the cluster-admin kubeconfig (T3, T22), the registry secret (T25) and the LLM API key (T18) are all long-lived secrets. R3 and R6 move to workload identity.
- Cross-level pattern 3 - shared stores without tenant partitioning: blob paths (T6), vector index (T8, T17), search tool (T28) and agent memory (T29). R5 applies one tenant-isolation model across them.

## 6. Architecture improvements

| ID | Priority | Improvement | Addresses | Ref |
|---|---|---|---|---|
{recs}

## 7. Open questions

| ID | Question | Ref | Threats |
|---|---|---|---|
{qs}

## 8. Downloads

example_threat_model.drawio (four pages with drill-down), example_threat_model_register.xlsx (all levels, cross-referenced) and the model JSON, produced by tm_generator.py.

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
