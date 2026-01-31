import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
import datetime

# --- 1. PROFESSIONAL UI CONFIGURATION ---
st.set_page_config(page_title="2026 Mission Control", page_icon="🚀", layout="centered")

# Custom CSS for the "Locked Button" Transparent UI
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
    /* Style for disabled buttons to make them look "Locked/Transparent" */
    .stButton>button:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        border-color: #238636;
        color: #8b949e;
    }
    h1 { color: #58a6ff; font-family: 'Inter', sans-serif; }
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
    current_fmt = None
    for fmt in possible_formats:
        if fmt in clean_dates:
            col_idx = clean_dates.index(fmt) + 1
            current_fmt = fmt
            break

    if col_idx:
        # Fetching Tasks and Statuses
        tasks = sheet.col_values(1)[1:17] 
        current_status = sheet.col_values(col_idx)[1:17]
        
        # --- 4. A-B-C-D STATS (Using A1 Notation to prevent crash) ---
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

        # --- 5. PROGRESS & SIDEBAR ---
        completed_count = current_status.count("TRUE") + current_status.count("D")
        progress_perc = min(completed_count / 16, 1.0)
        
        with st.sidebar:
            st.metric("Today's Progress", f"{int(progress_perc * 100)}%")
            st.progress(progress_perc)
            st.divider()
            st.subheader("📊 10-Day Intensity")
            for label, val in stats.items():
                st.write(f"{label}: **{val}**")
            if st.button("🔄 Refresh Data"):
                st.rerun()

        # --- 6. THE DASHBOARD UI ---
        st.title("🚀 2026 Mission Control")
        # Keep the header you liked
        st.write(f"Logged as: `{current_fmt}` | Active Station: `{today.strftime('%A')}`")

        if progress_perc == 1.0:
            st.balloons()
            st.success("Target Achieved. Mission for the day is complete.")

        st.subheader("Today's Objectives")
        
        # Grid layout for buttons
        col1, col2 = st.columns(2)
        
        for i, task in enumerate(tasks):
            # Checking if the task is done
            is_done = i < len(current_status) and (current_status[i] in ["TRUE", "D"])
            
            # Label changes based on completion
            btn_label = f"🔥 {task}" if is_done else f"◽ {task}"
            
            target_col = col1 if i % 2 == 0 else col2
            
            # The Transparent/Locked Button Logic
            if target_col.button(btn_label, key=f"btn_{i}", use_container_width=True, disabled=is_done):
                with st.spinner("Syncing..."):
                    sheet.update_cell(i + 2, col_idx, "TRUE")
                    st.toast(f"{task} Logged!", icon="✅")
                    st.rerun()
    else:
        st.error(f"Date {today.strftime('%-d/%-m/%Y')} not found. Check Row 1.")

# --- 7. FOOTER ---
st.divider()
st.caption("2026 Career Transition Tracker | Created by Karthik")
