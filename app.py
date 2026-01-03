import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="2026 Comeback Clicker", page_icon="🚀")
st.title("🚀 2026 Comeback Clicker")

# --- 2. AUTHENTICATION & CONNECTION ---
scope = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    # Pull secrets from Streamlit dashboard
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Fix the private_key formatting (handles both \n and actual newlines)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # Correctly pass the dict to the 'info' argument
    creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # --- 3. OPEN THE SHEET ---
    # Ensure this matches the title of your Google Sheet exactly
    SHEET_NAME = "mission-control-2026" 
    sheet = client.open(SHEET_NAME).worksheet("Daily Log")
    
    st.sidebar.success("✅ Connected to Mission Control")

except Exception as e:
    st.error("❌ Connection Error")
    st.info("Check if your Sheet is shared with the Service Account email and if the Secret is correct.")
    st.code(str(e)) # Diagnostic tool
    st.stop()

# --- 4. LOGIC TO FIND TODAY'S COLUMN ---
# Formatting to match '03-Jan'
today_date = datetime.date.today().strftime("%d-%b") 
dates_row = sheet.row_values(1)

if today_date in dates_row:
    col_idx = dates_row.index(today_date) + 1
    
    # Get Task names from Column A (Rows 2 to 17)
    tasks = sheet.col_values(1)[1:17] 
    
    st.subheader(f"Status for: {today_date}")
    st.write("Click to update your Google Sheet in real-time.")

    # Create 16 buttons in a clean vertical layout
    for i, task in enumerate(tasks):
        row_idx = i + 2
        # Each button needs a unique key
        if st.button(f"✅ {task}", key=f"btn_{i}", use_container_width=True):
            with st.spinner(f"Logging {task}..."):
                # Update the cell to 'TRUE' (ticks the checkbox)
                sheet.update_cell(row_idx, col_idx, "TRUE")
                st.toast(f"{task} completed!", icon="🔥")
                st.success(f"Verified: {task} is now ticked on your Sheet.")
else:
    st.warning(f"Today's date ({today_date}) not found in Row 1.")
    st.info("💡 Hint: Format Row 1 in your Sheet as 'Custom Date' (dd-mmm) so it looks like '03-Jan'.")

# --- 5. FOOTER ---
st.divider()
st.caption("Consistency Tracker v1.0 | Developer: Karthik")
