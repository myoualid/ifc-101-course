import ifcopenshell
import ifcopenshell.util.element as Element
import pprint
pp = pprint.PrettyPrinter()

file = ifcopenshell.open("./models/07_MAD_SCIENTIST_212.ifc")

def get_objects_data_by_class(file, class_type):
    def add_pset_attributes(psets):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(f'{pset_name}.{property_name}')
    
    pset_attributes = set()
    objects_data = []
    objects = file.by_type(class_type)
      
    for object in objects:
        psets = Element.get_psets(object, psets_only=True)
        add_pset_attributes(psets)
        qtos = Element.get_psets(object, qtos_only=True)
        add_pset_attributes(qtos)
        objects_data.append({
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
        })
    return objects_data, list(pset_attributes)


def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".",1)[0]
        prop_name = attribute.split(".",-1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        if pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
    else:
        return None
        

data, pset_attributes = get_objects_data_by_class(file, "IfcBuildingElement")

attributes = ["ExpressId", "GlobalId", "Class", "PredefinedType", "Name", "Level", "Type"] + pset_attributes

pandas_data = []
for object_data in data:
    row = []
    for attribute in attributes:
        value = get_attribute_value(object_data, attribute)
        row.append(value)
    pandas_data.append(tuple(row))

import pandas as pd
dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)

## Export to CSV ?
# dataframe.to_csv("./models/test.csv")

# ## Export to Excel ?
# writer = pd.ExcelWriter('./models/test.xlsx', engine='xlsxwriter')
# for object_class in dataframe["Class"].unique():
#     df_class = dataframe[dataframe["Class"] == object_class]
#     df_class = df_class.dropna(axis=1, how='all')
#     df_class.to_excel(writer, sheet_name=object_class)
# writer.save()

# print("Executed")

beams = dataframe[(dataframe["Class"] == "IfcBeam")]

# Sum values of Qto_BeamBaseQuantities.NetVolume per level and Type
values = beams.groupby(["Level", "Type", "PredefinedType"])["Qto_BeamBaseQuantities.NetVolume"].sum()
pp.pprint(values)