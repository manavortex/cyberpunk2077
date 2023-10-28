import bpy

# Specify the filename where you want to save the output.
# Make sure to use an existing folder!
output_filename = "C:\\Games\\Cyberpunk 2077\\archive\\pc\\mod\\apartment_corpo_cleaned_up.archive.xl"

# For indenting your .xl file
indent="  "

# --------------------------- DO NOT EDIT BELOW THIS LINE -------------------------------------

deletions = {}
expectedNodes = {}

# function to recursively count nested collections
def countChildNodes(collection):
    if 'expectedNodes' in collection:
        numChildNodes = collection['expectedNodes']
        return numChildNodes

# Function to find collections without children (these contain deletions)
def find_empty_collections(collection):
    empty_collections = []
    if len(collection.children) == 0 and len(collection.objects) == 0 and 'nodeIndex' in collection and 'nodeType' in collection:
        empty_collections.append(collection)
    for child_collection in collection.children:
        empty_collections.extend(find_empty_collections(child_collection))
    return empty_collections

# Function to write to a text file
def to_archive_xl(filename):
    with open(filename, "w") as file:
        file.write("streaming:\n")
        file.write(f"{indent}sectors:\n")
        for sectorName in deletions:
            file.write(f"{indent}{indent}- path: base\\worlds\\03_night_city\\_compiled\\default\\{sectorName}\n")
            file.write(f"{indent}{indent}{indent}expectedNodes: {expectedNodes[sectorName]}\n")
            file.write(f"{indent}{indent}{indent}nodeDeletions:\n")
            sectorData = deletions[sectorName]

            for empty_collection in sectorData:
                file.write(f"{indent}{indent}{indent}{indent}# {empty_collection.name}\n")
                file.write(f"{indent}{indent}{indent}{indent}- index: {empty_collection['nodeIndex']}\n")
                file.write(f"{indent}{indent}{indent}{indent}{indent}type: {empty_collection['nodeType']}\n")

# Iterate over matching collections and find empty ones
for sectorCollection in [c for c in bpy.data.collections if c.name.endswith("streamingsector")]:
    expectedNodes[sectorCollection.name] = countChildNodes(sectorCollection)
    collections = find_empty_collections(sectorCollection)
    if len(collections) > 0:
        deletions[sectorCollection.name] = collections

to_archive_xl(output_filename)
