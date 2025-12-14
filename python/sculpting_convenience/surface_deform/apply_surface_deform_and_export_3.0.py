import bpy
import os
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_collections_glb
from i_scene_cp77_gltf.meshtools.verttools import del_empty_vgroup
import time

# ==================== Set to False if you want to keep all vertex groups, even if they aren't used ====================
delete_unused_vertex_groups = True


# This script will do the following things:
# 1. Select an export folder
# 2. Ask you for a file extension (.glb for meshes, .morphtarget.glb otherwise)
# 3. Save your file
# 4. Switch to a backup file
# 5. Apply shapekeys (destructively)
# 6. Export all collections to the folder from step 1 (only meshes starting with "submesh_" will be considered
# 7. Open the original file from step 3


# ==================== Do not edit below this line unless you know what you're doing or want to FAFO ====================

original_path = ""
export_folder = "",

# Helper to set collections visible (recursive)
def set_visible(coll):
    coll.hide_viewport = False
    coll.hide_render = False
    for child in coll.children:
        child.hide_set(False)

# Informational popup (optional)
def showPopup(title, message_):
    try:
        from ctypes import windll
        windll.user32.MessageBoxW(None, message_, title, 1)
    except:
        # Fallback no-op or Blender custom message fallback
        print(f"{title}: {message_}")    
   
    
# Operator to select export folder
class SelectExportFolderOperator(Operator, ExportHelper):
    bl_idname = "wm.select_export_folder"
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
        global original_path
        global export_folder
        
        folder = self.directory
        if not folder:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}

        # Store selected folder globally for next operator usage
        export_folder = folder   
         
        # Proceed to apply shapekeys and export
        return bpy.ops.wm.backup_apply_export('INVOKE_DEFAULT')

    
# Operator to backup, apply shapekeys, export, and restore original file

class BackupApplyExportOperator(Operator):
    bl_idname = "wm.backup_apply_export"
    bl_label = "Backup, Apply Shapekeys, Export, Restore"

    def execute(self, context):
        global original_path
        global export_folder
        global delete_unused_vertex_groups
        
        wm = context.window_manager
        original_path = bpy.data.filepath

        if not original_path:
            self.report({'ERROR'}, "Save the current file first before continuing.")
            return {'CANCELLED'}
        if not export_folder or not os.path.isdir(export_folder):
            self.report({'ERROR'}, "Export folder not set or invalid.")
            return {'CANCELLED'}

        backup_path = original_path.rsplit(".", 1)[0] + "_EXPORT_TEMP.blend"

        # Save copy to backup path
        bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=False)
        self.report({'INFO'}, f"Backup saved: {backup_path}")
         
        bpy.ops.object.mode_set(mode='OBJECT')
        # Export each collection
        for collection in bpy.data.collections:    
                        
            if not collection.objects or len(collection.objects) == 0:
                continue        
            # Deselect all first
            bpy.ops.object.select_all(action='DESELECT')
            set_visible(collection)
            
            # Select objects for this collection
            for obj in collection.objects:
                if obj.type == 'ARMATURE' or (obj.type == 'MESH' and not obj.name.startswith('submesh_')):
                    continue
                obj.select_set(True)
                self.keep_shapekeys(obj)  
                if delete_unused_vertex_groups and context.object == obj:
                    del_empty_vgroup(context)          

        bpy.ops.object.select_all(action='DESELECT')
        
        export_cyberpunk_collections_glb(context, filepath=export_folder)    
            

        # Restore original file
        bpy.ops.wm.open_mainfile(filepath=original_path)
        self.report({'INFO'}, "Restored original file.")

        try:
            bpy.ops.object.mode_set(mode=current_mode)
        except:
            pass
       
        return {'FINISHED'}      
        
    def keep_shapekeys(self, obj):
        obj.hide_set(False)
        if obj.data.shape_keys is None or obj.data.shape_keys.key_blocks is None or len(obj.data.shape_keys.key_blocks) == 0:
            print(f"{obj.name} has no shape keys, applying modifiers directly")
            bpy.context.view_layer.objects.active = obj
            for mod in obj.modifiers:
                if mod.type == 'SURFACE_DEFORM':
                    bpy.ops.object.modifier_apply(modifier=mod.name)
            return {'FINISHED'}

        modifier = next((m for m in obj.modifiers if m.type == 'SURFACE_DEFORM'), None)
        if not modifier:
            return {'FINISHED'}

        # Duplicate object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()
        dup_obj = bpy.context.view_layer.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        dup_obj.select_set(True)

        # Apply all shape keys on the duplicate to get fully deformed shape
        while dup_obj.data.shape_keys and len(dup_obj.data.shape_keys.key_blocks) > 0:
            dup_obj.shape_key_remove(dup_obj.data.shape_keys.key_blocks[len(dup_obj.data.shape_keys.key_blocks)-1])
        
        # Apply the Surface Deform modifier on the deformed duplicate
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        
        
        bpy.ops.object.select_all(action='DESELECT')        
        obj.select_set(True)
        
        if obj.data.shape_keys is None or obj.data.shape_keys.key_blocks is None or len(obj.data.shape_keys.key_blocks) is 0:
            return {'FINISHED'}
        # Calculate offset between duplicate verts and original basis shape key verts
        basis_key = obj.data.shape_keys.key_blocks[0]
        for v, d_v in zip(basis_key.data, dup_obj.data.vertices):
            offset = d_v.co - v.co
            v.co += offset  # Update original basis shape key coords by offsetting
        
        # Delete duplicate object
        bpy.ops.object.select_all(action='DESELECT')
        dup_obj.select_set(True)
        bpy.ops.object.delete()

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(SelectExportFolderOperator)
    bpy.utils.register_class(BackupApplyExportOperator)

def unregister():
    bpy.utils.unregister_class(BackupApplyExportOperator)
    bpy.utils.unregister_class(SelectExportFolderOperator)
    
# ------------ main: run -------------
if __name__ == "__main__":
    register()
    bpy.ops.wm.select_export_folder('INVOKE_DEFAULT')
