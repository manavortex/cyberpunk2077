import json
import os
import re
import copy
from itertools import product

path = "F:\\CyberpunkFiles\\clothing\\arasaka_attire_overrides\\arasaka_attire\\source\\raw\\manavortex\\arasaka_attire\\arasaka_attire_kimono_i18n.json_old.json"
out_path = "F:\\CyberpunkFiles\\clothing\\arasaka_attire_overrides\\arasaka_attire\\source\\raw\\manavortex\\arasaka_attire\\arasaka_attire_kimono_i18n.json.json"

colors = [
        "black", "white", "grey", "brown", "red", "blue", "green", "gold", "silver", "pink",
        "black_glossy", "white_glossy", "grey_glossy", "brown_glossy", "red_glossy", "blue_glossy", "green_glossy", "gold_glossy", "silver_glossy", "pink_glossy",
        ]
variants = {
    "COLOR": copy.deepcopy(colors),
    "INNER": copy.deepcopy(colors),
    # "OBI": copy.deepcopy(colors),
}

entryTemplate = {
    "$type": "localizationPersistenceOnScreenEntry",
    "femaleVariant": "Kimono - COLOR, INNER sleeves, OBI obi",
    "maleVariant": "COLOR, INNER shirt, OBI obi",
    "primaryKey": "0",
    "secondaryKey": "kimono_COLOR_INNER_OBI_name"
}

stringReplacements = {
    "_glossy": " (glossy)",
    "_matte": " (matte)",
    "_": " "
}



def generate_entries():
    ret = []
    for color in variants["COLOR"]:
        for inner in variants["INNER"]:
            for obi in variants["OBI"]:
                ret.append({
                    "COLOR": color,
                    "INNER": inner,
                    "OBI": obi
                })
    return ret

def generate_entries_2():
    keys = list(variants.keys())
    values = [variants[key] for key in keys]
    
    ret = []
    for entry in product(*values):
        ret.append(dict(zip(keys, entry)))

    return ret


with open(path, 'r') as f:
    j=json.load(f)

    t=j['Data']['RootChunk']
    entries = t['root']['Data']['entries']

    alreadyCreatedEntries = []

    for entryPattern in generate_entries_2():
        updated_values = {}  # Create a new dictionary to store updated values

        newEntry = copy.deepcopy(entryTemplate)
        # Iterate over the keys and values in the entryTemplate
        for key in newEntry:
            value = newEntry[key]
            # Check if the value is a string
            if not isinstance(value, str):
                continue
            # Perform text replacements
            for pattern_key in entryPattern:
                value = value.replace(pattern_key, entryPattern[pattern_key])
            updated_values[key] = value  # Store the updated value

        # Update newEntry with the modified values
        newEntry.update(updated_values)

        if newEntry["secondaryKey"] in alreadyCreatedEntries:
            continue

        alreadyCreatedEntries.append(newEntry["secondaryKey"])

        entries.append(newEntry)

    for entry in entries:
        # make the human-readable names nice and pretty
        for key in stringReplacements:
            entry["femaleVariant"] = entry["femaleVariant"].replace(key, stringReplacements[key])
            entry["maleVariant"] = entry["maleVariant"].replace(key, stringReplacements[key])


with open(out_path, 'w') as outfile:
    json.dump(j, outfile,indent=2)
