from email.policy import default
import streamlit as st
from tools import ifchelper
from tools import graph_maker
from datetime import datetime

import ifcopenshell

def initialize_session_state():
    session["isHealthDataLoaded"] = False
    session["HealthData"] = {}
    session["Graphs"] = {}
    session["SequenceData"] = {}
    session["CostScheduleData"] = {}

def load_data():
    if "ifc_file" in session:
        session.Graphs = {
            "objects_graph": graph_maker.get_elements_graph(session.ifc_file),
            "high_frquency_graph": graph_maker.get_high_frequency_entities_graph(session.ifc_file)
        }
        load_cost_schedules()
        load_work_schedules()
        session["isHealthDataLoaded"] = True

def load_work_schedules():
    session.SequenceData = {
        "schedules": session.ifc_file.by_type("IfcWorkSchedule"),
        "tasks": session.ifc_file.by_type("IfcTask"),
        "ScheduleData": [{
            "Id": schedule.id(), 
            "Data": ifchelper.get_schedule_tasks(schedule)
            } for schedule in session.ifc_file.by_type("IfcWorkSchedule")
        ],
    }

def load_cost_schedules():
    session["CostData"] = {
        "schedules": session.ifc_file.by_type("IfcCostSchedule"),
        "cost_items": session.ifc_file.by_type("IfcCostItem")
    }
 
def add_cost_schedule():
    ifchelper.create_cost_schedule(session.ifc_file, session["cost_input"])
    load_cost_schedules()

def add_work_schedule():
    ifchelper.create_work_schedule(session.ifc_file, session["schedule_input"])
    load_work_schedules()
    
def draw_graphs():
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        graph = session.Graphs["objects_graph"]
        st.pyplot(graph)
    with row1_col2:
        graph = session.Graphs["high_frquency_graph"]
        st.pyplot(graph)
    
def draw_schedules():
    col1, col2 = st.columns(2)
    with col1:
        number_of_schedules = len(session.SequenceData["schedules"])
        st.subheader(
            f'Work Schedules: {number_of_schedules}'
        )
        schedules = [f'{work_schedule.Name} / {work_schedule.id()}'  for work_schedule in session.SequenceData["schedules"] or []]
        st.selectbox("Schedules", schedules, key="schedule_selector" )
        schedule_id = int(session.schedule_selector.split("/",1)[1]) if session.schedule_selector else None
        schedule = session.ifc_file.by_id(schedule_id) if schedule_id else None
        if schedule:
            tasks = ifchelper.get_schedule_tasks(schedule) if schedule else None
            if tasks:
                st.info(f'Number of Tasks : {len(tasks)}')
                task_data = ifchelper.get_task_data(tasks)
                st.table(task_data)
            else:
                st.warning("No Tasks 😥")
        else:
            st.warning("No Schedules 😥")

    with col2:
        number_of_schedules = len(session.CostData["schedules"])
        st.subheader(
            f'Cost Schedules: {number_of_schedules}'
        )
        st.selectbox("Cost Schedules", [f'{cost_schedule.Name} ({cost_schedule.id( )})' for cost_schedule in session.CostData["schedules"] or []])
        if not session.ifc_file.by_type("IfcCostItem"):
            st.warning("No Cost Items 😥")

def draw_side_bar():    
    def save_file():
        session.ifc_file.write(session.file_name)
    ## Cost Scheduler
    st.sidebar.header("💰 Cost Scheduler")
    st.sidebar.text_input("✏️ Schedule Name", key="cost_input")
    st.sidebar.button("➕ Add Schedule", key="add_schedule_button", on_click=add_cost_schedule)

    ## Work Scheduler
    st.sidebar.header("📅 Cost Scheduler")
    st.sidebar.text_input("✏️ Schedule Name", key="schedule_input")
    st.sidebar.button("➕ Add Schedule", key="add_work_schedule_button", on_click=add_work_schedule)

    ## File Saver
    st.sidebar.button("💾 Save File", key="save_file", on_click=save_file)

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
            step_id = fromId
        else:
            step_id = int(session.object_id) if session.object_id else 0
        debug_props = st.session_state.BIMDebugProperties
        debug_props["active_step_id"] = step_id
        crumb = {"name": str(step_id)}
        debug_props["step_id_breadcrumb"].append(crumb)
        element = session.ifc_file.by_id(step_id)
        debug_props["inverse_attributes"] = []
        debug_props["inverse_references"] = []
        
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
    
def execute():
    
    initialise_debug_props()
    st.header(" 🩺 Model Health")

    if "isHealthDataLoaded" not in session:
        initialize_session_state()

    if not session.isHealthDataLoaded:
        load_data()

    if session.isHealthDataLoaded:
        tab1, tab2, tab3 = st.tabs(["📊 Debug", "📈 Charts", "📝 Schedules"])
        
        ## REPLICATE IFC DEBUG PANNEL
        with tab1:
            row1_col1, row1_col2 = st.columns([1,5])
            with row1_col1:
                st.text_input("Object ID", key="object_id")
                st.button("Inspect from Object Id", key="get_object_button", on_click=get_object_data, args=(session.object_id,))
            if "BIMDebugProperties" in session and session.BIMDebugProperties:
                props = session.BIMDebugProperties
                ## DIRECT ATTRIBUTES
                if props["attributes"]:
                    st.subheader("Attributes")
                    for prop in props["attributes"]:
                        col2, col3 = st.columns([3,3])
                        if prop["int_value"]:
                            col2.text(f'🔗 {prop["name"]}')
                            col2.info(prop["string_value"])
                            col3.text("🔗")
                            col3.button("Get Object", key=f'get_object_pop_button_{prop["int_value"]}', on_click=get_object_data, args=(prop["int_value"],))
                        else:
                            col2.text_input(label=prop["name"], key=prop["name"], value=prop["string_value"])
                
                ## INVERSE ATTRIBUTES           
                if props["inverse_attributes"]:
                    st.subheader("Inverse Attributes")
                    for inverse in props["inverse_attributes"]:
                        col1, col2, col3 = st.columns([3,5,8])
                        col1.text(inverse["name"])
                        col2.text(inverse["string_value"])
                        if inverse["int_value"]:
                            col3.button("Get Object", key=f'get_object_pop_button_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))

                ## INVERSE REFERENCES    
                if props["inverse_references"]:
                    st.subheader("Inverse References")
                    for inverse in props["inverse_references"]:
                        col1, col3 = st.columns([3,3])
                        col1.text(inverse["string_value"])
                        if inverse["int_value"]:
                            col3.button("Get Object", key=f'get_object_pop_button_inverse_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))
        with tab2:
            draw_graphs()
        with tab3:
            draw_schedules()
        draw_side_bar()
    else:
        st.header("Step 1: Load a file from the Home Page")

session = st.session_state
execute()