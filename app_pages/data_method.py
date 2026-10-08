import pandas as pd
import streamlit as st

from app_pages.common import image, notice, num, results, table

R = results()
E = R["explore"]

st.title("ข้อมูลและวิธีการ")
notice()

st.header("ชุดข้อมูล")
st.markdown(
    """
**Procure-To-Payment (P2P) Object-centric Event Log in OCEL 2.0 Standard**
เผยแพร่บน [Zenodo record 8412920](https://zenodo.org/records/8412920) ภายใต้สัญญาอนุญาต CC BY 4.0
เป็นข้อมูลจำลองที่สร้างตามประเภทเอกสารและธุรกรรมของ SAP

ข้อมูลอยู่ในรูปแบบ **object-centric** กล่าวคือ event หนึ่งรายการเชื่อมกับเอกสารได้หลายใบพร้อมกัน
เช่น การจ่ายเงินหนึ่งครั้งเชื่อมกับ payment, ใบแจ้งหนี้, ใบรับของ และใบสั่งซื้อ
"""
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Events", num(E["n_events"]))
c2.metric("เอกสาร (objects)", num(E["n_objects"]))
c3.metric("กิจกรรม (activities)", E["n_activities"])
c4.metric("ช่วงเวลา", f"{E['time_span_days']} วัน")

left, right = st.columns(2)
with left:
    st.subheader("จำนวน events ต่อกิจกรรม")
    table(pd.DataFrame({"กิจกรรม": list(E["events_per_activity"]), "Events": list(E["events_per_activity"].values())}))
with right:
    st.subheader("จำนวนเอกสารต่อประเภท")
    table(pd.DataFrame({"ประเภทเอกสาร": list(E["objects_per_type"]), "จำนวน": list(E["objects_per_type"].values())}))

st.header("การตรวจคุณภาพข้อมูล")
st.markdown(
    f"""
- ไม่พบค่าว่างในข้อมูล event; timestamp ละเอียดถึงระดับนาที ({num(E['events_sharing_timestamp'])} events หรือ {E['share_events_sharing_timestamp_pct']}% มีเวลาตรงกับ event อื่น)
  จึงใช้รหัส event เป็นเกณฑ์เรียงลำดับรอง
- ลิงก์ระหว่างเอกสาร {num(E['dangling_object_links_total'])} ลิงก์อ้างถึงใบแจ้งหนี้ที่ไม่มีอยู่ในข้อมูล จึงใช้ความสัมพันธ์ที่บันทึกใน event เป็นหลัก
- รหัสใบขอซื้อมีเครื่องหมาย `:` เกินมา (เช่น `purchase_requisition:622:pr_trigger_622`) จึงอ่านประเภทเอกสารจากตาราง object แทนการแยกจากรหัส
- เอกสารประเภท material จำนวน {E['objects_without_events_total']} รายการไม่มี event และไม่ส่งผลต่อการวิเคราะห์
"""
)

st.header("การกำหนดเคส (case notion)")
st.markdown(
    f"""
กำหนดให้ **1 เคส = ใบขอซื้อ 1 ใบ และเอกสารทั้งหมดที่ตามมา** เนื่องจากสายเอกสารมีโครงสร้างแบบต้นไม้ที่มีใบขอซื้อเป็นราก
เอกสารทุกใบจึงสืบย้อนไปยังใบขอซื้อได้เพียงใบเดียว ผลที่ได้คือ event ทั้ง {num(E['events_mapped_to_a_case'])} รายการอยู่ในเคสเดียวพอดี
(อยู่หลายเคส {E['events_mapped_to_multiple_cases']} รายการ, ไม่อยู่ในเคสใด {E['events_not_mapped']} รายการ) รวม **{num(E['case_count'])} เคส**
เฉลี่ย {E['events_per_case']['mean']} events ต่อเคส
"""
)
st.caption("ข้อจำกัดของการกำหนดเคสแบบนี้: เคสที่มีหลาย PO จะมีกิจกรรมซ้ำใน trace ซึ่งไม่ใช่การทำงานซ้ำจริง "
           "จึงตรวจลำดับและการทำซ้ำในระดับเอกสารแยกอีกชั้นหนึ่ง")
image("01_case_size_duration.png", "จำนวน events ต่อเคส และระยะเวลาต่อเคส (วัน)")

st.header("ขั้นตอนการวิเคราะห์")
st.markdown(
    f"""
| ขั้น | Notebook | เนื้อหา |
|---|---|---|
| 1 | `01_explore` | สำรวจข้อมูล ตรวจคุณภาพ และกำหนดเคส |
| 2 | `02_discovery` | variants, directly-follows graph, Inductive Miner |
| 3 | `03_conformance` | โมเดลอ้างอิง, token-based replay, alignments, กฎธุรกิจระดับเอกสาร |
| 4 | `04_performance` | เวลารอระหว่างขั้น การแยกตามกลุ่ม และการทำซ้ำ |
| 5 | `05_recommendations` | สรุปประเด็น แผนภาพ as-is และ to-be |

เครื่องมือ: Python, pandas และ PM4Py {E['pm4py_version']} · ตัวเลขทุกตัวในเว็บไซต์นี้อ่านจากผลลัพธ์ที่ notebook บันทึกไว้ (`results/*.json`)
"""
)
