import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1  # Essential for converting numbers to A1 letters
import datetime

# --- 1. PROFESSIONAL UI CONFIGURATION ---
st.set_page_config(page_title="2026 Mission Control", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background-color: #21262d;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 8px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #58a6ff;
        background-color: #30363d;
    }
    .status-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE DIRECT CLOUD CONNECTION ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def connect_to_sheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # YOUR SHEET ID
        SHEET_ID = "1RSvGxbjWqO1tNlRYbEg6ck3b4G_KYqO3v5OwjVGoyWw" 
        spreadsheet = client.open_by_key(SHEET_ID)
        return spreadsheet.worksheet("Daily Log")
    except Exception as e:
        st.error(f"📡 Connection Failed: {str(e)}")
        return None

sheet = connect_to_sheet()

if sheet:
    # --- 3. UNIVERSAL DATE LOGIC ---
    today = datetime.date.today()
    # Checking common formats (d/m/yyyy and dd/mm/yyyy)
    possible_formats = [today.strftime("%-d/%-m/%Y"), today.strftime("%d/%m/%Y"), today.strftime("%#d/%#m/%Y")]
    
    dates_row = sheet.row_values(1, value_render_option='FORMATTED_VALUE')
    clean_dates = [str(d).strip() for d in dates_row]

    col_idx = None
    current_fmt = None
    for fmt in possible_formats:
        if fmt in clean_dates:
            col_idx = clean_dates.index(fmt) + 1
            current_fmt = fmt
            break

    if col_idx:
        # Fetching Column A (Tasks) and the current column's status
        tasks = sheet.col_values(1)[1:17] 
        current_status = sheet.col_values(col_idx)[1:17]
        
        # --- 4. INTEGRATED A-B-C-D LOGIC (Fixed for gspread) ---
        # We grab the last 10 columns for analysis
        start_col = max(2, col_idx - 9)
        
        # Create a range string like "B2:K17"
        range_to_fetch = f"{rowcol_to_a1(2, start_col)}:{rowcol_to_a1(17, col_idx)}"
        
        # Get values using the A1 range
        history_range = sheet.get(range_to_fetch)
        
        # Flatten the list of lists to count values
        flat_history = [item for sublist in history_range for item in sublist]
        stats = {
            "A (High)": flat_history.count("A"),
            "B (Med)": flat_history.count("B"),
            "C (Low)": flat_history.count("C"),
            "D (Done)": flat_history.count("D")
        }

        # --- 5. SIDEBAR & PROGRESS ---
        # We consider "TRUE" or "D" as a completed task
        completed_count = current_status.count("TRUE") + current_status.count("D")
        progress_perc = min(completed_count / 16, 1.0)
        
        with st.sidebar:
            st.title("👨‍💻 Developer Hub")
            st.metric("Daily Completion", f"{int(progress_perc * 100)}%")
            st.progress(progress_perc)
            
            st.divider()
            st.subheader("📊 10-Day Intensity (A-D)")
            for label, val in stats.items():
                st.write(f"{label}: **{val}**")
            
            st.divider()
            if st.button("🔄 Sync with Cloud"):
                st.rerun()
            
            st.info("💡 **Quick Tip:** To stop failure emails, remove `getUi()` from your Google Apps Script editor.")

        # --- 6. MAIN DASHBOARD ---
        st.title("🚀 2026 Mission Control")
        st.write(f"Logged as: `{current_fmt}` | Active Station: `{today.strftime('%A')}`")

        if progress_perc == 1.0:
            st.balloons()
            st.success("Target Achieved. All daily logs synced.")

        cols = st.columns(2)
        for i, task in enumerate(tasks):
            # Check if task is already marked done in the sheet
            is_done = False
            if i < len(current_status):
                if current_status[i] in ["TRUE", "D"]:
                    is_done = True
            
            with cols[i % 2]:
                if is_done:
                    st.markdown(f"""<div class='status-card' style='border-left: 5px solid #238636;'>
                                    <b>✅ {task}</b><br><small style='color:#8b949e;'>Synced to Cloud</small>
                                 </div>""", unsafe_allow_html=True)
                    st.write("") 
                else:
                    if st.button(f"◽ {task}", key=f"btn_{i}", use_container_width=True):
                        with st.spinner("Pushing update..."):
                            sheet.update_cell(i + 2, col_idx, "TRUE")
                            st.toast(f"Logged: {task}")
                            st.rerun()
    else:
        st.error(f"Date not found in Sheet. Checked: {possible_formats}")
        st.info(f"Make sure Row 1 of your sheet has dates formatted like 31/1/2026.")

# --- 7. FOOTER ---
st.divider()
st.caption("2026 Consistency Tracker v2.2 | Deployment: Streamlit Cloud | Engine: Python 3.13")
