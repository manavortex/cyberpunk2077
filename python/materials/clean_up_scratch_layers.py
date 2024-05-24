import os
import json

directory_path = 'E:\\Downloads\\cleaned_up_weapons'

# AAbdi gave me money for this, but they're fine with me sharing!

filenames_to_check = [
    "concrete_damage.xbm",
    "concrete_wear.xbm",
    "cracks.xbm",
    "cracks_concrete.xbm",
    "cracks2.xbm",
    "damp_stains_a.xbm",
    "dirt_stains.xbm",
    "dust_fine.xbm",
    "edgewear_01.xbm",
    "fine_filth.xbm",
    "fingerprints1.xbm",
    "leaks_vertical.xbm",
    "paint_brushtrokes.xbm",
    "paint_chips.xbm",
    "paint_patches.xbm",
    "paint_patches_horizontal.xbm",
    "paint_scratches.xbm",
    "scratches.xbm",
    "scratches_and_flakes_a.xbm",
    "scratches_horizontal_01.xbm",
    "scratches_horizontal_02.xbm",
    "scratches_random_01.xbm",
    "scratches_random_02.xbm",
    "scratches_vertical_01.xbm",
    "smudges.xbm",
    "spots.xbm",
    "spots_and_scrapes.xbm",
    "spots_dried.xbm",
    "spots_small.xbm",
    "stone_veins_01.xbm",
    "stone_veins_02.xbm",
    "stone_veins_03.xbm",
    "stripes_horizontal_a.xbm",
    "stripes_vertical_a.xbm",
    "stripes_vertical_b.xbm",
    "swipes_and_smears_a.xbm",
    "swirls_a.xbm",
    "wrinkles_01h.xbm",
    "wrinkles_01v.xbm",
    "wrinkles_02.xbm",
    "wrinkles_04.xbm",
    "wrinkles_chaotic.xbm",
    "wrinkles_horizontal.xbm",
    "wrinkles_vertical.xbm"
]  # Add your filenames here

num_findings = 0

def set_opacity(data, layer_no, opacity):
    if data['Data']["RootChunk"]["layers"][layer_no]["opacity"] == 0:
        return False
    data['Data']["RootChunk"]["layers"][layer_no]["opacity"] = opacity
    return True


def update_json_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('mlsetup.json'):
                print("skipping", file)
            else:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as json_file:
                    print(f"Checking '{file_path}'")
                    num_findings = 0
                    try:
                        data = json.load(json_file)
                        if not data or not data['Data'] or not data['Data']["RootChunk"] or not data['Data']["RootChunk"]["layers"]:
                            print(f"Can't find layers in {file_path}")
                        else:
                            for layer_no, layer_data in enumerate(data['Data']["RootChunk"]["layers"]):
                                if "material" not in layer_data.keys():
                                    continue
                                microblend = layer_data.get("microblend", "")
                                if "DepotPath" not in material.keys():
                                    continue
                                depot_path = material.get("DepotPath", "")
                                if "$value" not in depot_path.keys():
                                    continue
                                path = depot_path.get("$value", "")
                                if not path.endswith(tuple(filenames_to_check)):
                                    continue
                                if (set_opacity(data, int(layer_no), 0)):
                                    num_findings += 1

                            if num_findings > 0:
                                with open(file_path, 'w') as updated_json_file:
                                    json.dump(data, updated_json_file, indent=4)
                                    print(f"Updated {num_findings} layers in '{file_path}'")
                            else:
                                print(f"No changes made to '{file_path}'")

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in '{file_path}'")

if __name__ == "__main__":
    update_json_files(directory_path)
