"""Purchase-to-Pay Process Mining — Streamlit entry point.

Run locally:  streamlit run app.py   (or start.bat on Windows)
"""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

st.set_page_config(
    page_title="Purchase-to-Pay Process Mining",
    page_icon=":material/account_tree:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem; max-width: 1180px;}
      h1 {font-size: 2.0rem !important; letter-spacing: -0.01em;}
      h2 {font-size: 1.45rem !important; border-bottom: 2px solid #1f5f8b; padding-bottom: .3rem; margin-top: 1.6rem !important;}
      h3 {font-size: 1.15rem !important;}
      [data-testid="stMetric"] {background: #f3f6f9; border: 1px solid #d7dde3; border-radius: 6px; padding: .7rem .9rem;}
      [data-testid="stMetricValue"] {color: #1f5f8b;}
      .notice {background:#fff4e5; border-left:4px solid #d98a1b; padding:.6rem .9rem; border-radius:4px; font-size:.95rem; margin-bottom:1rem;}
      .lead {font-size:1.08rem; color:#3a4651;}
      .muted {color:#5b6672; font-size:.9rem;}
      .footer {color:#5b6672; font-size:.82rem; border-top:1px solid #d7dde3; margin-top:2.5rem; padding-top:.6rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

pages = {
    "รายงาน": [
        st.Page("app_pages/overview.py", title="ภาพรวม", icon=":material/dashboard:", default=True),
        st.Page("app_pages/data_method.py", title="ข้อมูลและวิธีการ", icon=":material/dataset:"),
    ],
    "ผลการวิเคราะห์": [
        st.Page("app_pages/discovery.py", title="กระบวนการที่เกิดขึ้นจริง", icon=":material/account_tree:"),
        st.Page("app_pages/conformance.py", title="ความสอดคล้องกับกระบวนการ", icon=":material/rule:"),
        st.Page("app_pages/performance.py", title="ระยะเวลาและคอขวด", icon=":material/timer:"),
        st.Page("app_pages/case_explorer.py", title="สำรวจรายเคส", icon=":material/search:"),
        st.Page("app_pages/real_data.py", title="ข้อมูลจริง: BPI 2019", icon=":material/verified:"),
    ],
    "ข้อสรุป": [
        st.Page("app_pages/recommendations.py", title="ข้อเสนอแนะ", icon=":material/task_alt:"),
        st.Page("app_pages/report.py", title="รายงานและข้อจำกัด", icon=":material/description:"),
    ],
}

with st.sidebar:
    st.markdown("**Purchase-to-Pay Process Mining**")
    st.caption("การวิเคราะห์กระบวนการจัดซื้อถึงจ่ายเงินจาก event log")

nav = st.navigation(pages)
nav.run()

st.markdown(
    '<div class="footer">ข้อมูล: Procure-To-Payment (P2P) Object-centric Event Log in OCEL 2.0 Standard '
    '(Zenodo 8412920, CC BY 4.0) · ข้อมูลจำลอง ไม่ใช่ข้อมูลของบริษัทจริง · โปรเจกต์ส่วนบุคคล</div>',
    unsafe_allow_html=True,
)
