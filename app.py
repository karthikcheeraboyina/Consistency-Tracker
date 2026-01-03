import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# 1. Setup Connection
# This reads your JSON key from Streamlit's secure settings
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# 2. Open the Sheet
# CHANGE THIS to the exact name of your Google Sheet
SHEET_NAME = "My 2026 Tracker" 
sheet = client.open(SHEET_NAME).worksheet("Daily Log")

st.set_page_config(page_title="Consistency Tracker", page_icon="🚀")
st.title("🚀 Consistency Tracker - 2026")

# 3. Logic to find Today's Column
today_date = datetime.date.today().strftime("%d-%b") # Matches '03-Jan' format
dates_row = sheet.row_values(1)

if today_date in dates_row:
    col_idx = dates_row.index(today_date) + 1
    tasks = sheet.col_values(1)[1:17] # Rows 2 to 17
    
    st.subheader(f"Tasks for Today: {today_date}")
    
    # Create 16 buttons
    for i, task in enumerate(tasks):
        row_idx = i + 2
        # Create a button for each task
        if st.button(f"Tick: {task}", key=f"btn_{i}"):
            sheet.update_cell(row_idx, col_idx, "TRUE")
            st.success(f"Verified: {task} completed!")
else:
    st.error(f"Date {today_date} not found in Row 1. Check your sheet format!")
