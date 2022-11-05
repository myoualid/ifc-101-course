from tools import ifchelper
from matplotlib import pyplot as plt


style = {
    "figure.figsize": (8, 4.5),
    "axes.facecolor": (0.0, 0.0, 0.0, 0),
    "axes.edgecolor": "white",
    "axes.labelcolor": "white",
    "figure.facecolor": (0.0, 0.0, 0.0, 0),  # red   with alpha = 30%
    "savefig.facecolor": (0.0, 0.0, 0.0, 0),
    "patch.edgecolor": "#0e1117",
    "text.color": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "white",
    "font.size": 12,
    "axes.labelsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
}

def get_elements_graph(file):
    types = ifchelper.get_types(file, "IfcBuildingElement")
    types_count = ifchelper.get_type_occurence(file, types)
    x_values, y_values = ifchelper.get_x_and_y(types_count)

    plt.rcParams.update(style)
    fig, ax = plt.subplots()
    ax.bar(x_values, y_values, width=0.5, align="center", color="red", alpha=0.5)
    ax.set_title("Building Objects Count")
    ax.tick_params(color="red", rotation=90, labelsize="7", labelcolor="red")
    ax.tick_params(axis="x", rotation=90)
    ax.set_xlabel("Element Class")
    ax.set_ylabel("Count")
    ax.xaxis.label.set_color("red")
    ax.yaxis.label.set_color("red")

    ax.set_box_aspect(aspect=1 / 2)
    ax.axis()
    # ax.xticks(y_pos, objects, rotation=90, size=10)
    return ax.figure

def get_high_frequency_entities_graph(file):
    types = ifchelper.get_types(file)
    types_count = ifchelper.get_type_occurence(file, types)
    x_values, y_values = ifchelper.get_x_and_y(types_count, 400)

    plt.rcParams.update(style)
    fig, ax = plt.subplots()
    ax.bar(x_values, y_values, width=0.5, align="center", color="red", alpha=0.5)

    ax.set_title("IFC entity types frequency")

    ax.tick_params(color="red", rotation=90, labelsize="7", labelcolor="red")
    ax.tick_params(axis="x", rotation=90)
    ax.set_xlabel("File Entities")
    ax.set_ylabel("No of occurences")
    ax.xaxis.label.set_color("red")
    ax.yaxis.label.set_color("red")

    ax.set_box_aspect(aspect=1 / 2)
    ax.axis()
    # ax.xticks(y_pos, objects, rotation=90, size=10)
    return ax.figure

def load_graph(dataframe, quantity_set, quantity, user_option):
    import plotly.express as px
    if quantity != "Count":
        column_name = f"{quantity_set}.{quantity}"
        figure_pie_chart = px.pie(
            dataframe,
            names=user_option,
            values=column_name,
        )
    return figure_pie_chart