import pandas as pd
import streamlit as st

from app_pages.common import (
    ad,
    hbar,
    image,
    notice,
    num,
    pct,
    results,
    rules_by_code,
    table,
)

R = results()
C = R["conformance"]
N = C["cases"]
rule = rules_by_code()

st.title("ความสอดคล้องกับกระบวนการที่ควรเป็น")
notice()

st.markdown(
    """
ตรวจสอบ 2 ระดับ เนื่องจากเคสหนึ่งมีเอกสารหลายใบ
1. **ระดับเคส:** เปรียบเทียบกับโมเดลอ้างอิงด้วย token-based replay และ alignments
2. **ระดับเอกสาร:** ตรวจกฎธุรกิจทีละเอกสาร เช่น PO ต้องได้รับอนุมัติก่อนรับของ และจ่ายเงินครั้งเดียวต่อใบแจ้งหนี้
"""
)

c1, c2, c3 = st.columns(3)
c1.metric("เคสที่ตรงกับโมเดลอ้างอิง", pct(C["alignment_perfect_pct"]))
c2.metric("เคสที่ละเมิดกฎอย่างน้อย 1 ข้อ", pct(C["cases_with_any_rule_violation_pct"]))
c3.metric("Alignment fitness เฉลี่ย", f"{C['alignment_mean_fitness']:.3f}")
st.caption(f"ผลการตรวจทั้งสองระดับสอดคล้องกันทุกเคส: เคสที่ alignment สมบูรณ์คือเคสที่ไม่ละเมิดกฎข้อใด "
           f"({num(C['alignment_vs_rules'].get('(True, True)', 0))} เคส)")

st.header("โมเดลอ้างอิง")
st.markdown(
    """
สร้างใบขอซื้อ → อนุมัติใบขอซื้อ → ขอใบเสนอราคา → สร้างและอนุมัติ PO (หลายใบได้)
→ รับของ / รับใบแจ้งหนี้ / จับคู่เอกสาร (หลายรอบได้) → **จ่ายเงินครั้งเดียวเป็นขั้นสุดท้าย**
"""
)
with st.expander("ดูโมเดลอ้างอิงในรูป Petri net"):
    image("03_reference_petri.png", "โมเดลอ้างอิง (Petri net)")

st.header("กฎที่ถูกละเมิด")
rows = [r for r in C["rules"] if r["kind"] == "rule"]
violated = pd.DataFrame([{"กฎ": f"{r['rule'][:2]} · {ad.RULE_LABELS_TH[r['rule'][:2]]}", "เคส (%)": r["cases_pct"]}
                         for r in rows if r["cases"] > 0]).sort_values("เคส (%)", ascending=False)
st.altair_chart(hbar(violated, "กฎ", "เคส (%)", "% ของเคส"), width="stretch")

rule_table = pd.DataFrame([{
    "รหัส": r["rule"][:2], "กฎ": ad.RULE_LABELS_TH[r["rule"][:2]], "เอกสาร": r["documents"],
    "เคส": r["cases"], "% ของเคส": r["cases_pct"], "ตัวอย่างเอกสาร": r["example_document"] or "–",
} for r in rows])
table(rule_table)
st.markdown(
    "กฎที่**ไม่พบการละเมิด**ก็เป็นข้อค้นพบเช่นกัน: ไม่มี PO ที่อนุมัติก่อนสร้าง ไม่มีการรับของก่อนอนุมัติ PO "
    "ไม่มีใบแจ้งหนี้ก่อนรับของ และ**ไม่มีการจ่ายเงินก่อนรับของครั้งแรก** แต่พบการจ่ายเงินก่อนรับของครบ (C5)"
)

st.header("รายละเอียดแต่ละประเด็น")
with st.container(border=True):
    st.markdown(f"**A1 · ขอใบเสนอราคาโดยไม่มีใบขอซื้อในระบบ ({num(rule['A1']['cases'])} เคส)**")
    st.markdown(
        f"เคสเริ่มที่ `Create Request for Quotation` โดยไม่มีการสร้างหรืออนุมัติใบขอซื้อ "
        f"แต่สถานะของใบขอซื้อทั้ง {num(C['pr_release_indicator_by_group']['Released']['no PR created'])} ใบยังเป็น `Released`  \n"
        "*ข้อสันนิษฐาน:* ใบขอซื้อถูกปลดล็อกโดยไม่ผ่านขั้นตอนอนุมัติ หรือเป็นการจัดซื้อนอกระบบ (maverick buying)"
    )
with st.container(border=True):
    st.markdown(f"**A2 · ส่งต่อการอนุมัติ แต่ไม่มีบันทึกการอนุมัติ ({num(rule['A2']['cases'])} เคส)**")
    st.markdown(
        "ใบขอซื้อถูกส่งต่อให้ผู้อื่นอนุมัติ แล้วดำเนินการขั้นต่อไปโดยไม่มีบันทึกการอนุมัติจากผู้รับมอบ  \n"
        "*ข้อสันนิษฐาน:* ระบบไม่บันทึกการอนุมัติของผู้รับมอบ หรือการส่งต่อถูกใช้เพื่อข้ามขั้นตอนอนุมัติ"
    )
with st.container(border=True):
    st.markdown(f"**D1 · สั่งจ่ายเงินซ้ำ ({num(C['D1_payments'])} payment)**")
    st.markdown(
        f"payment เดิมถูกสั่งจ่ายมากกว่าหนึ่งครั้ง รวม {num(C['D1_extra_executions'])} ครั้งที่เกินมา "
        f"ห่างกันมัธยฐาน {C['D1_days_between_executions']['50%']} วัน ทุกครั้งอ้างอิงใบรับของชุดเดิม "
        f"และยอดของ payment เท่ากับยอดใบแจ้งหนี้ทุกใบ ({pct(C['payment_amount_equals_invoice_pct'])})  \n"
        f"หากทุกครั้งเป็นการจ่ายเต็มจำนวน มูลค่าที่จ่ายเกินจะมี**เพดานบน** {pct(C['D1_exposure_pct_of_invoiced'])} ของยอดใบแจ้งหนี้รวม "
        "แต่ข้อมูลไม่มียอดเงินของการจ่ายแต่ละครั้ง จึงยืนยันไม่ได้ว่าเป็นการจ่ายเกินหรือการจ่ายเป็นงวด"
    )
with st.container(border=True):
    st.markdown(f"**C5 · จ่ายเงินให้ PO ก่อนรับของครบ ({num(rule['C5']['documents'])} PO)**")
    st.markdown(
        f"มีการรับของ {num(C['C5_postings_after_payment'])} ครั้งหลังจากที่ PO นั้นได้รับการจ่ายเงินแล้ว "
        f"(มัธยฐาน {C['C5_days_after_payment']['50%']} วันหลังจ่าย) ขณะที่ระบบบันทึกการจับคู่เป็น two-way match ทั้งหมด "
        f"({num(C['two_way_match_events'])} ครั้ง) ไม่มี three-way match  \n"
        "*ข้อสันนิษฐาน:* การจับคู่เปรียบเทียบเฉพาะ PO กับใบแจ้งหนี้ ไม่ได้เทียบกับจำนวนที่รับจริง"
    )

st.header("ผลจาก alignments")
moves = pd.DataFrame([{
    "ประเภท": "ขั้นที่ข้ามไป (model move)" if m["type"].startswith("skipped") else "ขั้นที่เกิน/ผิดตำแหน่ง (log move)",
    "กิจกรรม": m["activity"], "จำนวนครั้ง": m["moves"], "เคส": m["cases"], "% ของเคส": m["cases_pct"],
} for m in C["alignment_moves"]])
table(moves)
st.caption("model move ของ Execute Payment บางเคสเกิดจากวิธีจับคู่ของ alignment เมื่อมีการรับของหลังจ่ายเงิน "
           "ไม่ได้หมายความว่าไม่มีการจ่ายเงิน (ทุกเคสมี Execute Payment)")
