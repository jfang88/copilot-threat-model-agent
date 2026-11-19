"""Rebuild the agent pack from source.

Generates TM-03 and TM-04 from the generator script and the example model, runs the
generator on the example, and converts all knowledge files to .docx for upload to Copilot.

Usage (from repo root):  python tools/build_knowledge.py
Requires: Python 3.9+, pandas + openpyxl (for the register), pandoc (for .docx).
"""
import json, re, shutil, subprocess, sys
from collections import Counter
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
g.validate(model)
g.drawio(model, str(EX / "example_threat_model.drawio"))
g.register(model, str(EX / "example_threat_model_register.xlsx"))
mer = g.mermaid(model)
(EX / "example_dfd.mmd").write_text(mer + "\n", encoding="utf-8")

# 2. TM-03
(SRC / "TM-03_Generator_and_Schema.md").write_text(f'''---
title: "TM-03 Generator Script and JSON Model Schema"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v1.0"
---

# TM-03 What the generator does

tm_generator.py turns one JSON threat model into three outputs that always agree with each other:

- threat_model.drawio - editable diagram: trust boundaries as containers, DFD shapes, hexagon threat badges attached to elements (they move with the element), coloured flow arrows labelled with flow ID and ⚠threat IDs, legend.
- threat_model_register.xlsx - threat register sorted by severity with a Status column (falls back to CSV if Excel writing is unavailable).
- Mermaid text printed between MERMAID_START and MERMAID_END for display in chat.

It validates the model first and stops with MODEL INVALID if IDs are duplicated, references are broken, likelihood or impact are outside 1-5, or severity does not match likelihood x impact (Critical 20-25, High 12-19, Medium 6-11, Low 1-5).

# TM-03 How the agent runs it

1. Build the JSON model (schema below).
2. In code interpreter, paste the script exactly as written below. Do not rewrite, shorten or restructure it.
3. Replace only the line beginning MODEL = json.load( with MODEL = followed by the JSON model as a Python dict (true/false become True/False, or wrap the JSON in json.loads(\'\'\'...\'\'\')).
4. Run. If MODEL INVALID is printed, fix the listed problems in the model and run again.
5. Offer the .drawio and .xlsx files for download and paste the Mermaid text into the answer unchanged.

# TM-03 JSON model schema

```
{{
  "title": "Threat model - <system name>",
  "boundaries": [ {{"id": "TB1", "name": "Internet"}} ],
  "elements": [
    {{"id": "E1", "type": "external|process|store", "name": "...", "boundary": "TB1", "assumed": false}}
  ],
  "flows": [
    {{"id": "F1", "from": "E1", "to": "P1", "label": "data carried, protocol, authN", "assumed": false}}
  ],
  "threats": [
    {{"id": "T1", "target": "P1 or F1", "severity": "Critical|High|Medium|Low",
     "likelihood": 1-5, "impact": 1-5, "stride": "S|T|R|I|D|E",
     "frameworks": "A01:2025; API1:2023", "title": "...", "description": "...",
     "spec_ref": "section or gap", "control": "..."}}
  ]
}}
```

Field rules:

- IDs: letters and digits only, unique across the model.
- elements[].boundary must be a boundary ID. flows[].from and .to must be element IDs. threats[].target must be an element or flow ID.
- "assumed" is optional; true draws the element or flow dashed and adds (ASSUMED) to its label.
- Boundaries are drawn left to right in the order listed: most untrusted first, build and admin planes last.

# TM-03 Script: tm_generator.py

```python
{script}```
''', encoding="utf-8")

# 3. TM-04
reg = sorted(model["threats"], key=lambda t: int(t["id"][1:]))
c = Counter(t["severity"] for t in reg)
rows = "\n".join(f"| {t['id']} | {t['severity']} | {t['stride']} | {t['target']} | {t['title']} | {t['frameworks']} | {t['control']} |"
                 for t in reg if t["severity"] in ("Critical", "High"))
spec = (EX / "example_spec.md").read_text(encoding="utf-8").split("\n", 2)[2]
questions = [
    "How does the Review Portal authenticate to the Case DB, and is TLS enforced? (T9)",
    "Where are case changes and summary approvals audited, and who can alter the audit records? (T10)",
    "What notice do customers receive that documents are processed by AI and a third-party provider? (T13)",
    "What data processing terms, region and retention settings apply to the hosted LLM API? (T1)",
    "Is the vector index partitioned per customer, and where is the filter enforced? (T8)",
]
(SRC / "TM-04_Worked_Example.md").write_text(f'''---
title: "TM-04 Worked Example (gold standard output)"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v1.0"
---

# TM-04 How to use this example

This is the target structure and depth for every answer. The system is fictional. Reuse the structure, ID scheme, threat wording style and level of detail; do not copy its threats into other models unless the spec supports them.

# TM-04 Example input (spec excerpt)

Document Intake & AI Summary Service, spec v0.9.

{spec}
# TM-04 Example output

## 1. Scope

System: Document Intake & AI Summary Service, spec v0.9. Customers upload documents through an Internet-facing gateway; an AI agent summarises them using a third-party hosted LLM and a vector index, and staff approve summaries in a review portal. Deployment is by GitHub Actions to AKS.

Frameworks applied: STRIDE per element (always); LINDDUN (customer personal data in documents); OWASP Top 10:2025 (web portal and services); API Security 2023 (gateway APIs); LLM 2026 and Agentic 2026 (summariser agent, hosted LLM, vector index); CI/CD Top 10 (GitHub Actions pipeline).

Assumptions: F10 Review Portal to Case DB connection is not described (modelled as assumed). Queue between Intake and Summariser modelled as flow F4 for simplicity.

## 2. DFD

```mermaid
{mer}
```

## 3. Legend

Rectangle = external entity, circle = process, cylinder = data store, red dashed box = trust boundary, dashed line = assumed, hexagon = Critical/High threat, ⚠T# on an arrow = threat on that flow.

## 4. Downloads

threat_model.drawio (editable diagram) and threat_model_register.xlsx (full register with Status column), produced by tm_generator.py.

## 5. Threat summary

Critical {c["Critical"]} | High {c["High"]} | Medium {c["Medium"]} | Low {c["Low"]} | Total {len(reg)}

| ID | Severity | STRIDE | Target | Threat | Framework IDs | Control |
|---|---|---|---|---|---|---|
{rows}

## 6. Open questions for the spec author

''' + "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions)) + f'''

# TM-04 Example JSON model (input to tm_generator.py)

```json
{json.dumps(model, indent=1, ensure_ascii=False)}
```
''', encoding="utf-8")

# 4. Word versions for Copilot upload + script copy for attaching in chat
for md in sorted(SRC.glob("TM-0*.md")):
    docx = OUT / (md.stem + ".docx")
    subprocess.run(["pandoc", str(md), "-o", str(docx), "--no-highlight"], check=True)
shutil.copyfile(GEN, ROOT / "agent" / "tm_generator.txt")
print("Built:", ", ".join(p.name for p in sorted(OUT.glob("*.docx"))))
