import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="2026 Comeback Clicker", page_icon="🚀")
st.title("🚀 2026 Comeback Clicker")

# --- 2. AUTHENTICATION & CONNECTION ---
scope = ["https://www.googleapis.com/auth/spreadsheets"]

# Pull secrets and fix the newline issue automatically
try:
    creds_info = dict(st.secrets["gcp_service_account"])
    # This line handles both the literal \n and the raw newline characters
    creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
except Exception as auth_err:
    st.error("Authentication Error: Check your Streamlit Secrets format.")
    st.stop()

# --- 3. OPEN THE SHEET ---
# EXACT name of your Google Sheet
SHEET_NAME = "mission-control-2026" 

try:
    sheet = client.open(SHEET_NAME).worksheet("Daily Log")
except Exception as e:
    st.error(f"Cannot find sheet '{SHEET_NAME}'.")
    st.info(f"Make sure you shared the sheet with: {creds_info['client_email']}")
    st.stop()

# --- 4. LOGIC TO FIND TODAY'S COLUMN ---
# This matches the '03-Jan' format in your Row 1
today_date = datetime.date.today().strftime("%d-%b") 
dates_row = sheet.row_values(1)

if today_date in dates_row:
    col_idx = dates_row.index(today_date) + 1
    # Get all task names from Column A (Rows 2 to 17)
    tasks = sheet.col_values(1)[1:17] 
    
    st.subheader(f"Status for: {today_date}")
    st.write("Click a button to log your progress directly to Google Sheets.")

    # Create 16 buttons in a clean layout
    for i, task in enumerate(tasks):
        row_idx = i + 2
        # Buttons are created inside a loop
        if st.button(f"✅ {task}", key=f"btn_{i}", use_container_width=True):
            with st.spinner(f"Updating {task}..."):
                sheet.update_cell(row_idx, col_idx, "TRUE")
                st.toast(f"Success! {task} ticked.", icon="🔥")
                st.success(f"Verified: {task} completed!")
else:
    st.warning(f"Today's date ({today_date}) was not found in Row 1.")
    st.info("Check your Sheet's first row. It should look like: 01-Jan, 02-Jan, 03-Jan...")

# --- 5. FOOTER ---
st.divider()
st.caption("2026 Career Pivot Tracker | Built by Karthik")
