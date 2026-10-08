import pandas as pd
import streamlit as st

from app_pages.common import ad, case_log, case_table, notice, num, table

st.title("สำรวจรายเคส")
notice()
st.markdown("เลือกเงื่อนไขเพื่อกรองเคส แล้วเลือกเคสเพื่อดูลำดับกิจกรรมและกฎที่ถูกละเมิด")

t = case_table()
log = case_log()
rule_codes = [c for c in ad.RULE_LABELS_TH if c in t.columns and t[c].any()]

f1, f2, f3 = st.columns(3)
path_opts = ["ทั้งหมด"] + sorted(t["path_th"].unique())
path = f1.selectbox("เส้นทางของใบขอซื้อ", path_opts)
rule_opts = ["ทั้งหมด", "ไม่ละเมิดกฎใด"] + [f"{c} · {ad.RULE_LABELS_TH[c]}" for c in rule_codes]
rule_sel = f2.selectbox("กฎที่ละเมิด", rule_opts)
group_opts = ["ทั้งหมด"] + sorted(t["purchasing_group"].astype(str).unique())
group = f3.selectbox("กลุ่มจัดซื้อ", group_opts)

sel = t
if path != "ทั้งหมด":
    sel = sel[sel["path_th"] == path]
if rule_sel == "ไม่ละเมิดกฎใด":
    sel = sel[sel["rules_broken"] == 0]
elif rule_sel != "ทั้งหมด":
    sel = sel[sel[rule_sel.split(" · ")[0]]]
if group != "ทั้งหมด":
    sel = sel[sel["purchasing_group"].astype(str) == group]

st.caption(f"พบ {num(len(sel))} จาก {num(len(t))} เคส")
if sel.empty:
    st.warning("ไม่พบเคสที่ตรงกับเงื่อนไข")
    st.stop()

overview = pd.DataFrame({
    "เคส (ใบขอซื้อ)": [f"PR {ad.case_number(c)}" for c in sel.index],
    "เส้นทาง": sel["path_th"].values,
    "PO": sel["POs"].values, "ใบรับของ": sel["GRs"].values,
    "ระยะเวลา (วัน)": sel["duration"].round(1).values,
    "จำนวนกฎที่ละเมิด": sel["rules_broken"].values,
    "_case": sel.index,
}).sort_values("เคส (ใบขอซื้อ)", key=lambda s: s.str[3:].astype(int))
table(overview.drop(columns="_case"), max_height=320)

labels = dict(zip(overview["เคส (ใบขอซื้อ)"], overview["_case"]))
choice = st.selectbox("เลือกเคสเพื่อดูรายละเอียด", list(labels))
case_id = labels[choice]
row = t.loc[case_id]

st.header(f"รายละเอียด {choice}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("ระยะเวลา", f"{row['duration']:.1f} วัน")
m2.metric("PO / ใบรับของ", f"{row['POs']} / {row['GRs']}")
m3.metric("กฎที่ละเมิด", int(row["rules_broken"]))
m4.metric("Alignment fitness", f"{row['alignment_fitness']:.3f}")
st.markdown(f"**เส้นทาง:** {row['path_th']} · **กลุ่มจัดซื้อ:** {row['purchasing_group']} · "
            f"**ผู้ขาย:** {row['vendor']} · **วิธีจ่ายเงิน:** {row['payment_method']}")

broken = [f"- **{c}** · {ad.RULE_LABELS_TH[c]}" for c in rule_codes if bool(row[c])]
if broken:
    st.error("กฎที่ละเมิด\n\n" + "\n".join(broken), icon=":material/report:")
else:
    st.success("เคสนี้เป็นไปตามกระบวนการอ้างอิงทุกข้อ", icon=":material/check_circle:")

trace = log[log["case"] == case_id].copy()
start = trace["timestamp"].min()
trace["วันที่"] = trace["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
trace["วันที่นับจากเริ่ม"] = ((trace["timestamp"] - start).dt.total_seconds() / 86400).round(1)
st.subheader("ลำดับกิจกรรม")
table(trace[["วันที่", "วันที่นับจากเริ่ม", "activity", "department", "ocel_event_id"]]
      .rename(columns={"activity": "กิจกรรม", "department": "หน่วยงาน", "ocel_event_id": "รหัส event"}),
      max_height=1500)
