import pandas as pd
import streamlit as st

from app_pages.common import hbar, image, num, results, table

R = results()
B = R["bpi2019"]
P = R["performance"]

st.title("ต่อยอดด้วยข้อมูลจริง: BPI Challenge 2019")
st.markdown(
    '<div class="notice"><b>ข้อมูลชุดนี้เป็นข้อมูลจริง</b> จากบริษัทข้ามชาติด้านสีและสารเคลือบในเนเธอร์แลนด์ (ถูกทำให้นิรนาม) '
    "ใช้เพื่อทดสอบว่าวิธีวิเคราะห์ที่ใช้กับข้อมูลจำลองยังใช้ได้กับข้อมูลจริงที่ซับซ้อนกว่า</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "แหล่งข้อมูล: BPI Challenge 2019 (DOI 10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1, CC BY 4.0) "
    "ดาวน์โหลดจาก [figshare](https://figshare.com/articles/dataset/BPI_Challenge_2019/12715853) · "
    "1 เคส = รายการสินค้า 1 บรรทัดในใบสั่งซื้อ"
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("เคส (PO item)", num(B["cases"]))
c2.metric("Events", num(B["events"]))
c3.metric("Variants", num(B["variants"]))
c4.metric("มัธยฐานตั้งแต่สร้าง PO ถึงจ่ายเงิน",
          f"{B['stage_days']['PO item created -> invoice cleared (end to end)']['median']:.0f} วัน")

st.header("เปรียบเทียบกับข้อมูลจำลอง")
metric_th = {"Cases": "จำนวนเคส", "Events": "จำนวน events", "Variants": "จำนวน variants",
             "Variants for 80% of cases": "variants ที่ครอบคลุม 80% ของเคส",
             "Paid before any goods receipt": "จ่ายเงินก่อนรับของครั้งแรก",
             "Cases still open (not paid)": "เคสที่ยังไม่จ่ายเงิน",
             "Timestamps outside the data period": "timestamp นอกช่วงข้อมูล",
             "Median end-to-end days": "มัธยฐานระยะเวลาทั้งกระบวนการ (วัน)"}
comparison = pd.DataFrame(B["comparison"]).astype(str)
comparison["metric"] = comparison["metric"].map(metric_th).fillna(comparison["metric"])
table(comparison.rename(columns={
    "metric": "ตัวชี้วัด", "simulated (Zenodo P2P)": "ข้อมูลจำลอง (Zenodo P2P)", "real (BPI 2019)": "ข้อมูลจริง (BPI 2019)"}))
st.markdown(
    f"""
- จำนวน variants ทั้งหมดสูงกว่ามาก ({num(B['variants'])} แบบ เกิดเพียงเคสเดียว {num(B['variants_singletons'])} แบบ)
  แต่เคสส่วนใหญ่กระจุกตัว: {B['variants_needed_for_80pct']} variants ครอบคลุม 80% ของเคส
- ข้อมูลจริงมีเคสที่ยังไม่จ่ายเงิน ({B['open_cases_pct_of_invoiced_categories']}% ของประเภทที่ต้องมีใบแจ้งหนี้)
  และ timestamp ผิดปกติย้อนไปถึงปี {min(B['events_per_year'])} ({num(B['cases_with_events_before_2018'])} เคส) ซึ่งต้องจัดการก่อนวัดเวลา
"""
)

st.header("ประเภทของรายการและกติกาการจับคู่")
cat = pd.DataFrame({"ประเภท": list(B["item_category_cases"]), "เคส": list(B["item_category_cases"].values()),
                    "สัดส่วน (%)": list(B["item_category_pct"].values())})
table(cat)
rules = pd.DataFrame([{"กติกาที่ตรวจ": r["rule"][3:], "เคสที่ไม่เป็นไปตามกติกา": r["cases"],
                       "% ของประเภท": r["pct_of_category"], "เคสในประเภท": r["category_cases"]} for r in B["rules"]])
table(rules)
st.markdown(
    f"""
- การจ่ายเงินก่อนรับของแทบไม่เกิดขึ้น ({num(B['rules'][1]['cases'])} เคส หรือ {B['rules'][1]['pct_of_category']}% ของรายการแบบ 3-way match)
  และประเภท 2-way match กับ consignment เป็นไปตามกติกาทั้งหมด
- ในประเภทที่ใบแจ้งหนี้มาก่อนรับของได้ มี {num(B['ibgr_invoice_before_gr_cases'])} เคส ({B['ibgr_invoice_before_gr_pct']}%) ที่ใบแจ้งหนี้มาก่อนจริง
  และ {B['remove_payment_block_cases_pct']}% ของทุกเคสต้อง**ปลดบล็อกการจ่ายเงิน**
- มีใบขอซื้อในระบบ {B['cases_with_purchase_requisition_pct']}% ของเคส ข้อมูลชุดนี้ไม่ได้กำหนดว่าทุกการซื้อต้องมีใบขอซื้อ จึงไม่นับเป็นการผิดกติกา
"""
)

st.header("ระยะเวลา")
stages = pd.DataFrame([{"ขั้น": k, "มัธยฐาน (วัน)": v["median"], "P90 (วัน)": v["p90"], "จำนวนเคส": v["n"]}
                       for k, v in B["stage_days"].items()])
th = {"PO item created -> first goods receipt": "สร้าง PO → รับของครั้งแรก",
      "first goods receipt -> invoice recorded": "รับของครั้งแรก → บันทึกใบแจ้งหนี้",
      "invoice recorded -> invoice cleared": "บันทึกใบแจ้งหนี้ → จ่ายเงิน",
      "PO item created -> invoice cleared (end to end)": "สร้าง PO → จ่ายเงิน (ทั้งกระบวนการ)"}
stages["ขั้น"] = stages["ขั้น"].map(th)
st.altair_chart(hbar(stages, "ขั้น", "มัธยฐาน (วัน)", "มัธยฐาน (วัน)", label_fmt=".1f"), width="stretch")
table(stages)
st.info(
    f"ช่วงที่ใช้เวลานานที่สุดคือ**บันทึกใบแจ้งหนี้ → จ่ายเงิน** "
    f"(มัธยฐาน {B['stage_days']['invoice recorded -> invoice cleared']['median']:.0f} วัน) "
    f"และนานขึ้นเมื่อต้องปลดบล็อกการจ่าย ({B['invoice_to_clear_median_with_block_removal']:.0f} เทียบกับ "
    f"{B['invoice_to_clear_median_without_block_removal']:.0f} วัน) ต่างจากข้อมูลจำลองที่ทั้งกระบวนการใช้มัธยฐาน "
    f"{P['case_duration_days']['median']:.0f} วัน และไม่มีคอขวดจุดเดียว",
    icon=":material/insights:",
)
st.caption("ไม่รวมเคสที่มี timestamp ก่อนปี 2018 · การนับตั้งแต่สร้าง PO ถึงจ่ายเงินเฉพาะเคสที่จ่ายแล้ว")

st.header("การแก้ไขเอกสารและการทำงานซ้ำ")
rw = pd.DataFrame(B["rework"]).rename(columns={"activity": "กิจกรรม", "cases": "เคส", "pct_cases": "% ของเคส"})
table(rw)
st.markdown(f"เคสที่มีการแก้ไขหรือยกเลิกเอกสารอย่างน้อยหนึ่งครั้ง (ไม่รวมการปลดบล็อกการจ่าย): "
            f"**{B['cases_with_any_change_or_cancel_pct']}%**")

st.header("แผนภาพกระบวนการ (ประเภทหลัก)")
st.markdown(f"Directly-follows graph ของประเภท *3-way match, invoice before GR* แสดงเฉพาะเส้นที่เกิดในอย่างน้อย "
            f"{B['dfg_main_threshold_pct']}% ของเคส ({B['dfg_main_edges_shown']} จาก {num(B['dfg_main_edges_total'])} เส้น)")
image("06_dfg_main.png", "Directly-follows graph — BPI 2019, 3-way match, invoice before GR", width=760)

st.header("ข้อจำกัด")
st.markdown(
    """
- ยังไม่ได้ตรวจการจับคู่มูลค่า (ยอด PO ยอดรับของ และยอดใบแจ้งหนี้) ซึ่งเป็นโจทย์หลักของ BPI Challenge 2019
  เนื่องจาก log บันทึกเฉพาะมูลค่าสะสมของรายการ
- ไฟล์ข้อมูลมีขนาดประมาณ 700 MB จึงไม่ได้รวมไว้ใน repository ต้องดาวน์โหลดจากแหล่งข้อมูลก่อนรัน notebook 06
"""
)
