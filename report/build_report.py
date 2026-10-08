"""Build report/p2p_process_mining_report.html and .pdf from results/*.json.

Every number in the report is read from the JSON files written by the notebooks,
so the report cannot drift from the analysis. Run after the notebooks:

    python report/build_report.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
E = json.loads((RES / "01_explore.json").read_text())
D = json.loads((RES / "02_discovery.json").read_text())
C = json.loads((RES / "03_conformance.json").read_text())
P = json.loads((RES / "04_performance.json").read_text())
S = json.loads((RES / "05_recommendations.json").read_text())
rule = {r["rule"][:2]: r for r in C["rules"]}
N = C["cases"]
st = P["stage_wait_days"]
moves = {(m["type"].split()[0], m["activity"]): m for m in C["alignment_moves"]}
dur = {g["path"]: g for g in P["duration_by_group"]["path"]}
pg = {g["purchasing_group"]: g for g in P["duration_by_group"]["purchasing_group"]}
pm = {g["payment_method"]: g for g in P["duration_by_group"]["payment_method"]}
rp = {g["repeated_payment"]: g for g in P["duration_by_group"]["repeated_payment"]}
rw = {r["activity"]: r for r in P["rework"]}
q = D["discovered_model_quality"]["full log, noise 0.2"]
_main = {k: v["median"] for k, v in st.items() if not k.startswith("1b") and v["median"] > 1}
other_lo = min(v for k, v in _main.items() if k != P["longest_stage_by_median"])
other_hi = max(v for k, v in _main.items() if k != P["longest_stage_by_median"])
pay_max = next(r["max"] for r in E["repeats"] if r["object_type"] == "payment" and r["activity"] == "Execute Payment")


def n(x, d=0):
    return f"{x:,.{d}f}"


def fig(name, caption, width="100%"):
    return (f'<figure><img src="../figures/{name}" style="width:{width}">'
            f'<figcaption>{caption}</figcaption></figure>')


stage_rows = "".join(
    f"<tr><td>{k[2:] if k[0].isdigit() and k[1]==' ' else k[3:]}</td><td class=num>{int(v['n']):,}</td>"
    f"<td class=num>{v['median']:.2f}</td><td class=num>{v['mean']:.2f}</td><td class=num>{v['p90']:.2f}</td></tr>"
    for k, v in st.items() if not k.startswith("1b"))

rules_rows = "".join(
    f"<tr><td>{r['rule'][:2]}</td><td>{r['rule'][3:]}</td><td class=num>{r['documents']:,}</td>"
    f"<td class=num>{r['cases']:,}</td><td class=num>{r['cases_pct']}%</td></tr>"
    for r in C["rules"] if r["kind"] == "rule")

issue_rows = "".join(
    f"<tr><td><b>{i['id']}</b></td><td><b>{i['issue']}</b><br><span class=small>{i['evidence']}</span></td>"
    f"<td>{i['impact']}</td><td>{i['recommendation']}</td></tr>" for i in S["issues"])

sk = list(D["skeleton_variants"].items())
CSS = """
@font-face{font-family:Sarabun;font-weight:400;src:url(../static/fonts/sarabun-thai-400-normal.woff2);unicode-range:U+0E01-0E5B,U+200C-200D,U+25CC}
@font-face{font-family:Sarabun;font-weight:400;src:url(../static/fonts/sarabun-latin-400-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212}
@font-face{font-family:Sarabun;font-weight:600;src:url(../static/fonts/sarabun-thai-600-normal.woff2);unicode-range:U+0E01-0E5B,U+200C-200D,U+25CC}
@font-face{font-family:Sarabun;font-weight:600;src:url(../static/fonts/sarabun-latin-600-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212}
@font-face{font-family:Sarabun;font-weight:700;src:url(../static/fonts/sarabun-thai-700-normal.woff2);unicode-range:U+0E01-0E5B,U+200C-200D,U+25CC}
@font-face{font-family:Sarabun;font-weight:700;src:url(../static/fonts/sarabun-latin-700-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212}
@font-face{font-family:Plex;font-weight:400;src:url(../static/fonts/ibm-plex-sans-thai-thai-400-normal.woff2);unicode-range:U+0E01-0E5B,U+200C-200D,U+25CC}
@font-face{font-family:Plex;font-weight:400;src:url(../static/fonts/ibm-plex-sans-thai-latin-400-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212}
@font-face{font-family:Plex;font-weight:600;src:url(../static/fonts/ibm-plex-sans-thai-thai-600-normal.woff2);unicode-range:U+0E01-0E5B,U+200C-200D,U+25CC}
@font-face{font-family:Plex;font-weight:600;src:url(../static/fonts/ibm-plex-sans-thai-latin-600-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212}
@page{size:A4;margin:18mm 17mm 18mm 17mm}
:root{--ink:#1d2733;--muted:#5b6672;--accent:#1f5f8b;--red:#b23a3a;--line:#d7dde3;--soft:#f3f6f9}
body{font-family:Sarabun,sans-serif;color:var(--ink);font-size:10.6pt;line-height:1.55;margin:0}
h1,h2,h3{font-family:Plex,sans-serif;font-weight:600;color:var(--ink);line-height:1.25}
h1{font-size:21pt;margin:0 0 4px}
h2{font-size:14.5pt;margin:22px 0 8px;padding-bottom:4px;border-bottom:2px solid var(--accent);break-after:avoid}
h3{font-size:11.5pt;margin:14px 0 6px;color:var(--accent);break-after:avoid}
p{margin:6px 0}
.small{font-size:9pt;color:var(--muted)}
.page{break-before:page}
.cover-meta{color:var(--muted);font-size:9.5pt;margin-bottom:14px}
.banner{background:#fff4e5;border-left:4px solid #d98a1b;padding:7px 10px;font-size:9.4pt;margin:8px 0 12px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:10px 0 12px}
.kpi{background:var(--soft);border:1px solid var(--line);border-radius:6px;padding:8px 10px}
.kpi b{display:block;font-family:Plex;font-size:17pt;color:var(--accent);line-height:1.1}
.kpi span{font-size:8.6pt;color:var(--muted)}
table{width:100%;border-collapse:collapse;margin:8px 0 10px;font-size:9.3pt;break-inside:auto}
th{font-family:Plex;font-weight:600;text-align:left;background:var(--soft);border-bottom:1.5px solid var(--accent);padding:5px 6px}
td{border-bottom:1px solid var(--line);padding:4.5px 6px;vertical-align:top}
tr{break-inside:avoid}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
figure{margin:10px 0 12px;break-inside:avoid;text-align:center}
figure img{border:1px solid var(--line);border-radius:4px;box-sizing:border-box;object-fit:contain}
figcaption{font-size:8.8pt;color:var(--muted);margin-top:4px;text-align:left}
.callout{border:1px solid var(--line);border-radius:6px;padding:8px 12px;margin:8px 0;background:#fafbfc;break-inside:avoid}
.callout b.t{font-family:Plex;color:var(--accent)}
ul,ol{margin:4px 0 6px 0;padding-left:20px}
li{margin:2px 0}
code{font-size:8.8pt;background:var(--soft);padding:0 3px;border-radius:3px}
.hyp{color:var(--muted);font-style:normal}
.tag{display:inline-block;font-size:8pt;font-family:Plex;padding:0 6px;border-radius:9px;background:#fdecea;color:var(--red);margin-left:4px}
.wide{break-before:page;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px;align-items:start}
.wide>figure{min-width:0;margin:0}
.wide figure img{width:100%;height:auto;max-height:232mm;object-fit:contain}
.solo{break-before:page}
.solo figure img{max-height:228mm;max-width:100%;width:auto !important;height:auto}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
"""

html = f"""<!doctype html><html lang="th"><head><meta charset="utf-8">
<title>Process Mining: Purchase-to-Pay</title><style>{CSS}</style></head><body>

<h1>Process Mining ของกระบวนการจัดซื้อถึงจ่ายเงิน (Purchase-to-Pay)</h1>
<div class="cover-meta">รายงานแบบที่ปรึกษา · Thanakorn · ตุลาคม 2026 · โปรเจกต์ส่วนตัวสำหรับ portfolio</div>
<div class="banner"><b>หมายเหตุเรื่องข้อมูล:</b> วิเคราะห์จากชุดข้อมูลสาธารณะ <i>Procure-To-Payment (P2P) Object-centric Event Log in OCEL 2.0</i> (Zenodo 8412920, CC BY 4.0)
ซึ่งเป็น<b>ข้อมูลจำลอง</b>ตามโครงสร้างธุรกรรม SAP ไม่ใช่ข้อมูลของบริษัทจริง และไม่ใช่งานของบริษัทใดหรือการฝึกงาน
ตัวเลขทุกตัวคำนวณจากโค้ดใน repo (ดู <code>results.md</code>) ส่วนสาเหตุทุกข้อเป็นข้อสันนิษฐานที่ต้องยืนยันกับเจ้าของกระบวนการ</div>

<h2 style="margin-top:6px">สรุปผู้บริหาร</h2>
<p>ตรวจเส้นทางของใบขอซื้อ {n(N)} ใบ ({n(E['n_events'])} events, {E['time_min'][:7]} ถึง {E['time_max'][:7]}) ตั้งแต่ขอซื้อจนจ่ายเงิน
พบว่ามีเพียง <b>{C['cases_fully_compliant_pct']}%</b> ที่เดินตามกระบวนการที่ควรเป็นครบทุกข้อ อีก <b>{C['cases_with_any_rule_violation_pct']}%</b> เบี่ยงอย่างน้อย 1 จุด
จุดที่เบี่ยงส่วนใหญ่เป็นเรื่อง<b>การควบคุม (control)</b> ไม่ใช่เรื่องความเร็ว</p>
<div class="kpis">
<div class="kpi"><b>{C['cases_with_any_rule_violation_pct']}%</b><span>เคสที่เบี่ยงจากกระบวนการอ้างอิง</span></div>
<div class="kpi"><b>{rule['A1']['cases_pct']}%</b><span>เริ่มจัดซื้อโดยไม่มีใบขอซื้อในระบบ</span></div>
<div class="kpi"><b>{rule['D1']['cases_pct']}%</b><span>มีการสั่งจ่ายเงินซ้ำกับ payment เดิม</span></div>
<div class="kpi"><b>{P['case_duration_days']['median']:.1f} วัน</b><span>ค่ามัธยฐานตั้งแต่เริ่มถึงจ่ายเงิน</span></div>
</div>
<table><tr><th style="width:5%">#</th><th style="width:38%">ปัญหา</th><th class=num style="width:12%">เคส</th><th>ข้อเสนอแนะหลัก</th></tr>
<tr><td>P1</td><td>ขอใบเสนอราคาโดยไม่มีใบขอซื้อในระบบ</td><td class=num>{rule['A1']['cases_pct']}%</td><td>บังคับให้ RFQ ต้องอ้างใบขอซื้อที่อนุมัติแล้ว</td></tr>
<tr><td>P2</td><td>ส่งต่อการอนุมัติ แต่ไม่มีบันทึกการอนุมัติ</td><td class=num>{rule['A2']['cases_pct']}%</td><td>ผู้รับมอบต้องอนุมัติในระบบก่อนปลดล็อกใบขอซื้อ</td></tr>
<tr><td>P3</td><td>สั่งจ่ายเงินซ้ำกับ invoice เดิม</td><td class=num>{rule['D1']['cases_pct']}%</td><td>ตรวจการจ่ายซ้ำก่อนรันจ่ายเงิน และทบทวนรายการที่พบ</td></tr>
<tr><td>P4</td><td>จ่ายเงินให้ PO ก่อนรับของครบ</td><td class=num>{rule['C5']['cases_pct']}%</td><td>เปลี่ยนเป็น three-way match และจ่ายตามจำนวนที่รับจริง</td></tr>
<tr><td>P5</td><td>เวลาส่วนใหญ่อยู่ในการส่งต่องานภายใน</td><td class=num>ทุกเคส</td><td>อนุมัติอัตโนมัติเมื่อมูลค่าต่ำ, สร้าง RFQ อัตโนมัติ, รันจ่ายเงินถี่ขึ้น</td></tr>
</table>
<p><b>สิ่งที่ควรทำก่อน:</b> P3 และ P1 เพราะเกี่ยวกับเงินที่ออกไปแล้วและการผูกพันงบโดยไม่มีการอนุมัติ ให้ทีมการเงินตรวจ {n(C['D1_payments'])} payment ที่ถูกสั่งจ่ายซ้ำก่อน
เพื่อยืนยันว่าเป็นการจ่ายเกินจริงหรือไม่ (ข้อมูลไม่มียอดเงินรายครั้ง จึงยืนยันเองไม่ได้)</p>
<p class="small">รายงานนี้ไม่ได้อ้างว่าข้อเสนอแนะจะลดต้นทุนหรือเพิ่มประสิทธิภาพได้เท่าไร เพราะยังไม่ได้นำไปใช้จริง</p>

<h2 class="page">1. บริบทและคำถาม</h2>
<p>กระบวนการ Purchase-to-Pay (P2P) คือการจัดซื้อตั้งแต่มีคนขอซื้อจนถึงจ่ายเงินให้ผู้ขาย เป็นกระบวนการที่มีการควบคุมมาก เพราะเกี่ยวกับเงินที่ออกจากบริษัท
ลำดับมาตรฐานคือ ใบขอซื้อ (PR) → อนุมัติ → ขอใบเสนอราคา (RFQ) → ใบสั่งซื้อ (PO) → อนุมัติ PO → รับของ (GR) → รับใบแจ้งหนี้ (invoice) → จับคู่เอกสาร → จ่ายเงิน</p>
<p>process mining ใช้ event log ที่ระบบ ERP บันทึกไว้อยู่แล้ว มาสร้างภาพกระบวนการที่<b>เกิดขึ้นจริง</b> แทนการถามคนว่ากระบวนการเป็นอย่างไร แล้วเทียบกับกระบวนการที่<b>ควรเป็น</b></p>
<div class="callout"><b class="t">คำถามที่รายงานนี้ตอบ</b>
<ol><li>กระบวนการจริงมีกี่แบบ (variants) และกี่แบบครอบคลุมงานส่วนใหญ่</li>
<li>กี่เปอร์เซ็นต์ของเคสเดินตามลำดับที่ควรเป็น และที่เบี่ยงไปเบี่ยงแบบไหน</li>
<li>ขั้นไหนรอนานที่สุด และเกิดกับกลุ่มใดเป็นพิเศษ</li>
<li>มีการทำซ้ำ (rework) ที่ไหน บ่อยแค่ไหน</li>
<li>มีเคสที่ข้ามขั้นสำคัญหรือลำดับผิดหรือไม่ เช่น จ่ายเงินก่อนรับของ</li>
<li>ปัญหาสำคัญคืออะไร และควรแก้ในทางธุรกิจอย่างไร</li></ol></div>

<h2>2. ข้อมูลและวิธีการ</h2>
<h3>2.1 ชุดข้อมูล</h3>
<table><tr><th>รายการ</th><th class=num>ค่า</th><th>รายการ</th><th class=num>ค่า</th></tr>
<tr><td>Events</td><td class=num>{n(E['n_events'])}</td><td>Activities</td><td class=num>{E['n_activities']}</td></tr>
<tr><td>Objects (เอกสาร)</td><td class=num>{n(E['n_objects'])}</td><td>ประเภทเอกสาร</td><td class=num>{E['n_object_types']}</td></tr>
<tr><td>ลิงก์ event→เอกสาร</td><td class=num>{n(E['n_event_object_links'])}</td><td>ช่วงเวลา (วัน)</td><td class=num>{E['time_span_days']}</td></tr>
</table>
<p>ข้อมูลอยู่ในรูปแบบ <b>object-centric (OCEL 2.0)</b> คือ event หนึ่งตัวผูกกับเอกสารได้หลายใบพร้อมกัน เช่น การจ่ายเงินหนึ่งครั้งผูกกับ payment, invoice, ใบรับของ และ PO
ต่างจาก event log แบบดั้งเดิมที่ event หนึ่งตัวอยู่ในเคสเดียว</p>

<h3>2.2 การตรวจคุณภาพข้อมูล</h3>
<ul>
<li>ไม่มีค่าว่างใน event และ timestamp ละเอียดระดับนาที ({n(E['events_sharing_timestamp'])} events หรือ {E['share_events_sharing_timestamp_pct']}% มีเวลาตรงกับ event อื่น) จึงใช้รหัส event เป็นตัวเรียงลำดับรอง</li>
<li>ลิงก์ระหว่างเอกสาร {n(E['dangling_object_links_total'])} ลิงก์ชี้ไปหา invoice ที่ไม่มีอยู่จริง จึงใช้ความสัมพันธ์จาก event เป็นหลัก</li>
<li>รหัสใบขอซื้อมีเครื่องหมาย <code>:</code> เกินมา (เช่น <code>purchase_requisition:622:pr_trigger_622</code>) ต้องอ่านประเภทเอกสารจากตาราง object ไม่ใช่แยกจากรหัส</li>
<li>material {E['objects_without_events_total']} รายการไม่มี event เลย PM4Py ตัดทิ้งตอนโหลด ไม่กระทบการวิเคราะห์</li>
</ul>

<h3>2.3 การกำหนดเคส (case notion)</h3>
<p>ต้องเลือกว่า "1 เคส" คืออะไร เลือก <b>1 เคส = ใบขอซื้อ 1 ใบ และเอกสารทั้งหมดที่ตามมา</b> เพราะสายเอกสารเป็นโครงสร้างต้นไม้ที่มีใบขอซื้อเป็นราก
เอกสารทุกใบสืบกลับไปหาใบขอซื้อได้ใบเดียว ผลคือ event ทั้ง {n(E['events_mapped_to_a_case'])} ตัวอยู่ในเคสเดียวพอดี
(อยู่หลายเคส {E['events_mapped_to_multiple_cases']} ตัว, ไม่อยู่ในเคสใด {E['events_not_mapped']} ตัว) ได้ {n(E['case_count'])} เคส
เฉลี่ยเคสละ {E['events_per_case']['mean']} events</p>
<p class="small">ข้อเสียของการเลือกแบบนี้: เคสที่มีหลาย PO จะมี activity ซ้ำใน trace ซึ่งไม่ใช่การทำซ้ำจริง จึงตรวจลำดับและ rework ระดับเอกสารแยกอีกชั้น (ดูหัวข้อ 4–5)</p>

<h3>2.4 เครื่องมือและขั้นตอน</h3>
<p>Python 3.13, pandas และ PM4Py {E['pm4py_version']} แบ่งงานเป็น 5 notebook:
<code>01_explore</code> → <code>02_discovery</code> (variants, DFG, Inductive Miner) → <code>03_conformance</code> (token-based replay, alignments, กฎธุรกิจ)
→ <code>04_performance</code> (เวลารอ, rework) → <code>05_recommendations</code>. ทุก notebook เขียนตัวเลขลง <code>results/*.json</code> และรายงานนี้สร้างจากไฟล์ JSON นั้นโดยตรง</p>

<h2 class="page">3. กระบวนการที่เกิดขึ้นจริง</h2>
<p>ถ้านับลำดับ activity ทุกตัว มี <b>{D['variants_full']} variants</b> จาก {N} เคส โดย {D['variants_full_singletons']} variants เกิดแค่เคสเดียว
variant ที่พบบ่อยที่สุดครอบคลุม {D['top1_coverage_pct']}% ของเคส ต้องใช้ {D['variants_needed_for_50pct']} variants จึงครอบคลุม 50% และ {D['variants_needed_for_80pct']} variants จึงครอบคลุม 80%</p>
{fig('02_variant_coverage.png','รูป 1 · สัดส่วนเคสที่ครอบคลุมเมื่อเพิ่มจำนวน variants (เรียงจากพบบ่อยไปน้อย)','62%')}
<p>แต่ variants จำนวนมากไม่ได้แปลว่ากระบวนการยุ่ง เมื่อดูเฉพาะลำดับที่ activity แต่ละตัวปรากฏครั้งแรก (skeleton) จะเหลือเส้นทางหลักแค่ <b>{D['variants_skeleton']} แบบ</b>:</p>
<table><tr><th>เส้นทางหลัก</th><th class=num>เคส</th></tr>
{''.join(f"<tr><td>{k}</td><td class=num>{v}</td></tr>" for k,v in sk)}</table>
<p>ความหลากหลายที่เหลือมาจาก<b>จำนวนเอกสารต่อเคส</b> เคสที่มี PO 1 ใบและใบรับของ 1 ใบ ({D['cases_single_po_single_gr']} เคส) มีแค่ {D['variants_in_single_po_single_gr']} variants
ส่วนเคสที่มีหลาย PO แทบทุกเคสเป็น variant ของตัวเอง เพราะลำดับระหว่าง PO แต่ละใบสลับกันได้</p>
<p>จาก DFG (รูป 2 ท้ายหัวข้อนี้) เห็นสัญญาณของปัญหา 3 จุดก่อนตรวจละเอียด:</p>
<ul>
<li>มีจุดเริ่ม 2 จุด: {D['start_activities']['Create Request for Quotation']} เคสเริ่มที่การขอใบเสนอราคาโดยไม่มีใบขอซื้อ</li>
<li><code>Execute Payment → Execute Payment</code> คือการสั่งจ่ายต่อกัน</li>
<li><code>Execute Payment → Create Goods Receipt</code> และมี {D['end_activities'].get('Create Goods Receipt',0)} เคสที่จบด้วยการรับของ ไม่ใช่การจ่ายเงิน</li>
</ul>
<p>Inductive Miner (ทั้งแบบกรอง {D['im_top_k']} variants ยอดนิยมและแบบใช้ทั้ง log ที่ noise threshold 0.2) ให้ process tree ตัวเดียวกัน
โมเดลอธิบาย log ได้ดี (log fitness {q['log_fitness']}) แต่ precision ต่ำ ({q['precision']}) เพราะมี loop และ parallel เยอะ จึงใช้แค่อธิบายภาพรวม ไม่ได้ใช้เป็นมาตรฐานในการตรวจ</p>

<div class="solo">{fig('02_dfg_frequency_tb.png','รูป 2 · Directly-follows graph ของทั้ง log (ตัวเลข = จำนวนครั้งที่ activity หนึ่งตามด้วยอีก activity)')}</div><div class="solo">{fig('02_asis_bpmn_tb.png','รูป 3 · BPMN ที่ได้จาก Inductive Miner (as-is) วิธีอ่าน: อ่านจากบนลงล่าง ◇× = เลือกทางใดทางหนึ่ง, ◇+ = สองฝั่งทำคู่ขนานกันได้, เส้นประ = วนกลับไปทำซ้ำ (เช่น สร้าง PO หลายใบ) ฝั่งซ้ายคือการรับของ ฝั่งขวาคือใบแจ้งหนี้ → จับคู่ → จ่ายเงิน (ตัด gateway ที่มีทางเข้า 1 ทางออก 1 ออกเพื่อให้อ่านง่าย ความหมายของโมเดลไม่เปลี่ยน)')}</div>
<h2 class="page">4. เทียบกับกระบวนการที่ควรเป็น</h2>
<p>ตรวจ 2 ชั้น เพราะเคสหนึ่งมีหลายเอกสาร</p>
<ol>
<li><b>ระดับเคส:</b> โมเดลอ้างอิงตามหลัก P2P คือ สร้างใบขอซื้อ → อนุมัติ → RFQ → (สร้าง/อนุมัติ PO หลายใบได้) → (รับของ/ใบแจ้งหนี้/จับคู่ หลายรอบได้) → <b>จ่ายเงินครั้งเดียวเป็นขั้นสุดท้าย</b>
ตรวจด้วย token-based replay และ alignments กับทุกเคส ({N} เคส ใช้เวลา {C['alignment_runtime_s']} วินาที จึงไม่ต้องสุ่มตัวอย่าง)</li>
<li><b>ระดับเอกสาร:</b> กฎธุรกิจที่ตรวจทีละเอกสาร เช่น PO ต้องอนุมัติก่อนรับของ และจ่ายเงินครั้งเดียวต่อใบแจ้งหนี้</li>
</ol>
<div class="two">
<table><tr><th>ผลระดับเคส</th><th class=num>ค่า</th></tr>
<tr><td>เคสที่ตรงโมเดลอ้างอิง (alignment fitness = 1)</td><td class=num>{C['alignment_perfect_pct']}%</td></tr>
<tr><td>Token-replay: เคสที่ fit</td><td class=num>{C['tbr_fitting_traces_pct']}%</td></tr>
<tr><td>Log fitness (token replay)</td><td class=num>{C['tbr_log_fitness']}</td></tr>
<tr><td>ค่าเฉลี่ย alignment fitness</td><td class=num>{C['alignment_mean_fitness']}</td></tr></table>
<table><tr><th>ความเบี่ยงที่ alignment พบ</th><th class=num>เคส</th></tr>
{''.join(f"<tr><td>{'ข้าม' if m['type'].startswith('skipped') else 'เกิน/ผิดที่'}: {m['activity']}</td><td class=num>{m['cases']}</td></tr>" for m in C['alignment_moves'])}</table>
</div>
<p>ผลการตรวจทั้ง 2 ชั้นตรงกันทุกเคส: เคสที่ alignment สมบูรณ์คือเคสที่ไม่ผิดกฎข้อใดเลย ({C['alignment_vs_rules'].get('(True, True)',0)} เคส)
และเคสที่ผิดกฎคือเคสที่ alignment ไม่สมบูรณ์ ({C['alignment_vs_rules'].get('(False, False)',0)} เคส)</p>

<h3>4.1 กฎที่ถูกละเมิด</h3>
<table><tr><th>รหัส</th><th>กฎ</th><th class=num>เอกสาร</th><th class=num>เคส</th><th class=num>% เคส</th></tr>{rules_rows}</table>
{fig('03_rule_violations.png','รูป 4 · สัดส่วนเคสที่ละเมิดกฎแต่ละข้อ (เคสหนึ่งละเมิดได้หลายข้อ)','78%')}
<p>กฎที่<b>ไม่มีการละเมิดเลย</b>ก็เป็นข้อค้นพบเช่นกัน: ไม่มี PO ที่อนุมัติก่อนสร้าง ไม่มีการรับของก่อนอนุมัติ PO ไม่มีใบแจ้งหนี้ก่อนรับของ และ<b>ไม่มีการจ่ายเงินก่อนรับของครั้งแรก</b>
คำตอบของคำถาม "จ่ายเงินก่อนรับของหรือไม่" จึงเป็น "ไม่ แต่มีการจ่ายก่อนรับของ<b>ครบ</b>" (C5)</p>

<h3>4.2 รายละเอียดแต่ละประเด็น</h3>
<p><b>A1 · เริ่มจัดซื้อโดยไม่มีใบขอซื้อ ({rule['A1']['cases']} เคส).</b> เคสเริ่มที่ <code>Create Request for Quotation</code> ไม่มีการสร้างหรืออนุมัติใบขอซื้อ
แต่ข้อมูลสถานะของใบขอซื้อทั้ง {C['pr_release_indicator_by_group']['Released']['no PR created']} ใบยังเป็น <code>Released</code>
<span class="hyp">ข้อสันนิษฐาน: ใบขอซื้อถูกปลดล็อกโดยไม่ผ่าน workflow อนุมัติ หรือเป็นการซื้อนอกขั้นตอน (maverick buying)</span></p>
<p><b>A2 · ส่งต่อการอนุมัติแต่ไม่มีบันทึกการอนุมัติ ({rule['A2']['cases']} เคส).</b> ใบขอซื้อถูก delegate โดยเฉลี่ยไม่ถึงวันหลังสร้าง
(มัธยฐาน {st['1b PR created -> approval delegated']['median']} วัน) แล้วไปขั้น RFQ ต่อเลย โดยไม่มี event อนุมัติจากผู้รับมอบ
<span class="hyp">ข้อสันนิษฐาน: ระบบไม่บันทึกการอนุมัติของผู้รับมอบ หรือการ delegate ถูกใช้เป็นทางลัดข้ามการอนุมัติ</span></p>
<p><b>D1 · สั่งจ่ายเงินซ้ำ ({C['D1_payments']} payment).</b> payment เดิมถูกสั่งจ่าย 2–{pay_max} ครั้ง รวม {C['D1_extra_executions']} ครั้งที่เกินมา ห่างกันมัธยฐาน {C['D1_days_between_executions']['50%']} วัน
ทุกครั้งอ้างใบรับของชุดเดิม ({C['D1_same_goods_receipts_every_time']} จาก {C['D1_payments']}) และยอดของ payment เท่ากับยอดใบแจ้งหนี้ทุกใบ ({C['payment_amount_equals_invoice_pct']}%)
ถ้าทุกครั้งจ่ายยอดเต็ม เงินที่จ่ายเกินจะเป็น <b>เพดานบน</b> {C['D1_exposure_pct_of_invoiced']}% ของยอดใบแจ้งหนี้ทั้งหมด
แต่ข้อมูลไม่มียอดเงินของการจ่ายแต่ละครั้ง ({C['payment_change_rows_with_amount_value']} แถวที่มียอด) จึงยืนยันไม่ได้ว่าเป็นการจ่ายเกินหรือจ่ายเป็นงวด</p>
<p><b>C5 · จ่ายเงินให้ PO ก่อนรับของครบ ({rule['C5']['documents']} PO).</b> มีการรับของ {C['C5_postings_after_payment']} ครั้งหลังจาก PO นั้นถูกจ่ายเงินไปแล้ว (มัธยฐาน {C['C5_days_after_payment']['50%']} วันหลังจ่าย)
ระบบบันทึกการจับคู่เป็น <code>Perform Two-Way Match</code> ทั้งหมด ({n(C['two_way_match_events'])} ครั้ง) ไม่มี three-way match ทั้งที่ใบแจ้งหนี้ทุกใบมีใบรับของ
<span class="hyp">ข้อสันนิษฐาน: การจับคู่เทียบแค่ PO กับใบแจ้งหนี้ ไม่ได้เทียบจำนวนที่รับจริง จึงจ่ายได้ก่อนรับของครบ</span></p>

<h2 class="page">5. คอขวดและการทำซ้ำ</h2>
<p>ระยะเวลาทั้งเคส: มัธยฐาน <b>{P['case_duration_days']['median']:.1f} วัน</b>, เฉลี่ย {P['case_duration_days']['mean']:.1f} วัน, เปอร์เซ็นไทล์ที่ 90 อยู่ที่ {P['case_duration_days']['p90']:.1f} วัน และนานสุด {P['case_duration_days']['max']:.1f} วัน
เวลารอระหว่างขั้นวัดบน<b>เอกสารใบเดียวกัน</b>เท่านั้น เพื่อไม่ให้ปนกับเวลาระหว่างเอกสารคนละใบ</p>
<table><tr><th>ขั้น (เอกสารเดียวกัน)</th><th class=num>n</th><th class=num>มัธยฐาน (วัน)</th><th class=num>เฉลี่ย</th><th class=num>P90</th></tr>{stage_rows}</table>
{fig('04_stage_waits.png','รูป 5 · เวลารอระหว่างขั้น: แท่ง = มัธยฐาน, จุด = เปอร์เซ็นไทล์ที่ 90','80%')}
<div class="callout"><b class="t">ไม่มีคอขวดเดียว แต่มีการรอหลายทอด</b>
<p>ขั้นที่รอนานที่สุดคือ <b>{P['longest_stage_by_median'][2:]}</b> (มัธยฐาน {P['longest_stage_median_days']:.2f} วัน) ซึ่งเป็นช่วงรอผู้ขายส่งของ
แต่ขั้นอื่นอีกหลายขั้นก็รอใกล้เคียงกันที่ {other_lo:.1f}–{other_hi:.1f} วัน เมื่อรวมค่ามัธยฐาน ขั้นที่องค์กรควบคุมได้เอง (อนุมัติ, ส่งต่องาน, การเงิน) คิดเป็น <b>{P['internal_share_of_stage_medians_pct']}%</b>
({P['sum_of_stage_medians_by_group']['internal']} จาก {P['sum_of_stage_medians_by_group']['internal']+P['sum_of_stage_medians_by_group']['external']:.2f} วัน)
<span class="small">ผลรวมค่ามัธยฐานใช้ดูสัดส่วนคร่าวๆ เท่านั้น ไม่เท่ากับเวลาทั้งเคส เพราะเอกสารหลายใบทำคู่ขนานกัน</span></p></div>

<h3>5.1 แยกตามกลุ่ม</h3>
<table><tr><th>กลุ่ม</th><th class=num>เคส</th><th class=num>มัธยฐานทั้งเคส (วัน)</th></tr>
{''.join(f"<tr><td>เส้นทาง: {k}</td><td class=num>{v['cases']}</td><td class=num>{v['median']:.1f}</td></tr>" for k,v in dur.items())}
<tr><td>จ่ายเงินครั้งเดียว</td><td class=num>{rp['False']['cases']}</td><td class=num>{rp['False']['median']:.1f}</td></tr>
<tr><td>มีการสั่งจ่ายซ้ำ</td><td class=num>{rp['True']['cases']}</td><td class=num>{rp['True']['median']:.1f}</td></tr>
{''.join(f"<tr><td>กลุ่มจัดซื้อ {k}</td><td class=num>{v['cases']}</td><td class=num>{v['median']:.1f}</td></tr>" for k,v in pg.items())}
</table>
<ul>
<li>เคสที่<b>ไม่มีใบขอซื้อ</b>เร็วกว่าเคสปกติ ({dur['no PR created']['median']:.1f} vs {dur['PR approved']['median']:.1f} วัน) ส่วนต่างพอๆ กับเวลาของขั้นอนุมัติและส่งต่อใบขอซื้อ
<span class="hyp">อาจเป็นแรงจูงใจให้ข้ามขั้นตอน</span></li>
<li>เคสที่<b>สั่งจ่ายซ้ำ</b>จบช้ากว่า ({rp['True']['median']:.1f} vs {rp['False']['median']:.1f} วัน)</li>
<li>จำนวนเอกสารมีผลบ้าง: ความสัมพันธ์ (Spearman) ระหว่างระยะเวลากับจำนวนใบรับของคือ {P['corr_duration_vs_GRs']} และกับจำนวน PO คือ {P['corr_duration_vs_POs']}</li>
<li>กลุ่มจัดซื้อ วิธีจ่ายเงิน และผู้ขายต่างกันไม่มาก (มัธยฐานของผู้ขายที่มี 10 เคสขึ้นไปอยู่ระหว่าง {P['vendor_duration_median_range'][0]:.1f}–{P['vendor_duration_median_range'][1]:.1f} วัน)
<span class="hyp">การกระจายที่สม่ำเสมอแบบนี้น่าจะเป็นลักษณะของข้อมูลจำลอง</span></li>
</ul>

<h3>5.2 การทำซ้ำ (rework)</h3>
<p>activity ที่เกิดซ้ำในเคสส่วนใหญ่<b>ไม่ใช่ rework</b> แต่เป็นเพราะเคสมีเอกสารหลายใบ เช่น เคสที่มี PO หลายใบมี <code>Create Purchase Order</code> หลายครั้ง
ต้องแยกโดยดูว่า activity ซ้ำบน<b>เอกสารใบเดิม</b>หรือไม่</p>
<table><tr><th>Activity</th><th class=num>เคสที่มีซ้ำ</th><th class=num>เพราะหลายเอกสาร</th><th class=num>ซ้ำบนเอกสารเดิม</th></tr>
{''.join(f"<tr><td>{a}</td><td class=num>{r['cases_with_repeat']}</td><td class=num>{r['cases_repeat_only_from_multiple_documents']}</td><td class=num>{r['cases_with_repeat_on_same_document']}</td></tr>" for a,r in rw.items() if r['cases_with_repeat'])}
</table>
<ul>
<li><code>Create Goods Receipt</code> ซ้ำบนใบรับของเดียวกัน {n(rw['Create Goods Receipt']['documents_with_repeat'])} ใบ แต่ทุกครั้ง ({P['gr_postings_each_reference_different_po_pct']}%) อ้าง PO คนละใบ
จึงเป็นใบรับของที่รวมของจากหลาย PO <b>ไม่ใช่ rework</b></li>
<li>rework จริงมีอย่างเดียวคือ <code>Execute Payment</code> ซ้ำบน payment เดิม ({rw['Execute Payment']['documents_with_repeat']} payment, เกินมา {rw['Execute Payment']['extra_events_on_same_document']} ครั้ง) ซึ่งคือประเด็น D1</li>
</ul>

<h2 class="page">6. ข้อเสนอแนะ</h2>
<table><tr><th style="width:4%">#</th><th style="width:38%">ปัญหาและหลักฐาน</th><th style="width:24%">ผลกระทบที่น่าจะเกิด</th><th>ข้อเสนอแนะ</th></tr>{issue_rows}</table>
<p>แผนภาพ as-is แบบย่อและ to-be ที่เสนออยู่ในหน้าถัดไป (รูป 6–7)</p>
<div class="wide">{fig('05_asis_annotated_tb.png','รูป 6 · As-is แบบย่อ พร้อมจุดที่เบี่ยง (สีแดง)')}{fig('05_tobe_tb.png','รูป 7 · To-be ที่เสนอ แยกตามผู้รับผิดชอบ สีเขียว = control ใหม่ ป้าย [P1–P5] โยงกับปัญหา')}</div>
<h3 class="page">ลำดับการดำเนินการที่แนะนำ</h3>
<ol>
<li><b>ทันที (P3):</b> ให้การเงินตรวจ {C['D1_payments']} payment ที่สั่งจ่ายซ้ำ ยืนยันว่ามีการจ่ายเกินหรือไม่ แล้วเปิดใช้การตรวจจ่ายซ้ำในรอบจ่ายเงิน</li>
<li><b>ระยะสั้น (P1, P2):</b> บังคับให้ RFQ อ้างใบขอซื้อที่อนุมัติแล้ว และให้การ delegate ต้องมีการอนุมัติของผู้รับมอบ ทำรายงานรายสัปดาห์ของรายการที่ไม่ผ่าน</li>
<li><b>ระยะกลาง (P4):</b> เปลี่ยนการจับคู่เป็น three-way match และจ่ายตามจำนวนที่รับจริง</li>
<li><b>ต่อเนื่อง (P5):</b> กำหนดเพดานมูลค่าสำหรับอนุมัติอัตโนมัติ สร้าง RFQ อัตโนมัติเมื่อปลดล็อกใบขอซื้อ แล้ววัดผลด้วยตัวชี้วัดในข้อถัดไป</li>
</ol>
<h3>ตัวชี้วัดที่ควรติดตามหลังปรับ</h3>
<table><tr><th>ตัวชี้วัด</th><th class=num>ค่าปัจจุบัน (baseline)</th></tr>
<tr><td>% เคสที่ตรงกระบวนการอ้างอิง</td><td class=num>{C['cases_fully_compliant_pct']}%</td></tr>
<tr><td>% เคสที่เริ่มโดยไม่มีใบขอซื้อ</td><td class=num>{rule['A1']['cases_pct']}%</td></tr>
<tr><td>% เคสที่มีการสั่งจ่ายซ้ำ</td><td class=num>{rule['D1']['cases_pct']}%</td></tr>
<tr><td>% เคสที่จ่ายก่อนรับของครบ</td><td class=num>{rule['C5']['cases_pct']}%</td></tr>
<tr><td>มัธยฐานเวลาทั้งเคส (วัน)</td><td class=num>{P['case_duration_days']['median']:.1f}</td></tr>
</table>

<h2>7. ข้อจำกัดของการวิเคราะห์</h2>
<ul>
<li><b>ข้อมูลจำลอง:</b> ทุกเคสจบที่การจ่ายเงิน ไม่มีเคสค้าง กลุ่มต่างๆ แทบไม่ต่างกัน และเส้นทางหลักมีแค่ {D['variants_skeleton']} แบบ ข้อมูลจริงมักซับซ้อนกว่านี้มาก ผลจึงใช้แสดงวิธีการ ไม่ใช่ข้อสรุปเกี่ยวกับบริษัทจริง</li>
<li><b>Log บอกว่าอะไรเกิด แต่ไม่บอกว่าทำไม:</b> สาเหตุทุกข้อในรายงานเป็นข้อสันนิษฐาน ต้องสัมภาษณ์เจ้าของกระบวนการเพื่อยืนยัน</li>
<li><b>ยอดเงินรายครั้ง:</b> ไม่มียอดเงินของการจ่ายแต่ละครั้ง จึงประเมินการจ่ายเกินได้แค่เพดานบน</li>
<li><b>Timestamp:</b> ละเอียดแค่ระดับนาที และอาจเป็นเวลาที่บันทึกในระบบ ไม่ใช่เวลาที่ทำงานจริง</li>
<li><b>ความสัมพันธ์ระหว่างเอกสาร:</b> มีลิงก์ที่ชี้ไปหาเอกสารที่ไม่มีอยู่ ({n(E['dangling_object_links_total'])} ลิงก์) จึงใช้ความสัมพันธ์จาก event แทน</li>
<li><b>วันส่งของตามสัญญา:</b> ไม่มีข้อมูลที่เชื่อถือได้ จึงวัดการส่งของตรงเวลาของผู้ขายไม่ได้</li>
<li><b>ข้อเสนอแนะยังไม่ได้นำไปใช้:</b> จึงไม่มีตัวเลขผลลัพธ์หลังปรับ</li>
</ul>

<h2>ภาคผนวก: ที่มาของข้อมูลและการทำซ้ำ</h2>
<p class="small">ข้อมูล: <i>Procure-To-Payment (P2P) Object-centric Event Log in OCEL 2.0 Standard</i>, Zenodo record 8412920, CC BY 4.0, ไฟล์ <code>ocel2-p2p.sqlite</code> MD5 <code>{E['file_md5']}</code>.
ชุดที่วางแผนไว้แต่แรกคือ BPI Challenge 2019 (4TU.ResearchData) แต่ไฟล์ปิดให้ดาวน์โหลดชั่วคราวช่วงที่ทำงาน
เครื่องมือ: PM4Py {E['pm4py_version']} (AGPL v3), pandas, matplotlib, Graphviz.
ทำซ้ำได้โดยรัน notebook 01–05 ตามลำดับ แล้วรัน <code>python report/build_report.py</code>.
ตัวเลขทุกตัวในรายงานนี้อยู่ใน <code>results.md</code> พร้อมชื่อ notebook ที่คำนวณ</p>
</body></html>"""

out = ROOT / "report" / "p2p_process_mining_report.html"
out.write_text(html, encoding="utf-8")
print("wrote", out)

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg_ = b.new_page()
        pg_.goto(out.as_uri())
        pg_.wait_for_load_state("networkidle")
        pg_.evaluate("document.fonts.ready")
        pdf = out.with_suffix(".pdf")
        pg_.pdf(path=str(pdf), format="A4", print_background=True, display_header_footer=True,
                header_template="<span></span>",
                footer_template="<div style='font-size:8px;width:100%;text-align:right;padding-right:17mm;color:#888'><span class='pageNumber'></span> / <span class='totalPages'></span></div>",
                margin={"top": "16mm", "bottom": "16mm", "left": "17mm", "right": "17mm"})
        b.close()
    print("wrote", pdf)
except ImportError:
    print("playwright not installed; open the HTML and print to PDF")
