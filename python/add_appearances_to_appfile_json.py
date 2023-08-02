import json
import os
import re
import copy
import shutil

path = "F:\\CyberpunkFiles\\path\\to\\my\\file.app"

# appearanceNames=['black_gold', 'black_leather', 'black_red', 'black_silver', 'carbon_fiber', 'glass_fiber', 'glitch_latex', 'hex_black', 'hex_glass', 'hex_glitch', 'hex_gold_black', 'hex_redblack', 'hex_silver_black', 'hex_white_black', 'hex_white_gold', 'hex_white_matteblack', 'plain_glass', 'white_black', 'white_rubber']
# appearanceNames=['brown', 'blue', 'turquoise', 'red', 'orange', 'violet', 'yellow']
# appearanceNames=[ "black", "blue", "brown", "green", "pink", "purple", "red", "white", "red_2", "pink_2"]
# appearanceNames=[ "tactical", "blue", "yellow", "green", "pink", "purple", "red", "white" ]
appearanceNames=[
    "white",
    "black",
    "silver",
    "gold",
    "blue",
    "lightblue",
    "pink",
    "rose",
    "violet",
    "lightgreen",
    "yellow",
    "orange",
    "scarlet",
]


# appearances to duplicate (APPEARANCE NAMES)
baselist=["vest", "belt", "pouches", "decals" ]


# mesh appearances (of components) to ignore
blacklist=['belt_buckle_metal']


########################################################################################################################################################################################################################

# can copy export path from raw file this way, lazy
if path.endswith('.app'):
    path = path + '.json'
if "\\archive\\" in path:
    path = path.replace('\\archive\\', '\\raw\\')



if not os.path.isfile("{}.orig".format(path)):
    shutil.copy(path, "{}.orig".format(path))

def stringifyPotentialCname(cname):
    if isinstance(cname, str):
        return cname
    return cname['$value']


with open(path,'r') as f: 
    j=json.load(f)

    t=j['Data']['RootChunk']
    appearances=t['appearances']

    existing_apps=[]
    for __app in appearances:
        existing_apps.append(__app['Data']['name']["$value"])


    i = 0
    for _app in appearances:
        appearanceName = stringifyPotentialCname(_app['Data']['name'])
        if not (appearanceName in baselist):
            i += 1
            continue
        for variantName in appearanceNames:
            original =  copy.deepcopy(_app)
            if '' == variantName or 'default' == variantName:
                newname=variantName
            else:
                separator="" if appearanceName.endswith("_") else "_"
                newname=appearanceName + separator + variantName

            # print("creating " + newname + " from " + appearanceName)
            if newname not in existing_apps:
                existing_apps.append(newname)
                app =  copy.deepcopy(original)
                app['Data']['name']['$value'] = newname

                for i,override in enumerate(app['Data']['partsOverrides']):                        
                    for compOverride in override['componentsOverrides']:
                        overrideName = compOverride['meshAppearance']['$value']
                        if overrideName not in blacklist:
                            compOverride['meshAppearance']['$value'] = variantName
                            
                for i,component in enumerate(app['Data']['components']):
                    if component['name']['$value'] in baselist and component['meshAppearance']['$value'] not in blacklist:
                        component['meshAppearance']['$value'] = variantName


                t['appearances'].append(app)
                i += 1

   # t['appearances'] = t['appearances'].sort(key=lambda x: x['Data']['name']['$value'])

    with open(path, 'w') as outfile:
        json.dump(j, outfile,indent=2)

with open(path,'r') as f: 
    lines=f.readlines()

i=0
j=0
for x,line in enumerate(lines):
    if 'HandleId' in line:
        lines[x]=line[:line.find('"HandleId": "')+len('"HandleId": "')]+str(i)+line[-3:]
        i+=1
    if 'BufferId' in line:
        eol=-3
        if line[eol]!='"':
            eol=-2
        lines[x]=line[:line.find('"BufferId": "')+len('"BufferId": "')]+str(j)+line[eol:]
        j+=1
    if '"components": null,' in line:
        lines[x]=line.replace('"components": null,', '"components": [],')

with open(path, 'w') as outfile:
    outfile.writelines(lines)

