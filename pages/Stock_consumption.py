import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from rapidfuzz import process, fuzz

# ---------------- Page Config ----------------
st.set_page_config(page_title="Daily Stock Consumption", layout="wide")

# ---------------- Hide Streamlit UI ----------------
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stSidebar"] {display:none;}
.stApp {background: linear-gradient(135deg,#eef2f7,#d6e4ff);}
div.stButton > button {height:60px;font-size:20px;border-radius:10px;transition:0.3s;}
div.stButton > button:hover {background-color:#ff4b4b;color:white;}
</style>
""", unsafe_allow_html=True)

# ---------------- Page Title ----------------
st.markdown("<h1 style='text-align:center; color:red; font-size:60px;'>Daily Stock Consumption</h1>", unsafe_allow_html=True)

# ---------------- Google Sheets Setup ----------------
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("Master Inventory").sheet1
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
    st.stop()

# ---------------- Cached Sheet ----------------
@st.cache_data(ttl=300)
def load_sheet():
    try:
        data = sheet.get_all_values()
        headers = data[0]
        items = [row[0].strip() for row in data[1:]]
        items_lower = [i.lower() for i in items]
        return data, headers, items, items_lower
    except Exception as e:
        st.error(f"Error loading sheet data: {e}")
        st.stop()

sheet_data, headers, existing_items_list, existing_items_lower = load_sheet()

# ---------------- Session States ----------------
if "pending_updates" not in st.session_state:
    st.session_state.pending_updates = []

if "selected_items" not in st.session_state:
    st.session_state.selected_items = {}

if "pending_checkbox_state" not in st.session_state:
    st.session_state.pending_checkbox_state = {}

# ---------------- Date Input ----------------
date = st.date_input("Select Inventory Date")
date_str = str(date)
st.info(f"Inventory will be recorded under date: {date_str}")

# ---------------- Inventory Input ----------------
inventory_text = st.text_area("Paste your inventory (format: Item - Quantity)", height=300)

# ---------------- Parse Inventory ----------------
items_today = []
if inventory_text:
    for line in inventory_text.split("\n"):
        line = line.strip()
        if not line or "-" not in line:
            continue
        item, qty = line.rsplit("-", 1)
        item = item.strip()
        qty = qty.strip()
        try:
            qty = float(qty)
            items_today.append((item, qty))
        except:
            st.warning(f"Invalid quantity for line: {line}. Skipping.")

# ---------------- Match Items ----------------
for item_name, qty in items_today:
    matches = process.extract(
        item_name.lower(),
        existing_items_lower,
        scorer=fuzz.WRatio,
        limit=5
    )
    best_matches = [m for m in matches if m[1] > 50]

    if not best_matches:
        st.warning(f"Item '{item_name}' not found in inventory.")
        continue

    best_matches_original = [existing_items_list[existing_items_lower.index(m[0])] for m in best_matches]
    word_count = len(item_name.split())

    # Auto select if >2 words or only one match
    if word_count > 2 or len(best_matches_original) == 1:
        selected = best_matches_original[0]
        st.session_state.selected_items[item_name] = selected
        st.success(f"{selected} auto-selected")
    else:
        st.markdown(f"### Possible matches for '{item_name}' ({qty})")
        selected_option = None
        for option in best_matches_original:
            key = f"{item_name}_{option}"
            checked = st.checkbox(option, key=key,
                                  value=(st.session_state.selected_items.get(item_name) == option))
            if checked and selected_option is None:
                selected_option = option
        if selected_option:
            st.session_state.selected_items[item_name] = selected_option

# ---------------- Add to Pending Updates ----------------
if st.button("Add Inventory to Pending Updates"):
    for item_name, qty in items_today:
        if item_name in st.session_state.selected_items:
            selected = st.session_state.selected_items[item_name]
            if (selected, qty) not in st.session_state.pending_updates:
                st.session_state.pending_updates.append((selected, qty))
                st.session_state.pending_checkbox_state[selected] = True
    st.success("Selected items added to pending updates")

# ---------------- Show Pending Updates ----------------
if st.session_state.pending_updates:
    st.markdown("### Pending Updates (Check to update)")
    for i, (iname, qty) in enumerate(st.session_state.pending_updates):
        checked = st.checkbox(f"{iname} → {qty}", key=f"pending_{iname}",
                              value=st.session_state.pending_checkbox_state.get(iname, True))
        st.session_state.pending_checkbox_state[iname] = checked

# ---------------- Submit Updates ----------------
if st.button("Submit Pending Updates"):
    try:
        sheet_data, headers, existing_items_list, existing_items_lower = load_sheet()
        if date_str in headers:
            col_index = headers.index(date_str)
        else:
            col_index = len(headers)
            sheet.update_cell(1, col_index+1, date_str)
            headers.append(date_str)

        updates = []
        for item_name, qty in st.session_state.pending_updates:
            if not st.session_state.pending_checkbox_state.get(item_name, True):
                continue

            if item_name not in existing_items_list:
                st.warning(f"{item_name} not found in master inventory. Skipped.")
                continue

            row_index = existing_items_list.index(item_name) + 1
            try:
                cell_value = sheet_data[row_index][col_index]
            except:
                cell_value = ""

            if cell_value:
                st.warning(f"{item_name} already has data for {date_str}. Skipped.")
                continue

            cell = gspread.utils.rowcol_to_a1(row_index+1, col_index+1)
            updates.append({"range": cell, "values": [[qty]]})

        if updates:
            sheet.batch_update(updates)
            st.success(f"{len(updates)} items updated successfully.")
        else:
            st.info("No updates needed.")

        st.session_state.pending_updates = []
        st.session_state.pending_checkbox_state = {}
    except Exception as e:
        st.error(f"Error submitting updates: {e}")

# ---------------- Back Button ----------------
if st.button("⬅ Back"):
    st.experimental_rerun()
