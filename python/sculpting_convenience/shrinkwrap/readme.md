These scripts will help you refitting e.g. cyberware and scars to a custom head mesh. 
They will affect **every visible mesh** in your blend file.

**Select** the head mesh, then run [add_shrinkwrap.py](https://github.com/manavortex/cyberpunk2077/blob/master/python/sculpting_convenience/shrinkwrap/add_shrinkwrap.py).  
This will add a **shrinkwrap modifier** with the selection as a target and a default value.  

Before applying them, check for clippings etc. - especially anything around mouth and eyes might not snap correctly.

When you're satisfied, run [apply_shrinkwrap.py](https://github.com/manavortex/cyberpunk2077/blob/master/python/sculpting_convenience/shrinkwrap/apply_shrinkwrap.py) to **apply** the modifiers.  

Afterwards, you can export the meshes from Blender and import them into Wolvenkit.
