import json
import copy
import re
import os
from itertools import product
import sys

# If you don't know how to run this script, check the wiki: https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators/modding-guides/everything-else/running-python-scripts
# To learn more about ArchiveXL dynamic item additions, also check the wiki: https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators/modding-guides/items-equipment/adding-new-items/archivexl-dynamic-variants


########################################################################################################################################
# Step 0
# set the values below
########################################################################################################################################
# In Wolvenkit, right mouse click on the translation file and select 'convert to JSON'
# Put the absolute path to your converted file. All \ need to be converted to \\, or it won't work!
path =     "F:\\CyberpunkFiles\\mod_name\\archive\\raw\\blah\\my_item_i18n.json.json"

# This will re-create your file! Set this to False if you want to append entries that don't exist yet
overwrite_entries = True

# clean up human readable test for existing entries?
cleanup_existing_entries = False

########################################################################################################################################
# Step 1
# Define lists of colours. You can have as many as you want.
# You can define more than two lists for the variants
########################################################################################################################################

colors = [
            "black", "white", "grey", "brown", "red", "green", "blue", "gold", "silver", "pink", "darkred", 
            "black_glossy", "white_glossy", "grey_glossy", "brown_glossy", "red_glossy", "green_glossy", "blue_glossy", "gold_glossy", "silver_glossy", "pink_glossy", "darkred_glossy",
            "black_matte", "white_matte", "grey_matte", "brown_matte", "red_matte", "green_matte", "blue_matte", "gold_matte", "silver_matte", "pink_matte", "darkred_matte",
             "transparent_red", "transparent_white", "transparent_dark"
         ]
neon = [
            "white_neon", "red_neon", "green_neon", "blue_neon", "yellow_neon", "pink_neon", "violet_neon", "none_neon"
         ]

########################################################################################################################################
# Step 2
# Define your replacements to be used in entryTemplates below. For example, 
# COLOR will use "colors" from step 1, NEON will use "neon" from step 1, etc.
# Make sure to add same variants as in Step 1
########################################################################################################################################
variants = {
    "COLOR": colors,
    "NEON": neon,
}


########################################################################################################################################
# Step 3
# Define your entry templates. You only need to set the values here (right side of the colon), leave the keys alone.
# You can define as many templates as you need.
########################################################################################################################################

entryTemplates = [
    # {
    #     "$type": "localizationPersistenceOnScreenEntry",
    #     "femaleVariant": "Push-up bra - COLOR, NEON neon",
    #     "maleVariant":   "Push-up hotpants - COLOR, NEON neon",
    #     "primaryKey": "0",
    #     "secondaryKey": "manavortex_demo_item_i18n_COLOR_NEON"
    # },
    {
        "$type": "localizationPersistenceOnScreenEntry",
        "femaleVariant": "Thigh-high boots - COLOR, NEON neon",
        "maleVariant": "",
        "primaryKey": "0",
        "secondaryKey": "manavortex_demo_boots_i18n_COLOR_NEON"
    },
]


########################################################################################################################################
# Step 4 (optional)
# This will clean up the generated human-readable entries. You should be more or less OK with my default settings. 
# If you are not, add everything you want changed to "stringReplacementsRound2" ("old value": "new value")
# There are no more steps after this.
########################################################################################################################################

# 1: Replace left value (as regular expression) with right value.
# If you don'T know what that means, leave this alone and use stringReplacements instead!
regexReplacementsRound1 = {
    "- default$": "",
    " on - ": " - ",
    ",? [A-Z][a-z_ ]+: (a_z)*_?none": "",
    " - none glow": "",
    ",\s?$": "",
    ",\s?\,\s?$": "",
    "- - ": "- ",
}

# 2: Replace left value with right value.
stringReplacementsRound1 = {
    "transparent_dark": " transparent",
    "transparent_white": " transparent white",
    ", headband on": ", black headband",
    ", headband off": "",
    "_holo": " (holo)",
    "_emissive": " (glowing)",
    "_glossy": " (glossy)",
    "_matte": " (matte)",
    ", default eyes": "",
    "default -": " -",
    "default ": "standard ",
    " - -": " -",
    "_": " ",
    ")(": ", ",
    ") (": ", ",
    "  ": " "
}

# 3. Any lower case letters preceded by the left-hand value will be capitalized. We can decapitalize them again in the next step
# e.g. "_red" -> " Red", but "_Red" => "_Red"
uppercase_letters = {
    "_": " ",
}    

# 3. Any uppercase letters preceded by the left-hand will be decapitalized.
# e.g. "- Red" -> " red"
lowercase_letters = {
    "- ": "- ",    
}

# --------------------- fine tuning time ---------------------

# 1: Replace left value (as regular expression) with right value.
# If you don'T know what that means, leave this alone and use stringReplacementsRound2 instead!
regexReplacementsRound2 = {
    "- default$": "",
}

# 2: Replace left value with right value.
stringReplacementsRound2 = {
    "Glossy": "glossy"
}



########################################################################################################################################
# Do not edit below this line unless you know what you're doing!
########################################################################################################################################


# make sure users can't accidentally break these
def errorProofTemplate(template):
    if template is None:
        return {}
    
    template["$type"] = template.get("$type", "")
    template["femaleVariant"] = template.get("femaleVariant", "")
    template["maleVariant"] = template.get("maleVariant", "")
    template["primaryKey"] = template.get("primaryKey", "0")
    template["secondaryKey"] = template.get("secondaryKey", "")

    return template

# make sure users can't accidentally break these either
def errorProofDict(arg):
    if arg is None:
        return {}
    try:
        del arg['']
    except KeyError:
        pass
    return dict(arg)
                       

def generate_entries():
    keys = list(variants.keys())
    values = [variants[key] for key in keys]

    seen = set()
    for entry in product(*values):
        # Convert the entry to a frozenset so it can be added to a set
        entry_dict = dict(zip(keys, entry))
        entry_set = frozenset(entry_dict.items())
        if entry_set not in seen:
            seen.add(entry_set)
            yield entry_dict

# ------------------------------------------------------------------
# make the human-readable names nice and pretty
# ------------------------------------------------------------------
def cleanupHumanReadableText(entry):
    
    for key, value in errorProofDict(regexReplacementsRound1).items():
        entry["femaleVariant"] = re.sub(key, value, entry["femaleVariant"])
        entry["maleVariant"] = re.sub(key, value, entry["maleVariant"])

    for key, value in errorProofDict(stringReplacementsRound1).items():
        entry["femaleVariant"]  = entry["femaleVariant"].replace(key, value)
        entry["maleVariant"]    = entry["maleVariant"].replace(key, value)

    for key, value in errorProofDict(uppercase_letters).items():
        regex = re.compile(f"{key}([a-z])")
        entry["femaleVariant"] = regex.sub(lambda x: f"{value}{x.group(1).upper()}", entry["femaleVariant"])
        entry["maleVariant"] = regex.sub(lambda x: f"{value}{x.group(1).upper()}", entry["maleVariant"])
        
    for key, value in errorProofDict(lowercase_letters).items():
        regex = re.compile(f"{key}([A-Z])")
        entry["femaleVariant"] = regex.sub(lambda x: f"{value}{x.group(1).lower()}", entry["femaleVariant"])
        entry["maleVariant"] = regex.sub(lambda x: f"{value}{x.group(1).lower()}", entry["maleVariant"])
        
    for key, value in errorProofDict(regexReplacementsRound2).items():
        entry["femaleVariant"] = re.sub(key, value, entry["femaleVariant"])
        entry["maleVariant"] = re.sub(key, value, entry["maleVariant"])

    for key, value in errorProofDict(stringReplacementsRound2).items():
        entry["femaleVariant"]  = entry["femaleVariant"].replace(key, value)
        entry["maleVariant"]    = entry["maleVariant"].replace(key, value)


# ------------------- clean up variants --------------------
# having extra variants will wreak havoc on runtime, so let's only keep those that we really need
checkMeString = json.dumps(entryTemplates, indent=4)
for key in list(variants.keys()):  # We create a copy of the keys with list(d.keys())
    if key not in checkMeString:
        del variants[key]


# write to temp file
out_path = path.replace("json.json", "out.json")

# Cache for regular expressions and replacement functions
regex_cache = {}

alreadyCreatedEntries = set()

if not os.path.exists(path):
    sys.stdout.write(f"File {path} does not exist.\n")
    sys.stdout.write(f"Make sure to export it from Wolvenkit first!\n")
    exit(1)

sys.stdout.write(f"Generating entries. Please wait...\n")
with open(path, 'r', encoding = "utf-8") as f:
    j=json.load(f)

    t=j['Data']['RootChunk']
    entries = t['root']['Data']['entries']

    if overwrite_entries:
        entries.clear()

    # identify existing entries to avoid adding duplicates
    alreadyCreatedEntries = {entry['secondaryKey'] for entry in entries}

    original_entries = len(alreadyCreatedEntries)

    # create new entries based on template
    for entryTemplate in entryTemplates:
        for entryPattern in generate_entries():
            # input("Press Enter to continue...")
            newEntry = {}
            # Iterate over the keys and values in the entryTemplate
            for key in entryTemplate:
                value = entryTemplate[key]
                # Check if the value is a string
                if not isinstance(value, str):
                    continue
                # Perform text replacements
                for pattern_key in entryPattern:
                    value = value.replace(pattern_key, entryPattern[pattern_key])
                newEntry[key] = value  # Store the updated value

            entryName = newEntry["secondaryKey"] 
            if newEntry["secondaryKey"] in alreadyCreatedEntries:
                sys.stdout.write(f"Skipping duplicate entry {entryName}\n")
                continue

            alreadyCreatedEntries.add(newEntry["secondaryKey"])

            entries.append(newEntry)  

    # If we want to re-process, we'll do them all at once
    if cleanup_existing_entries:
        for entry in entries:
            cleanupHumanReadableText(entry)
    else:
        for entry in entries[original_entries:]:
            entryName = entry["secondaryKey"]
            cleanupHumanReadableText(entry)

    with open(out_path, 'w', encoding = "utf-8") as outfile:
        json.dump(j, outfile, indent=2)

os.remove(path)
os.rename(out_path, path)

sys.stdout.write(f"\nWrote {len(entries) - original_entries} new entries to {path}\n")
if not overwrite_entries:
    sys.stdout.write(f"Kept {original_entries} entry(ies)\n")


exit(0)
