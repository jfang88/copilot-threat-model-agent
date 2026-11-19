---
title: "TM-03 Generator Script and JSON Model Schema"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v2.0"
---

# TM-03 What the generator does

tm_generator.py turns one JSON threat model (all levels) into outputs that always agree with each other:

- <system>.drawio - one page per diagram (L0, L1-P#, L2-P#.#). Decomposed processes are double ellipses marked ⊞ and link to their child page; context elements are grey and link back to the page that defines them; every page has a Back link. Hover any element, flow or threat badge for its document references and threats.
- <system>_register.xlsx - one workbook for all levels: Read me, Threats (Problem, Solution and Document reference grouped together, with Refines / Refined by / Related / Arch. improvement / Open questions cross references as clickable links), Arch improvements, Open questions, Elements & flows, Diagrams, Documents.
- <system>_model.json - the model, so the run can be repeated or updated later.
- <system>_threatdragon.json - OWASP Threat Dragon v2 model: one Threat Dragon diagram per level, trust boundary boxes, actors/processes/stores/flows, and every threat on its element or flow with severity, STRIDE type, mitigation, score, and the T# ID, references and cross references in its title and description. Context elements are marked out of scope. Open it in Threat Dragon (web or desktop) with Open an existing threat model.
- Mermaid text for each diagram, printed between "MERMAID_START <diagram>: <title>" and "MERMAID_END".

It validates first and stops with MODEL INVALID on errors: duplicate IDs; broken references; child IDs not prefixed with the parent; a parent flow that is not in the parent diagram; threats whose target is not an own element or flow of their diagram; likelihood or impact outside 1-5; severity that does not match likelihood x impact; threats, improvements or questions without refs; refs to unknown documents; refines that does not point to a higher-level threat.

It prints WARNING for: a Critical/High threat not addressed by any improvement; a Critical/High threat on a decomposed element not refined in the child; a gap threat without a question; a diagram over 20 elements; a child diagram with fewer than 3 own elements; an element without refs.

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
4. Provide the .drawio, .xlsx, _model.json and _threatdragon.json files for download and paste each Mermaid block unchanged.

# TM-03 JSON model schema

```
{
  "title": "Threat model - <system name>",
  "documents": [ {"id": "DOC1", "name": "file name", "version": "0.9", "date": "2026-10-02", "pages": 24} ],
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
- Boundaries are drawn left to right in the order listed: most untrusted first, build and admin planes last. More than four elements in a boundary wrap into extra columns.

# TM-03 Script: tm_generator.py

```python
# tm_generator.py  v2.2 - multi-level threat model renderer for the Copilot DFD agent
# Copilot code interpreter: load this file with exec(open(path).read()), build MODEL (schema in TM-03), then run(MODEL, "<system>")
# Command line: python tm_generator.py model.json [output_name]
# Outputs: <name>.drawio (one page per diagram, clickable drill-down), <name>_register.xlsx (all levels, cross-referenced),
#          <name>_model.json (re-runnable), <name>_threatdragon.json (OWASP Threat Dragon v2 import),
#          Mermaid per diagram printed between MERMAID_START/MERMAID_END markers.
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
    if err: raise SystemExit("MODEL INVALID:\n" + "\n".join(err))
    # coverage warnings
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
    xml = '<mxfile host="tm_generator">' + "".join(_page(m, g, ix) for g in order) + "</mxfile>"
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
               ("Refined by (child threats)", 14), ("Related", 12), ("Open questions", 11), ("Status", 10), ("Owner", 14)]


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
                ", ".join(ix["asked_in"].get(t["id"], [])), t.get("status", "Open"), t.get("owner", "")] for t in ts]
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
        for i, r in enumerate(rows): rowmap[r[0]] = (sheet, i + 2)
    hdr_fill, hdr_font = PatternFill("solid", fgColor="1F3864"), Font(bold=True, color="FFFFFF")
    group = {"Problem": "FDEDEC", "Problem detail": "FDEDEC", "Solution (control)": "E8F5E9", "Arch. improvement": "E8F5E9",
             "Document reference": "EAF2FB", "Evidence (quote)": "EAF2FB"}
    linkcols = {"Arch. improvement", "Refines (parent threat)", "Refined by (child threats)", "Related", "Open questions",
                "Addresses threats", "Related threats", "Decomposed in", "Parent", "Threats", "Decomposes", "Diagram"}
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
             "Sheets: Threats (all levels: L0, L1, L2) | Arch improvements | Open questions | Elements & flows | Diagrams | Documents",
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


# ---------------------------------------------------------------- run
def run(m, name="threat_model"):
    warns = validate(m)
    ix = index(m)
    drawio(m, name + ".drawio", ix)
    reg = register(m, name + "_register.xlsx", ix)
    json.dump(m, open(name + "_model.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    threatdragon(m, name + "_threatdragon.json", ix)
    print("FILES:", name + ".drawio", reg, name + "_model.json", name + "_threatdragon.json")
    for w in warns: print("WARNING:", w)
    for g in sorted(m["diagrams"], key=lambda g: (g.get("level", 0), g["id"])):
        print(f'MERMAID_START {g["id"]}: {g["title"]}\n' + mermaid(m, g["id"], ix) + "\nMERMAID_END")
    return warns


if __name__ == "__main__" and "ipykernel" not in sys.modules and len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
    MODEL = json.load(open(sys.argv[1], encoding="utf-8"))
    run(MODEL, sys.argv[2] if len(sys.argv) > 2 else "threat_model")
```
