import ifcopenshell
import ifcopenshell.util.element as Element
import ifcopenshell.api
from datetime import datetime

def get_objects_data_by_class(file, class_type):
    def add_pset_attributes(psets):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(
                    f"{pset_name}.{property_name}"
                ) if property_name != "id" else None

    objects = file.by_type(class_type)
    objects_data = []
    pset_attributes = set()

    for object in objects:
        qtos = Element.get_psets(object, qtos_only=True)
        add_pset_attributes(qtos)
        psets = Element.get_psets(object, psets_only=True)
        add_pset_attributes(psets)
        objects_data.append(
            {
                "ExpressId": object.id(),
                "GlobalId": object.GlobalId,
                "Class": object.is_a(),
                "PredefinedType": Element.get_predefined_type(object),
                "Name": object.Name,
                "Level": Element.get_container(object).Name
                if Element.get_container(object)
                else "",
                "Type": Element.get_type(object).Name
                if Element.get_type(object)
                else "",
                "QuantitySets": qtos,
                "PropertySets": psets,
            }
        )
    return objects_data, list(pset_attributes)

def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".", 1)[0]
        prop_name = attribute.split(".", -1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        elif pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
        else:
            return None

def create_pandas_dataframe(data, pset_attributes):
    import pandas as pd

    ## List of Attributes
    attributes = [
        "ExpressId",
        "GlobalId",
        "Class",
        "PredefinedType",
        "Name",
        "Level",
        "Type",
    ] + pset_attributes
    ## Export Data to Pandas
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))
    return pd.DataFrame.from_records(pandas_data, columns=attributes)

def get_stories(file):
    dict = []
    for storey in file.by_type("IfcBuildingStorey"):
        dict.append({"Storey": storey.Name, "Elevation": storey.Elevation})
    return dict

def get_project(file):
    return file.by_type("IfcProject")[0]

def get_types(file, parent_class=None):
    if parent_class:
        return set(i.is_a() for i in file if i.is_a(parent_class))
    else:
        return set(i.is_a() for i in file)

def get_type_occurence(file, types):
    return {t: len(file.by_type(t)) for t in types}

def create_cost_schedule(file, name=None):
    ifcopenshell.api.run("cost.add_cost_schedule", file, name=name)

def create_work_schedule(file, name=None):
    ifcopenshell.api.run("sequence.add_work_schedule", file, name=name)


def get_x_and_y(values, higher_then=None):
    occurences = sorted(values.items(), key=lambda kv: kv[1], reverse=True)
    if higher_then:
        occurences = [
            occurence for occurence in occurences if occurence[1] > higher_then
        ]
    x_values = [val[0] for val in occurences]
    y_values = [val[1] for val in occurences]
    return x_values, y_values

def get_root_tasks(work_schedule):
    related_objects = []
    if work_schedule.Controls:
        for rel in work_schedule.Controls:
            for obj in rel.RelatedObjects:
                if obj.is_a("IfcTask"):
                    related_objects.append(obj)
    return related_objects

def get_nested_tasks(task):
    tasks = []
    for rel in task.IsNestedBy or []:
        for object in rel.RelatedObjects:
            if object.is_a("IfcTask"):
                tasks.append(object)
    return tasks

def get_nested_tasks2(task):
    return [object for object in [rel.RelatedObjects for rel in task.IsNestedBy] if object.is_a("IfcTask")]

def get_schedule_tasks(work_schedule):
    all_tasks = []
    def append_tasks(task):
        for nested_task in get_nested_tasks(task):
            all_tasks.append(nested_task)
            if nested_task.IsNestedBy:
                append_tasks(nested_task)

    root_tasks = get_root_tasks(work_schedule)
    for root_task in root_tasks:
        append_tasks(root_task)
    return all_tasks

def format_date_from_iso(iso_date=None):
    return datetime.fromisoformat(iso_date).strftime('%d %b %y') if iso_date else ""

def get_task_data(tasks):
    return [
        {
            "Identification":task.Identification, 
            "Name":task.Name, 
            "ScheduleStart": format_date_from_iso(task.TaskTime.ScheduleStart) if task.TaskTime else "", 
            "ScheduleFinish": format_date_from_iso(task.TaskTime.ScheduleFinish) if task.TaskTime else "", 
        } for task in tasks
    ]

def format_ifcjs_psets(ifcJSON):
    """
    Organise pset data from web-ifc-api response
    """
    dict= {}
    for pset in ifcJSON:
        if "Qto" in pset["Name"]["value"]:
            for quantity in pset["Quantities"]:
                quantity_name = quantity["Name"]["value"]
                quantity_value = ""
                for key in quantity.keys():
                    if "Value" in key:
                        quantity_value = quantity[key]["value"]
                # quantity_value = quantity[5]["value"]
                if pset["expressID"] not in dict:
                    dict[pset["expressID"]] = {
                        "Name":pset["Name"]["value"], 
                        "Data":[]
                    }
                dict[pset["expressID"]]["Data"].append({
                    "Name": quantity_name,
                    "Value": quantity_value
                })
        if "Pset" in pset["Name"]["value"]:
            for property in pset["HasProperties"]:
                property_name = property["Name"]["value"]
                property_value = ""
                for key in property.keys():
                    if "Value" in key:
                        property_value = property[key]["value"]
                # property_value = property[5]["value"]
                if pset["expressID"] not in dict:
                    dict[pset["expressID"]] = {
                        "Name":pset["Name"]["value"], 
                        "Data":[]
                    }
                dict[pset["expressID"]]["Data"].append({
                    "Name": property_name,
                    "Value": property_value
                })
    return dict
