import bpy
import math
from math import cos, pi, sin, tan
import random
from random import TWOPI, randint, uniform
import contextlib
from bpybb.random import time_seed
from bpybb.output import set_1080px_square_render_res
from bpybb.color import hex_color_to_rgba, hex_color_to_rgb
from bpybb.utils import clean_scene, active_object, clean_scene_experimental
from bpybb.object import track_empty
from bpybb.animate import set_fcurve_extrapolation_to_linear

clean_scene()


def setup_camera(loc, rot):
    """
    create and setup the camera
    """
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    camera = active_object()

    # set the camera as the "active camera" in the scene
    bpy.context.scene.camera = camera

    # set the Focal Length of the camera
    camera.data.lens = 14

    camera.data.passepartout_alpha = 0.9

    empty = track_empty(camera)

    return empty


def set_scene_props(fps, loop_seconds):
    """
    Set scene properties
    """
    frame_count = fps * loop_seconds

    scene = bpy.context.scene
    scene.frame_end = frame_count

    # set the world background to black
    world = bpy.data.worlds["World"]
    if "Background" in world.node_tree.nodes:
        world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

    scene.render.fps = fps

    scene.frame_current = 1
    scene.frame_start = 1

    scene.render.engine = "CYCLES"

    # Use the GPU to render
    scene.cycles.device = 'GPU'

    scene.cycles.samples = 96

    scene.view_settings.look = "Very High Contrast"

    set_1080px_square_render_res()


def scene_setup(i=0):
    fps = 30
    loop_seconds = 4
    frame_count = fps * loop_seconds

    project_name = "shapeshifting"
    bpy.context.scene.render.image_settings.file_format = "FFMPEG"
    bpy.context.scene.render.ffmpeg.format = "MPEG4"
    bpy.context.scene.render.filepath = f"/tmp/project_{project_name}/omar_{i}.mp4"

    seed = 0
    if seed:
        random.seed(seed)
    else:
        time_seed()

    # Utility Building Blocks
    use_clean_scene_experimental = False
    if use_clean_scene_experimental:
        clean_scene_experimental()
    else:
        clean_scene()

    set_scene_props(fps, loop_seconds)

    loc = (8, 0, 2.5)
    rot = (0, 0, 0)
    setup_camera(loc, rot)

    context = {
        "frame_count": frame_count,
    }

    return context

scene_setup()

bpy.ops.object.light_add(type="AREA", radius=10, location=(0, 0, 4))
bpy.context.object.data.energy = 800
bpy.context.object.data.color = hex_color_to_rgb("#F2E7DC")
bpy.context.object.data.shape = "DISK"

degrees = 180
bpy.ops.object.light_add(type="AREA", radius=10, location=(0, 0, -4), rotation=(0.0, math.radians(degrees), 0.0))
bpy.context.object.data.energy = 600
bpy.context.object.data.color = hex_color_to_rgb("#F29F05")
bpy.context.object.data.shape = "DISK"

#########################################################################

bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=True)
bpy.ops.curve.subdivide(number_cuts=18)

# Cache a reference to the curve.
curve = bpy.context.active_object

# Locate the array of bezier points.
bez_points = curve.data.splines[0].bezier_points

sz = len(bez_points)
i_to_theta = TWOPI / sz
for i in range(0, sz, 1):

    # Set every sixth coordinate's z to 0.5.
    if i % 6 == 0:
        bez_points[i].co.z = 0.5

    if i % 2 == 0:
        bez_points[i].handle_right *= 2.0
        bez_points[i].handle_left *= 0.5
    elif i % 4 == 0:
        bez_points[i].handle_right.z -= 5.0
        bez_points[i].handle_left.z += 5.0
    else:
        bez_points[i].co *= 0.5

    # Shift cos(t) from -1 .. 1 to 0 .. 4.
    scalar = 2.0 + 2.0 * cos(i * i_to_theta)

    # Multiply coordinate by cos(t).
    bez_points[i].co *= scalar

# Resize within edit mode.
bpy.ops.transform.resize(value=(3.0, 3.0, 1.0))

bpy.ops.object.mode_set(mode="OBJECT")

##########################################################################

for i in range(40):
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

    axis = bpy.context.active_object

    bpy.ops.object.constraint_add(type='FOLLOW_PATH')

    bpy.context.object.constraints["Follow Path"].target = curve

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2)

    bpy.context.view_layer.objects.active.parent = axis

    bpy.context.view_layer.objects.active = axis

    bpy.context.object.constraints["Follow Path"].use_curve_follow = True


    obj = axis.constraints["Follow Path"]
    data_path = 'offset'
    start_value=i*2.5
    mid_value=2.5+i*2.5
    start_frame=1
    loop_length=120

    setattr(obj, data_path, start_value)
    # add a keyframe at the start
    obj.keyframe_insert(data_path, frame=start_frame)

    # set the end value
    setattr(obj, data_path, mid_value)
    # add a keyframe in the end
    end_frame = start_frame + loop_length
    obj.keyframe_insert(data_path, frame=end_frame)
    set_fcurve_extrapolation_to_linear()

##############################################################################
