import json

# for a guide on how to use this, check https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators/3d-modelling/blender-getting-started/blender-running-python-scripts

# path to the folder with your prop files. Make sure to double your slashes!! 
# wrong: C:\Games 
# right: C:\\Games

# file_path = "C:\\Games\\Cyberpunk 2077\\bin\\x64\\plugins\\cyber_engine_tweaks\\mods\\AppearanceMenuMod\\User\\Decor"
file_path = "E:\\Downloads\\temp"

# name of file to write to
outfile_name = "my_propfile.json"

# name of files that you want to merge
merge_file_names = [
    "Cyber_Flat.json",
    "Hotel_Room.json",
    "Japantown.json",
    "Techie_Plaza.json",
]

#########################################################################################################################################################
############################################ do not change below this line unless you know what you're doing ############################################
#########################################################################################################################################################

fileData = {
    "customIncluded": False,
    "file_name" : outfile_name,
    "name": outfile_name.replace(".json", "").replace("_", " "),
    "lights": [],
    "props": [],
}

uid_dict = {}

def get_first_free_entry(uid):
    ret = uid if uid not in uid_dict else next(i for i in range(1, 20000) if i not in uid_dict)
    uid_dict[ret] = True
    return ret

def merge_filecontent(absolute_filepath):
    try:
        with open(absolute_filepath, 'r') as json_file:
            data = json.load(json_file)
            fileData["customIncluded"] = fileData["customIncluded"] or data["customIncluded"] == True
            if data["props"] is not None:
                for prop in data["props"]:
                    prop["uid"] = get_first_free_entry(prop["uid"])
                    fileData["props"].append(prop)
            if data["lights"] is not None:
                for light in data["lights"]:
                    if (light["uid"] is not None):
                        light["uid"] = get_first_free_entry(light["uid"])
                    fileData["lights"].append(light)

    except FileNotFoundError:
        print(f"File {absolute_filepath} not found…")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{absolute_filepath}'")
    except:
        print(f"Couldn't open file {absolute_filepath}, skipping…")

for file_name in merge_file_names:
    merge_filecontent(f"{file_path}\\{file_name}")

try:
    with open(f"{file_path}\\{outfile_name}", 'w') as outfile:
        json.dump(fileData, outfile, indent=2)
except:
    print("Couldn't write to {file_path}\\{outfile_name}")

