import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="2026 Comeback Clicker", page_icon="🚀", layout="centered")

# Custom CSS to make it look like a professional dashboard
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 10px;
        height: 3em;
        background-color: #0e1117;
        border: 1px solid #30363d;
    }
    .stButton>button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 2026 Comeback Clicker")

# --- 2. THE DIRECT CONNECTION ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # Read secrets and fix newlines
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    # --- ACTION REQUIRED: PASTE YOUR ID BELOW ---
    SHEET_ID = "1RSvGxbjWqO1tNlRYbEg6ck3b4G_KYqO3v5OwjVGoyWw"
    
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet("Daily Log")
    
    st.sidebar.success("✅ Connected to Mission Control")

except Exception as e:
    st.error("❌ Connection Error")
    st.info("Check your Sheet ID and Service Account permissions.")
    st.code(str(e))
    st.stop()

# --- 3. TASK LOGIC (CLEANED VERSION) ---
# We check for multiple date formats to be safe
today_date = datetime.date.today().strftime("%d-%b") # e.g., 03-Jan
today_alt = datetime.date.today().strftime("%-d-%b") # e.g., 3-Jan

# Fetch Row 1 exactly as it looks on your screen
dates_row = sheet.row_values(1, value_render_option='FORMATTED_VALUE')
# Clean the list: remove spaces and make strings
clean_dates = [str(d).strip() for d in dates_row]

if today_date in clean_dates or today_alt in clean_dates:
    # Identify the correct column
    if today_date in clean_dates:
        col_idx = clean_dates.index(today_date) + 1
    else:
        col_idx = clean_dates.index(today_alt) + 1
    
    # Get all task names from Column A (Rows 2 to 17)
    tasks = sheet.col_values(1)[1:17] 
    
    st.subheader(f"Log Mission: {today_date}")
    
    # --- 4. THE INTERFACE ---
    for i, task in enumerate(tasks):
        if st.button(f"✅ {task}", key=f"btn_{i}", use_container_width=True):
            with st.spinner(f"Logging {task}..."):
                # i + 2 because: Row 1 is header, list index i starts at 0
                sheet.update_cell(i + 2, col_idx, "TRUE")
                st.toast(f"{task} Logged!", icon="🔥")
                st.success(f"Success! {task} marked as completed.")
else:
    st.warning(f"Today's date ({today_date}) not found in Row 1.")
    st.info(f"💡 Python sees these values in your Sheet's first row: {clean_dates}")
    st.write("Ensure one of these matches exactly '03-Jan'.")

st.divider()
st.caption("2026 Consistency Tracker | Version 2.0 (Stable)")
