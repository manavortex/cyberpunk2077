import bpy
import os
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_glb
import time

# This script will do the following things:
# 1. Select an export folder
# 2. Ask you for a file extension (.glb for meshes, .morphtarget.glb otherwise)
# 3. Save your file
# 4. Switch to a backup file
# 5. Apply shapekeys (destructively)
# 6. Export all collections to the folder from step 1 (only meshes starting with "submesh_" will be considered
# 7. Open the original file from step 3


original_path = ""
export_folder = "",
export_file_extension = ""

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


def detect_extension(folder):
    if not folder or not os.path.isdir(folder):
        raise ValueError("Export folder invalid")
     
    files = os.listdir(folder) 

    # Detect extensions for all collections
    extensions = set()
    for coll in bpy.data.collections:        
        full_name = ([f for f in files if f.startswith(coll.name)] or [None])[0]
        
        if not full_name:
            continue
        parts = full_name.split('.', 1)
        if len(parts) <= 1:
            continue

        extensions.add(parts[1])
    
    print(extensions)
    if "morphtarget.glb" in extensions:
        return ".morphtarget.glb"

    if len(extensions) == 1:
        # All matched the same extension: use it
        return extensions.pop()
    
    # Query file exception
    bpy.ops.wm.query_extension('INVOKE_DEFAULT')
    
   
    
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
        global export_file_extension
        global export_folder
        
        folder = self.directory
        if not folder:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}

        # Store selected folder globally for next operator usage
        export_folder = folder

        try:
           export_file_extension = detect_extension(folder)
        except Exception as exception:
            self.report({'ERROR'}, "Exception message: {}".format(exception))
            return { 'CANCELLED' }

        if not export_file_extension:
            self.report({'ERROR'}, "No file extension")
            return { 'CANCELLED' }            
               
        if not export_file_extension.startswith("."):
            export_file_extension = "." + export_file_extension         
         
        # Proceed to apply shapekeys and export
        return bpy.ops.wm.backup_apply_export('INVOKE_DEFAULT')


# Operator to detect or query file extension
class QueryExtensionOperator(Operator):
    bl_idname = "wm.query_extension"
    bl_label = "Detect or Query File Extension"

    user_extension: StringProperty(
        name="File Extension",
        description="Specify file extension for export (include dot, e.g. .glb)",
        default=".glb"
    )

    def execute(self, context):
        global original_path
        global export_file_extension
        global export_folder
        
        folder = export_folder
        if not folder or not os.path.isdir(folder):
            self.report({'ERROR'}, "Export folder not set or invalid.")
            return {'CANCELLED'}


        # Multiple or no extensions found, prompt user
        ret = context.window_manager.invoke_props_diaprint(self)
        if ret == {'FINISHED'} and user_extension != ".glb":
            export_file_extension = user_extension
        return ret


    def draw(self, context):
        layout = self.layout
        layout.label(text="Please enter file extension (with leading .)")
        layout.prop(self, "user_extension", text="File extension to use")

    def cancel(self, context):
        pass

    def modal(self, context, event):
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # Overriding invoke to ensure proper dialog use
        result = context.window_manager.invoke_props_diaprint(self)
        return result

    def execute(self, context):
        export_file_extension = self.user_extension
        bpy.ops.wm.backup_apply_export('INVOKE_DEFAULT')
        return {'FINISHED'}
    
    
# Operator to backup, apply shapekeys, export, and restore original file

class BackupApplyExportOperator(Operator):
    bl_idname = "wm.backup_apply_export"
    bl_label = "Backup, Apply Shapekeys, Export, Restore"

    def execute(self, context):
        global original_path
        global export_file_extension
        global export_folder
        
        wm = context.window_manager
        original_path = bpy.data.filepath
        folder = export_folder
        file_extension = export_file_extension

        if not original_path:
            self.report({'ERROR'}, "Save the current file first before continuing.")
            return {'CANCELLED'}
        if not folder or not os.path.isdir(folder):
            self.report({'ERROR'}, "Export folder not set or invalid.")
            return {'CANCELLED'}

        backup_path = original_path.rsplit(".", 1)[0] + "_EXPORT_TEMP.blend"

        # Save copy to backup path
        bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=False)
        self.report({'INFO'}, f"Backup saved: {backup_path}")

        start_time = time.time()
        showPopup("Exporting collections", "Exporting collections - Blender will be unresponsive for a minute or two.")

        # Export collections
        exported_count = 0
        export_start_time = time.time()
        
        # Pre-calculate which objects to export
        objects_to_export = []
        for collection in bpy.data.collections:
            collection_objects = []
            for obj in collection.objects:
                if obj.type == 'MESH' and obj.name.startswith('submesh_'):
                    collection_objects.append(obj)
            if collection_objects:
                objects_to_export.append((collection, collection_objects))

        current_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # Export each collection
        for collection, objs in objects_to_export:            
            # Deselect all first
            bpy.ops.object.select_all(action='DESELECT')
            set_visible(collection)
            
            # Select objects for this collection
            for obj in objs:                
                obj.select_set(True)
                self.keep_shapekeys(obj)            
            
            bpy.ops.object.select_all(action='DESELECT')
            # Select objects for this collection
            for obj in objs:
                obj.select_set(True)
            
            if not objs:
                continue

            targetPath = os.path.join(folder, f"{collection.name}{file_extension}")
            print(f"Exporting: {targetPath}")
            
            export_cyberpunk_glb(
                bpy.context,
                targetPath,
                export_poses=False,
                export_visible=False,
                limit_selected=True
            )
            exported_count += 1

        export_time = time.time() - export_start_time
        print(f"Exported {exported_count} collections in {export_time:.2f} seconds")

        # Restore original file
        bpy.ops.wm.open_mainfile(filepath=original_path)
        self.report({'INFO'}, "Restored original file.")

        total_time = time.time() - start_time
        
        try:
            bpy.ops.object.mode_set(mode=current_mode)
        except:
            pass
        showPopup('Shapekeys applied :)', 
                 f"Your shapekeys have been applied; {exported_count} collections exported in {total_time:.1f}s!")
        
        
        return {'FINISHED'}   
   
        
    def keep_shapekeys(self, obj):
        obj.hide_set(False)
        if obj.data.shape_keys is None or len(obj.data.shape_keys.key_blocks) == 0:
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
    bpy.utils.register_class(QueryExtensionOperator)
    bpy.utils.register_class(BackupApplyExportOperator)

def unregister():
    bpy.utils.unregister_class(BackupApplyExportOperator)
    bpy.utils.unregister_class(QueryExtensionOperator)
    bpy.utils.unregister_class(SelectExportFolderOperator)
    
# ------------ main: run -------------
if __name__ == "__main__":
    register()
    bpy.ops.wm.select_export_folder('INVOKE_DEFAULT')
