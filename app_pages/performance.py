import pandas as pd
import streamlit as st

from app_pages.common import (
          ad,
          case_table,
          hbar,
          notice,
          num,
          pct,
          results,
          table,
)

R = results()
P = R["performance"]
cd = P["case_duration_days"]

st.title("ระยะเวลาและคอขวด")
notice()

c1, c2, c3, c4 = st.columns(4)
c1.metric("มัธยฐานต่อเคส", f"{cd['median']:.1f} วัน")
c2.metric("ค่าเฉลี่ยต่อเคส", f"{cd['mean']:.1f} วัน")
c3.metric("เปอร์เซ็นไทล์ที่ 90", f"{cd['p90']:.1f} วัน")
c4.metric("เวลารอในขั้นภายในองค์กร", pct(P["internal_share_of_stage_medians_pct"]),
          help="สัดส่วนของผลรวมค่ามัธยฐานเวลารอรายขั้น ที่เป็นขั้นอนุมัติ ส่งต่องาน และการเงิน")

st.header("เวลารอระหว่างขั้น")
st.markdown("วัดบน**เอกสารใบเดียวกัน**เท่านั้น เพื่อไม่ให้ปนกับเวลาระหว่างเอกสารคนละใบในเคสเดียวกัน")
stages = pd.DataFrame([
    {"ขั้น": ad.STAGE_LABELS_TH[k], "มัธยฐาน (วัน)": v["median"], "ค่าเฉลี่ย (วัน)": v["mean"],
     "P90 (วัน)": v["p90"], "จำนวนเอกสาร": int(v["n"])}
    for k, v in P["stage_wait_days"].items() if not k.startswith("1b")
])
metric = st.segmented_control("แสดงค่า", ["มัธยฐาน (วัน)", "P90 (วัน)"], default="มัธยฐาน (วัน)")
st.altair_chart(hbar(stages, "ขั้น", metric or "มัธยฐาน (วัน)", "วัน", label_fmt=".1f"), width="stretch")
table(stages)

longest = ad.STAGE_LABELS_TH[P["longest_stage_by_median"]]
st.info(
    f"**ไม่มีคอขวดจุดเดียว แต่มีการรอหลายทอด** ขั้นที่รอนานที่สุดคือ *{longest}* "
    f"(มัธยฐาน {P['longest_stage_median_days']:.2f} วัน) ซึ่งเป็นช่วงรอผู้ขายส่งของ ขณะที่ขั้นอื่นหลายขั้นรอใกล้เคียงกัน "
    f"ขั้นที่องค์กรควบคุมได้เองคิดเป็น {pct(P['internal_share_of_stage_medians_pct'])} ของผลรวมค่ามัธยฐานรายขั้น",
    icon=":material/insights:",
)

st.header("ระยะเวลาต่อเคสแยกตามกลุ่ม")
t = case_table()
dims = {
    "เส้นทางของใบขอซื้อ": "path_th",
    "กลุ่มจัดซื้อ (purchasing group)": "purchasing_group",
    "วิธีการจ่ายเงิน": "payment_method",
    "จำนวน PO ในเคส": "POs",
    "จำนวนใบรับของในเคส": "GRs",
    "มีการสั่งจ่ายซ้ำ": "repeated_payment",
}
dim = st.selectbox("แยกตาม", list(dims), index=0)
col = dims[dim]
g = (t.assign(group=t[col].astype(str).replace({"True": "ใช่", "False": "ไม่ใช่"}))
       .groupby("group")["duration"].agg(เคส="size", มัธยฐาน="median", P90=lambda s: s.quantile(.9))
       .reset_index().rename(columns={"group": dim}))
g["มัธยฐาน"] = g["มัธยฐาน"].round(1)
g["P90"] = g["P90"].round(1)
st.altair_chart(hbar(g, dim, "มัธยฐาน", "มัธยฐานระยะเวลาต่อเคส (วัน)", label_fmt=".1f"), width="stretch")
table(g)
st.markdown(
    f"""
- เคสที่ไม่มีใบขอซื้อใช้เวลาน้อยกว่าเคสปกติ ซึ่งส่วนต่างใกล้เคียงกับเวลาของขั้นอนุมัติและส่งต่อใบขอซื้อ *(ข้อสันนิษฐาน: อาจเป็นแรงจูงใจให้ข้ามขั้นตอน)*
- เคสที่มีการสั่งจ่ายซ้ำใช้เวลานานกว่า ({P['duration_median_repeated_payment']:.1f} เทียบกับ {P['duration_median_single_payment']:.1f} วัน)
- จำนวนเอกสารมีความสัมพันธ์กับระยะเวลาเล็กน้อย (Spearman: ใบรับของ {P['corr_duration_vs_GRs']}, PO {P['corr_duration_vs_POs']})
- กลุ่มจัดซื้อ วิธีการจ่ายเงิน และผู้ขาย มีความแตกต่างไม่มาก (มัธยฐานของผู้ขายที่มีตั้งแต่ 10 เคสขึ้นไปอยู่ระหว่าง
  {P['vendor_duration_median_range'][0]:.1f}–{P['vendor_duration_median_range'][1]:.1f} วัน) ซึ่งอาจเป็นลักษณะของข้อมูลจำลอง
"""
)

st.header("การทำงานซ้ำ (rework)")
st.markdown("กิจกรรมที่เกิดซ้ำในเคสส่วนใหญ่**ไม่ใช่การทำงานซ้ำ** แต่เกิดจากการที่เคสมีเอกสารหลายใบ "
            "จึงแยกกรณีที่กิจกรรมเกิดซ้ำบน**เอกสารใบเดิม**ออกมาพิจารณา")
rw = pd.DataFrame([{
    "กิจกรรม": r["activity"], "เคสที่มีกิจกรรมซ้ำ": r["cases_with_repeat"],
    "ซ้ำเพราะมีหลายเอกสาร": r["cases_repeat_only_from_multiple_documents"],
    "ซ้ำบนเอกสารเดิม": r["cases_with_repeat_on_same_document"],
    "ถือเป็นการทำงานซ้ำ": {"Execute Payment": "ใช่",
                           "Create Goods Receipt": "ไม่ใช่ (แต่ละครั้งอ้าง PO คนละใบ)"}.get(r["activity"], "ไม่ใช่"),
} for r in P["rework"] if r["cases_with_repeat"]])
table(rw)
gr = next(r for r in P["rework"] if r["activity"] == "Create Goods Receipt")
pay = next(r for r in P["rework"] if r["activity"] == "Execute Payment")
st.markdown(
    f"""
- การรับของซ้ำบนใบรับของเดียวกัน ({num(gr['documents_with_repeat'])} ใบ) ทุกครั้งอ้างอิง PO คนละใบ
  ({pct(P['gr_postings_each_reference_different_po_pct'])}) จึงเป็นใบรับของที่รวมสินค้าจากหลาย PO **ไม่ใช่การทำงานซ้ำ**
- การทำงานซ้ำที่เกิดจริงคือการสั่งจ่ายเงินซ้ำบน payment เดิม ({num(pay['documents_with_repeat'])} รายการ เกินมา {num(pay['extra_events_on_same_document'])} ครั้ง)
"""
)

st.header("ภาระงานรายแผนก")
wl = pd.DataFrame([{"หน่วยงาน": dep, "Events": sum(acts.values())}
                   for dep, acts in P["events_by_resource_activity"].items()]).sort_values("Events", ascending=False)
st.altair_chart(hbar(wl, "หน่วยงาน", "Events", "จำนวน events ตลอดช่วงข้อมูล", label_fmt=",.0f"), width="stretch")
st.caption(f"ฝ่ายการเงินรับผิดชอบการรับใบแจ้งหนี้ การจับคู่เอกสาร และการจ่ายเงิน "
           f"(มัธยฐาน {P['finance_events_per_month_median']:.0f} events ต่อเดือน)")
