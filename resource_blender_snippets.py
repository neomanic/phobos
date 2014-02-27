import bpy
import math


#definition

PI = math.pi

#extremities
alpha = 30 #angle between Y and leg socket
beta = 20  #angle between Y and arm socket
leg_1y = 0.4955 / 2
leg_1x = 0.469
leg_1_2 = 0.493
leg_2_3 = 0.488
arm_y = 0.6525 #distance of arm elements from origin
arm_0_1 = 0.3195 #mid-section to shoulder
arm_1_2 = 0.360 #length upper arm
arm_2_3 = 0.330 #length lower arm

#- two body joints (z)
#- one shoulder joint (y)
#- one neck joint (x)
#- one head joint (x)
#- one head joint (z)
#- one sensor joint (x)


#preprocessing
alpha = math.radians(alpha)
beta = math.radians(beta)
leg_1_3 = leg_1_2 + leg_2_3
arm_z = -math.sin(beta) * arm_0_1
arm_0_1 = math.cos(beta) * arm_0_1
arm_0_2 = arm_0_1 + arm_1_2
arm_0_3 = arm_0_2 + arm_2_3

x_vec = (0, PI/2, 0)
y_vec = (PI/2, 0, 0)
z_vec = (0, 0, PI/2)


#create model
legs_y = []
arms_y = []
for limb in range(4):
    #create leg
    leg = []
    x = leg_1x
    y = leg_1y
    z = 0
    leg.append([x, y, z])
    for seg in [leg_1_2, leg_1_3]:
                x = seg + leg_1x
                y = leg_1y
                leg.append([x, y, z])
    if limb < 2:
        for seg in leg:
            seg[0] = -seg[0]
    if limb == 1 or limb == 2:
        for seg in leg:
            seg[1] = -seg[1]
    legs_y.append(leg)

    if limb < 2:
        #create arm
        arm = []
        for seg in [arm_0_1, arm_0_2, arm_0_3]:
            x = seg
            y = arm_y
            z = arm_z
            arm.append([x, y, z])
        if limb == 0:
            for seg in arm:
                seg[0] = -seg[0]
        arms_y.append(arm)


legs_z = []
for limb in range(4):
    leg = []
    x = leg_1x
    y = leg_1y
    z = 0
    leg.append([x, y, z])
    x = (leg_1_3 + leg_1x)
    y = leg_1y
    leg.append([x, y, z])
    if limb < 2:
        for seg in leg:
            seg[0] = -seg[0]
    if limb == 1 or limb == 2:
        for seg in leg:
            seg[1] = -seg[1]
    legs_z.append(leg)

#body joints (first one kind of still related to legs)
body_x = [[[leg_1x/3.0, 0, 0], [-leg_1x/3.0, 0, 0.01]]]
body_y = [[[0, 0.58, 0]]]
body_z = [[[0, 0, -0.01], [0, 0, 0.01]]]

neck_base_y = (0.6525) + (0.1304-0.0725)
neck_top_y = neck_base_y + (0.2354-0.1304)
nose_y = neck_top_y + (0.2985-0.2355)
nose_z = -0.102
head_waggle_y = nose_y
head_x = [[[0, neck_base_y, 0], [0, neck_top_y, 0], [0, nose_y, nose_z]]]
head_y = [[[0, head_waggle_y, 0]]]

arms_x = [[[arm_0_1+arm_1_2/3.0, arm_y, arm_z], [-(arm_0_1+arm_1_2/3.0), arm_y, arm_z]]]

arms_ang1 = [[[arm_0_1/2, arm_y, arm_z/2]]]
arms_ang2 = [[[-arm_0_1/2, arm_y, arm_z/2]]]
legs_ang_v = [[[-leg_1x+math.cos(alpha)*leg_1x/3.0,
                leg_1y-math.sin(alpha)*leg_1x/3.0, 0],
               [leg_1x-math.cos(alpha)*leg_1x/3.0,
                -leg_1y+math.sin(alpha)*leg_1x/3.0, 0]]]
legs_ang_h = [[[leg_1x-math.cos(alpha)*leg_1x/3.0,
                leg_1y-math.sin(alpha)*leg_1x/3.0, 0],
               [-leg_1x+math.cos(alpha)*leg_1x/3.0,
                -leg_1y+math.sin(alpha)*leg_1x/3.0, 0]]]
#angled arms
#angled legs


def create_joints(js, name, rot_vec):
    joints = []
    for j in range(len(js)):
        for limb in range(len(js[j])):
            loc = js[j][limb]
            joints.append({"name": name+"_" + str(j) + ".00" + str(limb),
                          "location": tuple(loc),
                          "rotation": rot_vec})
    return joints
    #for leg in range(len(legs)):
    #    for limb in range(len(legs[leg])):
    #        loc = legs[leg][limb]
    #        joints.append({"name": "leg_" + str(leg) + ".00" + str(limb),
    #                      "location": tuple(loc),
    #                  "rotation": y_vec})

#for leg in legs:
#    print "Leg -----------------------\n", leg
#for arm in arms:
#    print "Arm -----------------------\n", arm


def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat


# Create the joints in blender

# joints is a list of dictionaries, each dictionary containing the 'location' and 'name' of a joint
# scale: a double value scaling the created objects
# material: name of the material that's supposed to be assigned to it
def create_joint_spheres(joints, scale, layer):
    green = makeMaterial('joint_spheres', (0, 1, 0), (1, 1, 1), 1)
    js_layers = 20*[False]
    js_layers[layer] = True
    for joint in joints:
        bpy.ops.mesh.primitive_uv_sphere_add(size = scale,
                                      layers = js_layers,
                                      location = joint['location'])
        obj = bpy.context.object
        obj.name = 'joint_sphere_' + joint['name']
        obj.data.materials.append(green)


def create_joint_arbors(joints, scale, layer):
    blue = makeMaterial('joint_spheres', (0, 0, 1), (1, 1, 1), 1)
    r1 = 0.075
    r2 = 1.5
    d1 = 4.0
    d2 = 0.05
    js_layers = 20*[False]
    js_layers[layer] = True
    for joint in joints:
        bpy.ops.mesh.primitive_cylinder_add(radius = r1*scale,
                                      depth = d1 * scale,
                                      layers = js_layers,
                                      location = joint['location'],
                                      rotation = joint['rotation'])
        j1 = bpy.context.object
        j1.data.materials.append(blue)
        bpy.ops.mesh.primitive_cylinder_add(radius = r2*scale,
                                      depth = d2 * scale,
                                      layers = js_layers,
                                      location = joint['location'],
                                      rotation = joint['rotation'])
        j2 = bpy.context.object
        j2.data.materials.append(blue)
        j1.select = True
        j2.select = True
        bpy.context.scene.objects.active = j1
        bpy.ops.object.join()
        j1.name = joint['name']
        j1["jointType"] = "hinge"
        j1["type"] = "joint"
        j1["anchor"] = "node2"
        j1["node2"] = ""

# do the magic
yJoints = []
yJoints.extend(create_joints(legs_y, "legY", y_vec))
yJoints.extend(create_joints(arms_y, "armY", y_vec))
yJoints.extend(create_joints(body_y, "bodyY", y_vec))
yJoints.extend(create_joints(head_y, "headY", y_vec))
zJoints = []
zJoints.extend(create_joints(legs_z, "legZ", z_vec))
zJoints.extend(create_joints(body_z, "bodyZ", z_vec))
xJoints = []
xJoints.extend(create_joints(body_x, "bodyX", x_vec))
xJoints.extend(create_joints(head_x, "headX", x_vec))
xJoints.extend(create_joints(arms_x, "armX", x_vec))
angled_armJoints = []
angled_armJoints.extend(create_joints(arms_ang1, "armAng", (0, PI/2+beta, 0)))
angled_armJoints.extend(create_joints(arms_ang2, "armAng", (0, -PI/2-beta, 0)))
angled_legJoints = []
angled_legJoints.extend(create_joints(legs_ang_v, "legAng", (0, PI/2, -alpha)))
angled_legJoints.extend(create_joints(legs_ang_h, "legAng", (0, PI/2, alpha)))


#note that objects can only be joined on the currently active layer, thus we have to switch to layer 1 before we create all these arbors
create_joint_spheres(xJoints, 0.01, 2)
create_joint_arbors(xJoints, 0.05, 1)
create_joint_spheres(yJoints, 0.01, 2)
create_joint_arbors(yJoints, 0.05, 1)
create_joint_spheres(zJoints, 0.01, 2)
create_joint_arbors(zJoints, 0.05, 1)
create_joint_spheres(angled_armJoints, 0.01, 2)
create_joint_arbors(angled_armJoints, 0.05, 1)
create_joint_spheres(angled_legJoints, 0.01, 2)
create_joint_arbors(angled_legJoints, 0.05, 1)


#import bpy
#
#for obj in bpy.context.selected_objects:
#    obj.name = obj.name.replace("AP5000-MantisHauptbaugruppe-010-101-SIM - ", "")
#    obj.data.name = obj.name

import bpy

for obj in bpy.context.selected_objects:
    obj["coll_bitmask"] = 0



#The following script places green haaelper sphere objects at the positions of all selected objects and fills in name and other properties, assuming that the selected objects are joints
#NOTE: For this script to work, you need to make all involved layers visible (probably 0, 1, 2)

import bpy

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

green = makeMaterial('joint_spheres', (0, 1, 0), (1, 1, 1), 1)
js_layers = 20*[False]
js_layers[2] = True
for joint in bpy.context.selected_objects:
    # create ball
    bpy.ops.mesh.primitive_uv_sphere_add(size = 0.01,
                                  layers = js_layers)
#                                  location = joint.location)
                                 # rotation = joint.rotation_euler)
    ball = bpy.context.object
    ball.name = 'joint_sphere_' + joint.name
    ball.data.materials.append(green)
    ball.parent = joint.parent
    ball.select = True
    bpy.context.scene.objects.active = joint.parent
    bpy.ops.object.parent_set() #makes active object parent of selected object
    ball.location = joint.location
    ball.rotation_euler = joint.rotation_euler

    #modify limb
    print(joint.name)
    print("    ", joint['node2'])
    print("")
    limb = bpy.context.scene.objects[joint['node2']]
    limb.select = True
    bpy.context.scene.objects.active = ball
    bpy.ops.object.parent_set()

    #modify joint
    joint['anchor'] = "node2"
    joint['node2'] = ball.name
    ball["coll_bitmask"] = 0
    ball["type"] = "body"


#gelenke stellen


import bpy
import math

m = 0

motor_specs = {
    "1": {"name": "Typ 1 (M70x18,CPL25-160)", "regularTorque": 176, "collisionTorque": 314, "maxSpeed": 0.2*2*math.pi},
    "2": {"name": "Typ 2 (M70x10,CPL20-160)", "regularTorque": 92, "collisionTorque": 147, "maxSpeed": 0.4*2*math.pi},
    "3": {"name": "Typ 3 (M50x14,CPL17-160)", "regularTorque": 54, "collisionTorque": 86, "maxSpeed": 0.3*2*math.pi},
    "beinSpindel": {"name": "Beinspindel_BJ2", "regularTorque": 200, "collisionTorque": 200, "maxSpeed": 1.0},
    "beinKreuz": {"name": "Beinkreuz_Spindel", "regularTorque": 288, "collisionTorque": 400, "maxSpeed": 0.03}
}

for obj in bpy.context.selected_objects:
    if "spec_motor" in obj:
        obj["maxForce"] = motor_specs[str(obj["spec_motor"])]["collisionTorque"]
        obj["maxSpeed"] = motor_specs[str(obj["spec_motor"])]["maxSpeed"]

for obj in bpy.context.selected_objects:
    obj["maxForce"] = 54
    obj["maxSpeed"] = 0.3*2*math.pi

graphics/src/GraphicsWidget.cpp


graphics/src/GraphicsWidget.cpp


#gelenktypen festlegen
import bpy
import math

def radMinMax(deg, fracPos):
    Min = -(deg / 360 * math.pi * 2 * (1-fracPos))
    Max = deg / 360 * math.pi * 2 * fracPos
    return Min, Max

for obj in bpy.context.selected_objects:#
    deg = -1
    fracPos = 0.5
    try:
        if obj["jointSpecification"] == 1:
            deg = 140
            fracPos = 0.5
        elif obj["jointSpecification"] == 2:
            deg = 270
            fracPos = 0.5
        elif obj["jointSpecification"] == 3:
            deg = 360
            fracPos = 0.5
        elif obj["jointSpecification"] == 4:
            deg = 50
            fracPos = 0.5
        elif obj["jointSpecification"] == 5:
            deg = 90
            fracPos = 0.5
        elif obj["jointSpecification"] == 6:
            deg = 90
            fracPos = 0.5
        elif obj["jointSpecification"] == 7:
            deg = 270
            fracPos = 0.5 - 20.0/270
        elif obj["jointSpecification"] == 8:
            deg = 270
            fracPos = 0.5 + 20.0/270
        elif obj["jointSpecification"] == 9:
            deg = 140
            fracPos = 0.5 - 30.0/140
        elif obj["jointSpecification"] == 10:
            deg = 140
            fracPos = 0.5 + 30.0/140
        try:
            if obj["invertAxis"] == 1:
                fracPos = 1 - fracPos
            print(obj.name, " has an inverted axis")
        except KeyError:
            print(obj.name, "has no inverted axis")
        obj["lowStop"], obj["highStop"] = radMinMax(deg, fracPos)
    except KeyError:
        print("No jointSpecification for joint", obj.name)




#create CameraSensor
import bpy

hud_i = 1
for obj in bpy.context.selected_objects:
    if obj["sensorType"] == "CameraSensor":
        obj["attached_node"] = 1
        obj["depth_image"] = "false"
        obj["show_cam"] = "true"
        obj["hud_idx"] = hud_i
        hud_i += 1
        obj["position_offset_x"] = 0.0
        obj["position_offset_y"] = 0.0
        obj["position_offset_z"] = 0.0
        obj["orientation_offset_yaw"] = 0.0
        obj["orientation_offset_pitch"] = 0.0
        obj["orientation_offset_roll"] = 0.0

#alle selected objects smooth machen
import bpy

for obj in bpy.context.selected_objects:
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all()
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.modifier_add(type='EDGE_SPLIT')


#physics collision!
for obj in bpy.context.selected_objects:
    print(obj.game.collision_mask)
#    obj.game.use_collision_bounds=True
#    obj.game.collision_bounds_type=True
#    bpy.types.GameObjectSettings.collision_bounds_type: enum in [‘BOX’, ‘SPHERE’, ‘CYLINDER’, ‘CONE’, ‘CONVEX_HULL’, ‘TRIANGLE_MESH’, ‘CAPSULE’], default ‘BOX’
