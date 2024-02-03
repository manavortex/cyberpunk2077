import json
import copy
import re
from itertools import product

path =     "F:\\CyberpunkFiles\\head\\yokai_international\\source\\raw\\manavortex\\clothing\\head\\seraph_mask\\seraph_mask_i18n.json - Copy.json"
out_path = "F:\\CyberpunkFiles\\head\\yokai_international\\source\\raw\\manavortex\\clothing\\head\\seraph_mask\\seraph_mask_i18n.json.json"

# colors = [
#         "red", "green", "white", "black", "silver", "gold", "blue", "lightblue", "pink", "rose", "violet", "lightgreen", "yellow", "orange", "scarlet"
#         "black", "white", "red", "lightblue", "lightgreen", "darkgreen", "darkblue", "gold", "silver", "pink", "hotpink", "violet",
#         "black_glossy", "white_glossy", "red_glossy", "lightblue_glossy", "lightgreen_glossy", "darkgreen_glossy", "darkblue_glossy", "gold_glossy", "silver_glossy", "pink_glossy", "hotpink_glossy", "violet_glossy",
#         "transparent_dark", "transparent_white", "transparent_red"
#         "black_glossy", "white_glossy", "grey_glossy", "brown_glossy", "red_glossy", "green_glossy", "blue_glossy", "gold_glossy", "silver_glossy", "pink_glossy",  "violet_glossy", "lightblue_glossy", "lightgreen_glossy",
#         "black_matte", "white_matte", "grey_matte", "brown_matte", "red_matte", "green_matte", "blue_matte", "gold_matte", "silver_matte", "pink_matte",  "violet_matte", "lightblue_matte", "lightgreen_matte",
#         ]

#colors = [
#        "default", "blue_holo", "gold_holo", "gold", "green_holo", "pink_holo", "red_holo", "silver", "steel", "turquoise_holo", "violet_holo", "white_holo",
#        "blue_emissive", "gold_emissive", "green_emissive", "pink_emissive", "red_emissive", "turquoise_emissive", "violet_emissive", "white_emissive", "black", "white",
#        ]
colors = [
    "red_wool", "green_wool", "white_wool", "black_wool", "silver_wool", "gold_wool", "blue_wool", "lightblue_wool", "pink_wool", "rose_wool", "violet_wool", "lightgreen_wool", "yellow_wool", "orange_wool", "scarlet_wool",
    "red_nylon", "green_nylon", "white_nylon", "black_nylon", "silver_nylon", "gold_nylon", "blue_nylon", "lightblue_nylon", "pink_nylon", "rose_nylon", "violet_nylon", "lightgreen_nylon", "yellow_nylon", "orange_nylon", "scarlet_nylon"
]
decals = [
     "none", "aldecaldos_a", "aldecaldos_flag", "aldecaldos_horse", "arasaka", "broken", "maelstrom_skull", "maelstrom_spider", "mlstrm", "militech", "ncpd", "tyger", "tyger_claws_kanji", "valentinos_roses", "valentinos_v", "samurai"
]
# beanie = [
#         "default", "6thstreet", "american", "camo_01", "camo_6thstreet", "flames_red", "flames_wraiths", "roses", "roses_02", "wraiths", "sticker_black", "sticker_white",
#         "black_beast", "pink_hexagon", "stripes_yellow_purple", "stripes_violet_green", "white_gold_net", "marine_black_logo", "marine_yellow_logo", "toms_diner", "moro_street", "moro_green_old",
#         "black", "white"
#         ]
beanie_states = [ "off", "on"]

variants = {
    "COLOR": copy.deepcopy(colors),
    "DECAL": copy.deepcopy(cdecalslors),
    # "TRIM": copy.deepcopy(colors),
}

entryTemplates = [
    {
        "$type": "localizationPersistenceOnScreenEntry",
        "femaleVariant": "Socks (short) - COLOR, Decal: DECAL",
        "maleVariant":  "",
        "primaryKey": "0",
        "secondaryKey": "manavortex__short_socks_i18n_COLOR_DECAL"
    },
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Socks (long) - COLOR, Decal: DECAL",
    #     "maleVariant":  "",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex__long_socks_i18n_COLOR_DECAL"
    # },
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Socks (mini) - COLOR, Decal: DECAL",
    #     "maleVariant":  "",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex__mini_socks_i18n_COLOR_DECAL"
    # },
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Tabi socks - COLOR, Decal: DECAL",
    #     "maleVariant":  "",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex__tabi_socks_i18n_COLOR_DECAL"
    # },
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Tabi socks (short) - COLOR, Decal: DECAL",
    #     "maleVariant":  "",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex__short_tabi_socks_i18n_COLOR_DECAL"
    # },
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Tabi socks (long) - COLOR, Decal: DECAL",
    #     "maleVariant":  "",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex__long_tabi_socks_i18n_COLOR_DECAL"
    # },
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Tabi socks (mini) - COLOR, Decal: DECAL",
    #     "maleVariant":  "",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex__mini_tabi_socks_i18n_COLOR_DECAL"
    # },
]

regexReplacenemnts = {
    "- default$": "",
    " on - ": " - ",
    " Decal: none": "",
    ",\s?$": "",
}

stringReplacements = {
    "transparent_dark": " transparent",
    "transparent_white": " transparent white",
    "_holo": " (holo)",
    "_emissive": " (glowing)",
    "_glossy": " (glossy)",
    "_matte": " (matte)",
    ", default eyes": "",
    "default -": " -",
    "default ": "standard ",
    "_a": " A",
    "_b": " B",
    "_m": " M",
    "_n": " N",
    "_t": " T",
    "_v": " V",
    "_s": " S",
    " a": " A",
    " b": " B",
    " m": " M",
    " n": " N",
    " t": " T",
    " v": " V",
    " s": " S",
    "_": " ",
    "  ": " "
}


def generate_entries():
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

    for entryTemplate in entryTemplates:
        for entryPattern in generate_entries():
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
            for key in regexReplacenemnts:
                if key == "": # fulltext search&replace prevention fix
                    continue
                entry["femaleVariant"] = re.sub(key, regexReplacenemnts[key], entry["femaleVariant"])
                entry["maleVariant"] = re.sub(key, regexReplacenemnts[key], entry["maleVariant"])
            for key in stringReplacements:
                if key == "": # fulltext search&replace prevention fix
                    continue
                entry["femaleVariant"] = entry["femaleVariant"].replace(key, stringReplacements[key])
                entry["maleVariant"] = entry["maleVariant"].replace(key, stringReplacements[key])


with open(out_path, 'w') as outfile:
    json.dump(j, outfile,indent=2)
