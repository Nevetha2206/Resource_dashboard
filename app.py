import os
import io
import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
import plotly.express as px
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from io import BytesIO
# ---------- CONFIG ----------
# <-- Change this to your actual Excel file path -->
EXCEL_PATH = r"https://github.com/Nevetha2206/Resource_dashboard/blob/main/data_crit%20(1).xlsx"
# Sheet name preferences
EXPECTED_SHEETS = {
    "resources": ["ResourceRequirements", "resources", "resource_requirements", "resources_sheet"],
    "so_details": ["SODetails", "so_details", "so"],
    "employees": ["Employees", "employees", "emp"],
}
RESOURCE_CANON = {
"sno": ["sno", "serial", "serialno"],
"skillRole": ["skillrole", "skill", "role", "skill_role","Skill/Role"],
"quantity": ["quantity", "qty", "count","Quantity"],
"aiaType": ["aiatype", "aia_type","AIA/NON AIA","AIA Type"],
"location": ["location", "loc","Location"],
"Priority": ["priority", "prio","Priority","Priortty (High, low)"],
"fulfilmentDateCutoff": ["Fulfilment date cut off","fulfilmentdatecutoff", "fulfillmentdatecutoff", "fulfilment", "fulfillment"],
"region": ["region","Region"],
"revLoss": ["revloss", "revenue_loss", "rev_loss","Rev Loss(oher vendir fulfilling, proje start ni sjul) -Y/N","revLoss"],
"deliveryRisk": ["deliveryrisk", "delivery_risk","Delivery Risk(proj is there no reso)","deliveryRisk"],
"positionCategory": ["positioncategory", "position_category","Position Category"],
"tower": ["tower", "technology", "techstack", "stack","Tower"],
"projectMapping": ["projectmapping", "project_mapping", "project"],
"requirementReceivedDate": ["Requirement received Date","requirementreceiveddate", "receiveddate", "reqreceived", "requirement_received_date"],
"sourcingStatus": ["sourcingstatus", "status", "requisitionstatus", "reqstatus", "sourcing_status","Sourcing status","sourcingStatus"],
"profileSharedOn": ["profilesharedon", "profile_shared_on","Profile Shared on","Profile Shared On"],
"commentsInDetail": ["commentsindetail", "comments", "notes", "remarks","Comments in Detail"],
"reqType": ["reqtype", "type", "requesttype","Req Type","Req Type (New - Addi/Roattion- Remap - no additi/Attrition-no addition)"],
"typeOfBackFill": ["typeofbackfill", "backfilltype", "backfill","Type of Backfill","Type of back fill (perfomnace, Resignation,Mediacl  leave)"],
"revenueContribution": ["revenuecontribution", "revenue_contribution","Revenue Contribution"],
"closingDate": ["closingdate", "closeddate", "close_date","Closing Date"],
"ctsPoc": ["ctspoc", "poc", "owner","CTS POC"],
}
# ---------- UI styling ----------
st.set_page_config(page_title="EMPLOYEE RESOURCE FULFILMENT MANAGEMENT", layout="wide")
st.markdown(
    """
<style>

        /* KPI Cards */
        .kpi-card {
            background: linear-gradient(135deg, #facc15, #ca8a04); /* dark yellow */
            color: white;
            border-radius: 8px;
            padding: 12px 10px;
            margin: 0.5rem 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            text-align: center;
            min-height: 90px;
        }
        .kpi-card.warn {
            background: linear-gradient(135deg, #f97316, #c2410c); /* dark orange */
            text-align: center;
        }
        .kpi-card.info {
            background: linear-gradient(135deg, #991b1b, #7f1d1d); /* dark red */
            text-align: center;
        }
        .kpi-card.loss {
            background: linear-gradient(135deg, #dc2626, #b91c1c); /* bright red gradient */
            color: white;
            text-align: center;
        }
        .kpi-title {
            opacity: 0.95;
            font-size: 1.1rem;
            text-align: center;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-weight: 700;
            font-size: 1.8rem;
            text-align: center;
            line-height: 1.2;
        }
        /* Tabs accent - Adaptive colors for light/dark themes */
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: #1f2937 !important; /* Dark gray for light theme */
            background-color: transparent !important;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            border-bottom: 3px solid #f97316;
            color: #f97316 !important;
            background-color: rgba(249, 115, 22, 0.1) !important;
        }
        .stTabs [data-baseweb="tab-list"] button:hover {
            color: #374151 !important;
            background-color: rgba(249, 115, 22, 0.05) !important;
        }

        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
            .stTabs [data-baseweb="tab-list"] button {
                color: #f9fafb !important; /* Light color for dark theme */
            }
            .stTabs [data-baseweb="tab-list"] button:hover {
                color: #e5e7eb !important;
            }
        }

        /* Force dark theme if Streamlit is in dark mode */
        .stApp[data-theme="dark"] .stTabs [data-baseweb="tab-list"] button {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stTabs [data-baseweb="tab-list"] button:hover {
            color: #e5e7eb !important;
        }

        /* Sub-tabs styling - ensure visibility */
        .stTabs .stTabs [data-baseweb="tab-list"] button {
            font-size: 1rem !important;
            font-weight: 500 !important;
            color: #374151 !important; /* Dark gray for light theme */
            background-color: transparent !important;
            border: 1px solid transparent !important;
        }
        .stTabs .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #f97316 !important;
            background-color: rgba(249, 115, 22, 0.1) !important;
            border-bottom: 2px solid #f97316 !important;
        }
        .stTabs .stTabs [data-baseweb="tab-list"] button:hover {
            color: #1f2937 !important;
            background-color: rgba(249, 115, 22, 0.05) !important;
        }

        /* Dark theme for sub-tabs */
        @media (prefers-color-scheme: dark) {
            .stTabs .stTabs [data-baseweb="tab-list"] button {
                color: #d1d5db !important;
            }
            .stTabs .stTabs [data-baseweb="tab-list"] button:hover {
                color: #f3f4f6 !important;
            }
        }

        .stApp[data-theme="dark"] .stTabs .stTabs [data-baseweb="tab-list"] button {
            color: #d1d5db !important;
        }
        .stApp[data-theme="dark"] .stTabs .stTabs [data-baseweb="tab-list"] button:hover {
            color: #f3f4f6 !important;
        }

        /* Ensure all tab content is visible */
        .stTabs [data-baseweb="tab-panel"] {
            color: #1f2937 !important;
        }

        .stApp[data-theme="dark"] .stTabs [data-baseweb="tab-panel"] {
            color: #f9fafb !important;
        }

        /* Fix any invisible text in tab content */
        .stTabs [data-baseweb="tab-panel"] * {
            color: inherit !important;
        }

        /* Comprehensive text visibility fixes for all elements */
        /* Main content text */
        .main .block-container {
            color: #1f2937 !important; /* Dark text for light theme */
        }

        /* Headers and titles */
        h1, h2, h3, h4, h5, h6 {
            color: #1f2937 !important;
        }

        /* Paragraphs and general text */
        p, div, span {
            color: #1f2937 !important;
        }

        /* Streamlit specific elements */
        .stMarkdown {
            color: #1f2937 !important;
        }

        .stText {
            color: #1f2937 !important;
        }

        .stSelectbox label {
            color: #1f2937 !important;
        }

        .stTextInput label {
            color: #1f2937 !important;
        }

        .stNumberInput label {
            color: #1f2937 !important;
        }

        .stDateInput label {
            color: #1f2937 !important;
        }

        .stTextArea label {
            color: #1f2937 !important;
        }

        .stSelectbox > div > div {
            color: #1f2937 !important;
        }

        /* Info boxes and alerts */
        .stAlert {
            color: #1f2937 !important;
        }

        .stInfo {
            color: #1f2937 !important;
        }

        .stSuccess {
            color: #1f2937 !important;
        }

        .stWarning {
            color: #1f2937 !important;
        }

        .stError {
            color: #1f2937 !important;
        }

        /* Dataframe styling */
        .stDataFrame {
            color: #1f2937 !important;
        }

        /* Button text */
        .stButton > button {
            color: #ffffff !important;
        }

        /* Form elements */
        .stForm {
            color: #1f2937 !important;
        }

        /* List items */
        ul, ol, li {
            color: #1f2937 !important;
        }

        /* Custom skill list styling */
        .skill-list {
            background-color: #f8f9fa !important;
            color: #1f2937 !important;
        }

        .skill-list li {
            color: #1f2937 !important;
        }

        /* Dark theme overrides */
        @media (prefers-color-scheme: dark) {
            .main .block-container {
                color: #f9fafb !important;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #f9fafb !important;
            }
            p, div, span {
                color: #f9fafb !important;
            }
            .stMarkdown {
                color: #f9fafb !important;
            }
            .stText {
                color: #f9fafb !important;
            }
            .stSelectbox label {
                color: #f9fafb !important;
            }
            .stTextInput label {
                color: #f9fafb !important;
            }
            .stNumberInput label {
                color: #f9fafb !important;
            }
            .stDateInput label {
                color: #f9fafb !important;
            }
            .stTextArea label {
                color: #f9fafb !important;
            }
            .stSelectbox > div > div {
                color: #f9fafb !important;
            }
            .stAlert {
                color: #f9fafb !important;
            }
            .stInfo {
                color: #f9fafb !important;
            }
            .stSuccess {
                color: #f9fafb !important;
            }
            .stWarning {
                color: #f9fafb !important;
            }
            .stError {
                color: #f9fafb !important;
            }
            .stDataFrame {
                color: #f9fafb !important;
            }
            .stForm {
                color: #f9fafb !important;
            }
            ul, ol, li {
                color: #f9fafb !important;
            }
            .skill-list {
                background-color: #374151 !important;
                color: #f9fafb !important;
            }
            .skill-list li {
                color: #f9fafb !important;
            }
        }

        /* Force dark theme if Streamlit is in dark mode */
        .stApp[data-theme="dark"] .main .block-container {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] h1,
        .stApp[data-theme="dark"] h2,
        .stApp[data-theme="dark"] h3,
        .stApp[data-theme="dark"] h4,
        .stApp[data-theme="dark"] h5,
        .stApp[data-theme="dark"] h6 {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] p,
        .stApp[data-theme="dark"] div,
        .stApp[data-theme="dark"] span {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stMarkdown {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stText {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stSelectbox label {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stTextInput label {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stNumberInput label {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stDateInput label {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stTextArea label {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stSelectbox > div > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stAlert {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stInfo {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stSuccess {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stWarning {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stError {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stDataFrame {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stForm {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] ul,
        .stApp[data-theme="dark"] ol,
        .stApp[data-theme="dark"] li {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .skill-list {
            background-color: #374151 !important;
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .skill-list li {
            color: #f9fafb !important;
        }

        /* Additional fixes for specific grey text issues */
        /* Info boxes and alert boxes */
        .stAlert > div {
            color: #1f2937 !important;
        }

        .stInfo > div {
            color: #1f2937 !important;
        }

        .stSuccess > div {
            color: #1f2937 !important;
        }

        .stWarning > div {
            color: #1f2937 !important;
        }

        .stError > div {
            color: #1f2937 !important;
        }

        /* Plotly chart text elements */
        .js-plotly-plot .plotly .xtick text,
        .js-plotly-plot .plotly .ytick text,
        .js-plotly-plot .plotly .legend text {
            fill: #1f2937 !important;
        }

        /* Streamlit metric and info elements */
        .stMetric {
            color: #1f2937 !important;
        }

        .stMetric > div {
            color: #1f2937 !important;
        }

        .stMetric label {
            color: #1f2937 !important;
        }

        /* Dark theme overrides for additional elements */
        @media (prefers-color-scheme: dark) {
            .stAlert > div {
                color: #f9fafb !important;
            }
            .stInfo > div {
                color: #f9fafb !important;
            }
            .stSuccess > div {
                color: #f9fafb !important;
            }
            .stWarning > div {
                color: #f9fafb !important;
            }
            .stError > div {
                color: #f9fafb !important;
            }
            .js-plotly-plot .plotly .xtick text,
            .js-plotly-plot .plotly .ytick text,
            .js-plotly-plot .plotly .legend text {
                fill: #f9fafb !important;
            }
            .stMetric {
                color: #f9fafb !important;
            }
            .stMetric > div {
                color: #f9fafb !important;
            }
            .stMetric label {
                color: #f9fafb !important;
            }
        }

        /* Force dark theme overrides for additional elements */
        .stApp[data-theme="dark"] .stAlert > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stInfo > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stSuccess > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stWarning > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stError > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .js-plotly-plot .plotly .xtick text,
        .stApp[data-theme="dark"] .js-plotly-plot .plotly .ytick text,
        .stApp[data-theme="dark"] .js-plotly-plot .plotly .legend text {
            fill: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stMetric {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stMetric > div {
            color: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .stMetric label {
            color: #f9fafb !important;
        }

        /* Additional Plotly chart fixes */
        .js-plotly-plot .plotly .gtitle text {
            fill: #1f2937 !important;
        }

        .js-plotly-plot .plotly .g-xtitle text,
        .js-plotly-plot .plotly .g-ytitle text {
            fill: #1f2937 !important;
        }

        .js-plotly-plot .plotly .gaxistitle text {
            fill: #1f2937 !important;
        }

        /* Dark theme Plotly fixes */
        @media (prefers-color-scheme: dark) {
            .js-plotly-plot .plotly .gtitle text {
                fill: #f9fafb !important;
            }
            .js-plotly-plot .plotly .g-xtitle text,
            .js-plotly-plot .plotly .g-ytitle text {
                fill: #f9fafb !important;
            }
            .js-plotly-plot .plotly .gaxistitle text {
                fill: #f9fafb !important;
            }
        }

        .stApp[data-theme="dark"] .js-plotly-plot .plotly .gtitle text {
            fill: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .js-plotly-plot .plotly .g-xtitle text,
        .stApp[data-theme="dark"] .js-plotly-plot .plotly .g-ytitle text {
            fill: #f9fafb !important;
        }
        .stApp[data-theme="dark"] .js-plotly-plot .plotly .gaxistitle text {
            fill: #f9fafb !important;
        }
</style>
    """, unsafe_allow_html=True
)
# ---------- Chart styling helper ----------
def get_chart_layout_config():
    """Get consistent chart layout configuration for proper text visibility"""
    return {
        'font': {'color': '#1f2937', 'size': 14},
        'xaxis': {'tickfont': {'color': '#1f2937'}, 'titlefont': {'color': '#1f2937'}},
        'yaxis': {'tickfont': {'color': '#1f2937'}, 'titlefont': {'color': '#1f2937'}},
        'legend': {'font': {'color': '#1f2937'}},
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)'
    }

def get_dark_chart_layout_config():
    """Get dark theme chart layout configuration"""
    return {
        'font': {'color': '#f9fafb', 'size': 14},
        'xaxis': {'tickfont': {'color': '#f9fafb'}, 'titlefont': {'color': '#f9fafb'}},
        'yaxis': {'tickfont': {'color': '#f9fafb'}, 'titlefont': {'color': '#f9fafb'}},
        'legend': {'font': {'color': '#f9fafb'}},
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)'
    }

# ---------- Caching & Excel loader ----------
def _pick_sheet_name(available: list[str], candidates: list[str]) -> str | None:
    lower_map = {name.lower(): name for name in available}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None
def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    col_map = {}
    lower_cols = {c.lower().replace(" ", "").replace("_", ""): c for c in df.columns}
    for canon, variants in RESOURCE_CANON.items():
        for v in variants:
            key = v.lower().replace(" ", "").replace("_", "")
            if key in lower_cols:
                col_map[lower_cols[key]] = canon
                break
    df = df.rename(columns=col_map)
    # Ensure required columns exist
    required = [
        "sourcingStatus","quantity","priority","location","tower","aiaType",
        "reqType","deliveryRisk","skillRole","revLoss","typeOfBackFill",
        "requirementReceivedDate","projectMapping","region","positionCategory",
        "closingDate","profileSharedOn","fulfilmentDateCutoff" # Added cutoff to ensure it exists
    ]
    for c in required:
        if c not in df.columns:
            df[c] = pd.NA
    # Types
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    for dcol in ["requirementReceivedDate", "closingDate", "profileSharedOn", "fulfilmentDateCutoff"]:
        if dcol in df.columns:
            df[dcol] = pd.to_datetime(df[dcol], errors="coerce")
    return df
@st.cache_data(show_spinner=False)
def _read_excel_with_mtime(path: str, mtime: float):
    """
    Cache keyed by file modification time (mtime) so reloading happens when the file changes.
    Returns 3 DataFrames: resource_df, so_df, emp_df
    """
    xls = pd.ExcelFile(path)
    sheets = xls.sheet_names
    res_sheet = _pick_sheet_name(sheets, EXPECTED_SHEETS["resources"]) or sheets[0]
    so_sheet = _pick_sheet_name(sheets, EXPECTED_SHEETS["so_details"]) or (sheets[1] if len(sheets) > 1 else sheets[0])
    emp_sheet = _pick_sheet_name(sheets, EXPECTED_SHEETS["employees"]) or (sheets[2] if len(sheets) > 2 else sheets[0])
    resource_df = pd.read_excel(xls, sheet_name=res_sheet)
    so_df = pd.read_excel(xls, sheet_name=so_sheet)
    emp_df = pd.read_excel(xls, sheet_name=emp_sheet)
    resource_df = _canonicalize_columns(resource_df)
    # Clean column names for safe lookups
    resource_df.columns = (
        resource_df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    return resource_df, so_df, emp_df, res_sheet, so_sheet, emp_sheet
def load_excel(path: str):
    if not os.path.exists(path):
        st.error(f"Excel file not found at: {path}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None, None, None
    mtime = os.path.getmtime(path)
    return _read_excel_with_mtime(path, mtime)
# ---------- Priority logic & ID generation ----------
def _def_is_closed(s):
    return isinstance(s, str) and any(k in s.lower() for k in ["closed","filled","completed"])
def _def_is_open(s):
    return isinstance(s, str) and any(k in s.lower() for k in ["open","progress","pending"])
def compute_priority_for_row(row):
    """
    Revised Rules:
    - If fulfilmentDateCutoff is in current month or earlier -> Critical
    - If revLoss == 'Y' (case-insensitive) -> Critical
    - If deliveryRisk in ('yes','y','true') -> Critical
    - Else -> Non-Critical
    """
    try:
        now = datetime.now()
        # --- Fulfilment cutoff month ---
        # Look for the canonical name 'fulfilmentDateCutoff'
        fd = row.get("fulfilmentDateCutoff")
        if pd.notna(fd):
            try:
                # Attempt to parse as date/datetime
                fd_dt = pd.to_datetime(fd, errors="coerce")
                if pd.notna(fd_dt) and (
                    fd_dt.year < now.year or
                    (fd_dt.year == now.year and fd_dt.month <= now.month)
                ):
                    return "Critical"
            except Exception:
                pass
        # --- Rev Loss ---
        rev = str(
            row.get("revLoss", "")
        ).strip().upper()
        if rev in ("Y", "YES", "TRUE", "1"):
            return "Critical"
        # --- Delivery risk ---
        dr = str(
            row.get("deliveryRisk", "")
        ).strip().lower()
        if dr in ("y", "yes", "true", "1"):
            return "Critical"
        # --- Existing Priority (Now 'Critical' or 'Non-Critical' in Excel) ---
        p = str(
            row.get("priority", "")
        ).strip().capitalize()
        # Check for the new Excel value
        if p == "Critical":
            return "Critical"
    except Exception:
        pass
    return "Non-Critical"
def ensure_requirement_ids(df: pd.DataFrame, id_col: str = "requirementID"):
    """
    Ensure unique RF IDs. If existing IDs with RF prefix present, continue sequence.
    Else generate from 1..n
    """
    if id_col not in df.columns:
        df[id_col] = pd.NA
    # find max existing
    existing = df[id_col].dropna().astype(str)
    max_num = 0
    for v in existing:
        if v.upper().startswith("RF"):
            numpart = ''.join(ch for ch in v[2:] if ch.isdigit())
            if numpart:
                try:
                    n = int(numpart)
                    if n > max_num:
                        max_num = n
                except:
                    pass
    # assign IDs for missing
    def gen_next(i):
        return f"RF{str(i).zfill(5)}"
    next_i = max_num + 1
    for idx in df.index:
        if pd.isna(df.at[idx, id_col]) or str(df.at[idx, id_col]).strip() == "":
            df.at[idx, id_col] = gen_next(next_i)
            next_i += 1
    return df
# ---------- Load data ----------
resource_df, so_df, emp_df, res_sheet_name, so_sheet_name, emp_sheet_name = load_excel(EXCEL_PATH)
# If empty resource_df, create empty with canonical columns
if resource_df is None:
    resource_df = pd.DataFrame()
# Apply requirementID + priority enforcement
if not resource_df.empty:
    # Ensure requirement IDs
    resource_df = ensure_requirement_ids(resource_df, id_col="requirementID")
    # Apply priority *after* canonicalizing columns, using the new function
    resource_df["priority"] = resource_df.apply(compute_priority_for_row, axis=1)
    # Remove sno column if present
    if "sno" in resource_df.columns:
        resource_df = resource_df.drop(columns=["sno"])
    # Reorder columns to keep requirementID first
    first_col = ["requirementID"]
    other_cols = [c for c in resource_df.columns if c not in first_col]
    resource_df = resource_df[first_col + other_cols]
# ---------- Session state setup ----------
if "resource_df" not in st.session_state:
    st.session_state.resource_df = resource_df.copy() if not resource_df.empty else pd.DataFrame()
if "so_df" not in st.session_state:
    st.session_state.so_df = so_df.copy() if so_df is not None else pd.DataFrame()
if "emp_df" not in st.session_state:
    st.session_state.emp_df = emp_df.copy() if emp_df is not None else pd.DataFrame()
if "filter_priority" not in st.session_state:
    st.session_state.filter_priority = None
def write_back_excel(path: str, res_df: pd.DataFrame, so_df: pd.DataFrame, emp_df: pd.DataFrame,
                     res_name: str = "Resources", so_name: str = "SO", emp_name: str = "Employees"):
    """
    Writes three DataFrames to an Excel file with specified sheet names.
    Ensures 'Sno' column is preserved or regenerated in res_df.
    Skips writing 'requirementID' column to Excel.
    """
    try:
        # --- Drop 'requirementID' if present ---
        if "requirementID" in res_df.columns:
            res_df = res_df.drop(columns=["requirementID"])
        # --- Ensure 'Sno' column is present and correctly ordered ---
        if "Sno" not in res_df.columns:
            res_df.insert(0, "Sno", range(1, len(res_df) + 1))
        else:
            res_df["Sno"] = range(1, len(res_df) + 1)
            cols = ["Sno"] + [col for col in res_df.columns if col != "Sno"]
            res_df = res_df[cols]
        # --- Write to Excel ---
        with pd.ExcelWriter(path, engine="openpyxl", mode="w") as writer:
            res_df.to_excel(writer, sheet_name=res_name, index=False)
            so_df.to_excel(writer, sheet_name=so_name, index=False)
            emp_df.to_excel(writer, sheet_name=emp_name, index=False)
        return True, None
    except Exception as e:
        return False, str(e)
# ---------- PDF Generation Helper ----------
# ----- Critical Report PDF Generator (MATCHES TAB 4 EXACTLY) -----
def generate_critical_report_pdf(df: pd.DataFrame) -> bytes:
    """Generate Critical Resource Report PDF identical to Tab 4 Streamlit report"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    import matplotlib.pyplot as plt
    from io import BytesIO
    import pandas as pd
    from datetime import datetime
    # ---- Initialize PDF ----
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16,
                                 alignment=1, textColor=colors.red)
    h2 = styles['Heading2']
    normal = styles['Normal']
    story = []
    story.append(Paragraph("🚨 Critical Resource Requirements Report", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal))
    story.append(Spacer(1, 20))
    if df.empty:
        story.append(Paragraph("✅ No critical requirements found matching the strict criteria!", normal))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    # ---- FILTERING LOGIC (EXACTLY AS TAB 4 PRIORITY) ----
    df = df.copy()
    now = datetime.now()
    # --- Priority Classification Functions ---
    def is_critical(row): # RENAMED FROM is_high
        sourcing = str(row.get("sourcingStatus", "")).strip().lower()
        if not sourcing.startswith("open"):
            return False  # sourcing must be open for any high priority
        # Fulfilment cutoff check
        fd = row.get("fulfilmentDateCutoff")
        fd_dt = pd.to_datetime(fd, errors="coerce") if pd.notna(fd) else None
        cutoff_passed = pd.notna(fd_dt) and (
            fd_dt.year < now.year or (fd_dt.year == now.year and fd_dt.month <= now.month)
        )
        # Revenue loss check
        rev = str(row.get("revLoss", "")).strip().lower()
        rev_loss = rev in ("y", "yes", "true", "1")
        # Delivery risk check
        dr = str(row.get("deliveryRisk", "")).strip().lower()
        delivery_risk = dr in ("y", "yes", "true", "1")
        # If any of the three risk flags are true, it's high
        if cutoff_passed or rev_loss or delivery_risk:
            return True
        # If none of the above, defer to priority column
        priority = str(row.get("priority", "")).strip().lower()
        return priority == "critical" # CHECKING FOR 'critical'
    # Filter only critical priority (matches Tab4)
    df = df[df.apply(is_critical, axis=1)] # USING is_critical
    if df.empty:
        story.append(Paragraph(
            "✅ No critical requirements match the criteria for Critical Priority "
            "+ (cutoff ≤ current month) + (rev loss or delivery risk).", normal))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    # ---- KPIs ----
    total_positions = int(df['quantity'].sum()) if 'quantity' in df else 0
    revenue_loss_count = int(df[df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])]['quantity'].sum()) if 'revLoss' in df else 0
    delivery_risk_count = int(df[df['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true'])]['quantity'].sum()) if 'deliveryRisk' in df else 0
    past_cutoff = 0
    if 'fulfilmentDateCutoff' in df.columns:
        past_cutoff = int(df[pd.to_datetime(df['fulfilmentDateCutoff'], errors='coerce') <= pd.Timestamp.now()]['quantity'].sum())
    story.append(Paragraph("📊 Critical Requirements Metrics", h2))
    story.append(Paragraph(f"• Total Critical Positions: {total_positions}", normal))
    story.append(Paragraph(f"• Revenue Loss Risk: {revenue_loss_count}", normal))
    story.append(Paragraph(f"• Delivery Risk: {delivery_risk_count}", normal))
    story.append(Paragraph(f"• Past Cut-off Date: {past_cutoff}", normal))
    story.append(Spacer(1, 20))
    # ---- Helper: function to add chart ----
    def add_chart(fig):
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        story.append(Image(buf, width=6*inch, height=3.5*inch))
        story.append(Spacer(1, 15))
    # ---- Chart 1: Urgency Analysis ----
    if {'fulfilmentDateCutoff', 'quantity'}.issubset(df.columns):
        urgency_data = df.copy()
        urgency_data['days_to_cutoff'] = (urgency_data['fulfilmentDateCutoff'] - pd.Timestamp.now()).dt.days
        urgency_data['urgency_level'] = urgency_data['days_to_cutoff'].apply(
            lambda x: 'Past Due' if x < 0 else 'Critical (0-2 days)' if x <= 2 else 'Urgent (3-10 days)'
        )
        chart = urgency_data.groupby('urgency_level')['quantity'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(chart['urgency_level'], chart['quantity'], color=['red', 'orange', 'yellow'])
        ax.set_title("Critical Urgency Distribution")
        ax.set_ylabel("Quantity")
        add_chart(fig)
    # ---- Chart 2: Critical Skills with Revenue Loss ----
    if {'skillRole', 'revLoss', 'quantity'}.issubset(df.columns):
        rev_loss_data = df[df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])]
        if not rev_loss_data.empty:
            rev_chart = rev_loss_data.groupby('skillRole')['quantity'].sum().sort_values(ascending=False).head(8).reset_index()
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.barh(rev_chart['skillRole'], rev_chart['quantity'], color='orange')
            ax.set_title("Critical Skills with Revenue Loss Risk")
            ax.invert_yaxis()
            add_chart(fig)
    # ---- Chart 3: Skills Distribution ----
    if {'skillRole', 'quantity'}.issubset(df.columns):
        skills_chart = df.groupby('skillRole')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(skills_chart['skillRole'], skills_chart['quantity'], color='purple')
        ax.set_title("Critical Skills Distribution")
        ax.invert_yaxis()
        add_chart(fig)
    # ---- Chart 4: Location Pie ----
    if {'location', 'quantity'}.issubset(df.columns):
        loc = df.copy()
        loc['location'] = loc['location'].fillna('Not Specified')
        loc_chart = loc.groupby('location')['quantity'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(loc_chart['quantity'], labels=loc_chart['location'], autopct='%1.1f%%', startangle=90)
        ax.set_title("Geographic Distribution of Critical Requirements")
        add_chart(fig)
    # ---- Chart 5: Tower ----
    if {'tower', 'quantity'}.issubset(df.columns):
        tower_chart = df.groupby('tower')['quantity'].sum().sort_values(ascending=False).reset_index()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(tower_chart['tower'], tower_chart['quantity'], color='blue')
        plt.xticks(rotation=45)
        ax.set_title("Critical Requirements by Technology Tower")
        add_chart(fig)
    # ---- Chart 6: Aging ----
    if 'requirementReceivedDate' in df.columns:
        aging = df.copy()
        aging['requirementReceivedDate'] = pd.to_datetime(aging['requirementReceivedDate'], errors='coerce')
        aging['days_open'] = (pd.Timestamp.now() - aging['requirementReceivedDate']).dt.days
        aging['aging_category'] = aging['days_open'].apply(
            lambda x: 'Critical (>60 days)' if x > 60 else 'Urgent (30-60 days)' if x > 30 else 'Recent (<30 days)'
        )
        chart = aging.groupby('aging_category')['quantity'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(chart['aging_category'], chart['quantity'], color=['red', 'orange', 'green'])
        ax.set_title("Aging Distribution of Critical Requirements")
        add_chart(fig)
    # ---- Chart 7: Risk Level ----
    risk_data = df.copy()
    risk_data['risk_score'] = 0
    risk_data.loc[risk_data['revLoss'].astype(str).str.upper().isin(['Y', 'YES']), 'risk_score'] += 2
    risk_data.loc[risk_data['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true']), 'risk_score'] += 2
    if 'fulfilmentDateCutoff' in risk_data.columns:
        risk_data['fulfilmentDateCutoff'] = pd.to_datetime(risk_data['fulfilmentDateCutoff'], errors='coerce')
        risk_data.loc[risk_data['fulfilmentDateCutoff'] <= pd.Timestamp.now(), 'risk_score'] += 3
        near_cutoff = (risk_data['fulfilmentDateCutoff'] - pd.Timestamp.now()).dt.days <= 2
        risk_data.loc[near_cutoff, 'risk_score'] += 2
    risk_data['risk_level'] = risk_data['risk_score'].apply(
        lambda x: 'Critical (5+)' if x >= 5 else 'High (3-4)' if x >= 3 else 'Medium (1-2)' if x >= 1 else 'Low (0)'
    )
    chart = risk_data.groupby('risk_level')['quantity'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(chart['quantity'], labels=chart['risk_level'], autopct='%1.1f%%', startangle=90)
    ax.set_title("Critical Risk Level Distribution")
    add_chart(fig)
    # ---- Chart 8: Sourcing Status ----
    if {'sourcingStatus', 'quantity'}.issubset(df.columns):
        status_chart = df.groupby('sourcingStatus')['quantity'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(status_chart['sourcingStatus'], status_chart['quantity'], color='green')
        plt.xticks(rotation=45)
        ax.set_title("Sourcing Status of Critical Requirements")
        add_chart(fig)
    # ---- Recommended Actions ----
    story.append(Paragraph("🎯 Recommended Actions", h2))
    past_due = df[pd.to_datetime(df['fulfilmentDateCutoff'], errors='coerce') <= pd.Timestamp.now()]
    if not past_due.empty:
        story.append(Paragraph(f"🚨 {past_due['quantity'].sum()} positions past cut-off date — ESCALATE IMMEDIATELY", normal))
    rev_loss = df[df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])]
    if not rev_loss.empty:
        story.append(Paragraph(f"💰 {rev_loss['quantity'].sum()} positions causing revenue loss — PRIORITIZE", normal))
    del_risk = df[df['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true'])]
    if not del_risk.empty:
        story.append(Paragraph(f"⚠️ {del_risk['quantity'].sum()} positions at delivery risk — ACCELERATE", normal))
    story.append(Spacer(1, 15))
    # ---- Focus Insights ----
    top_skills = df.groupby('skillRole')['quantity'].sum().sort_values(ascending=False).head(3)
    if not top_skills.empty:
        story.append(Paragraph(f"🎯 Focus recruitment on: {', '.join(top_skills.index)}", normal))
    top_locations = df.groupby('location')['quantity'].sum().sort_values(ascending=False).head(2)
    if not top_locations.empty:
        story.append(Paragraph(f"📍 Geographic focus: {', '.join(top_locations.index)}", normal))
    top_towers = df.groupby('tower')['quantity'].sum().sort_values(ascending=False).head(2)
    if not top_towers.empty:
        story.append(Paragraph(f"🏗️ Technology focus: {', '.join(top_towers.index)}", normal))
    story.append(Spacer(1, 20))
    # ---- Detailed Table ----
    story.append(Paragraph("📋 Detailed Critical Requirements", h2))
    display_cols = [
        'requirementID', 'quantity','priority',
        'sourcingStatus', 'revLoss', 'deliveryRisk', 'fulfilmentDateCutoff'
    ]
    available_cols = [c for c in display_cols if c in df.columns]
    table_data = [available_cols] + [
        [str(row[c]) if pd.notna(row[c]) else '' for c in available_cols] for _, row in df.iterrows()
    ]
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ]))
    story.append(table)
    # ---- Build PDF ----
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
# ---------- Header ----------
st.markdown(
    "<h1 style='text-align: center;'>EMPLOYEE RESOURCE FULFILMENT MANAGEMENT</h1>",
    unsafe_allow_html=True
)
# Create full-width button-style navigation
st.markdown("""
<style>
.nav-buttons {
    display: flex;
    width: 100%;
    margin-bottom: 2rem;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.nav-button {
    flex: 1;
    padding: 15px 20px;
    background: linear-gradient(135deg, #f8fafc, #e2e8f0);
    border: none;
    cursor: pointer;
    font-size: 60px;
    font-weight: 1500;
    color: #475569;
    transition: all 0.3s ease;
    border-right: 1px solid #cbd5e1;
}
.nav-button:last-child {
    border-right: none;
}
.nav-button:hover {
    background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
    color: #334155;
    transform: translateY(-1px);
}
.nav-button.active {
    background: linear-gradient(135deg, #f97316, #ea580c);
    color: white;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}
.nav-button.active:hover {
    background: linear-gradient(135deg, #ea580c, #dc2626);
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# Initialize current tab if not set
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "dashboard"

# Create navigation buttons with enhanced styling
st.markdown("""
<style>
/* Target all Streamlit buttons specifically */
div[data-testid="column"] button {
    font-weight: 1000 !important;
    font-size: 50px !important;
    padding: 15px 25px !important;
    text-align: center !important;
}

/* Target buttons with specific keys */
button[kind="primary"], button[kind="secondary"] {
    font-weight: 1000 !important;
    font-size: 50px !important;
    padding: 15px 25px !important;
}

/* More specific targeting for navigation buttons */
div[data-testid="column"] button[kind="primary"],
div[data-testid="column"] button[kind="secondary"] {
    font-weight: 1000 !important;
    font-size: 50px !important;
    padding: 15px 25px !important;
    font-family: inherit !important;
}

/* Ensure text is bold in all button states */
.stButton > button,
.stButton > button:focus,
.stButton > button:hover,
.stButton > button:active {
    font-weight: 1000 !important;
    font-size: 50px !important;
}

/* Override any Streamlit default styles */
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-secondary"] {
    font-weight: 1000 !important;
    font-size: 50px !important;
    padding: 15px 25px !important;
}
</style>
""", unsafe_allow_html=True)

# Create navigation buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    dashboard_active = st.session_state.current_tab == "dashboard"
    if st.button("📊 Resource Dashboard", key="nav_dashboard", use_container_width=True, type="primary" if dashboard_active else "secondary"):
        st.session_state.current_tab = "dashboard"
        st.rerun()
with col2:
    details_active = st.session_state.current_tab == "details"
    if st.button("📋 Resource Details", key="nav_details", use_container_width=True, type="primary" if details_active else "secondary"):
        st.session_state.current_tab = "details"
        st.rerun()
with col3:
    manage_active = st.session_state.current_tab == "manage"
    if st.button("⚙️ Manage Resources", key="nav_manage", use_container_width=True, type="primary" if manage_active else "secondary"):
        st.session_state.current_tab = "manage"
        st.rerun()
with col4:
    critical_active = st.session_state.current_tab == "critical"
    if st.button("🚨 Critical Report", key="nav_critical", use_container_width=True, type="primary" if critical_active else "secondary"):
        st.session_state.current_tab = "critical"
        st.rerun()
def make_columns_fully_unique(columns):
    """
    Guarantees all column names in the provided list are unique 
    by appending '_1', '_2', etc., only if necessary.
    """
    final_unique_columns = []
    seen_names = {}  # Tracks the base name and the highest count used
    
    for col in columns:
        base_name = col
        count = 0
        new_col_name = base_name
        
        # Check if the name already exists in the final list
        while new_col_name in final_unique_columns:
            count += 1
            new_col_name = f"{base_name}_{count}"
            
        final_unique_columns.append(new_col_name)
        
    return final_unique_columns

# --- SESSION STATE INITIALIZATION & DATA LOADING (Top of the Script) ---
if 'resource_df' not in st.session_state:
    try:
        # Load the Excel file
        loaded_df = pd.read_excel("C:/Users/2387781/Downloads/raw_data.xlsx", engine='openpyxl')
        
        # 1. APPLY THE DEDUPLICATION RIGHT AFTER LOADING
        loaded_df.columns = make_columns_fully_unique(loaded_df.columns) 
        
        # 2. Drop unwanted column
        loaded_df = loaded_df.drop(columns=["sno"], errors="ignore")

        # Store the clean, original data in session state
        st.session_state.original_df = loaded_df.copy()
        
    except FileNotFoundError:
        st.error("Error: raw_data.xlsx not found at the specified path.")
        st.session_state.original_df = pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.original_df = pd.DataFrame()

# Display content based on selected tab
if st.session_state.current_tab == "dashboard":
    st.subheader("📊 Resource Dashboard")
    # First row: Open Requirements & Critical Priority
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        open_requirements = resource_df.loc[
            resource_df["sourcingStatus"].apply(_def_is_open), "quantity"
        ].sum() if "sourcingStatus" in resource_df.columns else 0
        st.markdown(
            '<div class="kpi-card info" style="text-align:center">'
            '<div class="kpi-title">Open Requirements</div>'
            f'<div class="kpi-value">{int(open_requirements) if pd.notna(open_requirements) else 0}</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with row1_col2:
        critical_priority_in_open = 0
        if {"quantity"}.issubset(resource_df.columns):
            critical_priority_in_open = resource_df.loc[
                resource_df.apply(lambda row: compute_priority_for_row(row) == "Critical", axis=1),
                "quantity"
            ].sum()
        st.markdown(
            '<div class="kpi-card" style="text-align:center">'
            '<div class="kpi-title">Critical Priority</div>'
            f'<div class="kpi-value">{int(critical_priority_in_open) if pd.notna(critical_priority_in_open) else 0}</div>'
            '</div>',
            unsafe_allow_html=True
        )
    # Second row: Revenue Loss Risk & Requirements Aging
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        revenue_loss_count = 0
        if "revLoss" in resource_df.columns and "quantity" in resource_df.columns:
            rev_loss_filter = resource_df["revLoss"].astype(str).str.upper().isin(['Y', 'YES', 'TRUE', '1'])
            revenue_loss_count = resource_df.loc[rev_loss_filter, 'quantity'].sum()
        st.markdown(
            '<div class="kpi-card loss" style="text-align:center">'
            '<div class="kpi-title">Revenue Loss Risk</div>'
            f'<div class="kpi-value">{int(revenue_loss_count) if pd.notna(revenue_loss_count) else 0}</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with row2_col2:
        aging_count = 0
        if 'requirementReceivedDate' in resource_df.columns and 'quantity' in resource_df.columns:
            days_old = (pd.Timestamp.now(tz=None) - pd.to_datetime(resource_df['requirementReceivedDate'], errors='coerce')).dt.days
            aging_count = int(resource_df.loc[days_old > 30, 'quantity'].sum())
        elif 'requirementReceivedDate' in resource_df.columns:
            days_old = (pd.Timestamp.now(tz=None) - pd.to_datetime(resource_df['requirementReceivedDate'], errors='coerce')).dt.days
            aging_count = int((days_old > 30).sum())
        st.markdown(
            '<div class="kpi-card warn" style="text-align:center">'
            '<div class="kpi-title">Requirements Aging</div>'
            f'<div class="kpi-value">{aging_count}</div>'
            '</div>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    # Create subtabs to logically group many visualizations for readability
    import pandas as pd
    import streamlit as st
    import plotly.express as px
    # Assuming 'resource_df', '_def_is_open', and '_def_is_closed' are defined elsewhere in your full application.
    tab_overview, tab_skills_status, tab_status_backfill, tab_rev_delivery, Req_Type_and_Location_Insights = st.tabs([
        "🏗️ Tower wise distribution", "⚡ Technology fulfilment", "📈 Fulfilment summary", "⚠️ Risk summary", "📍 Location Insights"
    ])

    with tab_overview:
        # ROW 1: 2 Bar Charts (Priority & Technology/Tower) - Now Plotly
        c1, c2 = st.columns(2)
        with c1:
            if {'priority','quantity'}.issubset(resource_df.columns):
                priority_chart = resource_df.groupby('priority', dropna=False)['quantity'].sum().reset_index()
                # Custom color mapping for Critical and Non-Critical
                color_map = {'Critical': 'red', 'Non-Critical': 'green'}
                fig_priority = px.bar(
                    priority_chart,
                    x='priority',
                    y='quantity',
                    title='Priority Distribution',
                    color='priority',
                    color_discrete_map=color_map
                )
                fig_priority.update_layout(
                    font=dict(size=22),
                    legend=dict(font=dict(size=20)),
                    xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    title_font=dict(size=26)
                )
                fig_priority.update_layout(
                    font=dict(size=22),
                    legend=dict(font=dict(size=20)),
                    xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    title_font=dict(size=26)
                )
                st.plotly_chart(fig_priority, use_container_width=True)
        with c2:
            if {'tower','quantity'}.issubset(resource_df.columns):
                tower_chart = resource_df.groupby('tower')['quantity'].sum().reset_index().rename(columns={'tower':'Technology/Tower'})
                # Assign colors for towers A, B, C
                color_map = {'A': '#636EFA', 'B': '#EF553B', 'C': '#00CC96'}
                tower_chart['color'] = tower_chart['Technology/Tower'].map(color_map).fillna('#AB63FA')
                fig_tower = px.bar(
                    tower_chart,
                    y='Technology/Tower',
                    x='quantity',
                    orientation='h',
                    title='Tower Distribution',
                    color='Technology/Tower',
                    color_discrete_map=color_map
                )
                fig_tower.update_layout(
                    font=dict(size=22),
                    legend=dict(font=dict(size=20)),
                    xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    title_font=dict(size=26)
                )
                fig_tower.update_layout(
                    font=dict(size=22),
                    legend=dict(font=dict(size=20)),
                    xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    title_font=dict(size=26)
                )
                st.plotly_chart(fig_tower, use_container_width=True)
        st.markdown("---")
    with tab_skills_status:
        # ROW 3: 2 Bar Charts (Top Open Skills vs Closed & Open/Closed by Tower) - Now Plotly
        c5, c6 = st.columns(2)
        with c5:
            if {'skillRole','sourcingStatus','quantity'}.issubset(resource_df.columns):
                open_by_skill = resource_df.loc[resource_df['sourcingStatus'].apply(_def_is_open)].groupby('skillRole')['quantity'].sum()
                closed_by_skill = resource_df.loc[resource_df['sourcingStatus'].apply(_def_is_closed)].groupby('skillRole')['quantity'].sum()
                skill_chart = pd.DataFrame({'Open': open_by_skill, 'Closed': closed_by_skill}).fillna(0).sort_values('Open', ascending=False).head(10).reset_index()
                # --- Plotly Bar Chart Implementation (Melt/Unpivot for grouped bars if desired, but using 'skillRole' as x and 'Open'/'Closed' as y works best here) ---
                # To get a stacked/grouped bar, we reshape the data or use two separate bars. For simplicity and standard Plotly look, we reshape:
                skill_chart_melted = skill_chart.melt(id_vars='skillRole', value_vars=['Open', 'Closed'], var_name='Status', value_name='Quantity')
                fig_skill = px.bar(skill_chart_melted,
                                x='skillRole',
                                y='Quantity',
                                color='Status',
                                barmode='group', # Grouped bars for comparison
                                title='Top 10 Open Skills vs Closed')
                fig_skill.update_layout(
                    font=dict(size=22),
                    legend=dict(font=dict(size=20)),
                    xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    title_font=dict(size=26)
                )
                st.plotly_chart(fig_skill, use_container_width=True)
                # ----------------------------------------------------------------------------------------------------------------------------------------------
        with c6:
            if {'tower','sourcingStatus','quantity'}.issubset(resource_df.columns):
                open_by_tower = resource_df.loc[resource_df['sourcingStatus'].apply(_def_is_open)].groupby('tower')['quantity'].sum()
                closed_by_tower = resource_df.loc[resource_df['sourcingStatus'].apply(_def_is_closed)].groupby('tower')['quantity'].sum()
                tw_chart = pd.DataFrame({'Open': open_by_tower, 'Closed': closed_by_tower}).fillna(0).sort_values('Open', ascending=False).reset_index()
                # --- Plotly Bar Chart Implementation ---
                tw_chart_melted = tw_chart.melt(id_vars='tower', value_vars=['Open', 'Closed'], var_name='Status', value_name='Quantity')
                fig_tw = px.bar(tw_chart_melted,
                                x='tower',
                                y='Quantity',
                                color='Status',
                                barmode='group',
                                title='Open/Closed Status by Tower')
                fig_tw.update_layout(
                    font=dict(size=22),
                    legend=dict(font=dict(size=20)),
                    xaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    yaxis=dict(title_font=dict(size=22), tickfont=dict(size=18)),
                    title_font=dict(size=26)
                )
                st.plotly_chart(fig_tw, use_container_width=True)
                # -------------------------------------
        st.markdown("---")
    # New subtab: Open vs Closed & Backfill summary
    with tab_status_backfill:
        c7, c8 = st.columns(2)
        with c7:
            if {'sourcingStatus','quantity'}.issubset(resource_df.columns):
                open_sum = resource_df.loc[resource_df['sourcingStatus'].apply(_def_is_open), 'quantity'].sum()
                closed_sum = resource_df.loc[resource_df['sourcingStatus'].apply(_def_is_closed), 'quantity'].sum()
                fig_oc = px.pie(pd.DataFrame({"name":["Open","Closed"],"value":[open_sum, closed_sum]}), names='name', values='value', title='Open vs Closed Positions')
                # show labels and percentages inside slices, hide external legend
                fig_oc.update_traces(textposition='inside', textinfo='label+percent', insidetextfont=dict(size=16))
                fig_oc.update_layout(
                    showlegend=False,
                    font=dict(size=18),
                    title_font=dict(size=22)
                )
                st.plotly_chart(fig_oc, use_container_width=True)
        with c8:
            if {'typeOfBackFill','quantity'}.issubset(resource_df.columns):
                bf = resource_df.groupby('typeOfBackFill')['quantity'].sum().reset_index()
                fig_bf = px.pie(bf, names='typeOfBackFill', values='quantity', title='Backfill Summary')
                fig_bf.update_traces(textposition='inside', textinfo='label+percent', insidetextfont=dict(size=14))
                fig_bf.update_layout(
                    showlegend=False,
                    font=dict(size=18),
                    title_font=dict(size=22)
                )
                st.plotly_chart(fig_bf, use_container_width=True)
        st.markdown("---")
    # New subtab: Revenue Loss & Delivery Risk
    with tab_rev_delivery:
        c9, c10 = st.columns(2)
        with c9:
            st.markdown("### 💰 Top Skills with Revenue Loss")
            if {'skillRole','revLoss','quantity'}.issubset(resource_df.columns):
                rev = resource_df.copy()
                rev['isRevLoss'] = rev['revLoss'].astype(str).str.upper().eq('Y')
                rev_chart = rev.loc[rev['isRevLoss']].groupby('skillRole', dropna=False)['quantity'].sum().reset_index(name='Revenue Loss Count')
                rev_chart = rev_chart[rev_chart['Revenue Loss Count'] > 0].sort_values('Revenue Loss Count', ascending=False).head(8)

                # Create bullet point list with skill roles and their counts
                st.markdown("""
                <style>
                .skill-list {
                    padding: 20px 40px;
                    border-radius: 5px;
                    margin: 10px 0;
                    font-size: 18px;
                    border: 1px solid #e5e7eb;
                }
                .skill-list li {
                    margin: 10px 0;
                }
                </style>
                """, unsafe_allow_html=True)

                bullet_points = "<ul class='skill-list'>"
                for _, row in rev_chart.iterrows():
                    bullet_points += f"<li><b>{row['skillRole']}</b>: {int(row['Revenue Loss Count'])} positions</li>"
                bullet_points += "</ul>"

                st.markdown(bullet_points, unsafe_allow_html=True)
        with c10:
            if {'deliveryRisk','quantity'}.issubset(resource_df.columns):
                deliv = resource_df.groupby('deliveryRisk')['quantity'].sum().reset_index()
                # Replace Y/N with descriptive labels
                deliv['deliveryRisk'] = deliv['deliveryRisk'].replace({
                    'Y': 'Delivery Risk',
                    'y': 'Delivery Risk',
                    'N': 'No Risk',
                    'n': 'No Risk'
                })
                total = deliv['quantity'].sum()
                deliv['percentage'] = (deliv['quantity'] / total * 100).round(1)

                # Custom color map for risk categories
                color_map = {
                    'Delivery Risk': '#FF4B4B',  # Red
                    'No Risk': '#2E8B57'         # Green
                }

                # --- Plotly Pie Chart Implementation ---
                fig_deliv = px.pie(
                    deliv,
                    names='deliveryRisk',
                    values='quantity',
                    title='Delivery Risk Summary',
                    hover_data=['percentage'],
                    custom_data=['percentage'],
                    color='deliveryRisk',
                    color_discrete_map=color_map
                )

                fig_deliv.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    insidetextfont=dict(size=16)
                )

                fig_deliv.update_layout(
                    showlegend=False,
                    font=dict(size=18),
                    title_font=dict(size=22),
                    uniformtext_minsize=12,
                    uniformtext_mode='hide'
                )
                st.plotly_chart(fig_deliv, use_container_width=True)
                # -------------------------------------
        st.markdown("---")
    with Req_Type_and_Location_Insights:
        # ROW 6: Req Type and Location Insights - Already Plotly
        c11, c12 = st.columns(2)
        with c11:
            if {'reqType','quantity'}.issubset(resource_df.columns):
                nvb = resource_df.groupby('reqType')['quantity'].sum().reset_index()
                fig_nb = px.pie(nvb, names='reqType', values='quantity', title='New vs Backfill Requirements')
                fig_nb.update_traces(textposition='inside', textinfo='label+percent', insidetextfont=dict(size=14))
                fig_nb.update_layout(
                    showlegend=False,
                    font=dict(size=18),
                    title_font=dict(size=22)
                )
                st.plotly_chart(fig_nb, use_container_width=True)
        with c12:
            if {'location','quantity'}.issubset(resource_df.columns):
                loc_sum = resource_df.groupby('location')['quantity'].sum().reset_index(name='Quantity')
                fig_loc_det = px.pie(loc_sum, names='location', values='Quantity', title='Location Insights')
                fig_loc_det.update_traces(textposition='inside', textinfo='label+percent', insidetextfont=dict(size=12))
                fig_loc_det.update_layout(
                    showlegend=False,
                    font=dict(size=16),
                    title_font=dict(size=20)
                )
                st.plotly_chart(fig_loc_det, use_container_width=True)
        st.markdown("---")
    # ----- Manage Resources -----
# Assuming this elif is part of a larger conditional block (e.g., if/elif/else)

# Assuming this is inside your main application flow:

# ... (other if/elif statements)

elif st.session_state.current_tab == "details":
    
    st.subheader("📋 Resource Details")

    if st.session_state.resource_df.empty:
        st.warning("No data to display. Please ensure the Excel file is correctly loaded.")
         

    # --- Start with a copy of the full, loaded dataframe ---
    df_show = st.session_state.resource_df.copy() 

    # --- NEW CRITICAL STEP: Ensure Priority Column Names are Clean ---
    # Find all columns that contain 'priortty' or 'priority' (case-insensitive)
    priority_cols = [col for col in df_show.columns if 'prior' in col.lower()]
    
    # Standardize the name of the column used for priority filtering
    # Assuming 'Priortty (High, low)' is the actual column name used in your logic
    # and we want to rename it for clarity, then rename it back later if needed.
    
    # Let's check for the exact column name used in your priority logic:
    if "Priortty (High, low)" in df_show.columns:
        df_show = df_show.rename(columns={"Priortty (High, low)": "Priority_Flag_Internal"})
    # --- END NEW CRITICAL STEP ---
    
    # Search and filter inputs
    filt_col1, filt_col2 = st.columns([2, 1])
    with filt_col1:
        txt_search = st.text_input("Search skillRole / projectMapping / requirementID")
    with filt_col2:
        chosen_priority = st.selectbox("Filter by priority", options=["All", "Critical", "Non-Critical"], index=0)


    # 1. Apply text search filter
    if txt_search:
        s = txt_search.lower()
        
        df_show = df_show[
                df_show["skillRole"].astype(str).str.lower().str.contains(s) |
                df_show["projectMapping"].astype(str).str.lower().str.contains(s) |
                df_show["requirementID"].astype(str).str.lower().str.contains(s) |
                df_show["commentsInDetail"].astype(str).str.lower().str.contains(s)
            ]

        

    # 2. Apply priority filter
    if chosen_priority.lower() != "all":
        now = datetime.now()

        def is_high(row):
            sourcing = str(row.get("sourcingStatus", "")).strip().lower()
            if not sourcing.startswith("open"): return False
            fd = row.get("fulfilmentDateCutoff")
            fd_dt = pd.to_datetime(fd, errors="coerce") if pd.notna(fd) else None
            cutoff_passed = pd.notna(fd_dt) and (fd_dt.year < now.year or (fd_dt.year == now.year and fd_dt.month <= now.month))
            rev = str(row.get("revLoss", "")).strip().lower()
            rev_loss = rev in ("y", "yes", "true", "1")
            dr = str(row.get("deliveryRisk", "")).strip().lower()
            delivery_risk = dr in ("y", "yes", "true", "1")
            
            # CRITICAL ADJUSTMENT: Use the potentially renamed internal column or the original
            priority = str(row.get("Priority_Flag_Internal", row.get("Priortty (High, low)", ""))).strip().lower()
            priority_flag = priority == "critical"
            return cutoff_passed or rev_loss or delivery_risk or priority_flag

        def is_low(row):
            sourcing = str(row.get("sourcingStatus", "")).strip().lower()
            if not sourcing.startswith("open"): return False
            return not is_high(row)

        if chosen_priority.lower() == "critical":
            df_show = df_show[df_show.apply(is_high, axis=1)]
        elif chosen_priority.lower() == "non-critical":
            df_show = df_show[df_show.apply(is_low, axis=1)]

    st.markdown("### ✏️ Edit Resource Table")
    
    # --- FINAL CHECK BEFORE EDITOR ---
    # Ensure df_show columns are unique here one last time (though they should be from the initial load)
    df_show.columns = make_columns_fully_unique(df_show.columns)
    
    # Display editable data editor
    editable_df = st.data_editor(df_show, use_container_width=True, hide_index=True)
    
    if st.button("💾 Save Changes"):
        try:
            # Save the edited data back to the file (this DataFrame has unique names)
            editable_df.to_excel("C:/Users/2387781/Downloads/raw_data.xlsx", index=False)
            
            # Update the session state with the saved data (which also has unique names)
            st.session_state.resource_df = editable_df.copy() 
            
            st.success("Changes saved successfully to raw_data.xlsx!")
            st.rerun() 

        except Exception as e:
            st.error(f"Failed to save changes: {e}")
    
# The second half of the code (tab2, tab3, tab4 logic) will follow here.
# ----- Resource Dashboard -----
# Assuming _def_is_open, _def_is_closed, compute_priority_for_row, ensure_requirement_ids, write_back_excel, pd, st, px, datetime are defined/imported elsewhere.
# ----- Manage Resources -----
elif st.session_state.current_tab == "manage":
    st.subheader("⚙️ Manage Resources")
    subtab1, subtab2 = st.tabs(["➕ Add requirement", "🗑️ Requirement closure"])
    # ---------------------- ADD RESOURCE TAB ----------------------
    with subtab1:
        st.markdown("Fill the form to add a new requirement.")
        with st.form("add_requirement_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                skillRole = st.text_input("Skill / Role", value="")
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                tower = st.text_input("Tower", value="")
                location = st.selectbox("Location", options=["", "Offshore", "Onsite"], index=0)
                aiaType = st.selectbox("AIA Type", options=["AIA", "NON AIA", "Unknown"], index=2)
                reqType = st.selectbox("Req Type", options=["New", "Backfill", "Unknown"], index=2)
            with c2:
                fulfilmentDateCutoff = st.date_input("Fulfilment Date Cutoff", value=None)
                revLoss = st.selectbox("Revenue Loss (Yes/No)", options=["", "Yes", "No"], index=0)
                deliveryRisk = st.selectbox("Delivery Risk (Yes/No)", options=["", "Yes", "No"], index=0)
                sourcingStatus = st.selectbox("Sourcing Status", options=["Open", "Closed", ""], index=0)
                projectMapping = st.text_input("Project Mapping", value="")
                commentsInDetail = st.text_area("Comments")
            submitted = st.form_submit_button("Submit & Save")
            if submitted:
                new_row = {
                    "skillRole": skillRole or pd.NA,
                    "quantity": int(quantity),
                    "tower": tower or pd.NA,
                    "location": location or pd.NA,
                    "aiaType": aiaType or pd.NA,
                    "reqType": reqType or pd.NA,
                    "fulfilmentDateCutoff": pd.to_datetime(fulfilmentDateCutoff) if fulfilmentDateCutoff else pd.NaT,
                    "revLoss": revLoss or pd.NA,
                    "deliveryRisk": deliveryRisk or pd.NA,
                    "sourcingStatus": sourcingStatus or pd.NA,
                    "projectMapping": projectMapping or pd.NA,
                    "commentsInDetail": commentsInDetail or pd.NA,
                    "requirementReceivedDate": pd.Timestamp.now()
                }
                sdf = st.session_state.resource_df
                sdf = pd.concat([sdf, pd.DataFrame([new_row])], ignore_index=True)
                sdf = ensure_requirement_ids(sdf, id_col="requirementID")
                sdf["priority"] = sdf.apply(compute_priority_for_row, axis=1)
                st.session_state.resource_df = sdf
                success, err = write_back_excel(
                    EXCEL_PATH, sdf, st.session_state.so_df, st.session_state.emp_df,
                    res_name=res_sheet_name or "Resources",
                    so_name=so_sheet_name or "SO",
                    emp_name=emp_sheet_name or "Employees"
                )
                if success:
                    st.success("New requirement added and Excel saved.")
                    st.rerun()
                else:
                    st.error(f"Failed to save Excel: {err}")
    # ---------------------- RESOURCE CLOSURE TAB ----------------------
    with subtab2:
        df_show = st.session_state.resource_df.copy()
        if "requirementID" not in df_show.columns or df_show.empty:
            st.info("No deletable rows found.")
        else:
            open_tab, fulfilled_tab, closed_tab = st.tabs([
                "📂 Open Requirements",
                "✅ Fulfilled Requirements",
                "📁 Closed Requirements"
            ])
            for label, tab_df in zip(
                ["Open - Not Identified", "Fulfilled", "Closed"],
                [open_tab, fulfilled_tab, closed_tab]
            ):
                with tab_df:
                    filtered_df = df_show[df_show["sourcingStatus"] == label].copy()
                    if filtered_df.empty:
                        st.warning(f"No {label.lower()} requirements found.")
                    else:
                        del_ids = st.multiselect(
                            f"Select {label} Requirement IDs to Delete",
                            options=list(filtered_df["requirementID"]),
                            key=f"delete_{label.lower().replace(' ', '_')}_ids"
                        )
                        if del_ids and st.button(
                            f"❌ Delete Selected {label} Rows",
                            key=f"delete_{label.lower().replace(' ', '_')}_btn"
                        ):
                            updated_df = st.session_state.resource_df[
                                ~st.session_state.resource_df["requirementID"].isin(del_ids)
                            ].copy()
                            updated_df["Sno"] = range(1, len(updated_df) + 1)
                            cols = ["Sno"] + [col for col in updated_df.columns if col != "Sno"]
                            updated_df = updated_df[cols]
                            success, err = write_back_excel(
                                EXCEL_PATH,
                                updated_df,
                                st.session_state.so_df,
                                st.session_state.emp_df,
                                res_name=res_sheet_name or "Resources",
                                so_name=so_sheet_name or "SO",
                                emp_name=emp_sheet_name or "Employees"
                            )
                            if success:
                                st.session_state.resource_df = updated_df.drop(columns=["Sno"], errors="ignore")
                                st.success(f"Deleted {label.lower()} requirements: {', '.join(del_ids)}")
                                st.rerun()
                            else:
                                st.error(f"Failed to save Excel after delete: {err}")
                    st.dataframe(
                        filtered_df.drop(columns=["sno"], errors="ignore").reset_index(drop=True),
                        use_container_width=True,
                        hide_index=True
                )
elif st.session_state.current_tab == "critical":
    critical_df = resource_df.copy()
    # ✅ Ensure priority column is populated
    if 'priority' not in critical_df.columns or critical_df['priority'].isna().all():
        critical_df['priority'] = critical_df.apply(compute_priority_for_row, axis=1)
    # Convert fulfilmentDateCutoff safely
    if 'fulfilmentDateCutoff' in critical_df.columns:
        critical_df['fulfilmentDateCutoff'] = pd.to_datetime(
            critical_df['fulfilmentDateCutoff'], errors='coerce'
        )
    # -------------------------
    # 1. Critical Requirements Metrics
    # -------------------------
    st.markdown("### 📊 Critical Requirements Metrics")
    if not critical_df.empty:
        total_critical = int(critical_df['quantity'].sum())
        revenue_loss_count = int(
            critical_df[critical_df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])]['quantity'].sum()
        )
        delivery_risk_count = int(
            critical_df[critical_df['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true'])]['quantity'].sum()
        )
        urgent_cutoff_count = 0
        if 'fulfilmentDateCutoff' in critical_df.columns:
            urgent_cutoff_count = int(
                critical_df[
                    pd.to_datetime(critical_df['fulfilmentDateCutoff'], errors='coerce') <= pd.Timestamp.now()
                ]['quantity'].sum()
            )
        # First row
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown(
                f"""
                <div class="kpi-card" style="text-align:center">
                    <div class="kpi-title">Total Critical Positions</div>
                    <div class="kpi-value">{total_critical}</div>
                </div>
                """, unsafe_allow_html=True
            )
        with row1_col2:
            st.markdown(
                f"""
                <div class="kpi-card loss" style="text-align:center">
                    <div class="kpi-title">Revenue Loss Risk</div>
                    <div class="kpi-value">{revenue_loss_count}</div>
                </div>
                """, unsafe_allow_html=True
            )
        # Second row
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.markdown(
                f"""
                <div class="kpi-card info" style="text-align:center">
                    <div class="kpi-title">Delivery Risk</div>
                    <div class="kpi-value">{delivery_risk_count}</div>
                </div>
                """, unsafe_allow_html=True
            )
        with row2_col2:
            st.markdown(
                f"""
                <div class="kpi-card warn" style="text-align:center">
                    <div class="kpi-title">Past Cut-off Date</div>
                    <div class="kpi-value">{urgent_cutoff_count}</div>
                </div>
                """, unsafe_allow_html=True
            )
    st.markdown("---")
    # -------------------------
    # 2. Recommended Actions
    # -------------------------
    st.markdown("### 🎯 Recommended Actions")
    action_col1, action_col2 = st.columns(2)
    if critical_df.empty:
        st.info("✅ No critical requirements found matching the strict criteria!")
        st.markdown("**Criteria:** Critical Priority $\\lor$ (Fulfilment Cutoff in current or previous months up to current month) $\\lor$ (Revenue Loss OR Delivery Risk = Yes)")
    else:
        with action_col1:
            st.markdown("**Immediate Actions Required:**")
            past_cutoff = critical_df[
                pd.to_datetime(critical_df['fulfilmentDateCutoff'], errors='coerce') <= pd.Timestamp.now()
            ]
            if not past_cutoff.empty:
                st.error(f"🚨 {past_cutoff['quantity'].sum()} positions past cut-off date - ESCALATE IMMEDIATELY")
            rev_loss = critical_df[critical_df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])]
            if not rev_loss.empty:
                st.warning(f"💰 {rev_loss['quantity'].sum()} positions causing revenue loss - PRIORITIZE")
            del_risk = critical_df[critical_df['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true'])]
            if not del_risk.empty:
                st.warning(f"⚠️ {del_risk['quantity'].sum()} positions at delivery risk - ACCELERATE")
        with action_col2:
            st.markdown("**🎯 Critical Resource Allocation Insights:**")
            top_skills = critical_df.groupby('skillRole')['quantity'].sum().sort_values(ascending=False).head(3)
            if not top_skills.empty:
                st.info(f"🎯 Focus recruitment on: {', '.join(top_skills.index[:3])}")
            top_locations = critical_df.groupby('location')['quantity'].sum().sort_values(ascending=False).head(2)
            if not top_locations.empty:
                st.info(f"📍 Geographic focus: {', '.join(top_locations.index[:2])}")
            top_towers = critical_df.groupby('tower')['quantity'].sum().sort_values(ascending=False).head(2)
            if not top_towers.empty:
                st.info(f"🏗️ Technology focus: {', '.join(top_towers.index[:2])}")
    st.markdown("---")
    # --- Define individual conditions ---
    # Condition 1: fulfilmentDateCutoff within current or previous months (no future months)
    if 'fulfilmentDateCutoff' in critical_df.columns:
        now = pd.Timestamp.now()
        end_of_current_month = (
            now.replace(day=1) + pd.offsets.MonthEnd(0)
        ).normalize() + pd.Timedelta(hours=23, minutes=59, seconds=59)
        cutoff_condition = (
            critical_df['fulfilmentDateCutoff'].notna()
            & (critical_df['fulfilmentDateCutoff'] <= end_of_current_month)
        )
    else:
        cutoff_condition = pd.Series([False] * len(critical_df))
    # Condition 2: Revenue Loss = Yes
    if 'revLoss' in critical_df.columns:
        rev_loss_condition = critical_df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])
    else:
        rev_loss_condition = pd.Series([False] * len(critical_df))
    # Condition 3: Delivery Risk = Yes
    if 'deliveryRisk' in critical_df.columns:
        delivery_risk_condition = critical_df['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true'])
    else:
        delivery_risk_condition = pd.Series([False] * len(critical_df))
    # Condition 4: Priority = Critical (was High)
    if 'priority' in critical_df.columns:
        priority_map = {1: 'Critical', 2: 'Non-Critical', 3: 'Non-Critical', 'High': 'Critical', 'Medium': 'Non-Critical', 'Low': 'Non-Critical'}
        critical_df['priority'] = critical_df['priority'].replace(priority_map)
        priority_condition = critical_df['priority'].astype(str).str.lower().eq('critical')
    else:
        priority_condition = pd.Series([False] * len(critical_df))
    # --- Combine all conditions using OR ---
    combined_condition = cutoff_condition | rev_loss_condition | delivery_risk_condition | priority_condition
    # Apply combined condition
    critical_df = critical_df[combined_condition]
    # REMOVE closed sourcingStatus rows so "Closed" records are not shown in Tab 4
    if 'sourcingStatus' in critical_df.columns:
        critical_df = critical_df.loc[~critical_df['sourcingStatus'].apply(_def_is_closed)].copy()
    # -------------------------
    # Recommended Actions (moved to top of Tab 4 for visibility)
    # -------------------------
    # (Recommended Actions moved earlier) Continue with any remaining UI elements
    # -------------------------
    # Visualizations (TOP of Tab 4)
    # -------------------------
    tab_urgency, tab_skills_loc, tab_tower_aging, tab_risk_status = st.tabs([
        "⏰ Urgency & Revenue", "🎯 Skills & Location", "🏢 Tower & Aging", "📊 Risk & Status"
    ])
    with tab_urgency:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⏰ Critical Urgency by Cut-off Date")
            if 'fulfilmentDateCutoff' in critical_df.columns and 'quantity' in critical_df.columns:
                urgency_data = critical_df.copy()
                urgency_data['fulfilmentDateCutoff'] = pd.to_datetime(urgency_data['fulfilmentDateCutoff'], errors='coerce')
                urgency_data['days_to_cutoff'] = (urgency_data['fulfilmentDateCutoff'] - pd.Timestamp.now()).dt.days
                urgency_data['urgency_level'] = urgency_data['days_to_cutoff'].apply(
                    lambda x: 'Past Due' if x < 0 else 'Critical (0-2 days)' if x <= 2 else 'Urgent (3-10 days)'
                )
                urgency_chart = urgency_data.groupby('urgency_level')['quantity'].sum().reset_index()
                fig_urgency = px.bar(urgency_chart, x='urgency_level', y='quantity',
                                     title='Critical Urgency Distribution',
                                     color='quantity', color_continuous_scale='Reds')
                fig_urgency.update_layout(
                    showlegend=False,
                    title='',
                    font={'color': '#f9fafb'},
                    xaxis={'tickfont': {'color': '#f9fafb'}, 'titlefont': {'color': '#f9fafb'}},
                    yaxis={'tickfont': {'color': '#f9fafb'}, 'titlefont': {'color': '#f9fafb'}},
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_urgency, use_container_width=True)
        with c2:
            st.subheader("💰 Critical Skills with Revenue Loss")
            if {'skillRole', 'revLoss', 'quantity'}.issubset(critical_df.columns):
                rev_loss_data = critical_df[critical_df['revLoss'].astype(str).str.upper().isin(['Y', 'YES'])]
                if not rev_loss_data.empty:
                    rev_loss_chart = rev_loss_data.groupby('skillRole')['quantity'].sum().reset_index()
                    rev_loss_chart = rev_loss_chart.sort_values('quantity', ascending=False).head(8)
                    fig_rev = px.bar(rev_loss_chart, x='quantity', y='skillRole', orientation='h',
                                     title='Critical Skills with Revenue Loss Risk',
                                     color='quantity', color_continuous_scale='Oranges')
                    fig_rev.update_layout(
                        showlegend=False,
                        title='',
                        font={'color': '#f9fafb'},
                        xaxis={'tickfont': {'color': '#f9fafb'}, 'titlefont': {'color': '#f9fafb'}},
                        yaxis={'tickfont': {'color': '#f9fafb'}, 'titlefont': {'color': '#f9fafb'}},
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_rev, use_container_width=True)
                else:
                    st.info("No revenue loss risks in critical requirements")
    with tab_skills_loc:
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("🎯 Critical Skills Distribution")
            if {'skillRole', 'quantity'}.issubset(critical_df.columns):
                skills_chart = critical_df.groupby('skillRole')['quantity'].sum().reset_index()
                skills_chart = skills_chart.sort_values('quantity', ascending=False).head(10)
                fig_skills = px.treemap(skills_chart, path=['skillRole'], values='quantity',
                                         title='Critical Skills Distribution',
                                         color='quantity', color_continuous_scale='Viridis')
                fig_skills.update_layout(showlegend=False, title='')
                st.plotly_chart(fig_skills, use_container_width=True)
        with c4:
            st.subheader("📍 Critical Requirements by Location")
            if {'location', 'quantity'}.issubset(critical_df.columns):
                location_data = critical_df.copy()
                location_data['location'] = location_data['location'].fillna('Not Specified')
                location_chart = location_data.groupby('location')['quantity'].sum().reset_index()
                fig_location = px.pie(location_chart, names='location', values='quantity',
                                         title='Geographic Distribution of Critical Requirements',
                                         color_discrete_sequence=px.colors.qualitative.Set3)
                fig_location.update_layout(showlegend=True, title='')
                st.plotly_chart(fig_location, use_container_width=True)
    with tab_tower_aging:
        c5, c6 = st.columns(2)
        with c5:
            st.subheader("🏢 Critical Requirements by Tower")
            if {'tower', 'quantity'}.issubset(critical_df.columns):
                tower_chart = critical_df.groupby('tower')['quantity'].sum().reset_index()
                tower_chart = tower_chart.sort_values('quantity', ascending=False)
                fig_tower = px.bar(tower_chart, x='tower', y='quantity',
                                     title='Critical Requirements by Technology Tower',
                                     color='quantity', color_continuous_scale='Blues')
                fig_tower.update_layout(showlegend=False, title='')
                st.plotly_chart(fig_tower, use_container_width=True)
        with c6:
            st.subheader("📅 Critical Requirements Aging")
            if 'requirementReceivedDate' in critical_df.columns:
                aging_data = critical_df.copy()
                aging_data['requirementReceivedDate'] = pd.to_datetime(aging_data['requirementReceivedDate'], errors='coerce')
                aging_data['days_open'] = (pd.Timestamp.now() - aging_data['requirementReceivedDate']).dt.days
                aging_data['aging_category'] = aging_data['days_open'].apply(
                    lambda x: 'Critical (> 60 days)' if x > 60 else 'Urgent (30-60 days)' if x > 30 else 'Recent (< 30 days)'
                )
                aging_chart = aging_data.groupby('aging_category')['quantity'].sum().reset_index()
                fig_aging = px.bar(aging_chart, x='aging_category', y='quantity',
                                     title='Aging Distribution of Critical Requirements',
                                     color='quantity', color_continuous_scale='Reds')
                fig_aging.update_layout(showlegend=False, title='')
                st.plotly_chart(fig_aging, use_container_width=True)
    with tab_risk_status:
        c7, c8 = st.columns(2)
        with c7:
            st.subheader("⚠️ Critical Risk Level Distribution")
            risk_data = critical_df.copy()
            risk_data['risk_score'] = 0
            # Calculate risk score for critical requirements
            risk_data.loc[risk_data['revLoss'].astype(str).str.upper().isin(['Y', 'YES']), 'risk_score'] += 2
            risk_data.loc[risk_data['deliveryRisk'].astype(str).str.lower().isin(['yes', 'y', 'true']), 'risk_score'] += 2
            if 'fulfilmentDateCutoff' in risk_data.columns:
                risk_data['fulfilmentDateCutoff'] = pd.to_datetime(risk_data['fulfilmentDateCutoff'], errors='coerce')
                past_cutoff = risk_data['fulfilmentDateCutoff'] <= pd.Timestamp.now()
                risk_data.loc[past_cutoff, 'risk_score'] += 3
                near_cutoff = (risk_data['fulfilmentDateCutoff'] - pd.Timestamp.now()).dt.days <= 2
                risk_data.loc[near_cutoff, 'risk_score'] += 2
            risk_data['risk_level'] = risk_data['risk_score'].apply(
                lambda x: 'Critical (5+)' if x >= 5 else 'High (3-4)' if x >= 3 else 'Medium (1-2)' if x >= 1 else 'Low (0)'
            )
            risk_chart = risk_data.groupby('risk_level')['quantity'].sum().reset_index()
            fig_risk = px.pie(risk_chart, names='risk_level', values='quantity',
                              title='Critical Risk Level Distribution',
                              color_discrete_sequence=['#FF0000', '#FFA500', '#FFFF00', '#00FF00'])
            fig_risk.update_layout(showlegend=True, title='')
            st.plotly_chart(fig_risk, use_container_width=True)
        with c8:
            st.subheader("📊 Critical Requirements Sourcing Status")
            if {'sourcingStatus', 'quantity'}.issubset(critical_df.columns):
                status_chart = critical_df.groupby('sourcingStatus')['quantity'].sum().reset_index()
                fig_status = px.bar(status_chart, x='sourcingStatus', y='quantity',
                                     title='Sourcing Status of Critical Requirements',
                                     color='quantity', color_continuous_scale='RdYlGn_r')
                fig_status.update_layout(showlegend=False, title='')
                st.plotly_chart(fig_status, use_container_width=True)
    st.markdown("---")
    # -------------------------
    # Now Table + UI filters (after visualizations)
    # -------------------------
    st.markdown("### 📋 Detailed Critical Requirements")
    # Add filters for the detailed table
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    # Build safe options lists (handle empty df)
    tower_options = ["All"]
    location_options = ["All"]
    status_options = ["All"]
    if not critical_df.empty:
        if 'tower' in critical_df.columns:
            tower_options += list(critical_df['tower'].dropna().unique())
        if 'location' in critical_df.columns:
            location_options += list(critical_df['location'].dropna().unique())
        if 'sourcingStatus' in critical_df.columns:
            status_options += list(critical_df['sourcingStatus'].dropna().unique())
    import streamlit as st

    # Layout: Full-width dropdowns in two columns
    filter_col1, filter_col2 = st.columns([1, 1])

    with filter_col1:
        tower_filter = st.selectbox(
            "Filter by Tower",
            options=tower_options,
            key="critical_tower_filter",
            label_visibility="visible"
        )

    with filter_col2:
        location_filter = st.selectbox(
            "Filter by Location",
            options=location_options,
            key="critical_location_filter",
            label_visibility="visible"
        )

    # Apply filters to the dataframe
    filtered_critical_df = critical_df.copy()

    # Apply UI filters to create the displayed table
    filtered_critical_df = critical_df.copy()
    if tower_filter != "All":
        filtered_critical_df = filtered_critical_df[filtered_critical_df['tower'] == tower_filter]
    if location_filter != "All":
        filtered_critical_df = filtered_critical_df[filtered_critical_df['location'] == location_filter]
    # Display filtered table
    if not filtered_critical_df.empty:
        # Select key columns for display (as you defined)
        display_cols = ['requirementID', 'skillRole', 'quantity', 'tower', 'location',
                        'priority', 'sourcingStatus', 'revLoss', 'deliveryRisk',
                        'fulfilmentDateCutoff']
        # Only show columns that exist
        available_cols = [col for col in display_cols if col in filtered_critical_df.columns]
        # Format date columns nicely if present
        if 'fulfilmentDateCutoff' in filtered_critical_df.columns:
            display_df = filtered_critical_df.copy()
            display_df['fulfilmentDateCutoff'] = display_df['fulfilmentDateCutoff'].dt.strftime('%Y-%m-%d').fillna('')
        else:
            display_df = filtered_critical_df.copy()
        st.dataframe(display_df[available_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
        # Export option - PDF format using your existing PDF generator
        try:
            pdf_data = generate_critical_report_pdf(filtered_critical_df[available_cols])
            st.download_button(
                label="📥 Download Critical Requirements Report (PDF)",
                data=pdf_data,
                file_name=f"critical_requirements_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")
    else:
        st.info("No critical requirements match the selected filters or date criteria (current month + prior months only).")
    st.markdown("---")
