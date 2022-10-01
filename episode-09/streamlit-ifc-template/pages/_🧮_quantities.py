import streamlit as st
from tools import ifchelper
from tools import pandashelper
from tools import graph_maker

session = st.session_state

def execute():  
    st.set_page_config(
        page_title="Quantities",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.header(" 🧮 Model Quantities")
    
execute()