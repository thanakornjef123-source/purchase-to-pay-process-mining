"""The committed data files are complete and the headline numbers can be recomputed with plain SQL."""
import hashlib
import sqlite3

import pandas as pd
import pytest

EXPECTED_MD5 = "1a4238260019939239488b0b4befb515"   # published on Zenodo record 8412920


@pytest.fixture(scope="module")
def con(root):
    path = root / "data" / "ocel2-p2p.sqlite"
    if not path.exists():
        pytest.skip("raw OCEL file not present")
    c = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    yield c
    c.close()


def test_raw_file_checksum(root):
    path = root / "data" / "ocel2-p2p.sqlite"
    if not path.exists():
        pytest.skip("raw OCEL file not present")
    assert hashlib.md5(path.read_bytes()).hexdigest() == EXPECTED_MD5


def test_event_count(con, results):
    assert con.execute("select count(*) from event").fetchone()[0] == results["explore"]["n_events"]


def _rule(results, code):
    return next(r for r in results["conformance"]["rules"] if r["rule"].startswith(code))


def test_rfq_without_requisition(con, results):
    n = con.execute("""
        select count(*) from object o where o.ocel_type = 'purchase_requisition' and not exists (
          select 1 from event_object eo join event e on e.ocel_id = eo.ocel_event_id
          where eo.ocel_object_id = o.ocel_id and e.ocel_type = 'Create Purchase Requisition')""").fetchone()[0]
    assert n == _rule(results, "A1")["documents"]


def test_delegated_without_approval(con, results):
    n = con.execute("""
        select count(distinct eo.ocel_object_id) from event_object eo join event e on e.ocel_id = eo.ocel_event_id
        where e.ocel_type = 'Delegate Purchase Requisition Approval'
          and eo.ocel_object_id like 'purchase_requisition:%'
          and eo.ocel_object_id not in (
            select eo2.ocel_object_id from event_object eo2 join event e2 on e2.ocel_id = eo2.ocel_event_id
            where e2.ocel_type = 'Approve Purchase Requisition')""").fetchone()[0]
    assert n == _rule(results, "A2")["documents"]


def test_repeated_payments(con, results):
    n, extra = con.execute("""
        select count(*), sum(k - 1) from (
          select eo.ocel_object_id, count(*) k from event_object eo join event e on e.ocel_id = eo.ocel_event_id
          where e.ocel_type = 'Execute Payment' and eo.ocel_object_id like 'payment:%'
          group by 1 having k > 1)""").fetchone()
    assert n == results["conformance"]["D1_payments"]
    assert extra == results["conformance"]["D1_extra_executions"]


def test_paid_before_fully_received(con, results):
    n = con.execute("""
        with gr as (select eo.ocel_object_id po, max(t.ocel_time) last_gr from event_object eo
                    join event_CreateGoodsReceipt t on t.ocel_id = eo.ocel_event_id
                    where eo.ocel_object_id like 'purchase_order:%' group by 1),
             pay as (select eo.ocel_object_id po, min(t.ocel_time) first_pay from event_object eo
                     join event_ExecutePayment t on t.ocel_id = eo.ocel_event_id
                     where eo.ocel_object_id like 'purchase_order:%' group by 1)
        select count(*) from gr join pay using (po) where last_gr > first_pay""").fetchone()[0]
    assert n == _rule(results, "C5")["documents"]


def test_derived_tables_cover_every_case(root, results):
    n = results["explore"]["case_count"]
    log = pd.read_csv(root / "data" / "p2p_cases_by_pr.csv")
    attrs = pd.read_csv(root / "data" / "case_attributes.csv", index_col=0)
    rules = pd.read_csv(root / "data" / "case_rules.csv", index_col="case")
    assert log["case:concept:name"].nunique() == n
    assert len(log) == results["explore"]["n_events"]
    assert len(attrs) == len(rules) == n
    assert set(attrs.index) == set(rules.index) == set(log["case:concept:name"])


def test_compliance_share_matches_case_table(root, results):
    rules = pd.read_csv(root / "data" / "case_rules.csv", index_col="case")
    compliant = int((rules["rules_broken"] == 0).sum())
    assert compliant == results["conformance"]["cases_fully_compliant"]
    assert compliant == int((rules["alignment_fitness"] == 1).sum())
