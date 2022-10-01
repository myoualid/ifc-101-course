import streamlit as st
from tools import ifchelper
import json

##################### STREAMLIT IFC-JS COMPONENT MAGIC ######################
from pathlib import Path                                                    #
from re import L                                                            #
from typing import Optional                                                 #
import streamlit.components.v1 as components                                #
#                                                                           #
#                                                                           #
# Tell streamlit that there is a component called ifc_js_viewer,            #
# and that the code to display that component is in the "frontend" folder   #
frontend_dir = (Path(__file__).parent / "frontend-viewer").absolute()       #
_component_func = components.declare_component(                             #
	"ifc_js_viewer", path=str(frontend_dir)                                 #
)                                                                           #
#                                                                           #
# Create the python function that will be called                            #
def ifc_js_viewer(                                                          #    
    url: Optional[str] = None,                                              #
):                                                                          #
    component_value = _component_func(                                      #
        url=url,                                                            #
    )                                                                       #
    return component_value                                                  #
#                                                                           #
#############################################################################

def draw_3d_viewer():
    def get_current_ifc_file():
        return session.array_buffer

    if "ifc_js_response" not in session:
        session["ifc_js_response"] = ""
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())
    st.sidebar.success("Visualiser loaded")

def get_psets_from_ifc_js():
    if session.ifc_js_response:
        return json.loads(session.ifc_js_response)
        
def format_ifc_js_psets(psets):
    return ifchelper.format_ifcjs_psets(psets)

def write_pset_data():
    psets_JSON = get_psets_from_ifc_js()
    if psets_JSON:
        psets = format_ifc_js_psets(psets_JSON)
        for pset in psets.values():
            st.subheader(pset["Name"])
            st.table(pset["Data"])
    else:
        st.text("Where are your properties ?!")

session = st.session_state
def execute():
    st.header("🎮 IFC.js Viewer")
    if "ifc_file" in session and session["ifc_file"]:
        draw_3d_viewer()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧮 Object Properties")
            write_pset_data()
    else:
        st.header("Step 1: Load a file from the Home Page")

execute()