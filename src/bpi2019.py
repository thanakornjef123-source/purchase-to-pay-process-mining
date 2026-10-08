"""Streaming reader for the BPI Challenge 2019 XES log.

The XES file is ~700 MB, so it is read with lxml.iterparse (constant memory per trace)
instead of pm4py.read_xes, and cached as Parquet next to the source file.
Accepts the plain .xes or a gzip-compressed .xes.gz.
"""
from __future__ import annotations

import gzip
from pathlib import Path

import pandas as pd
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
XES_CANDIDATES = [DATA / "BPI_Challenge_2019.xes", DATA / "BPI_Challenge_2019.xes.gz"]
EVENTS_CACHE = DATA / "bpi2019_events.parquet"
CASES_CACHE = DATA / "bpi2019_cases.parquet"
SOURCE_URL = "https://figshare.com/articles/dataset/BPI_Challenge_2019/12715853"
EXPECTED_MD5 = "4eb909242351193a61e1c15b9c3cc814"   # of the uncompressed .xes (figshare / 4TU)

CASE_KEYS = {
    "concept:name": "case", "Purchasing Document": "document", "Item": "item",
    "Item Type": "item_type", "GR-Based Inv. Verif.": "gr_based_iv", "Goods Receipt": "goods_receipt",
    "Source": "source", "Purch. Doc. Category name": "doc_category", "Company": "company",
    "Spend classification text": "spend_class", "Spend area text": "spend_area",
    "Sub spend area text": "sub_spend_area", "Vendor": "vendor", "Name": "vendor_name",
    "Document Type": "document_type", "Item Category": "item_category",
}
EVENT_KEYS = {"concept:name": "activity", "time:timestamp": "timestamp", "org:resource": "resource",
              "User": "user", "Cumulative net worth (EUR)": "net_worth"}


def find_xes() -> Path:
    for p in XES_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(f"BPI_Challenge_2019.xes not found in data/. Download it from {SOURCE_URL}")


def _value(el):
    v = el.get("value")
    tag = etree.QName(el).localname
    if tag == "boolean":
        return v == "true"
    if tag == "float":
        return float(v)
    return v


def parse_xes(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    cases, events = [], []
    with opener(path, "rb") as fh:
        for _, trace in etree.iterparse(fh, events=("end",), tag="trace"):
            case = {}
            for child in trace:
                tag = etree.QName(child).localname
                if tag != "event":
                    key = CASE_KEYS.get(child.get("key"))
                    if key:
                        case[key] = _value(child)
            cid = case.get("case")
            for i, ev in enumerate(trace.iterfind("event")):
                row = {"case": cid, "position": i}
                for child in ev:
                    key = EVENT_KEYS.get(child.get("key"))
                    if key:
                        row[key] = _value(child)
                events.append(row)
            cases.append(case)
            trace.clear()
            while trace.getprevious() is not None:
                del trace.getparent()[0]
    ev = pd.DataFrame(events)
    ev["timestamp"] = pd.to_datetime(ev["timestamp"], utc=True, format="ISO8601")
    return ev, pd.DataFrame(cases)


def load(refresh: bool = False):
    """Events and case attributes, parsed once and cached as Parquet in data/."""
    if not refresh and EVENTS_CACHE.exists() and CASES_CACHE.exists():
        return pd.read_parquet(EVENTS_CACHE), pd.read_parquet(CASES_CACHE)
    DATA.mkdir(exist_ok=True)
    ev, cases = parse_xes(find_xes())
    ev.to_parquet(EVENTS_CACHE, index=False)
    cases.to_parquet(CASES_CACHE, index=False)
    return ev, cases
