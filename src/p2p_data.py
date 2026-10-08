"""Shared loaders for the P2P OCEL 2.0 SQLite file.

Reads the raw SQLite tables directly with pandas so every step is visible,
and uses PM4Py only where process-mining algorithms are needed.
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ocel2-p2p.sqlite"

# Folders the notebooks write into. Created on import so a fresh clone runs as-is.
for _folder in ("data", "results", "figures"):
    (ROOT / _folder).mkdir(exist_ok=True)


def connect(path=DATA):
    """Open the OCEL file read-only; fail with a clear message if it is missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} not found in data/. Download it from https://zenodo.org/records/8412920")
    return sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)


def load_events(con):
    """One row per event: id, activity, timestamp, resource, lifecycle."""
    ev = pd.read_sql("select ocel_id, ocel_type as activity from event", con)
    maps = pd.read_sql("select * from event_map_type", con)
    parts = [pd.read_sql(f'select * from "event_{t}"', con) for t in maps.ocel_type_map]
    attrs = pd.concat(parts, ignore_index=True)
    out = ev.merge(attrs, on="ocel_id", how="left", validate="one_to_one")
    out["ocel_time"] = pd.to_datetime(out["ocel_time"], utc=True)
    return out


def load_objects(con):
    obj = pd.read_sql("select ocel_id, ocel_type from object", con)
    return obj


def load_event_object(con):
    eo = pd.read_sql("select * from event_object", con)
    types = pd.read_sql("select ocel_id, ocel_type from object", con)
    eo["object_type"] = eo["ocel_object_id"].map(types.set_index("ocel_id").ocel_type)
    return eo


def load_object_object(con):
    oo = pd.read_sql("select * from object_object", con)
    # object IDs can contain extra colons (e.g. purchase_requisition:622:pr_trigger_622),
    # so take the type from the object table rather than parsing the ID
    types = pd.read_sql("select ocel_id, ocel_type from object", con).set_index("ocel_id").ocel_type
    oo["source_type"] = oo["ocel_source_id"].map(types)
    oo["target_type"] = oo["ocel_target_id"].map(types)
    return oo


def load_object_attributes(con, type_map):
    """Attribute table for one object type (initial values + change rows)."""
    df = pd.read_sql(f'select * from "object_{type_map}"', con)
    df["ocel_time"] = pd.to_datetime(df["ocel_time"], utc=True)
    return df


CASE_LOG = DATA.parent / "p2p_cases_by_pr.csv"   # created by notebooks/01_explore.ipynb


def load_case_log(path=CASE_LOG):
    """Flattened log: 1 case = 1 purchase requisition and every document that follows it.

    Sorted by case, timestamp, then numeric event id (timestamps are only minute-precise,
    so the event id breaks ties).
    """
    df = pd.read_csv(path, parse_dates=["time:timestamp"])
    df["event_no"] = df["ocel_event_id"].str.split(":").str[1].astype(int)
    df = df.sort_values(["case:concept:name", "time:timestamp", "event_no"]).reset_index(drop=True)
    return df


def event_object_table(con):
    """event_object joined with event attributes: one row per (event, object)."""
    ev = load_events(con)
    eo = load_event_object(con)
    return eo.merge(ev, left_on="ocel_event_id", right_on="ocel_id", how="left")


def short(activity):
    """Short activity labels for charts."""
    return (activity.replace("Purchase Requisition", "PR").replace("Purchase Order", "PO")
            .replace("Request for Quotation", "RFQ").replace("Goods Receipt", "GR")
            .replace("Invoice Receipt", "Invoice").replace("Perform Two-Way Match", "Two-Way Match")
            .replace("Delegate PR Approval", "Delegate PR Approval"))
