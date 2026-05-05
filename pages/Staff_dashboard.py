import streamlit as st
from background import set_background
import json
import os

# -------------------------
# PASSWORD FILE SETUP
# -------------------------
FILE_NAME = "passwords.json"

def init_file():
    if not os.path.exists(FILE_NAME):
        default_data = {
            "admin": "admin123",
            "Stock": "stock123",
            "Sales": "sales123",
            "NewStock": "new123"
        }
        with open(FILE_NAME, "w") as f:
            json.dump(default_data, f)

def load_passwords():
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def save_passwords(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f)

init_file()

# -------------------------
# SESSION STATE
# -------------------------
if "selected_branch" not in st.session_state:
    st.session_state.selected_branch = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False

# -------------------------
# ORIGINAL UI (UNCHANGED)
# -------------------------
set_background("barthomepage.jpg")

st.markdown("## Welcome to BART")
st.write("Your page content goes here...")

st.set_page_config(layout="wide")

hide_streamlit = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stSidebar"] {display:none;}
.block-container {
    padding:0 !important;
    margin:0 auto !important;
    max-width: 100% !important;
}
</style>
"""

st.markdown(hide_streamlit, unsafe_allow_html=True)

st.title("Staff Dashboard")

col1,col2,col3 = st.columns(3)

# -------------------------
# BUTTONS (LOGIC MODIFIED ONLY)
# -------------------------
with col1:
    if st.button("Daily Stock Consumption"):
        st.session_state.selected_branch = "Stock"

with col2:
    if st.button("Daily Sales Report"):
        st.session_state.selected_branch = "Sales"

with col3:
    if st.button("New Stock Report"):
        st.session_state.selected_branch = "NewStock"

st.write("")

# -------------------------
# AUTH SYSTEM (ADDED BELOW UI)
# -------------------------
passwords = load_passwords()

# LOGIN
if st.session_state.selected_branch and not st.session_state.authenticated and not st.session_state.reset_mode:
    st.subheader(f"Enter Password for {st.session_state.selected_branch}")

    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if password == passwords[st.session_state.selected_branch]:
            st.session_state.authenticated = True
        else:
            st.error("Incorrect password")

    if st.button("Reset Password"):
        st.session_state.reset_mode = True

# RESET PASSWORD
if st.session_state.reset_mode:
    st.subheader("Reset Password (Admin Required)")

    admin_pass = st.text_input("Admin Password", type="password")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        if admin_pass == passwords["admin"]:
            passwords[st.session_state.selected_branch] = new_pass
            save_passwords(passwords)
            st.success("Password updated successfully")
            st.session_state.reset_mode = False
        else:
            st.error("Invalid admin password")

# -------------------------
# REDIRECT AFTER LOGIN
# -------------------------
if st.session_state.authenticated:
    page_map = {
        "Stock": "pages/Stock_consumption.py",
        "Sales": "pages/Daily_sales.py",
        "NewStock": "pages/New_stock.py"
    }

    st.switch_page(page_map[st.session_state.selected_branch])

# -------------------------
# ORIGINAL BACK BUTTON (UNCHANGED)
# -------------------------
if st.button("⬅ Back"):
    st.switch_page("App.py")
