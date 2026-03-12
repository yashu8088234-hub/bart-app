import streamlit as st
import streamlit as st
from background import set_background

# Set the universal background
set_background("barthomepage.jpg")

# Rest of your page content stays the same
st.markdown("## Welcome to BART")
st.write("Your page content goes here...")

st.set_page_config(layout="wide")

hide_streamlit = """
<style>
/* Hide all Streamlit UI elements & prevent extra side columns */
#MainMenu {{visibility:hidden;}}
footer {{visibility:hidden;}}
header {{visibility:hidden;}}
[data-testid="stToolbar"] {{display:none;}}
[data-testid="stSidebar"] {{display:none;}}
.block-container {{
    padding:0 !important;
    margin:0 auto !important;
    max-width: 100% !important;
}}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stSidebar"] {display:none;}
</style>
"""

st.markdown(hide_streamlit, unsafe_allow_html=True)

st.title("Staff Dashboard")

col1,col2,col3 = st.columns(3)

with col1:
    if st.button("Daily Stock Consumption"):
        st.switch_page("pages/stock_consumption.py")

with col2:
    if st.button("Daily Sales Report"):
        st.switch_page("pages/daily_sales.py")

with col3:
    if st.button("New Stock Report"):
        st.switch_page("pages/new_stock.py")

st.write("")

if st.button("⬅ Back"):
    st.switch_page("app.py")