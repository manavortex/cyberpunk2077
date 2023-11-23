import os
import yaml
import json

# Converts your node removal .xl files for ArchiveXL 1.9
# Script frankensteined by me from Simarillius's code in the Blender plugin, then edited by me, then edited by Sim, then edited by me.
# Wouldn't exist without him, so a million thanks <3


# the wolvenkit project with your sector json files
wolvenkit_project="F:\\CyberpunkFiles\\world_editing\\apartment_glen_cleaned_up"

# the file that you want to convert
original_file="C:\\Games\\Cyberpunk 2077\\archive\\pc\\mod\\apartment_glen_cleaned_up.archive.xl"

# the file that you want to write to
output_file="C:\\Games\\Cyberpunk 2077\\archive\\pc\\mod\\apartment_glen_cleaned_up.converted.archive.xl"


# For indenting your .xl file
indent="  "

# --------------------------- DO NOT EDIT BELOW THIS LINE -------------------------------------

deletions = {}
expectedNodes = {}
# Function to write to a text file
def to_archive_xl(filename):
    with open(filename, "w") as file:
        file.write("streaming:\n")
        file.write(f"{indent}sectors:\n")
        for sectorPath in deletions:
            sectorData = deletions[sectorPath]
            if len(sectorData) == 0:
                continue
            file.write(f"{indent}{indent}- path: {sectorPath}\n")
            file.write(f"{indent}{indent}{indent}expectedNodes: {expectedNodes[sectorPath]}\n")
            file.write(f"{indent}{indent}{indent}nodeDeletions:\n")

            firstNode = sectorData[0]
            currentNodeIndex = firstNode['nodeIndex']
            currentNodeComment = firstNode['name']
            currentNodeType = firstNode['nodeType']
                    
            for empty_collection in sectorData:
                if empty_collection['nodeIndex'] > currentNodeIndex:
                    # new node! write the old one                    
                    file.write(f"{indent}{indent}{indent}{indent}# {currentNodeComment}\n")
                    file.write(f"{indent}{indent}{indent}{indent}- index: {currentNodeIndex}\n")
                    file.write(f"{indent}{indent}{indent}{indent}{indent}type: {currentNodeType}\n")
                    
                    # set instance variables
                    currentNodeIndex = empty_collection['nodeIndex']
                    currentNodeComment = empty_collection['name']
                    currentNodeType = empty_collection['nodeType']
                elif empty_collection['nodeIndex'] == currentNodeIndex:
                    currentNodeComment = f"{currentNodeComment}, {empty_collection['name']}"


with open(original_file, 'r') as xlfile:
    xl = yaml.safe_load(xlfile)

for sector in xl['streaming']['sectors']:
    #load the sector json so I can find nodes
    empty_collections = []
    sector_name=sector['path']
    print('\nProcessing sector ',sector_name)
    with open(os.path.join(wolvenkit_project,'source','raw',sector_name)+'.json', 'r') as jfile:
        j = json.load(jfile) 
    t=j['Data']['RootChunk']['nodeData']['Data']
    print('length of nodeData - ',len(t))
    expectedNodes[sector_name] =len(t)
    # go through the node deletions, and find the refs to them
    for i,delnode in enumerate(sector['nodeDeletions']):
        oldindex=delnode['index']
        instances = [id for id,x in enumerate(t) if x['NodeIndex'] == oldindex]
        print('NodeDeletion ',i,'now index',instances)
        for inst in instances:
            if 'mesh' in j['Data']['RootChunk']['nodes'][oldindex]['Data']:
                name=os.path.basename(j['Data']['RootChunk']['nodes'][oldindex]['Data']['mesh']['DepotPath']['$value'])
            elif 'entityTemplate' in j['Data']['RootChunk']['nodes'][oldindex]['Data']:
                name=os.path.basename(j['Data']['RootChunk']['nodes'][oldindex]['Data']['entityTemplate']['DepotPath']['$value'])
            else:
                name=delnode['name']
            node={'nodeIndex':inst,'nodeType':delnode['type'],'name':name}
            empty_collections.append(node)
    deletions[sector_name]=empty_collections

to_archive_xl(output_file)
