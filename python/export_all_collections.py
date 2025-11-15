import bpy
import os

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_glb

# ############################################################################################################################################################
# CHANGE THIS
# ############################################################################################################################################################

file_extension = ".morphtarget.glb"

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
  coll.hide_viewport = False
  coll.hide_render = False
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

        # Iterate over every collection
        successful_count = 0
        for collection in bpy.data.collections:
            
            set_visible(collection)

            # Deselect everything first
            bpy.ops.object.select_all(action='DESELECT')

            selected_objs = []
            # Select all mesh children starting with 'submesh_'
            for obj in collection.objects:
                if obj.type == 'MESH' and (not filter_submesh_name or obj.name.startswith('submesh_')):
                    obj.select_set(True)
                    selected_objs.append(obj)

            if not selected_objs:
              continue
            
            targetPath = os.path.join(directory, collection.name + file_extension)
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
            self.report({'INFO'}, f"Exported {collection.name}")

        showPopup("Done!", f"All {successful_count} collections were successfully exported")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SelectFolderOperator)

def unregister():
    bpy.utils.unregister_class(SelectFolderOperator)

if __name__ == "__main__":
    register()
    # Run operator (shows folder picker)
    bpy.ops.wm.select_folder('INVOKE_DEFAULT')
