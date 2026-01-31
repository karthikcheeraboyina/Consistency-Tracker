import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
import datetime

# --- 1. PROFESSIONAL UI CONFIGURATION ---
st.set_page_config(page_title="2026 Mission Control", page_icon="🚀", layout="centered")

# Restoring the original Transparent / Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        border-radius: 12px;
        height: 3.5em;
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
        background-color: #21262d;
        transform: translateY(-2px);
    }
    h1 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 2026 Mission Control")
st.caption("Consistency is the bridge between goals and accomplishment.")

# --- 2. THE DIRECT CLOUD CONNECTION ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def connect_to_sheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        SHEET_ID = "1RSvGxbjWqO1tNlRYbEg6ck3b4G_KYqO3v5OwjVGoyWw" 
        return client.open_by_key(SHEET_ID).worksheet("Daily Log")
    except Exception as e:
        st.error(f"📡 Connection Failed: {str(e)}")
        return None

sheet = connect_to_sheet()

if sheet:
    # --- 3. SMART DATE LOGIC ---
    today = datetime.date.today()
    possible_formats = [today.strftime("%-d/%-m/%Y"), today.strftime("%d/%m/%Y"), today.strftime("%#d/%#m/%Y")]
    
    dates_row = sheet.row_values(1, value_render_option='FORMATTED_VALUE')
    clean_dates = [str(d).strip() for d in dates_row]

    col_idx = None
    for fmt in possible_formats:
        if fmt in clean_dates:
            col_idx = clean_dates.index(fmt) + 1
            current_fmt = fmt
            break

    if col_idx:
        # Fetch data for tasks and current statuses
        tasks = sheet.col_values(1)[1:17] 
        current_status = sheet.col_values(col_idx)[1:17]
        
        # --- 4. A-B-C-D STATS (FIXED LOGIC) ---
        start_col = max(2, col_idx - 9)
        range_to_fetch = f"{rowcol_to_a1(2, start_col)}:{rowcol_to_a1(17, col_idx)}"
        history_range = sheet.get(range_to_fetch)
        
        flat_history = [item for sublist in history_range for item in sublist]
        stats = {
            "A (High)": flat_history.count("A"),
            "B (Med)": flat_history.count("B"),
            "C (Low)": flat_history.count("C"),
            "D (Done)": flat_history.count("D")
        }

        # --- 5. SIDEBAR & PROGRESS ---
        completed_count = current_status.count("TRUE") + current_status.count("D")
        progress_perc = min(completed_count / 16, 1.0)
        
        st.sidebar.metric("Today's Progress", f"{int(progress_perc * 100)}%")
        st.sidebar.progress(progress_perc)
        
        st.sidebar.divider()
        st.sidebar.subheader("📊 10-Day Intensity")
        for label, val in stats.items():
            st.sidebar.write(f"{label}: **{val}**")

        if st.sidebar.button("🔄 Refresh Data"):
            st.rerun()

        # --- 6. DASHBOARD UI (Transparent Buttons) ---
        st.subheader(f"Today's Objectives")
        
        col1, col2 = st.columns(2)
        
        for i, task in enumerate(tasks):
            # Check if task is done (TRUE or D)
            is_done = False
            if i < len(current_status):
                if current_status[i] in ["TRUE", "D"]:
                    is_done = True
            
            # Label logic: Fire icon for done, empty square for pending
            label = f"🔥 {task}" if is_done else f"◽ {task}"
            
            # Use columns for grid
            target_col = col1 if i % 2 == 0 else col2
            
            # If button is clicked, update sheet and refresh
            if target_col.button(label, key=f"btn_{i}", use_container_width=True, disabled=is_done):
                with st.spinner("Syncing..."):
                    sheet.update_cell(i + 2, col_idx, "TRUE")
                    st.toast(f"{task} Logged!", icon="✅")
                    st.rerun()

        if progress_perc == 1.0:
            st.balloons()

    else:
        st.warning(f"⚠️ Date {today.strftime('%d/%m/%Y')} not found in Row 1.")

# --- 7. FOOTER ---
st.divider()
st.caption("2026 Career Transition Tracker | Created by Karthik")
