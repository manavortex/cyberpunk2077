import json
import yaml
from collections import OrderedDict
from functools import reduce

infile = "C:\\Games\\Cyberpunk 2077\\bin\\x64\\plugins\\cyber_engine_tweaks\\mods\\removalEditor\\data\\dogtown.xl"
xlFile = "C:\\Games\\Cyberpunk 2077\\archive\\pc\\mod\\apartment_dogtown_cleaned_up.archive.working.bkp"
outfile = xlFile.replace("bkp", "xl")

jsonData = None
yamlData = None


def load_json():
    with open(infile, 'r') as json_file:
        jsonData = json.load(json_file)
        return jsonData

def load_yaml():
    with open(xlFile, 'r') as json_file:
        yamlData = yaml.safe_load(json_file)
        return yamlData

# Function to find the closest node with the same type
def find_closest_node_with_type_and_index(json_node, yaml_nodes):
    node_type = json_node["type"]
    node_index = json_node["index"]

    closest_node = None
    min_distance = float('inf')

    for yaml_node in yaml_nodes:
        if yaml_node["type"] == node_type:
            # Calculate distance based on the absolute difference of indices and types
            distance = abs(yaml_node["index"] - node_index) + (1 if yaml_node["type"] != node_type else 0)

            if distance < min_distance:
                closest_node = yaml_node
                min_distance = distance

    return closest_node


# Define the desired key order
desired_key_order = ["path", "expectedNodes", "nodeDeletions", "index", "type", "debugName"]

class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


with open(infile, 'r') as json_file:
    jsonData = load_json()
    yamlData = load_yaml()

    sectors = []

    for json_sector in jsonData["streaming"]["sectors"]:
        yaml_sector = next((sector for sector in yamlData["streaming"]["sectors"] if sector["path"] == json_sector["path"]), None)
        if yaml_sector == None:
            yaml_sector = {}
            yaml_sector["path"] = json_sector["path"]
            yaml_sector["expectedNodes"] = json_sector["expectedNodes"]
            yaml_sector["nodeDeletions"] = []

        for node in json_sector["nodeDeletions"]:
            # find closest node of the same type in yaml data
            yaml_node = find_closest_node_with_type_and_index(node, yaml_sector["nodeDeletions"])
            if yaml_node != None and "debugName" in yaml_node and yaml_node["debugName"] != None:
                node["debugName"] = yaml_node["debugName"]
            yaml_sector["nodeDeletions"].append(node)
        sectors.append(yaml_sector)


    yamlData["streaming"]["sectors"].clear()
    for yaml_sector in sectors:

        # sort nodes and filter duplicates
        node_deletions = sorted(yaml_sector["nodeDeletions"], key=lambda x: x["index"])
        node_deletions = reduce(lambda re, x: re+[x] if x not in re else re, node_deletions, [])

        yaml_sector["nodeDeletions"].clear()
        for _node in node_deletions:
            node = {
                "index": _node["index"],
                "type": _node["type"],
            }
            if "debugName" in _node:
                node["debugName"] = _node["debugName"]

            yaml_sector["nodeDeletions"].append(node)

        # Create a new ordered dictionary with the desired key order
        yamlData["streaming"]["sectors"].append(OrderedDict((key, yaml_sector[key]) for key in desired_key_order if key in yaml_sector))

    yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items()))
    with open(outfile, 'w') as outfile:
        outfile.write(yaml.dump(yamlData, Dumper=Dumper, sort_keys=False, default_flow_style=False))

