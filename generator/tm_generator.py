# tm_generator.py  v1.0  - threat model renderer for the Copilot DFD agent
# Usage : python tm_generator.py model.json [output_name]   |  in Copilot: replace the MODEL = json.load(...) line
# Input : MODEL (dict, schema in TM-03).  Output: <name>.drawio, <name>_register.xlsx, Mermaid text (printed)
# Do not modify this script. Only replace the MODEL dict at the bottom.
import json, re
from xml.sax.saxutils import escape

SEV = {"Critical": ("#f8d7da", "#b02a37"), "High": ("#fff3cd", "#b8860b"),
       "Medium": ("#dbe9f6", "#2b6cb0"), "Low": ("#e2e3e5", "#6c757d")}
RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
SHAPE = {"external": ("rounded=0;whiteSpace=wrap;html=1;", 150, 60),
         "process": ("ellipse;whiteSpace=wrap;html=1;", 150, 80),
         "store": ("shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=10;", 150, 70)}

def validate(m):
    err, ids = [], {}
    for k in ("boundaries", "elements", "flows", "threats"):
        for o in m.get(k, []):
            if o["id"] in ids: err.append("duplicate id " + o["id"])
            ids[o["id"]] = k
            if not re.fullmatch(r"[A-Za-z0-9]+", o["id"]): err.append("bad id " + o["id"])
    for e in m["elements"]:
        if e["type"] not in SHAPE: err.append(e["id"] + " bad type")
        if ids.get(e.get("boundary")) != "boundaries": err.append(e["id"] + " bad boundary")
    for f in m["flows"]:
        for end in (f["from"], f["to"]):
            if ids.get(end) != "elements": err.append(f["id"] + " bad endpoint " + end)
    for t in m["threats"]:
        if ids.get(t["target"]) not in ("elements", "flows"): err.append(t["id"] + " bad target")
        if t["severity"] not in SEV: err.append(t["id"] + " bad severity")
        sc = t.get("likelihood", 0) * t.get("impact", 0)
        exp = "Critical" if sc >= 20 else "High" if sc >= 12 else "Medium" if sc >= 6 else "Low"
        if not (1 <= t.get("likelihood", 0) <= 5 and 1 <= t.get("impact", 0) <= 5): err.append(t["id"] + " L/I must be 1-5")
        elif exp != t["severity"]: err.append(f'{t["id"]} severity should be {exp} (L{t["likelihood"]} x I{t["impact"]} = {sc})')
    if err: raise SystemExit("MODEL INVALID:\n" + "\n".join(err))

def by_target(m):
    d = {}
    for t in sorted(m["threats"], key=lambda t: (-RANK[t["severity"]], t["id"])):
        d.setdefault(t["target"], []).append(t)
    return d

def flow_label(f, tt):
    s = f["id"] + ": " + f["label"] + (" (ASSUMED)" if f.get("assumed") else "")
    return s + (" ⚠" + ",".join(t["id"] for t in tt) if tt else "")

def drawio(m, path):
    tt, cells, y0, gap = by_target(m), [], 70, 40
    cell = lambda i, v, st, p, x, y, w, h: cells.append(
        f'<mxCell id="{i}" value="{escape(v, {chr(34): "&quot;"})}" style="{st}" vertex="1" parent="{p}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    cell("title", m["title"], "text;fontSize=18;fontStyle=1;align=left;html=1;", "1", 20, 10, 800, 30)
    maxh, x = 0, 20
    for b in m["boundaries"]:
        els = [e for e in m["elements"] if e["boundary"] == b["id"]]
        h = 60 + sum(SHAPE[e["type"]][2] + 70 for e in els)
        maxh = max(maxh, h)
        cell(b["id"], b["id"] + ": " + b["name"],
             "rounded=1;dashed=1;dashPattern=8 4;strokeColor=#c0392b;strokeWidth=2;fillColor=none;"
             "verticalAlign=top;align=left;spacingLeft=8;fontStyle=1;container=1;collapsible=0;html=1;",
             "1", x, y0, 230, h)
        y = 50
        for e in els:
            st, w, hh = SHAPE[e["type"]]
            et = tt.get(e["id"], [])
            if et: st += f"strokeColor={SEV[et[0]['severity']][1]};strokeWidth=2;"
            if e.get("assumed"): st += "dashed=1;"
            cell(e["id"], e["id"] + ": " + e["name"] + (" (ASSUMED)" if e.get("assumed") else ""),
                 st, b["id"], 40, y, w, hh)
            for i, t in enumerate(et):
                f_, s_ = SEV[t["severity"]]
                cell(t["id"] + "b", t["id"], f"shape=hexagon;perimeter=hexagonPerimeter2;size=0.2;fillColor={f_};"
                     f"strokeColor={s_};fontColor={s_};fontStyle=1;fontSize=10;html=1;", e["id"],
                     w - 25 + (i % 3) * 38, -14 - (i // 3) * 24, 36, 22)
            y += hh + 70
        x += 230 + gap
    for f in m["flows"]:
        ft = tt.get(f["id"], [])
        col = SEV[ft[0]["severity"]][1] if ft else "#333333"
        st = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor={col};"
              f"fontSize=10;labelBackgroundColor=#ffffff;" + ("dashed=1;" if f.get("assumed") else ""))
        cells.append(f'<mxCell id="{f["id"]}" value="{escape(flow_label(f, ft), {chr(34): "&quot;"})}" style="{st}" '
                     f'edge="1" parent="1" source="{f["from"]}" target="{f["to"]}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    ly = y0 + maxh + 30
    cell("legend", "Legend: rectangle = external entity | ellipse = process | cylinder = data store | "
         "red dashed box = trust boundary | dashed = ASSUMED | hexagon = threat (colour = severity) | "
         "⚠T# on arrow = threat on that data flow", "text;align=left;fontSize=11;html=1;whiteSpace=wrap;",
         "1", 20, ly, 900, 30)
    for i, (s, (fc, sc)) in enumerate(SEV.items()):
        cell("lg" + s, s, f"rounded=1;fillColor={fc};strokeColor={sc};fontColor={sc};fontStyle=1;html=1;",
             "1", 20 + i * 100, ly + 35, 90, 24)
    xml = ('<mxfile host="tm_generator"><diagram id="dfd" name="DFD"><mxGraphModel grid="1" gridSize="10">'
           '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>")
    open(path, "w", encoding="utf-8").write(xml)

def mermaid(m):
    q = lambda s: s.replace('"', "'").replace("<", "(").replace(">", ")")
    tt, L, C = by_target(m), ["flowchart LR"], []
    for b in m["boundaries"]:
        L.append(f'  subgraph {b["id"]}["{q(b["id"] + ": " + b["name"])}"]')
        for e in [e for e in m["elements"] if e["boundary"] == b["id"]]:
            n = q(e["id"] + ": " + e["name"] + (" (ASSUMED)" if e.get("assumed") else ""))
            L.append("    " + {"external": f'{e["id"]}["{n}"]', "process": f'{e["id"]}(("{n}"))',
                                "store": f'{e["id"]}[("{n}")]'}[e["type"]])
            for t in tt.get(e["id"], []):
                if RANK[t["severity"]] >= 3:
                    L.append(f'    {t["id"]}{{{{"{t["id"]} {t["severity"]}"}}}} -.- {e["id"]}')
                    C.append(f'  class {t["id"]} {t["severity"][:4].lower()}')
        L.append("  end")
        L.append(f'  style {b["id"]} stroke:#c0392b,stroke-dasharray:6 4')
    for f in m["flows"]:
        arrow = "-.->" if f.get("assumed") else "-->"
        L.append(f'  {f["from"]} {arrow}|"{q(flow_label(f, tt.get(f["id"], [])))}"| {f["to"]}')
    L += ["  classDef crit fill:#f8d7da,stroke:#b02a37,color:#58151c",
          "  classDef high fill:#fff3cd,stroke:#b8860b,color:#5c4400"] + C
    return "\n".join(L)

def register(m, path):
    cols = ["id", "severity", "likelihood", "impact", "stride", "frameworks", "target", "title",
            "description", "spec_ref", "control", "status"]
    rows = sorted(m["threats"], key=lambda t: (-RANK[t["severity"]], int(re.sub(r"\D", "", t["id"]) or 0)))
    try:
        import pandas as pd
        pd.DataFrame([{c: t.get(c, "Open" if c == "status" else "") for c in cols} for t in rows]).to_excel(path, index=False)
    except Exception:
        import csv
        path = path.replace(".xlsx", ".csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, cols, extrasaction="ignore"); w.writeheader()
            for t in rows: w.writerow({c: t.get(c, "Open" if c == "status" else "") for c in cols})
    return path

def run(m, name):
    validate(m)
    drawio(m, name + ".drawio")
    reg = register(m, name + "_register.xlsx")
    print("FILES:", name + ".drawio", reg)
    print("MERMAID_START\n" + mermaid(m) + "\nMERMAID_END")

if __name__ == "__main__":
    import sys
    MODEL = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "model.json"))   # Copilot: replace this line with  MODEL = { ...the JSON model... }
    run(MODEL, sys.argv[2] if len(sys.argv) > 2 else "threat_model")
