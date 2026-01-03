import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

st.set_page_config(page_title="2026 Comeback Clicker", page_icon="🚀")
st.title("🚀 2026 Comeback Clicker")

# 1. Setup Connection
scope = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    # Convert secrets to a real dictionary and handle newline formatting
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(creds_info=creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # 2. Open the Sheet
    # Verify this matches your Google Sheet title exactly!
    SHEET_NAME = "mission-control-2026" 
    sheet = client.open(SHEET_NAME).worksheet("Daily Log")
    
except Exception as e:
    st.error("❌ Authentication or Connection Error")
    st.info("Debugging Info:")
    st.code(str(e)) # This will show us the EXACT error message now
    st.stop()

# 3. Logic to find Today's Column
today_date = datetime.date.today().strftime("%d-%b") 
dates_row = sheet.row_values(1)

if today_date in dates_row:
    col_idx = dates_row.index(today_date) + 1
    tasks = sheet.col_values(1)[1:17] 
    
    st.subheader(f"Tasks for Today: {today_date}")
    
    for i, task in enumerate(tasks):
        if st.button(f"✅ {task}", key=f"btn_{i}", use_container_width=True):
            sheet.update_cell(i + 2, col_idx, "TRUE")
            st.success(f"Verified: {task} completed!")
else:
    st.warning(f"Today's date ({today_date}) was not found in Row 1. Check your sheet format!")
