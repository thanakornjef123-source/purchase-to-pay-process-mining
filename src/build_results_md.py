"""Write results.md from results/*.json (every number with the notebook that computed it).

    python src/build_results_md.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
J = lambda n: json.loads((ROOT / "results" / n).read_text())
E, D, C, P, S = (J("01_explore.json"), J("02_discovery.json"), J("03_conformance.json"),
                 J("04_performance.json"), J("05_recommendations.json"))
B = J("06_bpi2019.json")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


L = []
a = L.append
a("# results.md — ตัวเลขทั้งหมดของโปรเจกต์\n")
a("ไฟล์นี้สร้างอัตโนมัติจาก `results/*.json` ด้วย `python src/build_results_md.py` ตัวเลขทุกตัวมาจากโค้ดที่รันจริง และระบุ notebook ที่คำนวณ")
a(f"ข้อมูล: P2P OCEL 2.0 (Zenodo 8412920, CC BY 4.0) **ข้อมูลจำลอง** ไม่ใช่ log จริงของบริษัท · `ocel2-p2p.sqlite` MD5 `{E['file_md5']}`\n")

a("## ช่วง 2 — สำรวจข้อมูล · `notebooks/01_explore.ipynb` → `results/01_explore.json`\n")
a(table(["รายการ", "ค่า"], [
    ["Events", f"{E['n_events']:,}"], ["Objects (ตาราง object)", f"{E['n_objects']:,}"],
    [f"Objects ที่ PM4Py {E['pm4py_version']} โหลด", f"{E['pm4py_n_objects']:,} (ตัด material ที่ไม่มี event {E['objects_without_events_total']})"],
    ["Activities / object types", f"{E['n_activities']} / {E['n_object_types']}"],
    ["ลิงก์ event→object / object→object", f"{E['n_event_object_links']:,} / {E['n_object_object_links']:,}"],
    ["ลิงก์ object→object ที่ชี้ไปหา object ที่ไม่มีอยู่", f"{E['dangling_object_links_total']:,}"],
    ["ช่วงเวลา", f"{E['time_min'][:16]} ถึง {E['time_max'][:16]} UTC ({E['time_span_days']} วัน)"],
    ["ค่าว่างใน event", sum(E['event_nulls'].values())],
    ["Events ที่มี timestamp ตรงกับ event อื่น", f"{E['events_sharing_timestamp']:,} ({E['share_events_sharing_timestamp_pct']}%)"],
    ["Invoice ที่มี event หลายตัวในเวลาเดียวกัน (Two-Way Match ซ้ำ)", sum(E['invoice_tie_patterns'].values())],
    ["Payments ที่มี Execute Payment > 1 ครั้ง", f"{E['payments_executed_more_than_once']} ({E['payment_events_total']:,} events)"],
    ["จำนวนเคส (1 เคส = 1 PR)", E['case_count']],
    ["Events ที่อยู่หลายเคส / ไม่อยู่ในเคสใด", f"{E['events_mapped_to_multiple_cases']} / {E['events_not_mapped']}"],
    ["Events ต่อเคส (เฉลี่ย / มัธยฐาน / ต่ำสุด / สูงสุด)", f"{E['events_per_case']['mean']} / {E['events_per_case']['50%']:.0f} / {E['events_per_case']['min']:.0f} / {E['events_per_case']['max']:.0f}"],
    ["ระยะเวลาเคส (วัน; เฉลี่ย / มัธยฐาน / สูงสุด)", f"{E['case_duration_days']['mean']} / {E['case_duration_days']['50%']} / {E['case_duration_days']['max']}"],
]))
a("\nEvents ต่อ activity\n")
a(table(["Activity", "Events"], [[k, f"{v:,}"] for k, v in E['events_per_activity'].items()]))
a("\nรูปแบบ activity ของ PR\n")
a(table(["รูปแบบ", "PRs"], [[k, v] for k, v in E['pr_activity_patterns'].items()]))

a("\n## ช่วง 3 — ค้นพบกระบวนการ · `notebooks/02_discovery.ipynb` → `results/02_discovery.json`\n")
q = D['discovered_model_quality']['full log, noise 0.2']
a(table(["รายการ", "ค่า"], [
    ["Variants (เต็ม)", f"{D['variants_full']} (เกิดครั้งเดียว {D['variants_full_singletons']})"],
    ["Variants (รวมขั้นซ้ำที่ติดกัน)", D['variants_collapsed']],
    ["Variants (skeleton: ลำดับครั้งแรก)", D['variants_skeleton']],
    ["Variant อันดับ 1 / top 5 / top 10 ครอบคลุม", f"{D['top1_coverage_pct']}% / {D['top5_coverage_pct']}% / {D['top10_coverage_pct']}%"],
    ["Variants ที่ต้องใช้ให้ครอบคลุม 50% / 80%", f"{D['variants_needed_for_50pct']} / {D['variants_needed_for_80pct']}"],
    ["เคสที่มี 1 PO 1 GR / variants ในกลุ่มนี้", f"{D['cases_single_po_single_gr']} / {D['variants_in_single_po_single_gr']}"],
    ["จุดเริ่ม", ", ".join(f"{k}: {v}" for k, v in D['start_activities'].items())],
    ["จุดจบ", ", ".join(f"{k}: {v}" for k, v in D['end_activities'].items())],
    ["Inductive Miner: top-k vs noise 0.2 ได้ tree เดียวกัน", D['trees_identical']],
    ["โมเดลที่ค้นพบ: fitting traces / log fitness / precision", f"{q['fitting_traces_pct']}% / {q['log_fitness']} / {q['precision']}"],
]))
a("\nSkeleton variants\n")
a(table(["เส้นทาง", "เคส"], [[k, v] for k, v in D['skeleton_variants'].items()]))

a("\n## ช่วง 4 — Conformance · `notebooks/03_conformance.ipynb` → `results/03_conformance.json`\n")
a(f"โมเดลอ้างอิง: `{C['reference_tree']}`\n")
a(table(["รายการ", "ค่า"], [
    ["Token replay: fitting traces / log fitness / precision", f"{C['tbr_fitting_traces_pct']}% / {C['tbr_log_fitness']} / {C['tbr_precision']}"],
    ["Alignments: เคสที่ตรวจ / fitness = 1", f"{C['alignment_cases']} / {C['alignment_perfect_cases']} ({C['alignment_perfect_pct']}%)"],
    ["Alignment fitness เฉลี่ย", C['alignment_mean_fitness']],
    ["เคสที่ไม่ผิดกฎเลย", f"{C['cases_fully_compliant']} ({C['cases_fully_compliant_pct']}%)"],
    ["เคสที่ผิดกฎอย่างน้อย 1 ข้อ", f"{C['cases_with_any_rule_violation']} ({C['cases_with_any_rule_violation_pct']}%)"],
    ["จำนวนกฎที่ผิดต่อเคส", ", ".join(f"{k} ข้อ: {v}" for k, v in C['rules_broken_per_case'].items())],
    ["D1 extra executions / ห่างกันมัธยฐาน (วัน)", f"{C['D1_extra_executions']} / {C['D1_days_between_executions']['50%']}"],
    ["D1 อ้างใบรับของชุดเดิมทุกครั้ง", f"{C['D1_same_goods_receipts_every_time']} จาก {C['D1_payments']}"],
    ["ยอด payment = ยอด invoice", f"{C['payment_amount_equals_invoice_pct']}%"],
    ["D1 เพดานบน exposure (ถ้าจ่ายยอดเต็มทุกครั้ง)", f"{C['D1_exposure_if_full_amount_each_time']:,.0f} ({C['D1_exposure_pct_of_invoiced']}% ของยอด invoice {C['total_invoice_amount']:,.0f})"],
    ["แถวการเปลี่ยนแปลงของ payment ที่มียอดเงิน", C['payment_change_rows_with_amount_value']],
    ["C5 การรับของหลังจ่าย / ห่างจากการจ่ายมัธยฐาน (วัน)", f"{C['C5_postings_after_payment']} / {C['C5_days_after_payment']['50%']}"],
    ["Two-way match / three-way match events", f"{C['two_way_match_events']:,} / {C['three_way_match_events']}"],
]))
a("\nAlignment moves\n")
a(table(["ประเภท", "Activity", "moves", "เคส", "% เคส"], [[m['type'], m['activity'], m['moves'], m['cases'], m['cases_pct']] for m in C['alignment_moves']]))
a("\nกฎธุรกิจระดับเอกสาร\n")
a(table(["กฎ", "ชนิด", "เอกสาร", "เคส", "% เคส", "ตัวอย่างเอกสาร"],
        [[r['rule'], r['kind'], r['documents'], r['cases'], r['cases_pct'], r['example_document']] for r in C['rules']]))

a("\n## ช่วง 5 — Performance · `notebooks/04_performance.ipynb` → `results/04_performance.json`\n")
cd = P['case_duration_days']
a(f"ระยะเวลาทั้งเคส (วัน): มัธยฐาน {cd['median']}, เฉลี่ย {cd['mean']}, P90 {cd['p90']}, สูงสุด {cd['max']}\n")
a(table(["ขั้น (เอกสารเดียวกัน)", "n", "มัธยฐาน", "เฉลี่ย", "P90", "สูงสุด"],
        [[k, int(v['n']), v['median'], v['mean'], v['p90'], v['max']] for k, v in P['stage_wait_days'].items()]))
a("")
a(table(["รายการ", "ค่า"], [
    ["ขั้นที่รอนานสุด (มัธยฐาน)", f"{P['longest_stage_by_median']} ({P['longest_stage_median_days']} วัน)"],
    ["ผลรวมค่ามัธยฐานรายขั้น: ภายใน / ภายนอก (วัน)", f"{P['sum_of_stage_medians_by_group']['internal']} / {P['sum_of_stage_medians_by_group']['external']}"],
    ["สัดส่วนขั้นภายใน", f"{P['internal_share_of_stage_medians_pct']}%"],
    ["Spearman: ระยะเวลา vs จำนวน PO / GR", f"{P['corr_duration_vs_POs']} / {P['corr_duration_vs_GRs']}"],
    ["มัธยฐานเคสที่จ่ายซ้ำ / จ่ายครั้งเดียว (วัน)", f"{P['duration_median_repeated_payment']} / {P['duration_median_single_payment']}"],
    ["ผู้ขายที่มี ≥10 เคส: ช่วงมัธยฐาน (วัน)", f"{P['vendor_duration_median_range'][0]}–{P['vendor_duration_median_range'][1]} ({P['vendors_with_10plus_cases']} ราย)"],
    ["ใบรับของที่บันทึกซ้ำ ทุกครั้งอ้าง PO คนละใบ", f"{P['gr_postings_each_reference_different_po_pct']}%"],
]))
a("\nมัธยฐานระยะเวลาเคสตามกลุ่ม\n")
rows = []
for grp, recs in P['duration_by_group'].items():
    for r in recs:
        key = [k for k in r if k not in ('cases', 'median', 'mean', 'p90')][0]
        rows.append([grp, r[key], r['cases'], r['median'], r['p90']])
a(table(["มิติ", "กลุ่ม", "เคส", "มัธยฐาน", "P90"], rows))
a("\nการทำซ้ำ\n")
a(table(["Activity", "เคสที่มีซ้ำ", "เพราะหลายเอกสาร", "ซ้ำบนเอกสารเดิม", "event เกินบนเอกสารเดิม"],
        [[r['activity'], r['cases_with_repeat'], r['cases_repeat_only_from_multiple_documents'], r['cases_with_repeat_on_same_document'], r['extra_events_on_same_document']] for r in P['rework']]))

a("\n## ช่วง 6 — ข้อเสนอแนะ · `notebooks/05_recommendations.ipynb` → `results/05_recommendations.json`\n")
a(table(["#", "ปัญหา", "หลักฐาน"], [[i['id'], i['issue'], i['evidence']] for i in S['issues']]))
a("")

a("\n## ต่อยอด — ข้อมูลจริง BPI Challenge 2019 · `notebooks/06_bpi2019_real_data.ipynb` → `results/06_bpi2019.json`\n")
a("ข้อมูล: BPI Challenge 2019, DOI 10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1, CC BY 4.0 · `BPI_Challenge_2019.xes` MD5 `4eb909242351193a61e1c15b9c3cc814`\n")
a(table(["รายการ", "ค่า"], [
    ["Cases (PO items) / events / activities", f"{B['cases']:,} / {B['events']:,} / {B['activities']}"],
    ["Purchase documents / vendors / companies", f"{B['purchase_documents']:,} / {B['vendors']:,} / {B['companies']}"],
    ["Events before 2018 / cases affected", f"{B['events_before_2018']} / {B['cases_with_events_before_2018']}"],
    ["Variants (singletons)", f"{B['variants']:,} ({B['variants_singletons']:,})"],
    ["Variants for 50% / 80% of cases", f"{B['variants_needed_for_50pct']} / {B['variants_needed_for_80pct']}"],
    ["Invoice before GR in invoice-before-GR category", f"{B['ibgr_invoice_before_gr_cases']:,} ({B['ibgr_invoice_before_gr_pct']}%)"],
    ["Cases with Remove Payment Block", f"{B['remove_payment_block_cases_pct']}%"],
    ["Open cases (no Clear Invoice) in invoiced categories", f"{B['open_cases_pct_of_invoiced_categories']}%"],
    ["Cases with a purchase requisition item", f"{B['cases_with_purchase_requisition_pct']}%"],
    ["Cases with any change/cancel (excl. payment block)", f"{B['cases_with_any_change_or_cancel_pct']}%"],
    ["Invoice → clear median days, with / without block removal", f"{B['invoice_to_clear_median_with_block_removal']} / {B['invoice_to_clear_median_without_block_removal']}"],
]))
a("\nItem categories\n")
a(table(["Category", "Cases", "%"], [[k, f"{v:,}", B['item_category_pct'][k]] for k, v in B['item_category_cases'].items()]))
a("\nRules\n")
a(table(["Rule", "Cases", "% of category", "Category cases"], [[r['rule'], f"{r['cases']:,}", r['pct_of_category'], f"{r['category_cases']:,}"] for r in B['rules']]))
a("\nStage durations (days, cases with timestamps before 2018 excluded)\n")
a(table(["Stage", "n", "median", "mean", "P90"], [[k, f"{v['n']:,}", v['median'], v['mean'], v['p90']] for k, v in B['stage_days'].items()]))
a("\nRework\n")
a(table(["Activity", "Cases", "% of cases"], [[r['activity'], f"{r['cases']:,}", r['pct_cases']] for r in B['rework']]))
a("\nComparison\n")
a(table(["Metric", "Simulated (Zenodo P2P)", "Real (BPI 2019)"], [[r['metric'], r['simulated (Zenodo P2P)'], r['real (BPI 2019)']] for r in B['comparison']]))
a("")
(ROOT / "results.md").write_text("\n".join(L), encoding="utf-8")
print("wrote results.md", len(L), "blocks")
