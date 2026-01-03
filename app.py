import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. PROFESSIONAL UI CONFIGURATION ---
st.set_page_config(page_title="2026 Mission Control", page_icon="🚀", layout="centered")

# Custom CSS for a sleek, modern Developer Dashboard
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
    .stProgress > div > div > div > div { background-color: #238636; }
    h1 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 2026 Mission Control")
st.caption("Consistency is the bridge between goals and accomplishment.")

# --- 2. THE DIRECT CLOUD CONNECTION ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource # Keeps the connection alive for speed
def connect_to_sheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # --- ACTION REQUIRED: PASTE YOUR ID HERE ---
        SHEET_ID = "1RSvGxbjWqO1tNlRYbEg6ck3b4G_KYqO3v5OwjVGoyWw" 
        
        spreadsheet = client.open_by_key(SHEET_ID)
        return spreadsheet.worksheet("Daily Log")
    except Exception as e:
        st.error(f"📡 Connection Failed: {str(e)}")
        return None

sheet = connect_to_sheet()

if sheet:
    # --- 3. SMART DATE LOGIC ---
    # We match your sheet's format: D/M/YYYY (e.g., 3/1/2026)
    today_sheet_format = datetime.date.today().strftime("%-d/%-m/%Y") 
    
    # Get all dates from Row 1
    dates_row = sheet.row_values(1, value_render_option='FORMATTED_VALUE')
    clean_dates = [str(d).strip() for d in dates_row]

    if today_sheet_format in clean_dates:
        col_idx = clean_dates.index(today_sheet_format) + 1
        
        # Get tasks from Column A and current status for progress bar
        tasks = sheet.col_values(1)[1:17] 
        current_status = sheet.col_values(col_idx)[1:17]
        
        # Calculate Progress
        completed_count = current_status.count("TRUE")
        progress_perc = completed_count / 16
        
        # --- 4. DASHBOARD UI ---
        st.sidebar.metric("Today's Progress", f"{int(progress_perc * 100)}%")
        st.sidebar.progress(progress_perc)
        st.sidebar.write(f"📅 Logged as: **{today_sheet_format}**")
        
        if st.sidebar.button("🔄 Refresh Data"):
            st.rerun()

        st.subheader(f"Today's Objectives")
        
        # Layout buttons in two columns for a neat grid on mobile
        col1, col2 = st.columns(2)
        
        for i, task in enumerate(tasks):
            # Check if already done to change the label
            is_done = i < len(current_status) and current_status[i] == "TRUE"
            label = f"🔥 {task}" if is_done else f"◽ {task}"
            
            # Place half in col1, half in col2
            target_col = col1 if i % 2 == 0 else col2
            
            if target_col.button(label, key=f"btn_{i}", use_container_width=True, disabled=is_done):
                with st.spinner("Syncing..."):
                    sheet.update_cell(i + 2, col_idx, "TRUE")
                    st.toast(f"{task} Logged!", icon="✅")
                    st.rerun() # Refresh to show progress bar update

    else:
        st.warning(f"⚠️ Date {today_sheet_format} not found in Row 1.")
        st.info(f"Python sees: {clean_dates[:5]}...")
        st.write("Ensure Row 1 has dates formatted as 1/1/2026, 2/1/2026, etc.")

# --- 5. FOOTER ---
st.divider()
st.caption("2026 Career Transition Tracker | Created by Karthik")
