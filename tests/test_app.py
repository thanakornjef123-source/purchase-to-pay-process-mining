"""Every page of the Streamlit app renders without an exception and the app writes no files."""
import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["overview", "data_method", "discovery", "conformance", "performance",
         "case_explorer", "real_data", "recommendations", "report"]


def _snapshot(root):
    return {p: p.stat().st_mtime for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
            and ".pytest_cache" not in p.parts}


@pytest.fixture(scope="module")
def before(root):
    return _snapshot(root)


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(root, page, before):
    at = AppTest.from_file(str(root / "app.py"), default_timeout=60)
    at.run()
    if page != "overview":
        at.switch_page(f"app_pages/{page}.py")
        at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.title, "page has no title"


def test_case_explorer_filters(root):
    at = AppTest.from_file(str(root / "app.py"), default_timeout=60)
    at.run()
    at.switch_page("app_pages/case_explorer.py")
    at.run()
    rule_box = next(s for s in at.selectbox if s.label == "กฎที่ละเมิด")
    rule_box.select(next(o for o in rule_box.options if o.startswith("D1"))).run()
    assert not at.exception
    assert any("กฎที่ละเมิด" in e.value for e in at.error), "a D1 case should list its broken rule"


def test_app_writes_no_files(root, before):
    after = _snapshot(root)
    assert set(after) == set(before)
    assert all(after[p] == before[p] for p in before)
