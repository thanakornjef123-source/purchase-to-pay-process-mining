"""BPI Challenge 2019 results match the published log size and, when the raw file is present, can be recomputed."""
import pandas as pd
import pytest

PUBLISHED = {"cases": 251_734, "events": 1_595_923, "activities": 42}   # from the dataset description


def test_counts_match_published_description(results):
    b = results["bpi2019"]
    for k, v in PUBLISHED.items():
        assert b[k] == v, k


def test_category_counts_add_up(results):
    b = results["bpi2019"]
    assert sum(b["item_category_cases"].values()) == b["cases"]


@pytest.fixture(scope="module")
def bpi(root):
    events = root / "data" / "bpi2019_events.parquet"
    if not events.exists():
        pytest.skip("BPI 2019 cache not present (download the XES and run notebook 06)")
    ev = pd.read_parquet(events)
    cs = pd.read_parquet(root / "data" / "bpi2019_cases.parquet")
    return ev, cs


def test_paid_before_goods_receipt_recomputed(bpi, results):
    ev, cs = bpi
    first = ev.groupby(["case", "activity"]).timestamp.min().unstack()
    cat = cs.set_index("case")["item_category"].reindex(first.index)
    gr, clr = first["Record Goods Receipt"], first["Clear Invoice"]
    three_way = cat.str.startswith("3-way")
    paid_early = ((clr < gr) | (clr.notna() & gr.isna())) & three_way
    assert int(paid_early.sum()) == results["bpi2019"]["rules"][1]["cases"]
