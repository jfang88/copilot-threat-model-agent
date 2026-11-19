"""Tests for tm_generator.py.  Run: python -m pytest tests  (or python tests/test_generator.py)"""
import copy, json, sys, tempfile, xml.dom.minidom
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))
import tm_generator as g  # noqa: E402

MODEL = json.loads((ROOT / "examples" / "example_model.json").read_text(encoding="utf-8"))
LIBRARY = (ROOT / "knowledge" / "src" / "TM-02_Threat_Library.md").read_text(encoding="utf-8")


def invalid(m):
    try:
        g.validate(m)
    except SystemExit as e:
        return str(e)
    return ""


def test_example_is_valid():
    assert invalid(MODEL) == ""


def test_severity_must_match_score():
    m = copy.deepcopy(MODEL)
    m["threats"][0]["severity"] = "Low"
    assert "severity should be Critical" in invalid(m)


def test_broken_reference_rejected():
    m = copy.deepcopy(MODEL)
    m["flows"][0]["to"] = "P99"
    assert "bad endpoint P99" in invalid(m)


def test_duplicate_id_rejected():
    m = copy.deepcopy(MODEL)
    m["threats"][1]["id"] = m["threats"][0]["id"]
    assert "duplicate id" in invalid(m)


def test_drawio_is_well_formed_and_complete():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.drawio"
        g.drawio(MODEL, str(p))
        doc = xml.dom.minidom.parse(str(p))
        ids = {c.getAttribute("id") for c in doc.getElementsByTagName("mxCell")}
        values = " ".join(c.getAttribute("value") for c in doc.getElementsByTagName("mxCell"))
    for o in MODEL["elements"] + MODEL["flows"] + MODEL["boundaries"]:
        assert o["id"] in ids
    for t in MODEL["threats"]:  # every threat visible as a badge or flow label
        assert t["id"] + "b" in ids or ("⚠" in values and t["id"] in values)


def test_every_threat_on_mermaid_or_flow_label():
    mer = g.mermaid(MODEL)
    for t in MODEL["threats"]:
        if t["target"].startswith("F") or t["severity"] in ("Critical", "High"):
            assert t["id"] in mer


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
