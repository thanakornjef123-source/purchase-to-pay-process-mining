import streamlit as st

from app_pages.common import ad, notice, num, results

R = results()
E, D = R["explore"], R["discovery"]

st.title("รายงานและข้อจำกัด")
notice()

st.header("รายงานฉบับเต็ม")
st.markdown("รายงานรูปแบบที่ปรึกษา (ภาษาไทย) ประกอบด้วยสรุปสำหรับผู้บริหาร บริบท วิธีการ ผลการวิเคราะห์ ข้อเสนอแนะ และข้อจำกัด")
if ad.REPORT_PDF.exists():
    st.download_button("ดาวน์โหลดรายงาน (PDF)", data=ad.REPORT_PDF.read_bytes(),
                       file_name="p2p_process_mining_report.pdf", mime="application/pdf",
                       icon=":material/download:", type="primary")
else:
    st.warning("ไม่พบไฟล์รายงาน")

st.header("ข้อจำกัดของการวิเคราะห์")
st.markdown(
    f"""
- **ข้อมูลจำลอง:** ทุกเคสสิ้นสุดที่การจ่ายเงิน ไม่มีเคสค้าง กลุ่มต่าง ๆ แทบไม่แตกต่างกัน และมีเส้นทางหลักเพียง {D['variants_skeleton']} แบบ
  ผลการศึกษาจึงใช้แสดงวิธีการวิเคราะห์ ไม่ใช่ข้อสรุปเกี่ยวกับบริษัทจริง
- **Event log บอกได้ว่าเกิดอะไรขึ้น แต่ไม่ได้บอกเหตุผล:** สาเหตุทุกข้อเป็นข้อสันนิษฐานที่ต้องยืนยันกับเจ้าของกระบวนการ
- **ยอดเงินรายครั้ง:** ข้อมูลไม่มียอดเงินของการจ่ายแต่ละครั้ง จึงประเมินการจ่ายซ้ำได้เพียงเพดานบน
- **Timestamp:** ละเอียดถึงระดับนาที และอาจเป็นเวลาที่บันทึกในระบบ ไม่ใช่เวลาที่ปฏิบัติงานจริง
- **ความสัมพันธ์ระหว่างเอกสาร:** มีลิงก์ที่อ้างถึงเอกสารที่ไม่มีอยู่ ({num(E['dangling_object_links_total'])} ลิงก์) จึงใช้ความสัมพันธ์จาก event แทน
- **วันส่งของตามสัญญา:** ไม่มีข้อมูลที่เชื่อถือได้ จึงวัดการส่งของตรงเวลาของผู้ขายไม่ได้
- **ข้อเสนอแนะยังไม่ได้นำไปปฏิบัติ:** จึงไม่มีตัวเลขผลลัพธ์หลังการปรับปรุง
"""
)

st.header("แหล่งข้อมูลและสัญญาอนุญาต")
st.markdown(
    f"""
- ข้อมูล: *Procure-To-Payment (P2P) Object-centric Event Log in OCEL 2.0 Standard*,
  [Zenodo record 8412920](https://zenodo.org/records/8412920), สัญญาอนุญาต CC BY 4.0
  (ไฟล์ `ocel2-p2p.sqlite`, MD5 `{E['file_md5']}`)
- เครื่องมือวิเคราะห์: PM4Py {E['pm4py_version']} (AGPL-3.0), pandas, Graphviz
- ฟอนต์: Sarabun และ IBM Plex Sans Thai (SIL Open Font License)
- โปรเจกต์ส่วนบุคคล ไม่ใช่งานของบริษัทใดและไม่ใช่งานฝึกงาน
"""
)
