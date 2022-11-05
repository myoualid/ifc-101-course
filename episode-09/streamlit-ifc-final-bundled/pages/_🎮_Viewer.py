import streamlit as st
from tools import ifchelper
import json
import ifcopenshell
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
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())
    st.sidebar.success("Visualiser loaded")

def get_psets_from_ifc_js():
    if session.ifc_js_response:
        return json.loads(session.ifc_js_response)
        
def format_ifc_js_psets(data):
    return ifchelper.format_ifcjs_psets(data)


def initialise_debug_props(force=False):
    if not "BIMDebugProperties" in session:
        session.BIMDebugProperties = {
            "step_id": 0,
            "number_of_polygons": 0,
            "percentile_of_polygons": 0,
            "active_step_id": 0,
            "step_id_breadcrumb": [],
            "attributes": [],
            "inverse_attributes": [],
            "inverse_references": [],
            "express_file": None,
        }
    if force:
        session.BIMDebugProperties = {
            "step_id": 0,
            "number_of_polygons": 0,
            "percentile_of_polygons": 0,
            "active_step_id": 0,
            "step_id_breadcrumb": [],
            "attributes": [],
            "inverse_attributes": [],
            "inverse_references": [],
            "express_file": None,
        }

def get_object_data(fromId=None):
    def add_attribute(prop, key, value):
        if isinstance(value, tuple) and len(value) < 10:
            for i, item in enumerate(value):
                add_attribute(prop, key + f"[{i}]", item)
            return
        elif isinstance(value, tuple) and len(value) >= 10:
            key = key + "({})".format(len(value))
        
        propy = {
            "name": key,
            "string_value": str(value),
            "int_value": int(value.id()) if isinstance(value, ifcopenshell.entity_instance) else None,
        }
        prop.append(propy)
            
    if session.BIMDebugProperties:
        initialise_debug_props(force=True)
        step_id = 0
        if fromId:
            step_id =  int(fromId)
        else:
            step_id = int(session.object_id) if session.object_id else 0
        debug_props = st.session_state.BIMDebugProperties
        debug_props["active_step_id"] = step_id
        
        crumb = {"name": str(step_id)}
        debug_props["step_id_breadcrumb"].append(crumb)
        element = session.ifc_file.by_id(step_id)
        debug_props["inverse_attributes"] = []
        debug_props["inverse_references"] = []
        
        if element:
        
            for key, value in element.get_info().items():
                add_attribute(debug_props["attributes"], key, value)

            for key in dir(element):
                if (
                    not key[0].isalpha()
                    or key[0] != key[0].upper()
                    or key in element.get_info()
                    or not getattr(element, key)
                ):
                    continue
                add_attribute(debug_props["inverse_attributes"], key, getattr(element, key))
            
            for inverse in session.ifc_file.get_inverse(element):
                propy = {
                    "string_value": str(inverse),
                    "int_value": inverse.id(),
                }
                debug_props["inverse_references"].append(propy)
                
            print(debug_props["attributes"])

def edit_object_data(object_id, attribute):
    entity = session.ifc_file.by_id(object_id)
    print(getattr(entity, attribute))
    
def write_pset_data():
    data = get_psets_from_ifc_js()
    if data:
        st.subheader("🧮 Object Properties")
        psets = format_ifc_js_psets(data['props'])
        for pset in psets.values():
            st.subheader(pset["Name"])
            st.table(pset["Data"])    

def write_health_data():
    st.subheader("🩺 Debugger")
    ## REPLICATE IFC DEBUG PANNEL
    row1_col1, row1_col2 = st.columns([1,5])
    with row1_col1:
        st.number_input("Object ID", key="object_id")
    with row1_col2:
        st.button("Inspect From Id", key="edit_object_button", on_click=get_object_data, args=(st.session_state.object_id,))
        data = get_psets_from_ifc_js()
        if data:
            st.button("Inspect from Model", key="get_object_button", on_click=get_object_data, args=(data['id'],)) if data else ""

    if "BIMDebugProperties" in session and session.BIMDebugProperties:
        props = session.BIMDebugProperties
        if props["attributes"]:
            st.subheader("Attributes")
            # st.table(props["attributes"])
            for prop in props["attributes"]:
                col2, col3 = st.columns([3,3])
                if prop["int_value"]:
                    col2.text(f'🔗 {prop["name"]}')
                    col2.info(prop["string_value"])
                    col3.write("🔗")
                    col3.button("Get Object", key=f'get_object_pop_button_{prop["int_value"]}', on_click=get_object_data, args=(prop["int_value"],))
                else:
                    col2.text_input(label=prop["name"], key=prop["name"], value=prop["string_value"])
                    # col3.button("Edit Object", key=f'edit_object_{prop["name"]}', on_click=edit_object_data, args=(props["active_step_id"],prop["name"]))
                    
        if props["inverse_attributes"]:
            st.subheader("Inverse Attributes")
            for inverse in props["inverse_attributes"]:
                col1, col2, col3 = st.columns([3,5,8])
                col1.text(inverse["name"])
                col2.text(inverse["string_value"])
                if inverse["int_value"]:
                    col3.button("Get Object", key=f'get_object_pop_button_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))
        
        ## draw inverse references
        if props["inverse_references"]:
            st.subheader("Inverse References")
            for inverse in props["inverse_references"]:
                col1, col3 = st.columns([3,3])
                col1.text(inverse["string_value"])
                if inverse["int_value"]:
                    col3.button("Get Object", key=f'get_object_pop_button_inverse_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))
            


    
def execute():
    initialise_debug_props()
    st.header("🎮 IFC.js Viewer")
    if "ifc_file" in session and session["ifc_file"]:
        if "ifc_js_response" not in session:
            session["ifc_js_response"] = ""
        draw_3d_viewer()
        tab1, tab2 = st.tabs(["🧮 Properties", "🩺 Debugger"])
        with tab1:
            write_pset_data()
        with tab2:
            write_health_data()
    else:
        st.header("Step 1: Load a file from the Home Page")
session = st.session_state
execute()