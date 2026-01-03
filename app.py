import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="2026 Comeback Clicker", page_icon="🚀", layout="centered")
st.title("🚀 2026 Comeback Clicker")

# --- 2. AUTHENTICATION & CONNECTION ---
# We use both Sheets and Drive scopes to ensure full 'write' access
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    # 1. Pull secrets from Streamlit dashboard
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 2. Fix the private_key formatting (handles both \n and raw newlines)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # 3. Create Credentials with BROAD scopes
    creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # 4. Open the Sheet
    # Ensure this matches the title of your Google Sheet exactly!
    SHEET_NAME = "mission-control-2026" 
    sheet = client.open(SHEET_NAME).worksheet("Daily Log")
    
    st.sidebar.success("✅ System Online: Connected to Mission Control")

except Exception as e:
    st.error("❌ System Error")
    st.info("Check if your Sheet is shared with the Service Account email.")
    st.code(str(e)) # Shows the 403 or 404 error if permissions fail
    st.stop()

# --- 3. LOGIC TO FIND TODAY'S COLUMN ---
# Formatting to match '03-Jan' in Row 1
today_date = datetime.date.today().strftime("%d-%b") 
dates_row = sheet.row_values(1)

if today_date in dates_row:
    col_idx = dates_row.index(today_date) + 1
    
    # Get Task names from Column A (Rows 2 to 17)
    tasks = sheet.col_values(1)[1:17] 
    
    st.subheader(f"Log Mission: {today_date}")
    st.write("Click a task below to update your status instantly.")

    # --- 4. BUTTON INTERFACE ---
    # Create 16 buttons in a clean vertical list
    for i, task in enumerate(tasks):
        row_idx = i + 2
        # unique key is vital for Streamlit loops
        if st.button(f"✅ {task}", key=f"btn_{i}", use_container_width=True):
            with st.spinner(f"Transmitting {task}..."):
                # This updates the checkbox to TRUE in your sheet
                sheet.update_cell(row_idx, col_idx, "TRUE")
                st.toast(f"{task} Logged!", icon="🔥")
                st.success(f"Success! {task} marked as completed.")
else:
    st.warning(f"Date '{today_date}' not found in Row 1.")
    st.info("💡 Pro Tip: In Google Sheets, select Row 1 -> Format -> Number -> Custom Date (05-Aug).")

# --- 5. FOOTER ---
st.divider()
st.caption("2026 Career Transition Project | Built with Python & Streamlit")
