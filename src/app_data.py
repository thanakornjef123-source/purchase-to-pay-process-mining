"""Read-only data access for the Streamlit app.

The app never writes files: it reads the JSON results and CSV tables that the
notebooks produced and that are committed with the repository. All paths are
relative to the repository root, so the app runs the same on any machine.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
REPORT_PDF = ROOT / "report" / "p2p_process_mining_report.pdf"

RESULT_FILES = {
    "explore": "01_explore.json",
    "discovery": "02_discovery.json",
    "conformance": "03_conformance.json",
    "performance": "04_performance.json",
    "recommendations": "05_recommendations.json",
}

RULE_LABELS_TH = {
    "A1": "ขอใบเสนอราคาโดยไม่มีใบขอซื้อในระบบ",
    "A2": "ส่งต่อการอนุมัติ แต่ไม่มีบันทึกการอนุมัติ",
    "A3": "ขอใบเสนอราคาก่อนอนุมัติใบขอซื้อ",
    "B1": "อนุมัติ PO ก่อนสร้าง PO",
    "B2": "รับของก่อนอนุมัติ PO",
    "B3": "PO ไม่เคยได้รับอนุมัติ",
    "C1": "รับใบแจ้งหนี้ก่อนรับของ",
    "C2": "จับคู่เอกสารก่อนรับใบแจ้งหนี้",
    "C3": "จ่ายเงินก่อนจับคู่เอกสาร",
    "C4": "จ่ายเงินก่อนรับของครั้งแรก",
    "C5": "จ่ายเงินให้ PO ก่อนรับของครบ",
    "D1": "สั่งจ่ายเงินซ้ำกับ payment เดิม",
}

PATH_LABELS_TH = {
    "PR approved": "อนุมัติใบขอซื้อตามปกติ",
    "PR delegated, no approval": "ส่งต่อการอนุมัติ ไม่มีบันทึกการอนุมัติ",
    "no PR created": "ไม่มีใบขอซื้อในระบบ",
}

PAYMENT_LABELS = {
    "A: Bank TransferB: Check": "A/B: Bank transfer / Check",
    "C: Bank Collection": "C: Bank collection",
    "D:Direct Debit": "D: Direct debit",
}

STAGE_LABELS_TH = {
    "1 PR created -> PR approved": "สร้างใบขอซื้อ → อนุมัติใบขอซื้อ",
    "1b PR created -> approval delegated": "สร้างใบขอซื้อ → ส่งต่อการอนุมัติ",
    "2 PR approved -> RFQ": "อนุมัติใบขอซื้อ → ขอใบเสนอราคา",
    "3 RFQ -> first PO created": "ขอใบเสนอราคา → สร้าง PO ใบแรก",
    "4 PO created -> PO approved": "สร้าง PO → อนุมัติ PO",
    "5 PO approved -> first goods receipt": "อนุมัติ PO → รับของครั้งแรก",
    "6 first goods receipt -> invoice": "รับของครั้งแรก → รับใบแจ้งหนี้",
    "7 invoice -> two-way match": "รับใบแจ้งหนี้ → จับคู่เอกสาร",
    "8 two-way match -> first payment": "จับคู่เอกสาร → จ่ายเงินครั้งแรก",
}


def load_results() -> dict[str, dict]:
    return {key: json.loads((RESULTS / name).read_text(encoding="utf-8"))
            for key, name in RESULT_FILES.items()}


def load_case_log() -> pd.DataFrame:
    df = pd.read_csv(DATA / "p2p_cases_by_pr.csv", parse_dates=["time:timestamp"])
    df["event_no"] = df["ocel_event_id"].str.split(":").str[1].astype(int)
    df = df.sort_values(["case:concept:name", "time:timestamp", "event_no"]).reset_index(drop=True)
    return df.rename(columns={"case:concept:name": "case", "concept:name": "activity",
                              "time:timestamp": "timestamp", "org:resource": "department"})


def load_case_table() -> pd.DataFrame:
    """One row per case: attributes from 04_performance and rule flags from 03_conformance."""
    attrs = pd.read_csv(DATA / "case_attributes.csv", index_col=0, dtype={"purchasing_group": str})
    rules = pd.read_csv(DATA / "case_rules.csv", index_col="case")
    table = attrs.join(rules, how="inner")
    table.index.name = "case"
    table["path_th"] = table["path"].map(PATH_LABELS_TH)
    table["payment_method"] = table["payment_method"].map(PAYMENT_LABELS).fillna(table["payment_method"])
    return table


def case_number(case_id: str) -> int:
    """'purchase_requisition:12:pr_trigger_12' -> 12 (for readable labels and sorting)."""
    return int(case_id.split(":")[1])


def figure(name: str) -> Path:
    return FIGURES / name
