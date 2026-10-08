# results.md — ตัวเลขทั้งหมดของโปรเจกต์

ไฟล์นี้สร้างอัตโนมัติจาก `results/*.json` ด้วย `python src/build_results_md.py` ตัวเลขทุกตัวมาจากโค้ดที่รันจริง และระบุ notebook ที่คำนวณ
ข้อมูล: P2P OCEL 2.0 (Zenodo 8412920, CC BY 4.0) **ข้อมูลจำลอง** ไม่ใช่ log จริงของบริษัท · `ocel2-p2p.sqlite` MD5 `1a4238260019939239488b0b4befb515`

## ช่วง 2 — สำรวจข้อมูล · `notebooks/01_explore.ipynb` → `results/01_explore.json`

| รายการ | ค่า |
|---|---|
| Events | 14,671 |
| Objects (ตาราง object) | 9,543 |
| Objects ที่ PM4Py 2.7.23.8 โหลด | 9,054 (ตัด material ที่ไม่มี event 489) |
| Activities / object types | 10 / 7 |
| ลิงก์ event→object / object→object | 35,927 / 20,402 |
| ลิงก์ object→object ที่ชี้ไปหา object ที่ไม่มีอยู่ | 2,028 |
| ช่วงเวลา | 2022-04-01 09:26 ถึง 2024-10-31 20:28 UTC (944 วัน) |
| ค่าว่างใน event | 0 |
| Events ที่มี timestamp ตรงกับ event อื่น | 1,223 (8.34%) |
| Invoice ที่มี event หลายตัวในเวลาเดียวกัน (Two-Way Match ซ้ำ) | 242 |
| Payments ที่มี Execute Payment > 1 ครั้ง | 188 (1,166 events) |
| จำนวนเคส (1 เคส = 1 PR) | 927 |
| Events ที่อยู่หลายเคส / ไม่อยู่ในเคสใด | 0 / 0 |
| Events ต่อเคส (เฉลี่ย / มัธยฐาน / ต่ำสุด / สูงสุด) | 15.83 / 14 / 7 / 38 |
| ระยะเวลาเคส (วัน; เฉลี่ย / มัธยฐาน / สูงสุด) | 22.5 / 21.7 / 66.0 |

Events ต่อ activity

| Activity | Events |
|---|---|
| Create Goods Receipt | 4,042 |
| Create Invoice Receipt | 1,941 |
| Perform Two-Way Match | 1,941 |
| Approve Purchase Order | 1,598 |
| Create Purchase Order | 1,598 |
| Execute Payment | 1,166 |
| Create Request for Quotation | 927 |
| Create Purchase Requisition | 729 |
| Approve Purchase Requisition | 607 |
| Delegate Purchase Requisition Approval | 122 |

รูปแบบ activity ของ PR

| รูปแบบ | PRs |
|---|---|
| Approve Purchase Requisition + Create Purchase Requisition + Create Request for Quotation | 607 |
| Create Request for Quotation | 198 |
| Create Purchase Requisition + Create Request for Quotation + Delegate Purchase Requisition Approval | 122 |

## ช่วง 3 — ค้นพบกระบวนการ · `notebooks/02_discovery.ipynb` → `results/02_discovery.json`

| รายการ | ค่า |
|---|---|
| Variants (เต็ม) | 388 (เกิดครั้งเดียว 330) |
| Variants (รวมขั้นซ้ำที่ติดกัน) | 247 |
| Variants (skeleton: ลำดับครั้งแรก) | 3 |
| Variant อันดับ 1 / top 5 / top 10 ครอบคลุม | 19.5% / 37.4% / 44.8% |
| Variants ที่ต้องใช้ให้ครอบคลุม 50% / 80% | 15 / 203 |
| เคสที่มี 1 PO 1 GR / variants ในกลุ่มนี้ | 345 / 11 |
| จุดเริ่ม | Create Purchase Requisition: 729, Create Request for Quotation: 198 |
| จุดจบ | Execute Payment: 786, Create Goods Receipt: 141 |
| Inductive Miner: top-k vs noise 0.2 ได้ tree เดียวกัน | True |
| โมเดลที่ค้นพบ: fitting traces / log fitness / precision | 87.8% / 0.996 / 0.612 |

Skeleton variants

| เส้นทาง | เคส |
|---|---|
| Create PR > Approve PR > Create RFQ > Create PO > Approve PO > Create GR > Create Invoice > Two-Way Match > Execute Payment | 607 |
| Create RFQ > Create PO > Approve PO > Create GR > Create Invoice > Two-Way Match > Execute Payment | 198 |
| Create PR > Delegate PR Approval > Create RFQ > Create PO > Approve PO > Create GR > Create Invoice > Two-Way Match > Execute Payment | 122 |

## ช่วง 4 — Conformance · `notebooks/03_conformance.ipynb` → `results/03_conformance.json`

โมเดลอ้างอิง: `->( 'Create Purchase Requisition', 'Approve Purchase Requisition', 'Create Request for Quotation', *( X( 'Create Purchase Order', 'Approve Purchase Order' ), tau ), *( X( 'Create Goods Receipt', 'Create Invoice Receipt', 'Perform Two-Way Match' ), tau ), 'Execute Payment' )`

| รายการ | ค่า |
|---|---|
| Token replay: fitting traces / log fitness / precision | 41.7% / 0.973 / 0.418 |
| Alignments: เคสที่ตรวจ / fitness = 1 | 927 / 387 (41.7%) |
| Alignment fitness เฉลี่ย | 0.944 |
| เคสที่ไม่ผิดกฎเลย | 387 (41.7%) |
| เคสที่ผิดกฎอย่างน้อย 1 ข้อ | 540 (58.3%) |
| จำนวนกฎที่ผิดต่อเคส | 0 ข้อ: 387, 1 ข้อ: 420, 2 ข้อ: 109, 3 ข้อ: 11 |
| D1 extra executions / ห่างกันมัธยฐาน (วัน) | 239 / 2.76 |
| D1 อ้างใบรับของชุดเดิมทุกครั้ง | 188 จาก 188 |
| ยอด payment = ยอด invoice | 100.0% |
| D1 เพดานบน exposure (ถ้าจ่ายยอดเต็มทุกครั้ง) | 15,090,800 (25.7% ของยอด invoice 58,785,600) |
| แถวการเปลี่ยนแปลงของ payment ที่มียอดเงิน | 0 |
| C5 การรับของหลังจ่าย / ห่างจากการจ่ายมัธยฐาน (วัน) | 269 / 2.07 |
| Two-way match / three-way match events | 1,941 / 0 |

Alignment moves

| ประเภท | Activity | moves | เคส | % เคส |
|---|---|---|---|---|
| skipped (model move) | Approve Purchase Requisition | 320 | 320 | 34.5 |
| extra / out of place (log move) | Execute Payment | 264 | 213 | 23.0 |
| skipped (model move) | Create Purchase Requisition | 198 | 198 | 21.4 |
| extra / out of place (log move) | Delegate Purchase Requisition Approval | 122 | 122 | 13.2 |
| extra / out of place (log move) | Create Goods Receipt | 140 | 116 | 12.5 |
| skipped (model move) | Execute Payment | 25 | 25 | 2.7 |

กฎธุรกิจระดับเอกสาร

| กฎ | ชนิด | เอกสาร | เคส | % เคส | ตัวอย่างเอกสาร |
|---|---|---|---|---|---|
| A1 RFQ without a purchase requisition created in the system | rule | 198 | 198 | 21.4 | purchase_requisition:108:pr_trigger_108 |
| A2 PR delegated, approval never recorded | rule | 122 | 122 | 13.2 | purchase_requisition:117:pr_trigger_117 |
| A3 RFQ created before PR approval | rule | 0 | 0 | 0.0 |  |
| B1 PO approved before it was created | rule | 0 | 0 | 0.0 |  |
| B2 goods received before PO approval | rule | 0 | 0 | 0.0 |  |
| B3 PO never approved | rule | 0 | 0 | 0.0 |  |
| C1 invoice before any goods received | rule | 0 | 0 | 0.0 |  |
| C2 match before invoice | rule | 0 | 0 | 0.0 |  |
| C3 payment before invoice matched | rule | 0 | 0 | 0.0 |  |
| C4 payment before any goods received | rule | 0 | 0 | 0.0 |  |
| C5 PO paid before its last goods receipt posting | rule | 234 | 163 | 17.6 | purchase_order:1 |
| D1 payment executed more than once | rule | 188 | 188 | 20.3 | payment:0 |
| C6 invoice before the last posting on its goods receipt document | observation | 683 | 364 | 39.3 | goods receipt:0 |

## ช่วง 5 — Performance · `notebooks/04_performance.ipynb` → `results/04_performance.json`

ระยะเวลาทั้งเคส (วัน): มัธยฐาน 21.75, เฉลี่ย 22.53, P90 32.78, สูงสุด 66.02

| ขั้น (เอกสารเดียวกัน) | n | มัธยฐาน | เฉลี่ย | P90 | สูงสุด |
|---|---|---|---|---|---|
| 1 PR created -> PR approved | 607 | 2.43 | 3.37 | 7.3 | 28.39 |
| 1b PR created -> approval delegated | 122 | 0.06 | 0.32 | 0.68 | 2.73 |
| 2 PR approved -> RFQ | 607 | 2.89 | 3.84 | 7.81 | 26.99 |
| 3 RFQ -> first PO created | 927 | 0.9 | 1.3 | 2.82 | 8.62 |
| 4 PO created -> PO approved | 1598 | 2.83 | 3.64 | 7.81 | 25.34 |
| 5 PO approved -> first goods receipt | 1598 | 3.01 | 3.92 | 8.31 | 25.6 |
| 6 first goods receipt -> invoice | 1941 | 2.41 | 2.82 | 5.58 | 17.46 |
| 7 invoice -> two-way match | 1941 | 0.23 | 0.49 | 1.85 | 2.71 |
| 8 two-way match -> first payment | 1941 | 2.93 | 3.76 | 8.01 | 24.32 |

| รายการ | ค่า |
|---|---|
| ขั้นที่รอนานสุด (มัธยฐาน) | 5 PO approved -> first goods receipt (3.01 วัน) |
| ผลรวมค่ามัธยฐานรายขั้น: ภายใน / ภายนอก (วัน) | 12.21 / 5.42 |
| สัดส่วนขั้นภายใน | 69.3% |
| Spearman: ระยะเวลา vs จำนวน PO / GR | 0.214 / 0.254 |
| มัธยฐานเคสที่จ่ายซ้ำ / จ่ายครั้งเดียว (วัน) | 25.92 / 21.07 |
| ผู้ขายที่มี ≥10 เคส: ช่วงมัธยฐาน (วัน) | 15.96–28.61 (49 ราย) |
| ใบรับของที่บันทึกซ้ำ ทุกครั้งอ้าง PO คนละใบ | 100.0% |

มัธยฐานระยะเวลาเคสตามกลุ่ม

| มิติ | กลุ่ม | เคส | มัธยฐาน | P90 |
|---|---|---|---|---|
| path | PR approved | 607 | 23.6 | 35.33 |
| path | PR delegated, no approval | 122 | 19.77 | 29.77 |
| path | no PR created | 198 | 16.59 | 26.94 |
| purchasing_group | 001 | 159 | 19.24 | 28.82 |
| purchasing_group | 002 | 189 | 23.07 | 35.55 |
| purchasing_group | 003 | 192 | 21.96 | 33.07 |
| purchasing_group | 004 | 194 | 22.59 | 35.45 |
| purchasing_group | 005 | 193 | 21.98 | 31.85 |
| payment_method | A: Bank TransferB: Check | 304 | 21.43 | 31.33 |
| payment_method | C: Bank Collection | 319 | 22.65 | 33.23 |
| payment_method | D:Direct Debit | 304 | 21.54 | 33.02 |
| POs | 1 | 494 | 20.31 | 31.84 |
| POs | 2 | 250 | 22.41 | 32.88 |
| POs | 3 | 128 | 23.45 | 35.9 |
| POs | 4 | 55 | 24.45 | 36.27 |
| repeated_payment | False | 739 | 21.07 | 30.39 |
| repeated_payment | True | 188 | 25.92 | 37.74 |

การทำซ้ำ

| Activity | เคสที่มีซ้ำ | เพราะหลายเอกสาร | ซ้ำบนเอกสารเดิม | event เกินบนเอกสารเดิม |
|---|---|---|---|---|
| Create Purchase Order | 433 | 433 | 0 | 0 |
| Approve Purchase Order | 433 | 433 | 0 | 0 |
| Create Goods Receipt | 582 | 149 | 433 | 2101 |
| Create Invoice Receipt | 582 | 582 | 0 | 0 |
| Perform Two-Way Match | 582 | 582 | 0 | 0 |
| Execute Payment | 188 | 0 | 188 | 239 |
| Create Purchase Requisition | 0 | 0 | 0 | 0 |
| Approve Purchase Requisition | 0 | 0 | 0 | 0 |
| Delegate Purchase Requisition Approval | 0 | 0 | 0 | 0 |
| Create Request for Quotation | 0 | 0 | 0 | 0 |

## ช่วง 6 — ข้อเสนอแนะ · `notebooks/05_recommendations.ipynb` → `results/05_recommendations.json`

| # | ปัญหา | หลักฐาน |
|---|---|---|
| P1 | เริ่มจัดซื้อโดยไม่มีใบขอซื้อในระบบ | 198 จาก 927 เคส (21.4%) เริ่มที่ 'Create Request for Quotation' และใบขอซื้อทั้ง 198 ใบยังมีสถานะ 'Released' |
| P2 | ส่งต่อการอนุมัติ แต่ไม่มีบันทึกการอนุมัติ | 122 เคส (13.2%) มี 'Delegate Purchase Requisition Approval' แต่ไม่มี event อนุมัติตามมา ทั้งที่ใบขอซื้อมีสถานะ 'Released' |
| P3 | สั่งจ่ายเงินซ้ำกับใบแจ้งหนี้เดิม | 188 payment (20.3% ของเคส) ถูกสั่งจ่าย 2–5 ครั้ง (เกินมา 239 ครั้ง) ทุกครั้งอ้างใบรับของชุดเดิม ห่างกันมัธยฐาน 2.76 วัน ถ้าทุกครั้งเป็นยอดเต็ม เพดานบนคือ 25.7% ของยอดใบแจ้งหนี้ |
| P4 | จ่ายเงินให้ PO ก่อนรับของครบ | 234 PO ใน 163 เคส (17.6%) มีการรับของ 269 ครั้งหลังจ่ายเงินแล้ว (มัธยฐาน 2.07 วันหลังจ่าย) การจับคู่ที่บันทึกเป็น two-way ทั้งหมด (1941 ครั้ง, three-way 0 ครั้ง) |
| P5 | เวลาส่วนใหญ่อยู่ในการส่งต่องานภายใน | มัธยฐานทั้งเคส 21.75 วัน ไม่มีขั้นใดเด่นเป็นคอขวดเดียว ขั้นที่องค์กรควบคุมเองได้ (อนุมัติ/ส่งต่อ/การเงิน) คิดเป็น 69.3% ของผลรวมค่ามัธยฐานรายขั้น |


## ต่อยอด — ข้อมูลจริง BPI Challenge 2019 · `notebooks/06_bpi2019_real_data.ipynb` → `results/06_bpi2019.json`

ข้อมูล: BPI Challenge 2019, DOI 10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1, CC BY 4.0 · `BPI_Challenge_2019.xes` MD5 `4eb909242351193a61e1c15b9c3cc814`

| รายการ | ค่า |
|---|---|
| Cases (PO items) / events / activities | 251,734 / 1,595,923 / 42 |
| Purchase documents / vendors / companies | 76,349 / 1,975 / 4 |
| Events before 2018 / cases affected | 318 / 264 |
| Variants (singletons) | 11,973 (9,030) |
| Variants for 50% / 80% of cases | 7 / 45 |
| Invoice before GR in invoice-before-GR category | 16,356 (7.4%) |
| Cases with Remove Payment Block | 22.2% |
| Open cases (no Clear Invoice) in invoiced categories | 22.6% |
| Cases with a purchase requisition item | 18.5% |
| Cases with any change/cancel (excl. payment block) | 17.5% |
| Invoice → clear median days, with / without block removal | 51.2 / 37.3 |

Item categories

| Category | Cases | % |
|---|---|---|
| 3-way match, invoice before GR | 221,010 | 87.8 |
| 3-way match, invoice after GR | 15,182 | 6.0 |
| Consignment | 14,498 | 5.8 |
| 2-way match | 1,044 | 0.4 |

Rules

| Rule | Cases | % of category | Category cases |
|---|---|---|---|
| R1 invoice recorded before goods receipt (invoice after GR required) | 0 | 0.0 | 15,182 |
| R2 invoice cleared (paid) before any goods receipt (3-way match) | 655 | 0.28 | 236,192 |
| R3 goods receipt recorded for 2-way match item | 0 | 0.0 | 1,044 |
| R4 invoice recorded for consignment item | 0 | 0.0 | 14,498 |

Stage durations (days, cases with timestamps before 2018 excluded)

| Stage | n | median | mean | P90 |
|---|---|---|---|---|
| PO item created -> first goods receipt | 234,232 | 10.0 | 15.5 | 34.1 |
| first goods receipt -> invoice recorded | 193,785 | 11.3 | 20.6 | 48.0 |
| invoice recorded -> invoice cleared | 183,013 | 42.1 | 48.2 | 97.1 |
| PO item created -> invoice cleared (end to end) | 183,419 | 77.0 | 80.0 | 126.2 |

Rework

| Activity | Cases | % of cases |
|---|---|---|
| Change Quantity | 17,590 | 6.99 |
| Change Price | 11,224 | 4.46 |
| Delete Purchase Order Item | 8,839 | 3.51 |
| Cancel Invoice Receipt | 6,471 | 2.57 |
| Cancel Goods Receipt | 2,470 | 0.98 |
| Change Approval for Purchase Order | 4,377 | 1.74 |
| Remove Payment Block | 55,839 | 22.18 |

Comparison

| Metric | Simulated (Zenodo P2P) | Real (BPI 2019) |
|---|---|---|
| Cases | 927 (1 case = 1 PR) | 251,734 (1 case = 1 PO item) |
| Events | 14,671 | 1,595,923 |
| Variants | 388 | 11,973 |
| Variants for 80% of cases | 203 | 45 |
| Paid before any goods receipt | 0% | 0.28% of 3-way items |
| Cases still open (not paid) | 0% | 22.6% of invoiced categories |
| Timestamps outside the data period | none | 264 cases |
| Median end-to-end days | 21.75 | 77.0 |
