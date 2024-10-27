These scripts are for easier sculpting of head meshes in Cyberpunk 2077 (they can be used for anything else, but that's the intended use case).  
You can find detailed step-by-step documentation [on the Cyberpunk2077 modding wiki](https://wiki.redmodding.org/cyberpunk-2077-modding/modding-guides/npcs/a-new-head-for-v#step-2-sculpting-prep).  

First, create a duplicate of your base mesh (the one you want to deform), and select it. I suggest giving it a unique name, such as **sculptme**.  
Then, run [add_surface_deform.py](https://github.com/manavortex/cyberpunk2077/blob/master/python/sculpting_convenience/surface_deform/add_surface_deform.py) to add the modifier to every visible mesh.

Now, you can sculpt your dedicated mesh at your heart's content.

Once you're done, simply run [apply_surface_deform.py](https://github.com/manavortex/cyberpunk2077/blob/master/python/sculpting_convenience/surface_deform/apply_surface_deform.py).  
Done! You can now export your morphtargets.
