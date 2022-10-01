def get_project_name(session):
    return session.ifc_file.by_type("IfcProject")[0].Name

def change_project_name(session):
    if session.project_name_input:
        session.ifc_file.by_type("IfcProject")[0].Name = session.project_name_input