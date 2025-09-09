These scripts are for easier sculpting of head meshes in Cyberpunk 2077 (they can be used for anything else, but that's the intended use case).  
You can find detailed step-by-step documentation [on the Cyberpunk2077 modding wiki](https://wiki.redmodding.org/cyberpunk-2077-modding/modding-guides/npcs/a-new-head-for-v#step-2-sculpting-prep).  

First, create a duplicate of your base mesh (the one you want to deform), and select it. I suggest giving it a unique name, such as **sculptme**.  
Then, run [add_surface_deform.py](https://github.com/manavortex/cyberpunk2077/python/sculpting_convenience/surface_deform/add_surface_deform.py) to add the modifier to every visible mesh.

Now, you can sculpt your dedicated mesh at your heart's content.

Once you're done, simply run [apply_surface_deform_and_export.py](https://github.com/manavortex/cyberpunk2077/python/sculpting_convenience/surface_deform/apply_surface_deform_and_export.py).  
This script will do the following things:
1. Select an export folder
2. Ask you for a file extension (.glb for meshes, .morphtarget.glb otherwise)
3. Save your file
4. Switch to a backup file
5. Apply shapekeys (destructively)
6. Export all collections to the folder from step 1 (only meshes starting with "submesh_" will be considered
7. Open the original file from step 3

If you run into trouble with the script, you can use [apply_surface_deform.py](https://github.com/manavortex/cyberpunk2077/python/sculpting_convenience/surface_deform/apply_surface_deform.py).
**Attention**: This script will destructively overwrite your file data - **save before using it**!
To quickly export your files, run [export_all_collections.py](https://github.com/manavortex/cyberpunk2077/blob/master/python/export_all_collections.py).
