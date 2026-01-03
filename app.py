import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="2026 Comeback Clicker", page_icon="🚀")
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
    
    # Direct connect avoids the 'Response 200' search error
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet("Daily Log")
    
    st.sidebar.success("✅ Connected to Mission Control")

except Exception as e:
    st.error("❌ Connection Error")
    st.info("Check your Sheet ID and ensure the sheet is shared with your Service Account email.")
    st.code(str(e))
    st.stop()

# --- 3. TASK LOGIC ---
# This matches '03-Jan'
today_date = datetime.date.today().strftime("%d-%b") 
dates_row = sheet.row_values(1)

if today_date in dates_row:
    col_idx = dates_row.index(today_date) + 1
    tasks = sheet.col_values(1)[1:17] # Rows 2 to 17
    
    st.subheader(f"Log Mission: {today_date}")
    
    # Use columns to make buttons look like a professional dashboard
    for i, task in enumerate(tasks):
        if st.button(f"✅ {task}", key=f"btn_{i}", use_container_width=True):
            with st.spinner("Syncing..."):
                sheet.update_cell(i + 2, col_idx, "TRUE")
                st.toast(f"{task} Logged!", icon="🔥")
                st.success(f"Success! {task} updated.")
else:
    st.warning(f"Today's date ({today_date}) not found in Row 1.")
    st.info("💡 Hint: Format Row 1 in Google Sheets as 'Custom Date' (dd-mmm).")

st.divider()
st.caption("v1.2 | Log successfully processed")
