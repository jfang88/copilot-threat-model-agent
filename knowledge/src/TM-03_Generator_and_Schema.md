---
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
MODEL = {"title": "Threat model - <system>", "documents": [...], "diagrams": [], "threats": [], "recommendations": [], "questions": []}
MODEL["diagrams"].append({...L0...})
MODEL["threats"] += [{...}, ...]
MODEL["diagrams"].append({...L1-P3...})
```

3. run(MODEL, "<system_name>"). Fix every MODEL INVALID error and rerun. Fix each WARNING or explain it in the review.
4. Paste the report between REPORT_START and REPORT_END into the chat unchanged (all Mermaid blocks included), then offer every file listed after FILES: for download.

# TM-03 JSON model schema

```
{
  "title": "Threat model - <system name>",
  "documents": [ {"id": "DOC1", "name": "file name", "version": "0.9", "date": "2026-10-02", "pages": 24} ],
  "summary": "3-5 sentence system summary", "frameworks_applied": "which frameworks and why",
  "assumptions": ["..."], "review": ["coverage result", "cross-level pattern", "..."],
  "diagrams": [
    {"id": "L0", "level": 0, "title": "System context", "refs": [...], "stop_reason": "what was decomposed and why / why not",
     "boundaries": [ {"id": "TB1", "name": "Internet"} ],
     "elements": [ {"id": "P3", "type": "external|process|store", "name": "...", "boundary": "TB3", "refs": [...], "assumed": false} ],
     "flows": [ {"id": "F6", "from": "P3", "to": "E3", "label": "data, protocol, authN", "refs": [...], "assumed": false} ]},
    {"id": "L1-P3", "level": 1, "parent": "P3", "title": "Summariser Agent", "refs": [...], "stop_reason": "...",
     "boundaries": [...],
     "elements": [ {"id": "E3", "type": "external", "name": "Hosted LLM API", "boundary": "TB5", "context": true},
                   {"id": "P3.1", "type": "process", "name": "Text Extractor", "boundary": "TB3", "refs": [...]} ],
     "flows": [ {"id": "P3.F6", "from": "P3.3", "to": "E3", "label": "...", "parent": "F6", "refs": [...]} ]}
  ],
  "threats": [
    {"id": "T14", "diagram": "L1-P3", "target": "P3.2", "severity": "Critical|High|Medium|Low", "likelihood": 1-5, "impact": 1-5,
     "stride": "S|T|R|I|D|E", "frameworks": "LLM01:2026; ASI01", "title": "problem (under 12 words)", "description": "problem detail",
     "control": "solution", "refs": [ {"doc": "DOC1", "section": "4.3", "page": 11, "loc": "Table 4", "quote": "<= 15 words"} ],
     "refines": "T2", "related": ["T16"], "status": "Open", "owner": ""}
  ],
  "recommendations": [
    {"id": "R1", "priority": "P1|P2|P3", "title": "...", "description": "...", "threats": ["T2", "T15"], "refs": [...], "effort": "S|M|L"}
  ],
  "questions": [
    {"id": "Q1", "question": "...", "threats": ["T9"], "refs": [...], "ask": "role who should answer"}
  ],
  "attack_paths": [
    {"id": "AP1", "title": "...", "actor": "External attacker with a customer account", "entry": "E1",
     "objective": "business impact at the end", "likelihood": 1-5, "impact": 1-5, "severity": "Critical|High|Medium|Low",
     "steps": [ {"threat": "T4", "action": "what the attacker does at this step"}, {"threat": "T14", "action": "..."} ]}
  ]
}
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
# tm_generator.py  v2.3 - multi-level threat model renderer for the Copilot DFD agent
# Copilot code interpreter: load this file with exec(open(path).read()), build MODEL (schema in TM-03), then run(MODEL, "<system>")
# Command line: python tm_generator.py model.json [output_name]
# Outputs: <name>.drawio (one page per diagram, clickable drill-down), <name>_register.xlsx (all levels, cross-referenced),
#          <name>_model.json (re-runnable), <name>_threatdragon.json (OWASP Threat Dragon v2 import),
#          <name>_report.md (full Markdown report incl. every Mermaid diagram and attack path), printed between
#          REPORT_START/REPORT_END so it can be pasted into the chat.
# Do not modify this script.
import json, re, sys, uuid
from xml.sax.saxutils import quoteattr

SEV = {"Critical": ("#f8d7da", "#b02a37"), "High": ("#fff3cd", "#b8860b"),
       "Medium": ("#dbe9f6", "#2b6cb0"), "Low": ("#e2e3e5", "#6c757d")}
RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
SHAPE = {"external": ("rounded=0;whiteSpace=wrap;html=1;", 160, 60),
         "process": ("ellipse;whiteSpace=wrap;html=1;", 160, 80),
         "store": ("shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=10;", 160, 70)}
ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9.\-]*")


def sev_for(score):
    return "Critical" if score >= 20 else "High" if score >= 12 else "Medium" if score >= 6 else "Low"


def ref_text(refs):
    """['DOC1 §4.3 p.12 Table 2', ...] -> 'DOC1 §4.3 p.12 Table 2; DOC2 §1'"""
    out = []
    for r in refs or []:
        s = r.get("doc", "?")
        if r.get("section"): s += " gap" if r["section"] == "gap" else " §" + str(r["section"]).lstrip("§")
        if r.get("page"): s += " p." + str(r["page"]).lstrip("p.")
        if r.get("loc"): s += " " + r["loc"]
        out.append(s)
    return "; ".join(out)


def quotes(refs):
    return " | ".join('"' + r["quote"] + '"' for r in refs or [] if r.get("quote"))


LINDDUN = {"L": "Linking", "I": "Identifying", "NR": "Non-repudiation", "DT": "Detecting", "DD": "Data disclosure",
           "U": "Unawareness", "NC": "Non-compliance"}


def linddun(t):
    """LINDDUN codes cited in a threat's frameworks, e.g. 'DD, NC'."""
    return ", ".join(re.findall(r"LINDDUN\s+([A-Z]+)", t.get("frameworks", "")))


def tnum(i):
    return int(re.sub(r"\D", "", i) or 0)


# ---------------------------------------------------------------- index + validation
def index(m):
    ix = {"diag": {}, "el": {}, "fl": {}, "home": {}, "t": {}, "r": {}, "q": {}, "doc": {}}
    for d in m.get("documents", []): ix["doc"][d["id"]] = d
    for g in m["diagrams"]:
        ix["diag"][g["id"]] = g
        for e in g["elements"]:
            ix["el"].setdefault(e["id"], []).append((g["id"], e))
            if not e.get("context"): ix["home"][e["id"]] = g["id"]
        for f in g["flows"]:
            ix["fl"][f["id"]] = (g["id"], f)
    for t in m["threats"]: ix["t"][t["id"]] = t
    for r in m.get("recommendations", []): ix["r"][r["id"]] = r
    for q in m.get("questions", []): ix["q"][q["id"]] = q
    # derived cross references
    ix["child"] = {g["parent"]: g["id"] for g in m["diagrams"] if g.get("parent")}
    ix["refined_by"], ix["addressed_by"], ix["asked_in"] = {}, {}, {}
    for t in m["threats"]:
        if t.get("refines"): ix["refined_by"].setdefault(t["refines"], []).append(t["id"])
    for r in m.get("recommendations", []):
        for tid in r.get("threats", []): ix["addressed_by"].setdefault(tid, []).append(r["id"])
    for q in m.get("questions", []):
        for tid in q.get("threats", []): ix["asked_in"].setdefault(tid, []).append(q["id"])
    ix["ap"] = {a["id"]: a for a in m.get("attack_paths", [])}
    ix["in_paths"] = {}
    for a in m.get("attack_paths", []):
        for st in a.get("steps", []):
            if a["id"] not in ix["in_paths"].setdefault(st.get("threat"), []): ix["in_paths"][st["threat"]].append(a["id"])
    ix["by_target"] = {}
    for t in sorted(m["threats"], key=lambda t: (-RANK.get(t["severity"], 0), tnum(t["id"]))):
        ix["by_target"].setdefault((t["diagram"], t["target"]), []).append(t)
    return ix


def check_refs(where, refs, ix, err, required=True):
    if not refs:
        if required: err.append(where + ": needs at least one document reference (refs)")
        return
    for r in refs:
        if r.get("doc") not in ix["doc"]: err.append(f"{where}: ref doc '{r.get('doc')}' not in documents")
        if not r.get("section"): err.append(f"{where}: ref needs a section (or 'gap')")


def validate(m):
    """Returns warnings; raises SystemExit('MODEL INVALID ...') on errors."""
    err, warn = [], []
    for k in ("documents", "diagrams", "threats"):
        if not m.get(k): err.append("missing or empty: " + k)
    if err: raise SystemExit("MODEL INVALID:\n" + "\n".join(err))
    ix = index(m)
    seen = set()
    fcount = {}
    for g in m["diagrams"]:
        for f in g["flows"]: fcount[f["id"]] = fcount.get(f["id"], 0) + 1
    for g in m["diagrams"]:
        if g["id"] in seen: err.append("duplicate diagram " + g["id"])
        seen.add(g["id"])
        lvl, par = g.get("level"), g.get("parent")
        if lvl == 0 and par: err.append(g["id"] + ": level 0 diagram cannot have a parent")
        if lvl and lvl > 0:
            if par not in ix["home"]: err.append(f'{g["id"]}: parent {par} is not an element of another diagram')
            elif ix["diag"][ix["home"][par]].get("level", 0) != lvl - 1: err.append(f'{g["id"]}: parent {par} is not on level {lvl-1}')
        bids = [b["id"] for b in g["boundaries"]]
        if len(bids) != len(set(bids)): err.append(g["id"] + ": duplicate boundary id")
        own = 0
        for e in g["elements"]:
            w = f'{g["id"]}/{e["id"]}'
            if not ID_RE.fullmatch(e["id"]): err.append(w + ": bad id")
            if e["type"] not in SHAPE: err.append(w + ": type must be external, process or store")
            if e.get("boundary") not in bids: err.append(w + ": boundary not in this diagram")
            if e.get("context"):
                if e["id"] not in ix["home"]: err.append(w + ": context element must be defined in another diagram")
            else:
                own += 1
                if sum(1 for _, x in ix["el"][e["id"]] if not x.get("context")) > 1: err.append(e["id"] + ": defined twice")
                if par and not e["id"].startswith(par + "."): err.append(f'{w}: own elements of a child diagram must be prefixed "{par}."')
                check_refs(w, e.get("refs"), ix, warn, required=True)
        n = len(g["elements"])
        if n > 20: warn.append(f'{g["id"]}: {n} elements - too large, decompose further or split')
        if par and own < 3: warn.append(f'{g["id"]}: only {own} own elements - decomposition may not be worthwhile')
        ids_here = {e["id"] for e in g["elements"]}
        for f in g["flows"]:
            w = f'{g["id"]}/{f["id"]}'
            if fcount[f["id"]] > 1: err.append(f["id"] + ": flow id used more than once")
            if not ID_RE.fullmatch(f["id"]): err.append(w + ": bad id")
            if par and not f["id"].startswith(par + "."): err.append(f'{w}: flows of a child diagram must be prefixed "{par}."')
            for end in (f["from"], f["to"]):
                if end not in ids_here: err.append(f"{w}: endpoint {end} not in this diagram")
            if f.get("parent") and (f["parent"] not in ix["fl"] or ix["fl"][f["parent"]][0] != ix["home"].get(par)):
                err.append(f"{w}: parent flow {f['parent']} not in the parent diagram")
    tids = [t["id"] for t in m["threats"]]
    if len(tids) != len(set(tids)): err.append("duplicate threat id")
    for t in m["threats"]:
        w = t["id"]
        g = ix["diag"].get(t.get("diagram"))
        if not g: err.append(w + ": diagram not found"); continue
        own = {e["id"] for e in g["elements"] if not e.get("context")} | {f["id"] for f in g["flows"]}
        if t.get("target") not in own: err.append(f'{w}: target {t.get("target")} is not an own element or flow of {g["id"]}')
        L, I = t.get("likelihood", 0), t.get("impact", 0)
        if not (1 <= L <= 5 and 1 <= I <= 5): err.append(w + ": likelihood and impact must be 1-5")
        elif sev_for(L * I) != t.get("severity"): err.append(f'{w}: severity should be {sev_for(L*I)} (L{L} x I{I} = {L*I})')
        check_refs(w, t.get("refs"), ix, err)
        if t.get("refines") and t["refines"] not in ix["t"]: err.append(f'{w}: refines unknown threat {t["refines"]}')
        if t.get("refines") in ix["t"]:
            pt = ix["t"][t["refines"]]
            if ix["diag"][pt["diagram"]].get("level", 0) >= g.get("level", 0): err.append(f"{w}: refines must point to a higher-level threat")
        for x in t.get("related", []):
            if x not in ix["t"]: err.append(f"{w}: related unknown threat {x}")
    for r in m.get("recommendations", []):
        if not r.get("threats"): err.append(r["id"] + ": must list the threats it addresses")
        for x in r.get("threats", []):
            if x not in ix["t"]: err.append(f'{r["id"]}: unknown threat {x}')
        check_refs(r["id"], r.get("refs"), ix, err)
    for q in m.get("questions", []):
        for x in q.get("threats", []):
            if x not in ix["t"]: err.append(f'{q["id"]}: unknown threat {x}')
        check_refs(q["id"], q.get("refs"), ix, err)
    ext = {i for i, lst in ix["el"].items() for _, e in lst if e["type"] == "external" and not e.get("context")}
    for a in m.get("attack_paths", []):
        w = a["id"]
        if not re.fullmatch(r"AP\d+", w): err.append(w + ": attack path IDs are AP1, AP2..")
        if a.get("entry") not in ext: err.append(f'{w}: entry {a.get("entry")} must be an external entity (E#)')
        if len(a.get("steps", [])) < 2: err.append(w + ": needs at least 2 steps")
        for st in a.get("steps", []):
            if st.get("threat") not in ix["t"]: err.append(f'{w}: step threat {st.get("threat")} unknown')
            if not st.get("action"): err.append(f"{w}: every step needs an attacker action")
        L, I = a.get("likelihood", 0), a.get("impact", 0)
        if not (1 <= L <= 5 and 1 <= I <= 5): err.append(w + ": likelihood and impact must be 1-5")
        elif sev_for(L * I) != a.get("severity"): err.append(f'{w}: severity should be {sev_for(L*I)} (L{L} x I{I} = {L*I})')
        for k in ("title", "actor", "objective"):
            if not a.get(k): err.append(f"{w}: missing {k}")
    if err: raise SystemExit("MODEL INVALID:\n" + "\n".join(err))
    # coverage warnings
    for a in m.get("attack_paths", []):
        if not any(ix["addressed_by"].get(st["threat"]) for st in a["steps"]):
            warn.append(f'{a["id"]}: no improvement breaks any step of this attack path')
    if any(RANK[t["severity"]] == 4 for t in m["threats"]) and not m.get("attack_paths"):
        warn.append("model has Critical threats but no attack_paths")
    for t in m["threats"]:
        hi = RANK[t["severity"]] >= 3
        if hi and t["id"] not in ix["addressed_by"]: warn.append(f'{t["id"]}: {t["severity"]} threat not addressed by any recommendation')
        if hi and t["target"] in ix["child"] and t["id"] not in ix["refined_by"]:
            warn.append(f'{t["id"]}: {t["severity"]} threat on decomposed {t["target"]} not refined in {ix["child"][t["target"]]}')
        if any(r.get("section") == "gap" for r in t.get("refs", [])) and t["id"] not in ix["asked_in"]:
            warn.append(f'{t["id"]}: gap threat without an open question')
    return warn


# ---------------------------------------------------------------- draw.io (one page per diagram)
def _cell(cells, cid, label, style, parent, x, y, w, h, tooltip="", link="", edge=None, extra=None):
    geo = (f'<mxGeometry relative="1" as="geometry"/>' if edge else
           f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>')
    kind = (f'edge="1" source="{edge[0]}" target="{edge[1]}"' if edge else 'vertex="1"')
    if tooltip or link or extra:
        attrs = " ".join(f"{k}={quoteattr(str(v))}" for k, v in (extra or {}).items() if v)
        cells.append(f'<UserObject id={quoteattr(cid)} label={quoteattr(label)}'
                     + (f" tooltip={quoteattr(tooltip)}" if tooltip else "")
                     + (f" link={quoteattr(link)}" if link else "") + (" " + attrs if attrs else "")
                     + f'><mxCell style={quoteattr(style)} {kind} parent="{parent}">{geo}</mxCell></UserObject>')
    else:
        cells.append(f'<mxCell id={quoteattr(cid)} value={quoteattr(label)} style={quoteattr(style)} {kind} parent="{parent}">{geo}</mxCell>')


def _flow_label(f, tt):
    s = f["id"] + ": " + f["label"] + (" (ASSUMED)" if f.get("assumed") else "")
    return s + (" ⚠" + ",".join(t["id"] for t in tt) if tt else "")


def _page(m, g, ix):
    cells, gid = [], g["id"]
    pre = gid + "|"  # cell ids are unique per page; prefix keeps them distinct in a multi-page file
    head = f'{gid}: {g["title"]}'
    if g.get("parent"):
        head += f'  (decomposes {g["parent"]})'
    _cell(cells, pre + "title", head, "text;fontSize=18;fontStyle=1;align=left;html=1;", "1", 20, 10, 900, 30)
    if g.get("parent"):
        up = ix["home"][g["parent"]]
        _cell(cells, pre + "up", f"▲ Back to {up}", "text;fontSize=11;fontColor=#2b6cb0;align=left;html=1;", "1",
              20, 40, 200, 20, link="data:page/id," + up)
    x, maxh, y0 = 20, 0, 75
    for b in g["boundaries"]:
        els = [e for e in g["elements"] if e["boundary"] == b["id"]]
        per = 4  # max elements stacked per column inside a boundary; more wrap into extra columns
        cols = [els[i:i + per] for i in range(0, len(els), per)] or [[]]
        h = 60 + max(sum(SHAPE[e["type"]][2] + 75 for e in c) for c in cols)
        bw = 40 + 215 * len(cols)
        maxh = max(maxh, h)
        _cell(cells, pre + b["id"], b["id"] + ": " + b["name"],
              "rounded=1;dashed=1;dashPattern=8 4;strokeColor=#c0392b;strokeWidth=2;fillColor=none;verticalAlign=top;"
              "align=left;spacingLeft=8;fontStyle=1;container=1;collapsible=0;html=1;", "1", x, y0, bw, h)
        for ci, col in enumerate(cols):
            y = 50
            for e in col:
                st, w, hh = SHAPE[e["type"]]
                tt = [] if e.get("context") else ix["by_target"].get((gid, e["id"]), [])
                link, tip = "", ref_text(e.get("refs"))
                if e.get("context"):
                    st += "dashed=1;fillColor=#f5f5f5;fontColor=#666666;strokeColor=#999999;"
                    link = "data:page/id," + ix["home"][e["id"]]
                    tip = f'Context from {ix["home"][e["id"]]}. ' + tip
                else:
                    if e["id"] in ix["child"]:
                        st = st.replace("ellipse;", "shape=doubleEllipse;") if e["type"] == "process" else st + "strokeWidth=3;"
                        link = "data:page/id," + ix["child"][e["id"]]
                        tip = f'Decomposed in {ix["child"][e["id"]]} (click to open). ' + tip
                    if tt: st += f"strokeColor={SEV[tt[0]['severity']][1]};strokeWidth=2;"
                    if e.get("assumed"): st += "dashed=1;"
                if tt: tip += " | Threats: " + ", ".join(t["id"] for t in tt)
                label = e["id"] + ": " + e["name"] + (" (ASSUMED)" if e.get("assumed") else "") + \
                        (" ⊞" if e["id"] in ix["child"] and not e.get("context") else "")
                _cell(cells, pre + e["id"], label, st, pre + b["id"], 30 + 215 * ci, y, w, hh, tooltip=tip.strip(), link=link,
                      extra={"docref": ref_text(e.get("refs"))})
                for i, t in enumerate(tt):
                    fc, sc = SEV[t["severity"]]
                    _cell(cells, pre + t["id"], t["id"], f"shape=hexagon;perimeter=hexagonPerimeter2;size=0.2;fillColor={fc};"
                          f"strokeColor={sc};fontColor={sc};fontStyle=1;fontSize=10;html=1;", pre + e["id"],
                          w - 25 + (i % 3) * 40, -14 - (i // 3) * 24, 38, 22,
                          tooltip=f'{t["id"]} {t["severity"]}: {t["title"]} [{ref_text(t["refs"])}]')
                y += hh + 75
        x += bw + 40
    for f in g["flows"]:
        tt = ix["by_target"].get((gid, f["id"]), [])
        col = SEV[tt[0]["severity"]][1] if tt else "#333333"
        st = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor={col};fontSize=10;"
              f"labelBackgroundColor=#ffffff;" + ("dashed=1;" if f.get("assumed") else ""))
        tip = ref_text(f.get("refs")) + (f' | refines {f["parent"]}' if f.get("parent") else "") + \
            (" | Threats: " + ", ".join(t["id"] for t in tt) if tt else "")
        _cell(cells, pre + f["id"], _flow_label(f, tt), st, "1", 0, 0, 0, 0, tooltip=tip.strip(" |"),
              edge=(pre + f["from"], pre + f["to"]), extra={"docref": ref_text(f.get("refs"))})
    ly = y0 + maxh + 30
    _cell(cells, pre + "legend", "Legend: rectangle = external entity | ellipse = process | double ellipse ⊞ = decomposed "
          "(click to open) | cylinder = data store | grey dashed = context from another level (click) | red dashed box = "
          "trust boundary | dashed = ASSUMED | hexagon = threat | ⚠T# on arrow = threat on flow | hover for document references",
          "text;align=left;fontSize=11;html=1;whiteSpace=wrap;", "1", 20, ly, 1000, 34)
    for i, (s, (fc, sc)) in enumerate(SEV.items()):
        _cell(cells, pre + "lg" + s, s, f"rounded=1;fillColor={fc};strokeColor={sc};fontColor={sc};fontStyle=1;html=1;",
              "1", 20 + i * 100, ly + 40, 90, 24)
    name = f'{gid} {g["title"]}'[:60]
    return (f'<diagram id={quoteattr(gid)} name={quoteattr(name)}><mxGraphModel grid="1" gridSize="10" tooltips="1">'
            f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(cells)}</root></mxGraphModel></diagram>')


def drawio(m, path, ix=None):
    ix = ix or index(m)
    order = sorted(m["diagrams"], key=lambda g: (g.get("level", 0), g["id"]))
    xml = '<mxfile host="tm_generator">' + "".join(_page(m, g, ix) for g in order) + \
        "".join(_ap_page(m, a, ix) for a in m.get("attack_paths", [])) + "</mxfile>"
    open(path, "w", encoding="utf-8").write(xml)


# ---------------------------------------------------------------- Mermaid (one block per diagram)
def mermaid(m, gid, ix=None):
    ix = ix or index(m)
    g = ix["diag"][gid]
    q = lambda s: s.replace('"', "'").replace("<", "(").replace(">", ")")
    nid = lambda i: re.sub(r"[^A-Za-z0-9_]", "_", i)
    L, C = ["flowchart LR"], []
    for b in g["boundaries"]:
        L.append(f'  subgraph {nid(gid + "_" + b["id"])}["{q(b["id"] + ": " + b["name"])}"]')
        for e in [e for e in g["elements"] if e["boundary"] == b["id"]]:
            dec = e["id"] in ix["child"] and not e.get("context")
            n = q(e["id"] + ": " + e["name"] + (" (ASSUMED)" if e.get("assumed") else "") + (" ⊞" if dec else ""))
            shape = {"external": f'["{n}"]', "store": f'[("{n}")]',
                     "process": f'((("{n}")))' if dec else f'(("{n}"))'}[e["type"]]
            L.append(f'    {nid(e["id"])}{shape}')
            if e.get("context"):
                C.append(f'  class {nid(e["id"])} ctx')
                continue
            for t in ix["by_target"].get((gid, e["id"]), []):
                if RANK[t["severity"]] >= 3:
                    L.append(f'    {nid(t["id"])}{{{{"{t["id"]} {t["severity"]}"}}}} -.- {nid(e["id"])}')
                    C.append(f'  class {nid(t["id"])} {t["severity"][:4].lower()}')
        L.append("  end")
        L.append(f'  style {nid(gid + "_" + b["id"])} stroke:#c0392b,stroke-dasharray:6 4')
    for f in g["flows"]:
        arrow = "-.->" if f.get("assumed") else "-->"
        L.append(f'  {nid(f["from"])} {arrow}|"{q(_flow_label(f, ix["by_target"].get((gid, f["id"]), [])))}"| {nid(f["to"])}')
    L += ["  classDef crit fill:#f8d7da,stroke:#b02a37,color:#58151c",
          "  classDef high fill:#fff3cd,stroke:#b8860b,color:#5c4400",
          "  classDef ctx fill:#f5f5f5,stroke:#999999,color:#666666,stroke-dasharray:4 3"] + C
    return "\n".join(L)


# ---------------------------------------------------------------- workbook
THREAT_COLS = [("ID", 7), ("Diagram", 10), ("Level", 6), ("Target", 26), ("Severity", 9),
               ("Problem", 34), ("Problem detail", 50), ("Solution (control)", 50), ("Arch. improvement", 12),
               ("Document reference", 22), ("Evidence (quote)", 40), ("STRIDE", 7), ("LINDDUN", 9), ("Frameworks", 24),
               ("Likelihood", 9), ("Impact", 8), ("Score", 7), ("Refines (parent threat)", 12),
               ("Refined by (child threats)", 14), ("Related", 12), ("Open questions", 11), ("Attack paths", 11),
               ("Status", 10), ("Owner", 14)]


def _name(ix, i):
    if i in ix["home"]:
        e = next(x for _, x in ix["el"][i] if not x.get("context")); return f"{i}: {e['name']}"
    if i in ix["fl"]: return f"{i}: {ix['fl'][i][1]['label']}"
    return i


def tables(m, ix=None):
    """Returns {sheet: (columns, rows)} - used by the xlsx and csv writers and by tests."""
    ix = ix or index(m)
    lvl = lambda gid: "L" + str(ix["diag"][gid].get("level", 0))
    ts = sorted(m["threats"], key=lambda t: tnum(t["id"]))
    threats = [[t["id"], t["diagram"], lvl(t["diagram"]), _name(ix, t["target"]), t["severity"], t["title"],
                t.get("description", ""), t.get("control", ""), ", ".join(ix["addressed_by"].get(t["id"], [])),
                ref_text(t.get("refs")), quotes(t.get("refs")), t.get("stride", ""), linddun(t), t.get("frameworks", ""),
                t["likelihood"], t["impact"], t["likelihood"] * t["impact"], t.get("refines", ""),
                ", ".join(ix["refined_by"].get(t["id"], [])), ", ".join(t.get("related", [])),
                ", ".join(ix["asked_in"].get(t["id"], [])), ", ".join(ix["in_paths"].get(t["id"], [])),
                t.get("status", "Open"), t.get("owner", "")] for t in ts]
    aps = []
    for a in m.get("attack_paths", []):
        aps.append([a["id"], "", a["severity"], a["title"], f'{a["actor"]} (entry {a["entry"]})', a["objective"], "", "", "",
                    "", "", a["likelihood"], a["impact"], a["likelihood"] * a["impact"]])
        for n, st in enumerate(a["steps"], 1):
            t = ix["t"][st["threat"]]
            aps.append([a["id"], n, t["severity"], st["action"], st["threat"], t["title"], t["diagram"], _name(ix, t["target"]),
                        ", ".join(ix["addressed_by"].get(t["id"], [])), ref_text(t.get("refs")), quotes(t.get("refs")), "", "", ""])
    recs = []
    for r in m.get("recommendations", []):
        tl = [ix["t"][x] for x in r["threats"]]
        top = max(tl, key=lambda t: RANK[t["severity"]])["severity"] if tl else ""
        recs.append([r["id"], r.get("priority", ""), r["title"], r.get("description", ""), ", ".join(r["threats"]),
                     top, ", ".join(sorted({t["diagram"] for t in tl})), ref_text(r.get("refs")), quotes(r.get("refs")),
                     r.get("effort", ""), r.get("status", "Proposed"), r.get("owner", "")])
    qs = [[q["id"], q["question"], ref_text(q.get("refs")), quotes(q.get("refs")), ", ".join(q.get("threats", [])),
           q.get("ask", ""), q.get("answer", ""), q.get("status", "Open")] for q in m.get("questions", [])]
    els = []
    for g in sorted(m["diagrams"], key=lambda g: (g.get("level", 0), g["id"])):
        for e in g["elements"]:
            if e.get("context"): continue
            els.append([e["id"], g["id"], lvl(g["id"]), e["type"], e["name"], e["boundary"], g.get("parent", ""),
                        ix["child"].get(e["id"], ""), ref_text(e.get("refs")),
                        ", ".join(t["id"] for t in ix["by_target"].get((g["id"], e["id"]), [])), "Yes" if e.get("assumed") else ""])
        for f in g["flows"]:
            els.append([f["id"], g["id"], lvl(g["id"]), "flow", f'{f["from"]} → {f["to"]}: {f["label"]}', "",
                        f.get("parent", ""), "", ref_text(f.get("refs")),
                        ", ".join(t["id"] for t in ix["by_target"].get((g["id"], f["id"]), [])), "Yes" if f.get("assumed") else ""])
    diags = []
    for g in sorted(m["diagrams"], key=lambda g: (g.get("level", 0), g["id"])):
        c = {s: 0 for s in RANK}
        for t in m["threats"]:
            if t["diagram"] == g["id"]: c[t["severity"]] += 1
        own = sum(1 for e in g["elements"] if not e.get("context"))
        diags.append([g["id"], lvl(g["id"]), g["title"], g.get("parent", ""), own, len(g["flows"]),
                      c["Critical"], c["High"], c["Medium"], c["Low"], g.get("stop_reason", ""), ref_text(g.get("refs"))])
    docs = [[d["id"], d.get("name", ""), d.get("version", ""), d.get("date", ""), d.get("pages", "")] for d in m["documents"]]
    return {
        "Threats": ([c for c, _ in THREAT_COLS], threats),
        "Arch improvements": (["ID", "Priority", "Improvement", "Description", "Addresses threats", "Highest severity",
                               "Diagrams", "Document reference", "Evidence (quote)", "Effort", "Status", "Owner"], recs),
        "Open questions": (["ID", "Question", "Document reference", "Evidence (quote)", "Related threats", "Ask (role)",
                            "Answer", "Status"], qs),
        "Attack paths": (["Attack path", "Step", "Severity", "Title / attacker action", "Actor / threat", "Objective / threat title",
                          "Diagram", "Target", "Broken by (improvement)", "Document reference", "Evidence (quote)",
                          "Likelihood", "Impact", "Score"], aps),
        "Elements & flows": (["ID", "Diagram", "Level", "Type", "Name / flow", "Boundary", "Parent", "Decomposed in",
                              "Document reference", "Threats", "Assumed"], els),
        "Diagrams": (["Diagram", "Level", "Title", "Decomposes", "Own elements", "Flows", "Critical", "High", "Medium",
                      "Low", "Decomposition stop / scope note", "Document reference"], diags),
        "Documents": (["ID", "Document", "Version", "Date", "Pages"], docs),
    }


def register(m, path, ix=None):
    ix = ix or index(m)
    tb = tables(m, ix)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.hyperlink import Hyperlink
    except ImportError:
        import csv
        paths = []
        for sheet, (cols, rows) in tb.items():
            p = path.replace(".xlsx", "_" + sheet.replace(" ", "_").replace("&", "and") + ".csv")
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                w = csv.writer(fh); w.writerow(cols); w.writerows(rows)
            paths.append(p)
        return ", ".join(paths)
    wb = Workbook()
    wb.remove(wb.active)
    widths = {"Threats": dict(THREAT_COLS)}
    rowmap = {}
    for sheet, (cols, rows) in tb.items():
        for i, r in enumerate(rows): rowmap.setdefault(r[0], (sheet, i + 2))
    hdr_fill, hdr_font = PatternFill("solid", fgColor="1F3864"), Font(bold=True, color="FFFFFF")
    group = {"Problem": "FDEDEC", "Problem detail": "FDEDEC", "Solution (control)": "E8F5E9", "Arch. improvement": "E8F5E9",
             "Document reference": "EAF2FB", "Evidence (quote)": "EAF2FB"}
    linkcols = {"Arch. improvement", "Refines (parent threat)", "Refined by (child threats)", "Related", "Open questions",
                "Addresses threats", "Related threats", "Decomposed in", "Parent", "Threats", "Decomposes", "Diagram",
                "Attack paths", "Actor / threat", "Broken by (improvement)"}
    for sheet, (cols, rows) in tb.items():
        ws = wb.create_sheet(sheet)
        ws.append(cols)
        for r in rows: ws.append(r)
        for j, c in enumerate(cols, 1):
            cell = ws.cell(1, j); cell.fill, cell.font = hdr_fill, hdr_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[get_column_letter(j)].width = widths.get(sheet, {}).get(c, max(10, min(45, len(c) + 4)))
            for i in range(2, len(rows) + 2):
                v = ws.cell(i, j)
                v.alignment = Alignment(wrap_text=True, vertical="top")
                if sheet == "Threats" and c in group: v.fill = PatternFill("solid", fgColor=group[c])
                if c in ("Severity", "Highest severity") and v.value in SEV:
                    v.fill = PatternFill("solid", fgColor=SEV[v.value][0].lstrip("#"))
                    v.font = Font(bold=True, color=SEV[v.value][1].lstrip("#"))
                first = str(v.value or "").split(",")[0].split(":")[0].strip()
                if c in linkcols and first in rowmap:
                    s, rr = rowmap[first]
                    v.hyperlink = Hyperlink(ref=v.coordinate, location=f"'{s}'!A{rr}", display=str(v.value))
                    v.font = Font(color="2B6CB0", underline="single")
        ws.freeze_panes = "B2"
        ws.page_setup.orientation = "landscape"
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.auto_filter.ref = ws.dimensions
    ws = wb.create_sheet("Read me", 0)
    lines = [m["title"], "",
             "Sheets: Threats (all levels: L0, L1, L2) | Arch improvements | Open questions | Attack paths | Elements & flows | Diagrams | Documents",
             "Attack paths: one header row per path (actor, objective, score), then one row per step with the threat it exploits and the improvement that breaks it.",
             "Threats sheet: Problem (red) - Solution (green) - Document reference (blue) are grouped together.",
             "Cross references: Refines/Refined by link L0 threats to child threats; Arch. improvement links to the improvement "
             "that solves it; Open questions links to the question for spec gaps. Blue underlined IDs are clickable.",
             "Reference format: DOC1 §4.3 p.12 Table 2 = document DOC1, section 4.3, page 12, Table 2. 'gap' = the document is silent.",
             "IDs are stable for discussion: T# threats, R# improvements, Q# questions, P#/D#/E#/F# elements and flows; "
             "child IDs are prefixed with the parent (P3.1, P3.D1, P3.F2).", "", "Severity counts"]
    for l in lines: ws.append([l])
    for s in RANK: ws.append([s, sum(1 for t in m["threats"] if t["severity"] == s)])
    ws["A1"].font = Font(bold=True, size=14)
    ws.column_dimensions["A"].width = 120
    wb.save(path)
    return path


# ---------------------------------------------------------------- OWASP Threat Dragon v2 export
TD_STRIDE = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information disclosure",
             "D": "Denial of service", "E": "Elevation of privilege"}
TD_SHAPE = {"external": ("actor", "tm.Actor"), "process": ("process", "tm.Process"), "store": ("store", "tm.Store")}


def _uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "tm_generator/" + "/".join(parts)))


def _ports(cid):
    grp = {k: {"position": k, "attrs": {"circle": {"r": 4, "magnet": True, "stroke": "#5F95FF", "strokeWidth": 1,
                                                   "fill": "#fff", "style": {"visibility": "hidden"}}}}
           for k in ("top", "right", "bottom", "left")}
    return {"groups": grp, "items": [{"group": k, "id": _uid(cid, "port", k)} for k in grp]}


def _td_threat(t, ix):
    extra = [f'Ref: {ref_text(t.get("refs"))}']
    if quotes(t.get("refs")): extra.append("Evidence: " + quotes(t.get("refs")))
    extra.append("Frameworks: " + t.get("frameworks", ""))
    if t.get("refines"): extra.append("Refines: " + t["refines"])
    if ix["refined_by"].get(t["id"]): extra.append("Refined by: " + ", ".join(ix["refined_by"][t["id"]]))
    if t.get("related"): extra.append("Related: " + ", ".join(t["related"]))
    if ix["asked_in"].get(t["id"]): extra.append("Questions: " + ", ".join(ix["asked_in"][t["id"]]))
    recs = ix["addressed_by"].get(t["id"], [])
    return {"id": _uid("threat", t["id"]), "threatId": _uid("threat", t["id"]), "number": tnum(t["id"]),
            "title": f'{t["id"]}: {t["title"]}', "type": TD_STRIDE.get(t.get("stride", ""), "Tampering"),
            "modelType": "STRIDE", "status": t.get("status", "Open"), "severity": t["severity"],
            "score": str(t["likelihood"] * t["impact"]),
            "description": t.get("description", "") + "\n\n" + "\n".join(extra),
            "mitigation": t.get("control", "") + (("\n\nArchitecture improvement: " + ", ".join(recs)) if recs else "")}


def _td_layout(g):
    """Same column-per-boundary layout as the draw.io pages: returns boundary and element boxes (absolute)."""
    boxes, x, y0 = {}, 20, 120
    for b in g["boundaries"]:
        els = [e for e in g["elements"] if e["boundary"] == b["id"]]
        cols = [els[i:i + 4] for i in range(0, len(els), 4)] or [[]]
        h = 60 + max(sum(SHAPE[e["type"]][2] + 75 for e in c) for c in cols)
        bw = 40 + 215 * len(cols)
        boxes[b["id"]] = (x, y0, bw, h)
        for ci, col in enumerate(cols):
            y = y0 + 50
            for e in col:
                w, hh = (110, 110) if e["type"] == "process" else SHAPE[e["type"]][1:]
                boxes[e["id"]] = (x + 30 + 215 * ci, y, w, hh)
                y += SHAPE[e["type"]][2] + 75
        x += bw + 40
    return boxes


def threatdragon(m, path, ix=None):
    ix = ix or index(m)
    diagrams = []
    for n, g in enumerate(sorted(m["diagrams"], key=lambda d: (d.get("level", 0), d["id"]))):
        gid, cells, box = g["id"], [], _td_layout(g)
        head = f'{gid}: {g["title"]}' + (f' (decomposes {g["parent"]})' if g.get("parent") else "")
        note = head + "\n" + ref_text(g.get("refs")) + ("\n" + g["stop_reason"] if g.get("stop_reason") else "")
        cells.append({"position": {"x": 20, "y": 10}, "size": {"width": 900, "height": 90}, "attrs": {"text": {"text": note}},
                      "visible": True, "shape": "td-text-block", "zIndex": 1, "id": _uid(gid, "title"),
                      "data": {"type": "tm.Text", "name": note, "hasOpenThreats": False}})
        for b in g["boundaries"]:
            x, y, w, h = box[b["id"]]
            cells.append({"position": {"x": x, "y": y}, "size": {"width": w, "height": h},
                          "attrs": {"label": {"text": f'{b["id"]}: {b["name"]}'}}, "visible": True,
                          "shape": "trust-boundary-box", "zIndex": -1, "id": _uid(gid, b["id"]),
                          "data": {"type": "tm.BoundaryBox", "name": f'{b["id"]}: {b["name"]}', "description": "",
                                   "isTrustBoundary": True, "hasOpenThreats": False}})
        for e in g["elements"]:
            shape, typ = TD_SHAPE[e["type"]]
            x, y, w, h = box[e["id"]]
            ctx = bool(e.get("context"))
            tt = [] if ctx else ix["by_target"].get((gid, e["id"]), [])
            name = f'{e["id"]}: {e["name"]}' + (" (ASSUMED)" if e.get("assumed") else "") + \
                (f' [see {ix["child"][e["id"]]}]' if e["id"] in ix["child"] and not ctx else "")
            col = SEV[tt[0]["severity"]][1] if tt else ("#999999" if ctx else "#333333")
            line = {"stroke": col, "strokeWidth": 2.5 if tt else 1, "strokeDasharray": "4 3" if ctx or e.get("assumed") else None}
            attrs = {"text": {"text": name}}
            if shape == "store": attrs.update(topLine=dict(line), bottomLine=dict(line))
            else: attrs["body"] = line
            data = {"name": name, "type": typ, "isTrustBoundary": False, "outOfScope": ctx,
                    "reasonOutOfScope": f'Context from {ix["home"][e["id"]]}' if ctx else "",
                    "description": ("Ref: " + ref_text(e.get("refs"))) if e.get("refs") else "",
                    "hasOpenThreats": any(t.get("status", "Open") == "Open" for t in tt),
                    "threats": [_td_threat(t, ix) for t in tt]}
            if shape == "actor": data["providesAuthentication"] = False
            if shape == "store": data.update(isALog=False, storesCredentials=False, isEncrypted=False, isSigned=False)
            cid = _uid(gid, e["id"])
            cells.append({"position": {"x": x, "y": y}, "size": {"width": w, "height": h}, "attrs": attrs, "visible": True,
                          "shape": shape, "zIndex": 2, "ports": _ports(cid), "id": cid, "data": data})
        for f in g["flows"]:
            tt = ix["by_target"].get((gid, f["id"]), [])
            label = f'{f["id"]}: {f["label"]}' + (" (ASSUMED)" if f.get("assumed") else "")
            cells.append({"shape": "flow", "zIndex": 10, "id": _uid(gid, f["id"]), "connector": "smooth",
                          "attrs": {"line": {"stroke": SEV[tt[0]["severity"]][1] if tt else "#333333",
                                             "targetMarker": {"name": "block"},
                                             "strokeDasharray": "4 3" if f.get("assumed") else None}},
                          "labels": [{"attrs": {"labelText": {"text": label, "textAnchor": "middle", "textVerticalAnchor": "middle"},
                                                "labelBody": {"ref": "labelText", "refRx": "50%", "refRy": "60%", "fill": "#fff", "strokeWidth": 0}},
                                      "markup": [{"tagName": "ellipse", "selector": "labelBody"}, {"tagName": "text", "selector": "labelText"}],
                                      "position": 0.5}],
                          "source": {"cell": _uid(gid, f["from"])}, "target": {"cell": _uid(gid, f["to"])},
                          "data": {"type": "tm.Flow", "name": label, "description": ("Ref: " + ref_text(f.get("refs")) +
                                   (f' | refines {f["parent"]}' if f.get("parent") else "")) if f.get("refs") else "",
                                   "outOfScope": False, "reasonOutOfScope": "", "isBidirectional": False, "isEncrypted": False,
                                   "isPublicNetwork": False, "protocol": "", "isTrustBoundary": False,
                                   "hasOpenThreats": any(t.get("status", "Open") == "Open" for t in tt),
                                   "threats": [_td_threat(t, ix) for t in tt]}})
        diagrams.append({"id": n, "version": "2.3.0", "title": head[:80], "diagramType": "STRIDE",
                         "description": ref_text(g.get("refs")), "thumbnail": "./public/content/images/thumbnail.stride.jpg",
                         "cells": cells})
    docs = "; ".join(f'{d["id"]} = {d.get("name", "")} v{d.get("version", "")}' for d in m["documents"])
    out = {"version": "2.3.0",
           "summary": {"title": m["title"], "owner": m.get("owner", ""), "id": 0,
                       "description": "Generated by tm_generator.py. Threat IDs (T#), references and cross references are in each "
                                      "threat's title and description. Documents: " + docs},
           "detail": {"contributors": [], "diagrams": diagrams, "diagramTop": len(diagrams),
                      "reviewer": "", "threatTop": max((tnum(t["id"]) for t in m["threats"]), default=0)}}
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


# ---------------------------------------------------------------- shared layout (draw.io, Threat Dragon, PNG, PowerPoint)
def layout(g):
    """Column-per-boundary layout. Returns {id: (x, y, w, h)} for boundaries and elements, plus '_size': (w, h)."""
    boxes, x, y0, maxh = {}, 20, 20, 0
    for b in g["boundaries"]:
        els = [e for e in g["elements"] if e["boundary"] == b["id"]]
        cols = [els[i:i + 4] for i in range(0, len(els), 4)] or [[]]
        h = 60 + max(sum(SHAPE[e["type"]][2] + 75 for e in c) for c in cols)
        bw = 40 + 215 * len(cols)
        boxes[b["id"]] = (x, y0, bw, h)
        maxh = max(maxh, h)
        for ci, col in enumerate(cols):
            y = y0 + 50
            for e in col:
                _, w, hh = SHAPE[e["type"]]
                boxes[e["id"]] = (x + 30 + 215 * ci, y, w, hh)
                y += hh + 75
        x += bw + 40
    boxes["_size"] = (x, y0 + maxh + 20)
    return boxes


def ap_layout(a):
    """Attack path chain: actor, steps, objective. Snakes onto further rows (right-to-left on even rows) after 6 boxes
    so arrows never cross. Returns boxes and '_size'."""
    boxes, W, H, GAP, per = {}, 190, 115, 45, 6
    items = ["actor"] + [f"s{n}" for n in range(1, len(a["steps"]) + 1)] + ["impact"]
    for k, key in enumerate(items):
        row, col = divmod(k, per)
        if row % 2: col = per - 1 - col
        boxes[key] = (20 + col * (W + GAP), 20 + row * (H + 110), W, H)
    rows = (len(items) - 1) // per + 1
    boxes["_size"] = (20 + min(len(items), per) * (W + GAP), 20 + rows * (H + 110) - 40)
    return boxes


def _ap_rows(a, ix):
    out = []
    for n, st in enumerate(a["steps"], 1):
        t = ix["t"][st["threat"]]
        out.append((n, st, t, ix["addressed_by"].get(t["id"], [])))
    return out


# ---------------------------------------------------------------- attack path Mermaid
def mermaid_attack(m, aid, ix=None):
    ix = ix or index(m)
    a = ix["ap"][aid]
    q = lambda s: s.replace('"', "'").replace("<", "(").replace(">", ")")
    L = ["flowchart LR", f'  A0["Attacker: {q(a["actor"])}<br/>entry {a["entry"]}"]']
    C, prev = ["  class A0 actor"], "A0"
    for n, st, t, recs in _ap_rows(a, ix):
        L.append(f'  S{n}["{n}. {t["id"]} {t["severity"]} - {q(_name(ix, t["target"]))}<br/>{q(st["action"])}"]')
        L.append(f"  {prev} --> S{n}")
        C.append(f'  class S{n} {t["severity"][:4].lower()}')
        for r in recs:
            L.append(f'  B{n}_{r}{{{{"{r} breaks"}}}} -.- S{n}')
            C.append(f"  class B{n}_{r} rec")
        prev = f"S{n}"
    L.append(f'  IMP(["Objective: {q(a["objective"])}"])')
    L.append(f"  {prev} ==> IMP")
    L += ["  classDef crit fill:#f8d7da,stroke:#b02a37,color:#58151c",
          "  classDef high fill:#fff3cd,stroke:#b8860b,color:#5c4400",
          "  classDef medi fill:#dbe9f6,stroke:#2b6cb0,color:#1a365d",
          "  classDef low fill:#e2e3e5,stroke:#6c757d,color:#343a40",
          "  classDef actor fill:#1f3864,stroke:#1f3864,color:#ffffff",
          "  classDef rec fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20",
          "  style IMP fill:#b02a37,stroke:#58151c,color:#ffffff"] + C
    return "\n".join(L)


# ---------------------------------------------------------------- attack path draw.io pages
def _ap_page(m, a, ix):
    cells, pre, box = [], a["id"] + "|", ap_layout(a)
    _cell(cells, pre + "title", f'{a["id"]}: {a["title"]} ({a["severity"]}, L{a["likelihood"]} x I{a["impact"]})',
          "text;fontSize=18;fontStyle=1;align=left;html=1;", "1", 20, -40, 1200, 30)
    x, y, w, h = box["actor"]
    _cell(cells, pre + "actor", f'Attacker: {a["actor"]} (entry {a["entry"]})',
          "rounded=1;whiteSpace=wrap;html=1;fillColor=#1f3864;fontColor=#ffffff;strokeColor=#1f3864;", "1", x, y, w, h,
          link="data:page/id," + ix["home"][a["entry"]])
    prev = pre + "actor"
    for n, st, t, recs in _ap_rows(a, ix):
        x, y, w, h = box[f"s{n}"]
        fc, sc = SEV[t["severity"]]
        sid = pre + f"s{n}"
        _cell(cells, sid, f'{n}. {t["id"]} {t["severity"]}<br><b>{_name(ix, t["target"])}</b><br>{st["action"]}',
              f"rounded=1;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={sc};fontSize=10;", "1", x, y, w, h,
              tooltip=f'{t["title"]} [{ref_text(t.get("refs"))}] on {t["diagram"]} (click to open)',
              link="data:page/id," + t["diagram"])
        _cell(cells, pre + f"e{n}", "", "endArrow=block;html=1;strokeWidth=2;strokeColor=#b02a37;", "1", 0, 0, 0, 0,
              edge=(prev, sid))
        for i, r in enumerate(recs):
            rid = pre + f"r{n}_{r}"
            _cell(cells, rid, f"{r} breaks", "shape=hexagon;perimeter=hexagonPerimeter2;size=0.15;whiteSpace=wrap;html=1;"
                  "fillColor=#e8f5e9;strokeColor=#2e7d32;fontColor=#1b5e20;fontSize=10;fontStyle=1;", "1",
                  x + 10 + i * 62, y + h + 22, 58, 28, tooltip=ix["r"][r]["title"])
            _cell(cells, rid + "l", "", "endArrow=none;dashed=1;html=1;strokeColor=#2e7d32;", "1", 0, 0, 0, 0, edge=(rid, sid))
        prev = sid
    x, y, w, h = box["impact"]
    _cell(cells, pre + "impact", f'Objective: {a["objective"]}',
          "shape=ellipse;whiteSpace=wrap;html=1;fillColor=#b02a37;fontColor=#ffffff;strokeColor=#58151c;", "1", x, y, w, h)
    _cell(cells, pre + "ei", "", "endArrow=block;html=1;strokeWidth=3;strokeColor=#b02a37;", "1", 0, 0, 0, 0,
          edge=(prev, pre + "impact"))
    return (f'<diagram id={quoteattr(a["id"])} name={quoteattr((a["id"] + " " + a["title"])[:60])}>'
            f'<mxGraphModel grid="1" gridSize="10" tooltips="1"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            f'{"".join(cells)}</root></mxGraphModel></diagram>')


# ---------------------------------------------------------------- Markdown report (what the agent pastes into chat)
def _md(s):
    return str(s if s is not None else "").replace("|", "/").replace("\n", " ")


def report_md(m, ix=None):
    ix = ix or index(m)
    order = sorted(m["diagrams"], key=lambda d: (d.get("level", 0), d["id"]))
    tcols, trows = tables(m, ix)["Threats"]
    T = [dict(zip(tcols, r)) for r in trows]
    out = [f'# {m["title"]}', ""]
    out += ["## 1. Scope", "", "| Doc | Document | Version | Date | Pages |", "|---|---|---|---|---|"]
    out += [f'| {d["id"]} | {_md(d.get("name"))} | {_md(d.get("version"))} | {_md(d.get("date"))} | {_md(d.get("pages"))} |'
            for d in m["documents"]]
    if m.get("summary"): out += ["", m["summary"]]
    if m.get("frameworks_applied"): out += ["", "**Frameworks applied:** " + m["frameworks_applied"]]
    if m.get("assumptions"): out += ["", "**Assumptions:**"] + [f"- {x}" for x in m["assumptions"]]

    def tree(gid, depth=0):
        d = ix["diag"][gid]
        line = f"{'  ' * depth}- **{gid} {d['title']}**" + (f" (decomposes {d['parent']})" if d.get("parent") else "") + \
            f" [{ref_text(d.get('refs'))}] - {d.get('stop_reason', '')}"
        kids = [c for c in order if c.get("parent") and ix["home"].get(c["parent"]) == gid]
        return [line] + [x for c in kids for x in tree(c["id"], depth + 1)]
    out += ["", "## 2. Decomposition map", ""] + tree(order[0]["id"])
    out += ["", "## 3. Diagrams and threats", "",
            "Legend: rectangle = external entity, circle = process, double circle ⊞ = decomposed, cylinder = data store, "
            "grey dashed = context from another level, red dashed box = trust boundary, dashed line = assumed, "
            "hexagon = Critical/High threat, ⚠T# on an arrow = threat on that flow."]
    for d in order:
        out += ["", f"### {d['id']} {d['title']}" + (f" - decomposes {d['parent']}" if d.get("parent") else "") +
                f" [{ref_text(d.get('refs'))}]", "", "```mermaid", mermaid(m, d["id"], ix), "```", "",
                "| ID | Severity | STRIDE | LINDDUN | Target | Problem | Solution | Ref | Refines | Paths |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        out += [f"| {t['ID']} | {t['Severity']} | {t['STRIDE']} | {t['LINDDUN'] or '-'} | {_md(t['Target'])} | {_md(t['Problem'])} | "
                f"{_md(t['Solution (control)'])} | {t['Document reference']} | {t['Refines (parent threat)'] or '-'} | "
                f"{t['Attack paths'] or '-'} |" for t in T if t["Diagram"] == d["id"]]
    out += ["", "## 4. Threat summary", "", "| Diagram | Critical | High | Medium | Low |", "|---|---|---|---|---|"]
    for d in order:
        c = [sum(1 for t in m["threats"] if t["diagram"] == d["id"] and t["severity"] == s) for s in RANK]
        out.append(f"| {d['id']} | " + " | ".join(map(str, c)) + " |")
    out.append("| **Total** | " + " | ".join(str(sum(1 for t in m["threats"] if t["severity"] == s)) for s in RANK) + " |")
    out += ["", "**Privacy (LINDDUN):**", "", "| Category | Threats |", "|---|---|"]
    for code, name in LINDDUN.items():
        ids = [t["ID"] for t in T if code in [c.strip() for c in t["LINDDUN"].split(",")]]
        out.append(f"| {code} {name} | {', '.join(ids) or 'none found'} |")
    if m.get("attack_paths"):
        out += ["", "## 5. Attack paths", "", "| ID | Severity | Attack path | Actor | Steps | Broken by |", "|---|---|---|---|---|---|"]
        for a in m["attack_paths"]:
            recs = sorted({r for _, _, _, rs in _ap_rows(a, ix) for r in rs}, key=tnum)
            out.append(f'| {a["id"]} | {a["severity"]} | {_md(a["title"])} | {_md(a["actor"])} | '
                       f'{" → ".join(s["threat"] for s in a["steps"])} | {", ".join(recs)} |')
        for a in m["attack_paths"]:
            out += ["", f'### {a["id"]} {a["title"]} ({a["severity"]}, L{a["likelihood"]} x I{a["impact"]})', "",
                    f'**Actor:** {a["actor"]} (entry {a["entry"]}). **Objective:** {a["objective"]}', "",
                    "```mermaid", mermaid_attack(m, a["id"], ix), "```", "",
                    "| Step | Threat | Diagram | Target | Attacker action | Broken by | Ref |", "|---|---|---|---|---|---|---|"]
            out += [f'| {n} | {t["id"]} {t["severity"]} | {t["diagram"]} | {_md(_name(ix, t["target"]))} | {_md(st["action"])} | '
                    f'{", ".join(recs) or "-"} | {ref_text(t.get("refs"))} |' for n, st, t, recs in _ap_rows(a, ix)]
    n = 6 if m.get("attack_paths") else 5
    if m.get("review"):
        out += ["", f"## {n}. Review findings", ""] + [f"- {x}" for x in m["review"]]
    n += 1
    out += ["", f"## {n}. Architecture improvements", "", "| ID | Priority | Improvement | Addresses | Attack paths broken | Ref |",
            "|---|---|---|---|---|---|"]
    for r in m.get("recommendations", []):
        aps = sorted({p for x in r["threats"] for p in ix["in_paths"].get(x, [])}, key=tnum)
        out.append(f'| {r["id"]} | {r.get("priority", "")} | **{_md(r["title"])}** - {_md(r.get("description", ""))} | '
                   f'{", ".join(r["threats"])} | {", ".join(aps) or "-"} | {ref_text(r.get("refs"))} |')
    out += ["", f"## {n + 1}. Open questions", "", "| ID | Question | Ask | Ref | Threats |", "|---|---|---|---|---|"]
    out += [f'| {q["id"]} | {_md(q["question"])} | {_md(q.get("ask", ""))} | {ref_text(q.get("refs"))} | {", ".join(q.get("threats", []))} |'
            for q in m.get("questions", [])]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- PNG images (matplotlib)
def _png_dfd(m, gid, path, ix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle, RegularPolygon
    g, box = ix["diag"][gid], layout(ix["diag"][gid])
    W, H = box["_size"]
    fig, ax = plt.subplots(figsize=(max(8, W / 110), max(5, (H + 60) / 110)))
    ax.set_xlim(0, W); ax.set_ylim(H + 40, -50); ax.axis("off")
    ax.text(10, -25, f'{gid}: {g["title"]}' + (f'  (decomposes {g["parent"]})' if g.get("parent") else ""),
            fontsize=12, weight="bold", color="#1f3864")
    for b in g["boundaries"]:
        x, y, w, h = box[b["id"]]
        ax.add_patch(Rectangle((x, y), w, h, fill=False, ec="#c0392b", lw=1.5, ls=(0, (6, 3))))
        ax.text(x + 6, y + 16, f'{b["id"]}: {b["name"]}', fontsize=7, color="#c0392b", weight="bold")
    for e in g["elements"]:
        x, y, w, h = box[e["id"]]
        ctx = bool(e.get("context"))
        tt = [] if ctx else ix["by_target"].get((gid, e["id"]), [])
        ec = "#999999" if ctx else (SEV[tt[0]["severity"]][1] if tt else "#333333")
        fc, ls = ("#f5f5f5", "--") if ctx else ("#ffffff", "-")
        if e["type"] == "process":
            ax.add_patch(Ellipse((x + w / 2, y + h / 2), w, h, fc=fc, ec=ec, lw=1.6, ls=ls))
            if e["id"] in ix["child"] and not ctx:
                ax.add_patch(Ellipse((x + w / 2, y + h / 2), w - 10, h - 10, fill=False, ec=ec, lw=1))
        elif e["type"] == "store":
            ax.add_patch(Rectangle((x, y + 6), w, h - 12, fc=fc, ec="none"))
            for yy in (y + 6, y + h - 6):
                ax.add_patch(Ellipse((x + w / 2, yy), w, 12, fc=fc, ec=ec, lw=1.4, ls=ls))
            ax.plot([x, x], [y + 6, y + h - 6], color=ec, lw=1.4, ls=ls); ax.plot([x + w, x + w], [y + 6, y + h - 6], color=ec, lw=1.4, ls=ls)
        else:
            ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.6, ls=ls))
        label = f'{e["id"]}: {e["name"]}' + (" ⊞" if e["id"] in ix["child"] and not ctx else "")
        ax.text(x + w / 2, y + h / 2, "\n".join(_wrap(label, 22)), ha="center", va="center", fontsize=6.5,
                color="#666666" if ctx else "#111111")
        for i, t in enumerate(tt):
            fcol, scol = SEV[t["severity"]]
            cx, cy = x + w - 5 + (i % 3) * 30, y - 6 - (i // 3) * 20
            ax.add_patch(RegularPolygon((cx, cy), 6, radius=13, orientation=0.52, fc=fcol, ec=scol, lw=1))
            ax.text(cx, cy, t["id"], ha="center", va="center", fontsize=5.5, color=scol, weight="bold")
    for f in g["flows"]:
        (x1, y1, w1, h1), (x2, y2, w2, h2) = box[f["from"]], box[f["to"]]
        p1, p2 = _edge_pts((x1, y1, w1, h1), (x2, y2, w2, h2))
        tt = ix["by_target"].get((gid, f["id"]), [])
        col = SEV[tt[0]["severity"]][1] if tt else "#444444"
        ax.annotate("", p2, p1, arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, ls="--" if f.get("assumed") else "-",
                                                 shrinkA=0, shrinkB=0))
        lab = f["id"] + (" ⚠" + ",".join(t["id"] for t in tt) if tt else "")
        ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, lab, fontsize=5.5, ha="center", va="center", color=col,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _png_attack(m, aid, path, ix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, RegularPolygon
    a, box = ix["ap"][aid], ap_layout(ix["ap"][aid])
    W, H = box["_size"]
    fig, ax = plt.subplots(figsize=(max(8, W / 110), max(3.2, (H + 60) / 110)))
    ax.set_xlim(0, W); ax.set_ylim(H + 30, -45); ax.axis("off")
    ax.text(10, -22, f'{a["id"]}: {a["title"]}  ({a["severity"]}, L{a["likelihood"]} x I{a["impact"]})',
            fontsize=11, weight="bold", color="#1f3864")

    def card(key, text, fc, ec, tc="#111111"):
        x, y, w, h = box[key]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=2,rounding_size=10", fc=fc, ec=ec, lw=1.4))
        ax.text(x + w / 2, y + h / 2, "\n".join(_wrap(text, 30)[:7]), ha="center", va="center", fontsize=6.2, color=tc)
    card("actor", f'Attacker: {a["actor"]}\n(entry {a["entry"]})', "#1f3864", "#1f3864", "#ffffff")
    prev = "actor"
    for n, st, t, recs in _ap_rows(a, ix):
        fc, sc = SEV[t["severity"]]
        card(f"s{n}", f'{n}. {t["id"]} {t["severity"]}\n{_name(ix, t["target"])}\n{st["action"]}', fc, sc)
        _arrow(ax, box[prev], box[f"s{n}"])
        x, y, w, h = box[f"s{n}"]
        for i, r in enumerate(recs):
            cx, cy = x + 25 + i * 48, y + h + 28
            ax.add_patch(RegularPolygon((cx, cy), 6, radius=20, orientation=0.52, fc="#e8f5e9", ec="#2e7d32"))
            ax.text(cx, cy, r, ha="center", va="center", fontsize=6.5, color="#1b5e20", weight="bold")
            ax.plot([cx, cx], [y + h, cy - 18], color="#2e7d32", lw=0.8, ls="--")
        prev = f"s{n}"
    card("impact", "Objective: " + a["objective"], "#b02a37", "#58151c", "#ffffff")
    _arrow(ax, box[prev], box["impact"])
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _wrap(text, n):
    import textwrap
    return [l for part in str(text).split("\n") for l in (textwrap.wrap(part, n) or [""])]


def _edge_pts(a, b):
    (x1, y1, w1, h1), (x2, y2, w2, h2) = a, b
    c1, c2 = (x1 + w1 / 2, y1 + h1 / 2), (x2 + w2 / 2, y2 + h2 / 2)
    if abs(c2[0] - c1[0]) >= abs(c2[1] - c1[1]):
        s = 1 if c2[0] > c1[0] else -1
        return (c1[0] + s * w1 / 2, c1[1]), (c2[0] - s * w2 / 2, c2[1])
    s = 1 if c2[1] > c1[1] else -1
    return (c1[0], c1[1] + s * h1 / 2), (c2[0], c2[1] - s * h2 / 2)


def _arrow(ax, a, b):
    p1, p2 = _edge_pts(a, b)
    ax.annotate("", p2, p1, arrowprops=dict(arrowstyle="-|>", color="#b02a37", lw=1.8, shrinkA=2, shrinkB=2))


def pngs(m, name, ix=None):
    ix = ix or index(m)
    files = []
    for d in sorted(m["diagrams"], key=lambda d: (d.get("level", 0), d["id"])):
        p = f'{name}_{d["id"]}.png'; _png_dfd(m, d["id"], p, ix); files.append(p)
    for a in m.get("attack_paths", []):
        p = f'{name}_{a["id"]}.png'; _png_attack(m, a["id"], p, ix); files.append(p)
    return files


def embed_images(xlsx, files, ix):
    """Adds a 'Diagram images' sheet with every PNG (needs openpyxl + Pillow)."""
    from openpyxl import load_workbook
    from openpyxl.drawing.image import Image
    wb = load_workbook(xlsx)
    ws = wb.create_sheet("Diagram images", 1)
    ws.column_dimensions["A"].width = 160
    row = 1
    for f in files:
        ws.cell(row, 1, f.rsplit("_", 1)[-1].replace(".png", "")).style = "Headline 2"
        img = Image(f)
        scale = min(1.0, 1100 / img.width)
        img.width, img.height = img.width * scale, img.height * scale
        ws.add_image(img, f"A{row + 1}")
        row += int(img.height / 20) + 4
    wb.save(xlsx)


# ---------------------------------------------------------------- PowerPoint deck (python-pptx, native editable shapes)
NAVY = "1F3864"


def deck(m, path, ix=None, images=None):
    ix = ix or index(m)
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.oxml.ns import qn
    from pptx.util import Emu, Inches, Pt
    rgb = lambda h: RGBColor.from_string(h.lstrip("#").upper())
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    order = sorted(m["diagrams"], key=lambda d: (d.get("level", 0), d["id"]))

    def text(slide, x, y, w, h, s, size=12, bold=False, color="222222", align=None, anchor=None):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame; tf.word_wrap = True
        if anchor: tf.vertical_anchor = anchor
        for i, line in enumerate(str(s).split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = rgb(color)
            if align: p.alignment = align
        return tb

    def page(title, source=""):
        s = prs.slides.add_slide(blank)
        text(s, 0.4, 0.25, 12.5, 0.8, title, 20, True, NAVY)
        ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.4), Inches(1.05), Inches(12.93), Inches(1.05))
        ln.line.color.rgb = rgb(NAVY); ln.line.width = Pt(1.5)
        if source: text(s, 0.4, 7.05, 12.5, 0.3, "Source: " + source, 8, False, "666666")
        text(s, 12.3, 7.05, 0.7, 0.3, str(len(prs.slides._sldIdLst)), 8, False, "666666", PP_ALIGN.RIGHT)
        return s

    def table(s, cols, rows, widths, y=1.25, size=8, header=NAVY):
        if not rows: return
        t = s.shapes.add_table(len(rows) + 1, len(cols), Inches(0.4), Inches(y), Inches(sum(widths)), Inches(0.3)).table
        for j, (c, w) in enumerate(zip(cols, widths)):
            t.columns[j].width = Inches(w)
            cell = t.cell(0, j); cell.text = c
            cell.fill.solid(); cell.fill.fore_color.rgb = rgb(header)
            for p in cell.text_frame.paragraphs: p.font.size = Pt(size); p.font.bold = True; p.font.color.rgb = rgb("FFFFFF")
        for i, r in enumerate(rows, 1):
            for j, v in enumerate(r):
                cell = t.cell(i, j); cell.text = str(v)
                cell.fill.solid(); cell.fill.fore_color.rgb = rgb(SEV[v][0] if v in SEV else ("FFFFFF" if i % 2 else "F2F4F8"))
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(size); p.font.color.rgb = rgb(SEV[v][1] if v in SEV else "222222"); p.font.bold = v in SEV

    def shape(s, kind, x, y, w, h, label, fill, line, size=8, dash=False, font="111111", bold=False):
        sh = s.shapes.add_shape(kind, Emu(x), Emu(y), Emu(w), Emu(h))
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        sh.line.color.rgb = rgb(line); sh.line.width = Pt(1.25)
        if dash:
            from pptx.enum.dml import MSO_LINE
            sh.line.dash_style = MSO_LINE.DASH
        tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(tf, side, Emu(20000))
        for i, line_ in enumerate(str(label).split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line_; p.alignment = PP_ALIGN.CENTER
            p.font.size = Pt(size); p.font.color.rgb = rgb(font); p.font.bold = bold
        return sh

    SITES = {"oval": {"top": 0, "left": 2, "bottom": 4, "right": 6}}  # OOXML ellipse: 8 sites counter-clockwise from top
    SITES4 = {"top": 0, "left": 1, "bottom": 2, "right": 3}            # rectangle, rounded rectangle, can

    def connect(s, a, b, color, width=1.25, dash=False, arrow=True, attach=True):
        def side(p, q):
            dx, dy = (q[0] + q[2] / 2) - (p[0] + p[2] / 2), (q[1] + q[3] / 2) - (p[1] + p[3] / 2)
            return ("right" if dx > 0 else "left") if abs(dx) >= abs(dy) else ("bottom" if dy > 0 else "top")
        pa, pb = (a.left, a.top, a.width, a.height), (b.left, b.top, b.width, b.height)
        (x1, y1), (x2, y2) = _edge_pts(pa, pb)
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, int(x1), int(y1), int(x2), int(y2))
        if attach:  # glue both ends so the line follows when shapes are moved in PowerPoint
            for end, sh, sd in (("begin", a, side(pa, pb)), ("end", b, side(pb, pa))):
                getattr(c, end + "_connect")(sh, 0)
                kind = "oval" if sh.auto_shape_type == MSO_SHAPE.OVAL else "rect"
                idx = SITES.get(kind, SITES4)[sd]
                cx = c._element.nvCxnSpPr.cNvCxnSpPr
                (cx.stCxn if end == "begin" else cx.endCxn).set("idx", str(idx))
            c.begin_x, c.begin_y, c.end_x, c.end_y = int(x1), int(y1), int(x2), int(y2)
        c.line.color.rgb = rgb(color); c.line.width = Pt(width)
        if dash:
            from pptx.enum.dml import MSO_LINE
            c.line.dash_style = MSO_LINE.DASH
        if arrow:
            ln = c.line._get_or_add_ln()
            ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
        return c

    # 1 title
    s = prs.slides.add_slide(blank)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = rgb(NAVY); bg.line.fill.background()
    text(s, 0.8, 2.3, 11.5, 1.4, m["title"], 32, True, "FFFFFF")
    text(s, 0.8, 3.9, 11.5, 1.6, "\n".join(f'{d["id"]}: {d.get("name", "")} v{d.get("version", "")}' for d in m["documents"]),
         14, False, "D9E1F2")
    # 2 executive summary
    cnt = {k: sum(1 for t in m["threats"] if t["severity"] == k) for k in RANK}
    crit = [t for t in sorted(m["threats"], key=lambda t: tnum(t["id"])) if t["severity"] == "Critical"]
    p1 = [r for r in m.get("recommendations", []) if r.get("priority") == "P1"]
    s = page(f'{cnt["Critical"]} Critical and {cnt["High"]} High threats across {len(order)} diagrams; '
             f'{len(p1)} P1 architecture changes break {len(m.get("attack_paths", []))} key attack paths')
    for i, (k, v) in enumerate(cnt.items()):
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4 + i * 1.6), Inches(1.3), Inches(1.45), Inches(0.9),
              f"{v}\n{k}", SEV[k][0].lstrip("#"), SEV[k][1].lstrip("#"), 14, font=SEV[k][1].lstrip("#"), bold=True)
    text(s, 0.4, 2.4, 6.2, 0.4, "Critical threats", 13, True, NAVY)
    text(s, 0.4, 2.8, 6.2, 4.1, "\n".join(f'{t["id"]} {t["title"]} [{ref_text(t.get("refs"))}]' for t in crit[:9]), 10)
    text(s, 6.9, 2.4, 6.0, 0.4, "P1 architecture improvements", 13, True, NAVY)
    text(s, 6.9, 2.8, 6.0, 4.1, "\n".join(f'{r["id"]} {r["title"]} - addresses {", ".join(r["threats"])}' for r in p1), 10)
    # 3 decomposition map
    s = page("System modelled top-down: " + ", ".join(d["id"] for d in order),
             "; ".join(ref_text(d.get("refs")) for d in order[:2]))
    rows = [[d["id"], "L" + str(d.get("level", 0)), d["title"], d.get("parent", "-"), d.get("stop_reason", "")] for d in order]
    table(s, ["Diagram", "Level", "Title", "Decomposes", "Why opened / where it stopped"], rows, [1.2, 0.6, 2.4, 1.1, 7.2], size=9)
    # 4 per diagram: DFD (native shapes) + threat tables
    for d in order:
        gid = d["id"]
        tt_all = [t for t in sorted(m["threats"], key=lambda t: tnum(t["id"])) if t["diagram"] == gid]
        top = next((t for t in tt_all if t["severity"] == "Critical"), tt_all[0] if tt_all else None)
        c = {k: sum(1 for t in tt_all if t["severity"] == k) for k in RANK}
        title = f'{gid} {d["title"]}: {c["Critical"]} Critical, {c["High"]} High' + (f' - key risk {top["id"]} {top["title"]}' if top else "")
        s = page(title, ref_text(d.get("refs")))
        box = layout(d); W, H = box["_size"]
        sc = min(Inches(12.5) / W, Inches(5.7) / H)
        X = lambda v: int(Inches(0.4) + v * sc); Y = lambda v: int(Inches(1.25) + v * sc)
        for b in d["boundaries"]:
            x, y, w, h = box[b["id"]]
            r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, X(x), Y(y), int(w * sc), int(h * sc))
            r.fill.background(); r.line.color.rgb = rgb("C0392B"); r.line.width = Pt(1.5)
            from pptx.enum.dml import MSO_LINE
            r.line.dash_style = MSO_LINE.DASH
            tf = r.text_frame; tf.vertical_anchor = MSO_ANCHOR.TOP; tf.word_wrap = True
            tf.paragraphs[0].text = f'{b["id"]}: {b["name"]}'; tf.paragraphs[0].font.size = Pt(8)
            tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.color.rgb = rgb("C0392B"); tf.paragraphs[0].alignment = PP_ALIGN.LEFT
        shp = {}
        for e in d["elements"]:
            x, y, w, h = box[e["id"]]
            ctx = bool(e.get("context"))
            tt = [] if ctx else ix["by_target"].get((gid, e["id"]), [])
            kind = {"external": MSO_SHAPE.RECTANGLE, "process": MSO_SHAPE.OVAL, "store": MSO_SHAPE.CAN}[e["type"]]
            dec = e["id"] in ix["child"] and not ctx
            line = "999999" if ctx else (SEV[tt[0]["severity"]][1].lstrip("#") if tt else "333333")
            shp[e["id"]] = shape(s, kind, X(x), Y(y), int(w * sc), int(h * sc),
                                 f'{e["id"]}: {e["name"]}' + (" ⊞" if dec else ""), "F5F5F5" if ctx else "FFFFFF", line,
                                 7, dash=ctx, font="666666" if ctx else "111111")
            if dec: shp[e["id"]].line.width = Pt(3)
            for i, t in enumerate(tt):
                fcol, scol = SEV[t["severity"]]
                shape(s, MSO_SHAPE.HEXAGON, X(x + w - 20 + (i % 3) * 34), Y(y - 18 - (i // 3) * 22), int(32 * sc * 1.3),
                      int(18 * sc * 1.3), t["id"], fcol.lstrip("#"), scol.lstrip("#"), 6, font=scol.lstrip("#"), bold=True)
        for f in d["flows"]:
            tt = ix["by_target"].get((gid, f["id"]), [])
            col = SEV[tt[0]["severity"]][1].lstrip("#") if tt else "444444"
            cn = connect(s, shp[f["from"]], shp[f["to"]], col, dash=bool(f.get("assumed")))
            mx, my = (cn.begin_x + cn.end_x) // 2, (cn.begin_y + cn.end_y) // 2
            lb = s.shapes.add_textbox(mx - Inches(0.45), my - Inches(0.1), Inches(0.9), Inches(0.2))
            lb.text_frame.paragraphs[0].text = f["id"] + (" ⚠" + ",".join(t["id"] for t in tt) if tt else "")
            lb.text_frame.paragraphs[0].font.size = Pt(6); lb.text_frame.paragraphs[0].font.color.rgb = rgb(col)
            lb.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        for k in range(0, len(tt_all), 7):
            chunk = tt_all[k:k + 7]
            s = page(f'{gid} threats ({k + 1}-{k + len(chunk)} of {len(tt_all)}): problem, solution and reference',
                     ref_text(d.get("refs")))
            table(s, ["ID", "Severity", "STRIDE / LINDDUN", "Target", "Problem", "Solution", "Ref", "Refines / paths"],
                  [[t["id"], t["severity"], t.get("stride", "") + (" / " + linddun(t) if linddun(t) else ""),
                    _name(ix, t["target"]), t["title"] + ". " + t.get("description", ""), t.get("control", ""),
                    ref_text(t.get("refs")), (t.get("refines", "") or "-") + " / " + (", ".join(ix["in_paths"].get(t["id"], [])) or "-")]
                   for t in chunk], [0.5, 0.8, 0.9, 1.6, 3.6, 3.1, 1.1, 0.9], size=8)
    # 5 attack paths
    if m.get("attack_paths"):
        s = page(f'{len(m["attack_paths"])} key attack paths chain threats across levels; each is broken by at least one improvement')
        table(s, ["ID", "Severity", "Attack path", "Actor", "Steps", "Broken by"],
              [[a["id"], a["severity"], a["title"], a["actor"], " → ".join(x["threat"] for x in a["steps"]),
                ", ".join(sorted({r for _, _, _, rs in _ap_rows(a, ix) for r in rs}, key=tnum))] for a in m["attack_paths"]],
              [0.6, 0.9, 4.2, 2.6, 2.6, 1.6], size=10)
        for a in m["attack_paths"]:
            s = page(f'{a["id"]} ({a["severity"]}): {a["title"]}',
                     "; ".join(sorted({ref_text(ix["t"][x["threat"]].get("refs")) for x in a["steps"]})))
            box = ap_layout(a); W, H = box["_size"]
            sc = min(Inches(12.5) / W, Inches(2.9) / (H + 40))
            X = lambda v: int(Inches(0.4) + v * sc); Y = lambda v: int(Inches(1.3) + v * sc)
            x, y, w, h = box["actor"]
            prev = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, X(x), Y(y), int(w * sc), int(h * sc),
                         f'Attacker: {a["actor"]}\n(entry {a["entry"]})', NAVY, NAVY, 8, font="FFFFFF", bold=True)
            for n, st, t, recs in _ap_rows(a, ix):
                x, y, w, h = box[f"s{n}"]
                fcol, scol = SEV[t["severity"]]
                cur = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, X(x), Y(y), int(w * sc), int(h * sc),
                            f'{n}. {t["id"]} {t["severity"]}\n{_name(ix, t["target"])}', fcol.lstrip("#"), scol.lstrip("#"), 7)
                connect(s, prev, cur, "B02A37", 2)
                for i, r in enumerate(recs):
                    hx = shape(s, MSO_SHAPE.HEXAGON, X(x + 10 + i * 62), Y(y + h + 30), int(56 * sc), int(32 * sc), r,
                               "E8F5E9", "2E7D32", 7, font="1B5E20", bold=True)
                    vx = hx.left + hx.width // 2
                    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, vx, hx.top, vx, cur.top + cur.height)
                    ln.line.color.rgb = rgb("2E7D32"); ln.line.width = Pt(1)
                    from pptx.enum.dml import MSO_LINE
                    ln.line.dash_style = MSO_LINE.DASH
                prev = cur
            x, y, w, h = box["impact"]
            imp = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, X(x), Y(y), int(w * sc), int(h * sc), "Objective: " + a["objective"],
                        "B02A37", "58151C", 7, font="FFFFFF", bold=True)
            connect(s, prev, imp, "B02A37", 2.5)
            table(s, ["Step", "Threat", "Diagram", "Target", "Attacker action", "Broken by", "Ref"],
                  [[n, f'{t["id"]} {t["severity"]}', t["diagram"], _name(ix, t["target"]), st["action"],
                    ", ".join(recs) or "-", ref_text(t.get("refs"))] for n, st, t, recs in _ap_rows(a, ix)],
                  [0.5, 1.2, 1.0, 2.2, 4.6, 1.2, 1.8], y=4.45, size=8)
    # 6 improvements and questions
    recs = m.get("recommendations", [])
    for k in range(0, len(recs), 6):
        s = page(f'Architecture improvements ({k + 1}-{min(k + 6, len(recs))} of {len(recs)}): structural changes, not point fixes')
        table(s, ["ID", "Priority", "Improvement", "Addresses", "Attack paths broken", "Ref"],
              [[r["id"], r.get("priority", ""), r["title"] + ": " + r.get("description", ""), ", ".join(r["threats"]),
                ", ".join(sorted({p for x in r["threats"] for p in ix["in_paths"].get(x, [])}, key=tnum)) or "-",
                ref_text(r.get("refs"))] for r in recs[k:k + 6]], [0.5, 0.7, 6.6, 1.9, 1.3, 1.5], size=9)
    qs = m.get("questions", [])
    for k in range(0, len(qs), 8):
        s = page(f'Open questions for the document authors ({k + 1}-{min(k + 8, len(qs))} of {len(qs)})')
        table(s, ["ID", "Question", "Ask", "Ref", "Threats"],
              [[q["id"], q["question"], q.get("ask", ""), ref_text(q.get("refs")), ", ".join(q.get("threats", []))]
               for q in qs[k:k + 8]], [0.5, 7.0, 2.0, 1.6, 1.4], size=10)
    # 7 legend / method
    s = page("Method and legend")
    text(s, 0.4, 1.3, 12.4, 5.6,
         "Method: L0 context DFD, then L1/L2 decomposition where the documents describe 3+ internal parts and the component is "
         "high-risk; full STRIDE per element, LINDDUN for personal data and the applicable OWASP lists at every level; "
         "likelihood x impact scoring (Critical 20-25, High 12-19, Medium 6-11, Low 1-5); attack paths chain threats from an "
         "attacker entry point to an objective.\n\n"
         "Legend: rectangle = external entity; oval = process (thick border ⊞ = decomposed); cylinder = data store; grey dashed = "
         "context from another level; red dashed box = trust boundary; hexagon = threat (colour = severity); green hexagon = "
         "improvement that breaks an attack step; ⚠T# on a flow = threat on that flow.\n\n"
         "References: DOC1 §4.3 p.11 Table 4 = document, section, page, location; 'gap' = the documents are silent.\n\n"
         "All shapes and tables are native PowerPoint objects and can be edited.", 12)
    prs.save(path)

# ---------------------------------------------------------------- run
def run(m, name="threat_model"):
    warns = validate(m)
    ix = index(m)
    files = [name + ".drawio"]
    drawio(m, name + ".drawio", ix)
    files.append(register(m, name + "_register.xlsx", ix))
    json.dump(m, open(name + "_model.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    threatdragon(m, name + "_threatdragon.json", ix)
    report = report_md(m, ix)
    open(name + "_report.md", "w", encoding="utf-8").write(report)
    files += [name + "_model.json", name + "_threatdragon.json", name + "_report.md"]
    try:  # optional: needs matplotlib (and Pillow for embedding in Excel)
        imgs = pngs(m, name, ix)
        import zipfile
        with zipfile.ZipFile(name + "_diagrams_png.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for f in imgs: z.write(f)
        files.append(name + "_diagrams_png.zip")
        try:
            if files[1].endswith(".xlsx"): embed_images(files[1], imgs, ix)
        except Exception as e:
            print("SKIPPED images in Excel:", type(e).__name__, e)
    except Exception as e:
        imgs = []
        print("SKIPPED PNG images:", type(e).__name__, e)
    try:  # optional: needs python-pptx
        deck(m, name + "_deck.pptx", ix)
        files.append(name + "_deck.pptx")
    except Exception as e:
        print("SKIPPED PowerPoint deck:", type(e).__name__, e)
    print("FILES:", ", ".join(files))
    for w in warns: print("WARNING:", w)
    print("REPORT_START\n" + report + "REPORT_END")
    return warns


if __name__ == "__main__" and "ipykernel" not in sys.modules and len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
    MODEL = json.load(open(sys.argv[1], encoding="utf-8"))
    run(MODEL, sys.argv[2] if len(sys.argv) > 2 else "threat_model")
```
