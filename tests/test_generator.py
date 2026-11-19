"""Tests for tm_generator.py v2.  Run: python -m pytest tests  (or python tests/test_generator.py)"""
import copy, json, sys, tempfile, xml.dom.minidom
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))
import tm_generator as g  # noqa: E402

MODEL = json.loads((ROOT / "examples" / "example_model.json").read_text(encoding="utf-8"))
SPEC = (ROOT / "examples" / "example_spec.md").read_text(encoding="utf-8")
LIBRARY = (ROOT / "knowledge" / "src" / "TM-02_Threat_Library.md").read_text(encoding="utf-8")


def errors(m):
    try:
        g.validate(m)
    except SystemExit as e:
        return str(e)
    return ""


def diagram(m, gid):
    return next(d for d in m["diagrams"] if d["id"] == gid)


def test_example_is_valid_without_warnings():
    assert g.validate(copy.deepcopy(MODEL)) == []


def test_severity_must_match_score():
    m = copy.deepcopy(MODEL)
    m["threats"][0]["severity"] = "Low"
    assert "severity should be Critical" in errors(m)


def test_threat_needs_document_reference():
    m = copy.deepcopy(MODEL)
    m["threats"][3]["refs"] = []
    assert "needs at least one document reference" in errors(m)


def test_unknown_document_rejected():
    m = copy.deepcopy(MODEL)
    m["threats"][3]["refs"][0]["doc"] = "DOC9"
    assert "DOC9" in errors(m)


def test_child_ids_must_be_prefixed_with_parent():
    m = copy.deepcopy(MODEL)
    diagram(m, "L1-P3")["elements"][1]["id"] = "X1"
    assert 'must be prefixed "P3."' in errors(m)


def test_parent_flow_must_exist_in_parent_diagram():
    m = copy.deepcopy(MODEL)
    diagram(m, "L1-P3")["flows"][0]["parent"] = "P5.F1"
    assert "parent flow P5.F1 not in the parent diagram" in errors(m)


def test_refines_must_point_up_a_level():
    m = copy.deepcopy(MODEL)
    t = next(t for t in m["threats"] if t["id"] == "T1")
    t["refines"] = "T14"
    assert "refines must point to a higher-level threat" in errors(m)


def test_missing_refinement_and_improvement_warn():
    m = copy.deepcopy(MODEL)
    for t in m["threats"]:
        if t.get("refines") == "T2": del t["refines"]
    m["recommendations"] = [r for r in m["recommendations"] if r["id"] != "R4"]
    w = "\n".join(g.validate(m))
    assert "T2: Critical threat on decomposed P3 not refined" in w
    assert "T23: High threat not addressed" in w


def test_drawio_has_a_page_per_diagram_with_drilldown_links():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.drawio"
        g.drawio(MODEL, str(p))
        doc = xml.dom.minidom.parse(str(p))
    pages = {x.getAttribute("id") for x in doc.getElementsByTagName("diagram")}
    assert pages == {x["id"] for x in MODEL["diagrams"]}
    links = {u.getAttribute("id"): u.getAttribute("link") for u in doc.getElementsByTagName("UserObject")}
    assert links["L0|P3"] == "data:page/id,L1-P3"          # decomposed process opens its child
    assert links["L1-P3|P3.3"] == "data:page/id,L2-P3.3"
    assert links["L1-P3|E3"] == "data:page/id,L0"           # context element links back
    assert links["L1-P3|up"] == "data:page/id,L0"


def test_every_threat_is_visible_on_its_page():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.drawio"
        g.drawio(MODEL, str(p))
        doc = xml.dom.minidom.parse(str(p))
    ids = {u.getAttribute("id") for u in doc.getElementsByTagName("UserObject")}
    labels = " ".join(u.getAttribute("label") for u in doc.getElementsByTagName("UserObject"))
    for t in MODEL["threats"]:
        assert f'{t["diagram"]}|{t["id"]}' in ids or ("⚠" in labels and t["id"] in labels), t["id"]


def test_mermaid_has_one_diagram_per_level_and_high_threats():
    ix = g.index(MODEL)
    for d in MODEL["diagrams"]:
        mer = g.mermaid(MODEL, d["id"], ix)
        assert mer.startswith("flowchart LR")
        for t in MODEL["threats"]:
            if t["diagram"] == d["id"] and (t["severity"] in ("Critical", "High") or t["target"] in ix["fl"]):
                assert t["id"] in mer, (d["id"], t["id"])


def test_workbook_groups_problem_solution_reference_and_cross_refs():
    tb = g.tables(MODEL)
    cols, rows = tb["Threats"]
    i = cols.index("Problem")
    assert cols[i:i + 6] == ["Problem", "Problem detail", "Solution (control)", "Arch. improvement",
                             "Document reference", "Evidence (quote)"]
    row = {r[0]: dict(zip(cols, r)) for r in rows}
    assert row["T2"]["Refined by (child threats)"] == "T14, T15"
    assert row["T14"]["Refines (parent threat)"] == "T2"
    assert row["T14"]["Arch. improvement"] == "R2"
    assert row["T9"]["Open questions"] == "Q1"
    assert {"Threats", "Arch improvements", "Open questions", "Elements & flows", "Diagrams", "Documents"} <= set(tb)


def test_xlsx_writes():
    with tempfile.TemporaryDirectory() as d:
        out = g.register(MODEL, str(Path(d) / "r.xlsx"))
        assert Path(out.split(",")[0]).exists()


def test_quotes_are_verbatim_and_short():
    items = MODEL["threats"] + MODEL["recommendations"] + MODEL["questions"]
    for i in items:
        for r in i.get("refs", []):
            if r.get("quote"):
                assert r["quote"] in SPEC, (i["id"], r["quote"])
                assert len(r["quote"].split()) <= 15, i["id"]


def test_framework_ids_exist_in_library():
    for t in MODEL["threats"]:
        for f in (x.strip() for x in t["frameworks"].split(";")):
            if f.startswith("CWE-"):
                continue
            if f.startswith("LINDDUN"):
                assert f.split()[1] in {"L", "I", "NR", "DT", "DD", "U", "NC"}
            else:
                assert f in LIBRARY, f


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
