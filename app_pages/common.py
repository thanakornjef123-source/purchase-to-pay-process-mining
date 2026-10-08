"""Cached data access and small UI helpers shared by the pages."""
import sys
from pathlib import Path

import altair as alt
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import app_data as ad  # noqa: E402

BLUE = "#1f5f8b"
INK = "#1d2733"
MUTED = "#5b6672"


ROOT = Path(__file__).resolve().parents[1]


def _signature(*folders):  # passed as a normal (hashed) argument to the cached loaders
    """Names and modification times of the data files, used as the cache key.

    A redeploy can update the files while the server process keeps running, so the
    cache must be invalidated whenever a results/data file changes or is added.
    """
    files = sorted(p for f in folders for p in (ROOT / f).glob("*") if p.suffix in {".json", ".csv"})
    return tuple((p.name, p.stat().st_mtime_ns) for p in files)


@st.cache_data(show_spinner=False)
def _results(sig):
    import json
    return {p.stem.split("_", 1)[1]: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((ROOT / "results").glob("[0-9][0-9]_*.json"))}


def results():
    return _results(_signature("results"))


@st.cache_data(show_spinner=False)
def _case_log(sig):
    return ad.load_case_log()


def case_log():
    return _case_log(_signature("data"))


@st.cache_data(show_spinner=False)
def _case_table(sig):
    return ad.load_case_table()


def case_table():
    return _case_table(_signature("data"))


def rules_by_code():
    return {r["rule"][:2]: r for r in results()["conformance"]["rules"]}


def pct(x, digits=1):
    return f"{x:.{digits}f}%"


def num(x, digits=0):
    return f"{x:,.{digits}f}"


def notice():
    st.markdown(
        '<div class="notice"><b>หมายเหตุ:</b> วิเคราะห์จากชุดข้อมูลสาธารณะที่เป็น<b>ข้อมูลจำลอง</b>ตามโครงสร้างธุรกรรม SAP '
        "ไม่ใช่ข้อมูลของบริษัทจริง สาเหตุที่ระบุในรายงานเป็นข้อสันนิษฐานซึ่งต้องยืนยันกับเจ้าของกระบวนการ</div>",
        unsafe_allow_html=True,
    )


def image(name, caption, width="stretch"):
    st.image(str(ad.figure(name)), caption=caption, width=width)


def table(df, **kw):
    """Dataframe sized to show every row (up to a cap) instead of an inner scrollbar."""
    height = min(36 * (len(df) + 1) + 4, kw.pop("max_height", 640))
    st.dataframe(df, hide_index=True, width="stretch", height=height, **kw)


def hbar(df, y, x, x_title, y_title="", label_fmt=",.1f", height=None, color=BLUE):
    """Horizontal single-series bar chart with value labels and tooltips."""
    height = height or max(160, 34 * len(df))
    base = alt.Chart(df).encode(
        y=alt.Y(f"{y}:N", sort=None, title=y_title, axis=alt.Axis(labelLimit=360, labelColor=INK)),
        x=alt.X(f"{x}:Q", title=x_title, axis=alt.Axis(grid=True, gridColor="#eef1f4", labelColor=MUTED, tickCount=6)),
        tooltip=[alt.Tooltip(f"{y}:N", title=y_title or " "), alt.Tooltip(f"{x}:Q", title=x_title, format=label_fmt)],
    )
    bars = base.mark_bar(color=color, cornerRadiusEnd=3, height=18)
    text = base.mark_text(align="left", dx=4, color=INK, fontSize=12).encode(text=alt.Text(f"{x}:Q", format=label_fmt))
    return (bars + text).properties(height=height).configure_view(stroke=None).configure_axis(
        domainColor="#c9d1d9", tickColor="#c9d1d9", labelFont="Sarabun", titleFont="Sarabun", titleColor=MUTED
    )
