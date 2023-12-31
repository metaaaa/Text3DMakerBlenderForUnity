from email.policy import default
import os
import bpy
from bpy.props import *
import sys
import argparse
# import tkinter
# from tkinter import filedialog

bl_info = {
    "name": "3DTextMakerAddOn",
    "description": "This AddOn divides the input text for each character and outputs it as an FBX file",
    "author": "dmiyamo3",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "support": "COMMUNITY",
    "category": "Tutorial",
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": ""
}

text_list = []

def makesplittext(i, text, fontpath, extrude, offset, bevel_depth, bevel_resolution):
    bpy.ops.object.text_add(enter_editmode=False, location=(0, 0, 0))
    txt = bpy.context.object
    txt.name = str(i) + "_" + text
    txt.data.body = text

    if fontpath == "":
        fontpath = "C:/Windows/Fonts/meiryo.ttc"
    fnt = bpy.data.fonts.load(fontpath)
    txt.data.font = fnt

    # extrude
    bpy.context.object.data.extrude = extrude

    # offset
    bpy.context.object.data.offset = offset

    # bevel
    bpy.context.object.data.bevel_depth = bevel_depth
    bpy.context.object.data.bevel_resolution = bevel_resolution
    bpy.ops.object.editmode_toggle()
    
    center_x = 0.0
    center_y = 0.0
    center_z = 0.0
    for vert_boundbox in txt.bound_box:
        center_x += vert_boundbox[0]
        center_y += vert_boundbox[1]
        center_z += vert_boundbox[2]
        
    center_x /= 8
    center_y /= 8
    center_z /= 8
    print("origin_offset," + str(center_x)+ "," +str(center_y)+ "," +str(center_z))
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
    bpy.ops.object.editmode_toggle()

    bpy.ops.transform.rotate(value=-1.5708, orient_axis='X', orient_type='GLOBAL')
    text_list.append(text)


def savetext(i, text, dirname):
    # save fbx
    # dirname = dirdialog()
    filename = os.path.join(dirname, str(i) + "_" + text + ".fbx")
    bpy.ops.export_scene.fbx(filepath=filename, use_selection=True, apply_scale_options='FBX_SCALE_ALL')


def savetext2(i, text, dirname):
    # save fbx
    # dirname = dirdialog()
    filename = os.path.join(dirname, text + "_" + str(i) + ".fbx")
    bpy.ops.export_scene.fbx(filepath=filename, use_selection=True, apply_scale_options='FBX_SCALE_ALL')

# tkinterがblenderと競合(?)して使えないのでファイルダイアログは一旦保留
# def dirdialog():
#     root = tkinter.Tk()
#     root.withdraw()

#     dirname = filedialog.askdirectory(initialdir = dir)

#     return dirname
###



def Make3DText(text, fontpath, extrude, offset, bevel_depth, bevel_resolution):
    for i, c in enumerate(text):
        makesplittext(i, c, fontpath, extrude,
                        offset, bevel_depth, bevel_resolution)

    print(bpy.context.scene.text)
    for i, c in enumerate(bpy.context.scene.text):
        print(i,c)
        bpy.data.objects[str(i) + "_" + c].location.x = i * 1.0

    return {'FINISHED'}

#
# TUTORIAL_OT_3DTextMaker
#
class TUTORIAL_OT_3DTextMaker(bpy.types.Operator):
    bl_idname = "tutorial.3dtextmaker"
    bl_label = "3DTextMaker"
    bl_options = {'REGISTER', 'UNDO'}

    #--- properties ---#
    text:       StringProperty(default="", options={"HIDDEN"})
    fontpath:   StringProperty(default="", options={"HIDDEN"})
    extrude:    FloatProperty()
    offset:     FloatProperty()
    bevel_depth:        FloatProperty()
    bevel_resolution:   IntProperty()

    #--- execute ---#
    def execute(self, context):
        return Make3DText(self.text, self.fontpath, self.extrude, self.offset, self.bevel_depth, self.bevel_resolution)

#
# TUTORIAL_OT_SaveText
#

def SaveText(save_option_full_text, dirname):
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
        
    tex = ""
    for c in text_list:
        tex += c
        
    dirname = os.path.join(dirname, tex)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    # for i, c in enumerate(bpy.context.scene.text):
    for i, c in enumerate(text_list):
        bpy.data.objects[str(i) + "_" + c].select_set(True)
        if save_option_full_text is True:
            savetext2(i, tex, dirname)
        else:
            savetext(i, c, dirname)
        bpy.data.objects[str(i) + "_" + c].select_set(False)

    return {'FINISHED'}

class TUTORIAL_OT_SaveText(bpy.types.Operator):
    bl_idname = "tutorial.savetext"
    bl_label = "savetext"
    bl_options = {'REGISTER', 'UNDO'}

    #--- properties ---#
    dirname: StringProperty(default="", options={"HIDDEN"})
    save_option_full_text: BoolProperty(name="チェック", default=True)

    #--- execute ---#
    def execute(self, context):
        return SaveText(self.save_option_full_text, self.dirname)


#
# TUTORIAL_PT_3DTextMakerPanel
#
class TUTORIAL_PT_3DTextMakerPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "3DTextMaker"
    bl_label = "3DTextMaker"

    #--- draw ---#
    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "fontpath")

        layout.prop(context.scene, "text")

        layout.prop(context.scene, "extrude")
        layout.prop(context.scene, "offset")
        layout.prop(context.scene, "bevel_depth")
        layout.prop(context.scene, "bevel_resolution")

        on_prop = layout.operator(
            TUTORIAL_OT_3DTextMaker.bl_idname, text="Create")
        on_prop.text = context.scene.text
        on_prop.fontpath = context.scene.fontpath
        on_prop.extrude = context.scene.extrude
        on_prop.offset = context.scene.offset
        on_prop.bevel_depth = context.scene.bevel_depth
        on_prop.bevel_resolution = context.scene.bevel_resolution

        layout.prop(context.scene, "dirname")
        layout.prop(context.scene, "save_option_full_text")

        on_prop_save = layout.operator(
            TUTORIAL_OT_SaveText.bl_idname, text="Save")
        on_prop_save.dirname = context.scene.dirname
        on_prop_save.save_option_full_text = context.scene.save_option_full_text


#
# register classs
#
classes = [
    TUTORIAL_OT_3DTextMaker,
    TUTORIAL_OT_SaveText,
    TUTORIAL_PT_3DTextMakerPanel
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    # Panel用変数の登録
    bpy.types.Scene.text = StringProperty(default="")
    bpy.types.Scene.dirname = StringProperty(default="")
    bpy.types.Scene.fontpath = StringProperty(default="")
    bpy.types.Scene.extrude = FloatProperty()
    bpy.types.Scene.offset = FloatProperty()
    bpy.types.Scene.bevel_depth = FloatProperty()
    bpy.types.Scene.bevel_resolution = IntProperty()
    bpy.types.Scene.save_option_full_text = BoolProperty(default=True)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    # Panel用変数の登録解除
    del bpy.types.Scene.text
    del bpy.types.Scene.dirname
    del bpy.types.Scene.fontpath
    del bpy.types.Scene.extrude
    del bpy.types.Scene.offset
    del bpy.types.Scene.bevel_depth
    del bpy.types.Scene.bevel_resolution
    del bpy.types.Scene.save_option_full_text

def cli_register(argv):
    argv = argv[argv.index("--") + 1:]
        
    parser = argparse.ArgumentParser()
    parser.add_argument('--fontpath', dest="fontpath", type=str, required=False, help='')
    parser.add_argument('--text', dest="text", type=str, required=False, help='')
    parser.add_argument('--dirname', dest="dirname", type=str, required=False, help='')
    parser.add_argument('--extrude', dest="extrude", type=float, required=False, help='')
    parser.add_argument('--offset', dest="offset", type=float, required=False, help='')
    parser.add_argument('--bevel_depth', dest="bevel_depth", type=float, required=False, help='')
    parser.add_argument('--bevel_resolution', dest="bevel_resolution", type=int, required=False, help='')

    args = parser.parse_args(argv)
    
    text_list.clear()

    text = args.text
    fontpath = args.fontpath
    extrude = args.extrude
    offset = args.offset
    bevel_depth = args.bevel_depth
    bevel_resolution = args.bevel_resolution
    # print(text, fontpath, extrude, offset, bevel_depth, bevel_resolution)
    Make3DText(text, fontpath, extrude, offset, bevel_depth, bevel_resolution)
    
    dirname = args.dirname
    save_option_full_text = True
    # print(save_option_full_text, dirname)
    SaveText(save_option_full_text, dirname)


if __name__ == "__main__":
    argv = sys.argv

    if "--" not in argv:
        register()
    else:
        cli_register(argv)