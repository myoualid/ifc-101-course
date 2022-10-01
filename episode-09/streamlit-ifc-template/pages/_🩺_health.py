import streamlit as st
from tools import ifchelper
from tools import graph_maker
from datetime import datetime

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
    

def draw_model_health_ui():
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        graph = session.Graphs["objects_graph"]
        st.pyplot(graph)
    with row1_col2:
        graph = session.Graphs["high_frquency_graph"]
        st.pyplot(graph)
    
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

def execute():
    st.header(" 🩺 Model Health")

    if "isHealthDataLoaded" not in session:
        initialize_session_state()

    if not session.isHealthDataLoaded:
        load_data()

    if session.isHealthDataLoaded:
        draw_model_health_ui()
        draw_side_bar()
    else:
        st.header("Step 1: Load a file from the Home Page")

session = st.session_state
execute()