These scripts are for easier sculpting of head meshes in Cyberpunk 2077 (they can be used for anything else, but that's the intended use case).  
You can find detailed step-by-step documentation [on the Cyberpunk2077 modding wiki](https://wiki.redmodding.org/cyberpunk-2077-modding/modding-guides/npcs/a-new-head-for-v#step-2-sculpting-prep).  

## How to use

1. Create a duplicate of your base mesh (the one you want to deform)
2. Give it a unique name (something like `sculptme`)
3. Make sure this is the only selected mesh in object mode
4. Make sure that every mesh you want to affect is **visible**
5. Run [add_surface_deform.py](https://github.com/manavortex/cyberpunk2077/python/sculpting_convenience/surface_deform/add_surface_deform.py)

This will apply a surface deform modifier to **every visible mesh** and bind it to the object you have selected (your `sculptme` mesh)

Now, you can hide everything else and sculpt/edit away.

## How to export

Once you're done, simply run [apply_surface_deform_and_export.py](https://github.com/manavortex/cyberpunk2077/python/sculpting_convenience/surface_deform/apply_surface_deform_and_export.py).  
The changes will **not** be applied destructively, so you can continue editing afterwards.

This script will do the following things:
1. Select an export folder
2. Pick a file extension (`.morphtarget.glb` if there are morphtargets in the folder, `.glb` otherwise)
3. Save your file
4. Switch to a new file
5. Go over every collection and do the following:
   - Apply shapekeys (destructively) to every mesh child starting with `_submesh`
   - Export the collection to the folder from step `1` - name will be `collectionName`.`extension` (from step `2`)
8. Open the original file from step `3`

## If you run into trouble with the script, fall back to the previous version: 
1. Apply surface deform via [apply_surface_deform.py](https://github.com/manavortex/cyberpunk2077/python/sculpting_convenience/surface_deform/apply_surface_deform.py)
  **Attention**: This script will destructively overwrite your file data - **save before using it**!
2. Run [export_all_collections.py](https://github.com/manavortex/cyberpunk2077/blob/master/python/export_all_collections.py) to export all collections
