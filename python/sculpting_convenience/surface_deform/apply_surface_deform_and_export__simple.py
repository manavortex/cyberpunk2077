# basically does the same as the other file, but will not apply to apply deforms to shapekeys, 
# and will export armatures instead of collections. I used this to do custom sculpting on an NPV head.

import bpy
import os
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_glb
import time

full_debug_output = False
original_path = ""
export_file_extension = ""
export_folder = ""

# ############################################################################################################################################################
# CHANGE THIS
# ############################################################################################################################################################

file_extension = ".glb"

# Will only consider children that have names starting in "submesh_" (ignoring e.g. "sculptme")
filter_submesh_name = True

# ############################################################################################################################################################
# STOP CHANGING
# ############################################################################################################################################################

# ------------ dialog -------------

# show user feedback (if we can)
def showPopup(title, message_):
    try:
        windll.user32.MessageBoxW(None, message_, title, 1)
    except: 
        try:
            bpy.ops.cp77.message_box('INVOKE_DEFAULT', message=message_)
        except:
            pass

# ------------ Set collection and its children visible -------------
def set_visible(coll):
  coll.hide_set(False)
  for child in coll.children:
      set_visible(child)

class SelectFolderOperator(Operator, ExportHelper):
    bl_idname = "wm.select_folder"
    bl_label = "Select Export Folder"
    filename_ext = ""
    use_filter_folder = True

    directory: StringProperty(
        name="Export Folder",
        description="Choose the folder to export to",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    def execute(self, context): 
        directory = self.directory
        if not directory:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}

        self.create_backup(context)
                
        apply_surface_deform_to_all_objects()
        showPopup('Shapekeys applied :)', "Your shapekeys have been applied! You can now export your deforms")   
        
        # Iterate over every collection
        successful_count = 0
        for armature in [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']:
            
            set_visible(armature)

            # Deselect everything first
            bpy.ops.object.select_all(action='DESELECT')

            selected_objs = []
            # Select all mesh children starting with 'submesh_'
            for obj in armature.children:
                if obj.type == 'MESH' and (not filter_submesh_name or obj.name.startswith('submesh_')):
                    obj.select_set(True)
                    selected_objs.append(obj)

            if not selected_objs:
              continue
            
            targetPath = os.path.join(directory, armature.name + file_extension)
            print(f"Exporting: {targetPath}")
            export_cyberpunk_glb(
                bpy.context,
                targetPath,
                export_poses=False,
                export_visible=False,
                limit_selected=True,
                is_skinned=True
            )
            successful_count = successful_count + 1
            self.report({'INFO'}, f"Exported {armature.name}")

        showPopup("Done!", f"All {successful_count} collections were successfully exported")
        self.restore_backup(context)
        return {'FINISHED'}


    def create_backup(self, context):
        global original_path
        global export_file_extension
        global export_folder
        
        wm = context.window_manager
        original_path = bpy.data.filepath
        folder = export_folder
        file_extension = export_file_extension

        backup_path = original_path.rsplit(".", 1)[0] + "_EXPORT_TEMP.blend"

        # Save copy to backup path
        bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=False)
        
    def restore_backup(self, context):
        global original_path
        try:
            bpy.ops.wm.open_mainfile(filepath=original_path)         
        except Exception as e:
            pass
        
        
def register():
    bpy.utils.register_class(SelectFolderOperator)

def unregister():
    bpy.utils.unregister_class(SelectFolderOperator)

    
def delete_all_shapekeys(obj):
    """Deletes all shapekeys for a given object, iterating backwards."""
    if obj.data.shape_keys:
        for key_block in reversed(obj.data.shape_keys.key_blocks):
            obj.shape_key_remove(key_block)

def replace_mesh_with_copy(mesh, mesh_copy):
    """Replaces the vertex data of the original mesh with the copied mesh."""
    # Delete all vertices from the original mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Replace the original mesh data with the copied mesh data
    mesh.data = mesh_copy.data.copy()

    # Remove the temporary mesh copy
    bpy.data.objects.remove(mesh_copy, do_unlink=True)
    print(f"Replaced vertex data for mesh '{mesh.name}'")

def apply_surface_deform_to_shapekeys(mesh, modifier_name="Surface Deform"):
    """Applies Surface Deform modifier to shapekeys or replaces mesh data if no shapekeys exist."""
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')

    # Check if the Surface Deform modifier exists
    surf_def_mod = mesh.modifiers.get(modifier_name)
    if not surf_def_mod:
        print(f"No Surface Deform modifier found on {mesh.name}.")
        return

    # Create a temporary copy of the mesh to apply the modifier
    mesh_copy = mesh.copy()
    mesh_copy.data = mesh.data.copy()
    bpy.context.collection.objects.link(mesh_copy)

    # Apply the Surface Deform modifier to the copy
    bpy.context.view_layer.objects.active = mesh_copy
    delete_all_shapekeys(mesh_copy)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
    except Exception as e:
        print(f"Failed applying Surface Deform to mesh '{mesh.name}': {e}")
        bpy.data.objects.remove(mesh_copy, do_unlink=True)
        return

    if mesh.data.shape_keys:
        # Apply the deformed vertex positions to each shapekey
        deformed_verts = [v.co for v in mesh_copy.data.vertices]
        shape_keys = mesh.data.shape_keys.key_blocks
        for shapekey in shape_keys:
            mesh.active_shape_key_index = shape_keys.keys().index(shapekey.name)
            for i, vert in enumerate(mesh.data.vertices):
                shapekey.data[i].co += deformed_verts[i] - vert.co
            if full_debug_output:
              print(f"Applied Surface Deform offsets to shapekey '{shapekey.name}' for mesh '{mesh.name}'")        
        bpy.data.objects.remove(mesh_copy, do_unlink=True)
    else:
        # Replace the original mesh with the modified copy
        replace_mesh_with_copy(mesh, mesh_copy)

def apply_surface_deform_to_all_objects():
    """Applies Surface Deform modifier to all mesh objects in the scene."""
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and any(mod.type == 'SURFACE_DEFORM' for mod in obj.modifiers):
            print(f"Applying Surface Deform to '{obj.name}'...")
            apply_surface_deform_to_shapekeys(obj)
        else:
            print(f"Skipping '{obj.name}': No Surface Deform modifier found.")   


        
# ------------ main: run -------------

if __name__ == "__main__":
    try:
        register()     
        bpy.ops.wm.select_folder('INVOKE_DEFAULT')
    except Exception as e:
        showPopup('There was an error!', "An error has occurred! Please select View -> Toggle Blender Console and find help on discord.gg/redmodding!")
        raise e
