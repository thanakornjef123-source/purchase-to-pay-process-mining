import pandas as pd
import streamlit as st

from app_pages.common import image, notice, num, results, table

R = results()
D = R["discovery"]
N = D["cases"]

st.title("กระบวนการที่เกิดขึ้นจริง")
notice()

st.header("รูปแบบของกระบวนการ (variants)")
c1, c2, c3 = st.columns(3)
c1.metric("Variants ทั้งหมด", num(D["variants_full"]), help="นับจากลำดับกิจกรรมครบทุกขั้นของแต่ละเคส")
c2.metric("Variants ที่ต้องใช้ให้ครอบคลุม 80%", num(D["variants_needed_for_80pct"]))
c3.metric("เส้นทางหลัก", D["variants_skeleton"], help="นับเฉพาะลำดับที่กิจกรรมแต่ละประเภทปรากฏครั้งแรก")

st.markdown(
    f"""
หากนับลำดับกิจกรรมทุกขั้น จะได้ {num(D['variants_full'])} variants จาก {num(N)} เคส และ {num(D['variants_full_singletons'])} variants เกิดขึ้นเพียงเคสเดียว
variant ที่พบบ่อยที่สุดครอบคลุม {D['top1_coverage_pct']}% ของเคส

อย่างไรก็ตาม จำนวน variants ที่สูงไม่ได้หมายความว่ากระบวนการซับซ้อน เมื่อพิจารณาเฉพาะลำดับที่กิจกรรมปรากฏครั้งแรก
จะเหลือเส้นทางหลักเพียง **{D['variants_skeleton']} แบบ** ความหลากหลายที่เหลือเกิดจาก **จำนวนเอกสารต่อเคส**
โดยเคสที่มี PO 1 ใบและใบรับของ 1 ใบ ({num(D['cases_single_po_single_gr'])} เคส) มีเพียง {D['variants_in_single_po_single_gr']} variants
"""
)

for i, (path, n) in enumerate(D["skeleton_variants"].items(), 1):
    with st.container(border=True):
        st.markdown(f"**เส้นทาง {i}** · {num(n)} เคส ({100 * n / N:.1f}%)  \n"
                    + " → ".join(f"`{step}`" for step in path.split(" > ")))

st.subheader("สัดส่วนเคสที่ครอบคลุมตามจำนวน variants")
shapes = pd.DataFrame(D["doc_shapes"]).rename(columns={"shape": "จำนวนเอกสารต่อเคส", "cases": "เคส", "variants": "variants"})
left, right = st.columns([3, 2])
with left:
    image("02_variant_coverage.png", "สัดส่วนเคสที่ครอบคลุมเมื่อเพิ่มจำนวน variants (เรียงจากพบบ่อยไปน้อย)")
with right:
    st.markdown("**จำนวนเอกสารต่อเคส กับจำนวน variants**")
    table(shapes, max_height=330)

st.header("แผนภาพกระบวนการ")
tab1, tab2 = st.tabs(["Directly-follows graph", "BPMN (Inductive Miner)"])
with tab1:
    st.markdown(
        f"ตัวเลขบนเส้นคือจำนวนครั้งที่กิจกรรมหนึ่งตามด้วยอีกกิจกรรมหนึ่งโดยตรง เส้นหนาแสดงความถี่สูง "
        f"กระบวนการมีจุดเริ่มต้น 2 จุด: {num(D['start_activities']['Create Purchase Requisition'])} เคสเริ่มจากการสร้างใบขอซื้อ "
        f"และ {num(D['start_activities']['Create Request for Quotation'])} เคสเริ่มจากการขอใบเสนอราคาโดยตรง"
    )
    image("02_dfg_frequency_tb.png", "Directly-follows graph ของทั้ง log", width=760)
with tab2:
    q = D["discovered_model_quality"]["full log, noise 0.2"]
    st.markdown(
        f"โมเดลอธิบาย log ได้ดี (log fitness {q['log_fitness']}) แต่มี precision ต่ำ ({q['precision']}) "
        "เนื่องจากมี loop และการทำงานคู่ขนานจำนวนมาก จึงใช้เพื่ออธิบายภาพรวมเท่านั้น ไม่ได้ใช้เป็นมาตรฐานในการตรวจ  \n"
        "วิธีอ่าน: ◇× คือการเลือกเส้นทางใดเส้นทางหนึ่ง ◇+ คือการทำงานคู่ขนาน และเส้นประคือการวนกลับไปทำซ้ำ"
    )
    image("02_asis_bpmn_tb.png", "BPMN ที่ได้จาก Inductive Miner (as-is)", width=620)

st.header("สัญญาณที่พบจากแผนภาพ")
st.markdown(
    f"""
- {num(D['start_activities']['Create Request for Quotation'])} เคสเริ่มต้นที่การขอใบเสนอราคาโดยไม่มีใบขอซื้อ
- พบการสั่งจ่ายเงินต่อเนื่องกัน (`Execute Payment → Execute Payment`)
- พบการรับของหลังการจ่ายเงิน และมี {num(D['end_activities'].get('Create Goods Receipt', 0))} เคสที่สิ้นสุดด้วยการรับของแทนการจ่ายเงิน

รายละเอียดของแต่ละประเด็นอยู่ในหน้า **ความสอดคล้องกับกระบวนการ**
"""
)
