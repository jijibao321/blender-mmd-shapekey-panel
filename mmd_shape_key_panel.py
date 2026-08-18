bl_info = {
    "name": "MMD Shape Key Panel and Face Controller",
    "author": "Your Name",
    "version": (2, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N 面板 > MMD 形态键",
    "description": "MMD 中文形态键面板与可跟随 MMR 控制器的视图嘴型控制器",
    "category": "Animation",
}

import re

import bpy
from bpy.props import BoolProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Matrix

# ============================================================
# Shape Key 分类
# ============================================================

EYE_KEYS = {
    "まばたき",
    "笑い",
    "ウィンク",
    "ウィンク右",
    "ウィンク２",
    "ウィンク２右",
    "なごみ",
    "なごみ左",
    "なごみ右",
    "びっくり",
    "じと目",
    "悲しむ",
    "怒り目",
    "ジト目",
    "眼角上",
    "眼角下",
    "下眼上",
    "星目",
    "じと目2",
    "はちゅ目",
}

MOUTH_KEYS = {
    "あ",
    "い",
    "う",
    "え",
    "お",
    "にやり",
    "ワ",
    "ん",
    "い１",
    "い２",
    "あ２",
    "お２",
    "にやり２",
    "にやり３",
    "ω",
    "てへぺ",
    "ぺろっ",
    "口角上げ",
    "口横広げ",
    "口横狭め",
    "舌広げ",
    "もぐもぐ口",
}

BROW_KEYS = {
    "真面目",
    "困る",
    "にこり",
    "怒り",
    "恥ずかしい",
    "上",
    "下",
    "前",
    "困る左",
    "困る右",
    "にこり左",
    "にこり右",
    "怒り左",
    "怒り右",
    "恥ずかしい左",
    "恥ずかしい右",
    "上左",
    "上右",
    "下左",
    "下右",
    "前左",
    "前右",
}

OTHER_KEYS = {
    "噛む",
    "もぐもぐ",
}

CATEGORY_MAP = {
    "眼睛": EYE_KEYS,
    "嘴": MOUTH_KEYS,
    "眉毛": BROW_KEYS,
    "其他": OTHER_KEYS,
}

DISPLAY_NAME_MAP = {
    "まばたき": "闭眼（眼角凹）",
    "笑い": "闭眼（笑）",
    "ウィンク": "左闭眼（笑）",
    "ウィンク右": "右闭眼（笑）",
    "ウィンク２": "左闭眼（眼角凹）",
    "ウィンク２右": "右闭眼（眼角凹）",
    "なごみ": "闭眼（眼角平）",
    "なごみ左": "左闭眼（眼角平）",
    "なごみ右": "右闭眼（眼角平）",
    "びっくり": "眼睛微睁大",
    "じと目": "生气",
    "悲しむ": "伤心",
    "怒り目": "非常生气",
    "ジト目": "眼神空洞",
    "眼角上": "眼角上",
    "眼角下": "眼角下",
    "下眼上": "下眼皮微向上",
    "星目": "星星眼",
    "じと目2": "死鱼眼",
    "はちゅ目": "懵圈眼",

    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
    "にやり": "微笑",
    "ワ": "wa",
    "ん": "n（撅嘴）",
    "い１": "i（呲牙）",
    "い２": "i（呲牙咧嘴）",
    "あ２": "a（吃惊）",
    "お２": "o",
    "にやり２": "邪魅一笑",
    "にやり３": "邪魅大笑",
    "ω": "抿嘴成 W",
    "てへぺ": "向上吐舌头",
    "ぺろっ": "中间吐舌头",
    "口角上げ": "嘴角上扬",
    "口横广げ": "嘴角下扬",
    "口横広げ": "嘴角下扬",
    "口横狭め": "嘴变小",
    "舌広げ": "舌头变宽",
    "もぐもぐ口": "生气（可爱版）",

    "真面目": "严肃认真眉",
    "困る": "为难",
    "にこり": "浅笑",
    "怒り": "发怒",
    "恥ずかしい": "为难害羞",
    "上": "眼皮上抬",
    "下": "眼皮下降",
    "前": "眉向中心动",
    "困る左": "左困惑苦恼",
    "困る右": "右困惑苦恼",
    "にこり左": "左浅笑",
    "にこり右": "右浅笑",
    "怒り左": "左发怒",
    "怒り右": "右发怒",
    "恥ずかしい左": "左害羞",
    "恥ずかしい右": "右害羞",
    "上左": "左眉上动",
    "上右": "右眉上动",
    "下左": "左眉下动",
    "下右": "右眉下动",
    "前左": "左眉向中心动",
    "前右": "右眉向中心动",

    "噛む": "下巴变长",
    "もぐもぐ": "鼓腮帮子",
}

# ============================================================
# 控制器配置
# ============================================================

# 所有面板内部元素缩放至旧版本的 50%。
CONTROLLER_SCALE = 0.5

PANEL_SIZE = 0.5 * CONTROLLER_SCALE
PANEL_HALF = PANEL_SIZE * 0.5

# ------------------------------------------------------------
# 最终面板位置。
#
# 这些数值是实际 Blender 场景单位，不会再被角色根骨、
# Armature 或 MMR 控制骨的 Scale 压缩。
# ------------------------------------------------------------
PANEL_OFFSET_X = 0.3
PANEL_OFFSET_Y = 1.4
PANEL_OFFSET_Z = 0.0

# 面板旋转：X = -90°，Y = 0°，Z = 0°。
PANEL_ROTATION_X = -1.5707963267948966
PANEL_ROTATION_Y = 0.0
PANEL_ROTATION_Z = 0.0

MOUTH_BOX_SIZE = 0.16 * CONTROLLER_SCALE
MOUTH_BOX_HALF = MOUTH_BOX_SIZE * 0.5
MOUTH_TARGET_DISTANCE = 0.055 * CONTROLLER_SCALE

A_SLIDER_LENGTH = 0.16 * CONTROLLER_SCALE
LABEL_SIZE = 0.09 * CONTROLLER_SCALE

COLLECTION_NAME = "MMD_Face_Controller"

CONTROLLER_ROOT_NAME = "MMD_FaceControls"
MOUTH_CONTROL_NAME = "CTRL_Mouth_Vowels"
A_CONTROL_NAME = "CTRL_Mouth_A"

FOLLOW_CONSTRAINT_NAME = "MMD MMR Follow"

ROOT_BONE_CANDIDATES = (
    "root",
    "Root",
    "ROOT",
    "全ての親",
    "全ての親.root",
    "センター",
    "center",
    "Center",
)

MORPH_ALIASES = {
    "mouth_a": ("あ", "a", "mouth_a", "moutha", "口あ"),
    "mouth_i": ("い", "i", "mouth_i", "mouthi", "口い"),
    "mouth_u": ("う", "u", "mouth_u", "mouthu", "口う"),
    "mouth_e": ("え", "e", "mouth_e", "mouthe", "口え"),
    "mouth_o": ("お", "o", "mouth_o", "moutho", "口お"),
}

# ============================================================
# 通用辅助函数
# ============================================================

def normalize_name(name):
    return re.sub(r"[\s_\-.]+", "", name).lower().strip()

def get_shape_key_category(name):
    for category, key_names in CATEGORY_MAP.items():
        if name in key_names:
            return category

    return "其他"

def get_display_name(name):
    return DISPLAY_NAME_MAP.get(name, name)

def has_shape_keys(obj):
    return (
        obj is not None
        and obj.type == "MESH"
        and obj.data is not None
        and obj.data.shape_keys is not None
        and len(obj.data.shape_keys.key_blocks) > 1
    )

def find_armature(obj):
    current = obj

    while current is not None:
        if current.type == "ARMATURE":
            return current

        current = current.parent

    return None

def resolve_armature(context):
    props = context.scene.mmd_face_props

    if props.character_armature is not None:
        selected = props.character_armature

        if selected.type == "ARMATURE":
            return selected

        return find_armature(selected)

    active_object = context.active_object

    if active_object is None:
        return None

    if active_object.type == "ARMATURE":
        return active_object

    return find_armature(active_object)

def find_character_meshes(armature):
    if armature is None:
        return []

    return [
        obj
        for obj in armature.children_recursive
        if has_shape_keys(obj)
    ]

def find_root_bone(armature, requested_name=""):
    if armature is None or armature.type != "ARMATURE":
        return None

    bones = armature.data.bones

    if requested_name:
        bone = bones.get(requested_name)

        if bone is not None:
            return bone

    for candidate in ROOT_BONE_CANDIDATES:
        bone = bones.get(candidate)

        if bone is not None:
            return bone

    for bone in bones:
        if bone.parent is None:
            return bone

    return bones[0] if bones else None

def get_shape_key_matches(meshes, morph_id):
    aliases = {
        normalize_name(name)
        for name in MORPH_ALIASES.get(morph_id, ())
    }

    matches = []

    for mesh in meshes:
        for key_block in mesh.data.shape_keys.key_blocks:
            if key_block.name == "Basis":
                continue

            if normalize_name(key_block.name) in aliases:
                matches.append(key_block)

    return matches

# ============================================================
# 矩阵与位置计算
# ============================================================

def make_panel_local_matrix():
    """
    创建面板自身的偏移和旋转矩阵。

    偏移：
        X = 0.3
        Y = 0.7
        Z = 0.0

    旋转：
        X = -90°
        Y = 0°
        Z = 0°
    """
    translation = Matrix.Translation(
        (
            PANEL_OFFSET_X,
            PANEL_OFFSET_Y,
            PANEL_OFFSET_Z,
        )
    )

    rotation_x = Matrix.Rotation(
        PANEL_ROTATION_X,
        4,
        "X",
    )

    rotation_y = Matrix.Rotation(
        PANEL_ROTATION_Y,
        4,
        "Y",
    )

    rotation_z = Matrix.Rotation(
        PANEL_ROTATION_Z,
        4,
        "Z",
    )

    return translation @ rotation_x @ rotation_y @ rotation_z

def get_pose_bone_world_matrix(armature, bone_name):
    pose_bone = armature.pose.bones.get(bone_name)

    if pose_bone is None:
        raise RuntimeError(
            f"在 Armature“{armature.name}”中找不到骨骼“{bone_name}”。"
        )

    return armature.matrix_world @ pose_bone.matrix

def remove_matrix_scale(matrix):
    """
    分解矩阵后重新组合，只保留位置与旋转，故意移除 Scale。

    这样 MMD 导入模型常见的 0.05 左右 Armature Scale
    不会将 0.7m 缩小为约 0.036389m。
    """
    location, rotation, _scale = matrix.decompose()

    return (
        Matrix.Translation(location)
        @ rotation.to_matrix().to_4x4()
    )

def build_initial_panel_world_matrix(armature, root_bone_name):
    """
    生成初始世界矩阵。

    角色根骨只提供：
    - 世界位置；
    - 世界旋转；

    根骨与 Armature 的缩放均被移除。
    """
    root_world_matrix = get_pose_bone_world_matrix(
        armature,
        root_bone_name,
    )

    root_without_scale = remove_matrix_scale(
        root_world_matrix
    )

    return root_without_scale @ make_panel_local_matrix()

# ============================================================
# Child Of 跟随约束
# ============================================================

def get_follow_target_world_matrix(follow_object, bone_name=""):
    """
    获取 Child Of 目标的实际世界矩阵。

    - 普通 Object：返回 object.matrix_world；
    - Armature + 骨骼：返回 Armature 世界矩阵 × Pose Bone 矩阵。
    """
    if follow_object is None:
        raise RuntimeError("没有指定 MMR 跟随控制器。")

    if follow_object.type == "ARMATURE" and bone_name:
        pose_bone = follow_object.pose.bones.get(bone_name)

        if pose_bone is None:
            raise RuntimeError(
                f"在跟随 Armature“{follow_object.name}”中找不到控制骨“{bone_name}”。"
            )

        return follow_object.matrix_world @ pose_bone.matrix

    return follow_object.matrix_world.copy()

def add_follow_constraint(
    obj,
    follow_object,
    follow_bone_name,
    desired_world_matrix,
):
    """
    使用 Child Of 约束跟随 MMR 控制器。

    这是本版最重要的修正：

    不再使用：
        obj.parent_type = "BONE"

    因为直接 Bone Parent 会导致 obj.location 被换算为
    MMR 控制骨局部坐标，并被控制骨 Scale 压缩。

    现在 obj 保持无父级，Location 是自身基础数值；
    跟随关系通过 Child Of Constraint 完成。
    """
    if follow_object is None:
        return None, "WORLD", ""

    bone_name = follow_bone_name.strip()

    if follow_object.type != "ARMATURE":
        bone_name = ""

    target_world_matrix = get_follow_target_world_matrix(
        follow_object,
        bone_name,
    )

    constraint = obj.constraints.new("CHILD_OF")
    constraint.name = FOLLOW_CONSTRAINT_NAME
    constraint.target = follow_object

    if bone_name:
        constraint.subtarget = bone_name

    # 先关闭约束，保证可安全地写入初始位置。
    constraint.influence = 0.0

    obj.parent = None
    obj.parent_type = "OBJECT"
    obj.parent_bone = ""
    obj.matrix_parent_inverse = Matrix.Identity(4)

    # 此时对象没有 Parent，因此这里的 Transform 是对象自身坐标。
    obj.matrix_world = desired_world_matrix

    bpy.context.view_layer.update()

    # Child Of 的 inverse 应是目标当前矩阵的逆矩阵。
    #
    # 这样约束启用后：
    # target_matrix @ inverse_matrix @ object_matrix
    # = target_matrix @ target_matrix.inverted() @ object_matrix
    # = object_matrix
    #
    # 因此启用约束时不会发生跳位。
    constraint.inverse_matrix = target_world_matrix.inverted()

    constraint.influence = 1.0

    bpy.context.view_layer.update()

    if bone_name:
        return constraint, "CONSTRAINT_BONE", bone_name

    return constraint, "CONSTRAINT_OBJECT", ""

# ============================================================
# 控制器对象创建
# ============================================================

def get_or_create_collection():
    collection = bpy.data.collections.get(COLLECTION_NAME)

    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(collection)

    return collection

def create_empty(
    name,
    collection,
    display_type="PLAIN_AXES",
    size=0.02,
):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)

    obj.empty_display_type = display_type
    obj.empty_display_size = size
    obj.hide_render = True

    return obj

def parent_to_object(
    obj,
    parent,
    local_location=(0.0, 0.0, 0.0),
    local_rotation=(0.0, 0.0, 0.0),
):
    """
    用于面板内部元素。

    注意：只有面板内部元素会 Parent 到 MMD_FaceControls。
    MMD_FaceControls 本身不会 Parent 到 MMR 控制骨。
    """
    obj.parent = parent
    obj.parent_type = "OBJECT"
    obj.parent_bone = ""
    obj.matrix_parent_inverse = Matrix.Identity(4)

    obj.location = local_location
    obj.rotation_euler = local_rotation
    obj.scale = (1.0, 1.0, 1.0)

def create_wire(name, points, collection, parent):
    mesh = bpy.data.meshes.new(name)

    vertices = [
        (x, 0.0, z)
        for x, z in points
    ]

    edges = [
        (index, index + 1)
        for index in range(len(vertices) - 1)
    ]

    mesh.from_pydata(vertices, edges, [])
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)

    parent_to_object(obj, parent)

    obj.display_type = "WIRE"
    obj.hide_render = True
    obj.hide_select = True

    return obj

def create_text(
    name,
    text,
    location,
    size,
    collection,
    parent,
):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size

    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)

    parent_to_object(
        obj,
        parent,
        local_location=location,
        local_rotation=(
            1.5707963267948966,
            0.0,
            0.0,
        ),
    )

    obj.hide_render = True
    obj.hide_select = True

    return obj

def add_xz_limits(obj, min_x, max_x, min_z, max_z):
    constraint = obj.constraints.new("LIMIT_LOCATION")
    constraint.name = "MMD Controller Limits"
    constraint.owner_space = "LOCAL"

    constraint.use_min_x = True
    constraint.min_x = min_x

    constraint.use_max_x = True
    constraint.max_x = max_x

    constraint.use_min_y = True
    constraint.min_y = 0.0

    constraint.use_max_y = True
    constraint.max_y = 0.0

    constraint.use_min_z = True
    constraint.min_z = min_z

    constraint.use_max_z = True
    constraint.max_z = max_z

# ============================================================
# Shape Key Driver
# ============================================================

def get_driver_fcurve(key_block, replace_existing):
    data_path = key_block.path_from_id("value")
    shape_keys = key_block.id_data
    animation_data = shape_keys.animation_data

    if animation_data is not None:
        existing_driver = animation_data.drivers.find(data_path)

        if existing_driver is not None:
            if not replace_existing:
                return None

            key_block.driver_remove("value")

    return key_block.driver_add("value")

def add_transform_variable(
    driver,
    variable_name,
    controller,
    transform_type,
):
    variable = driver.variables.new()
    variable.name = variable_name
    variable.type = "TRANSFORMS"

    target = variable.targets[0]
    target.id = controller
    target.transform_type = transform_type
    target.transform_space = "LOCAL_SPACE"

def add_direction_driver(
    key_block,
    controller,
    center_x,
    center_z,
    direction,
    target_distance,
    replace_existing,
):
    fcurve = get_driver_fcurve(
        key_block,
        replace_existing,
    )

    if fcurve is None:
        return False

    driver = fcurve.driver
    driver.type = "SCRIPTED"

    add_transform_variable(
        driver,
        "x",
        controller,
        "LOC_X",
    )

    add_transform_variable(
        driver,
        "z",
        controller,
        "LOC_Z",
    )

    distance = max(float(target_distance), 0.000001)

    positive_x = (
        f"max(0.0, (x - {center_x:.6f}) / "
        f"{distance:.6f})"
    )

    negative_x = (
        f"max(0.0, ({center_x:.6f} - x) / "
        f"{distance:.6f})"
    )

    positive_z = (
        f"max(0.0, (z - {center_z:.6f}) / "
        f"{distance:.6f})"
    )

    negative_z = (
        f"max(0.0, ({center_z:.6f} - z) / "
        f"{distance:.6f})"
    )

    total = (
        f"max(1.0, {positive_x} + {negative_x} + "
        f"{positive_z} + {negative_z})"
    )

    if direction == "i":
        component = positive_z
    elif direction == "u":
        component = negative_z
    elif direction == "o":
        component = negative_x
    elif direction == "e":
        component = positive_x
    else:
        raise ValueError(f"未知嘴型方向：{direction}")

    driver.expression = f"{component} / {total}"

    return True

def add_a_driver(
    key_block,
    controller,
    slider_start_x,
    slider_length,
    replace_existing,
):
    fcurve = get_driver_fcurve(
        key_block,
        replace_existing,
    )

    if fcurve is None:
        return False

    driver = fcurve.driver
    driver.type = "SCRIPTED"

    add_transform_variable(
        driver,
        "x",
        controller,
        "LOC_X",
    )

    driver.expression = (
        "max(0.0, min(1.0, "
        f"(x - {slider_start_x:.6f}) / "
        f"{slider_length:.6f}))"
    )

    return True

def is_plugin_driver(fcurve):
    controller_names = {
        CONTROLLER_ROOT_NAME,
        MOUTH_CONTROL_NAME,
        A_CONTROL_NAME,
    }

    for variable in fcurve.driver.variables:
        for target in variable.targets:
            if target.id is not None:
                if target.id.name in controller_names:
                    return True

    return False

def remove_plugin_drivers():
    for obj in bpy.data.objects:
        if not has_shape_keys(obj):
            continue

        shape_keys = obj.data.shape_keys
        animation_data = shape_keys.animation_data

        if animation_data is None:
            continue

        for fcurve in list(animation_data.drivers):
            if is_plugin_driver(fcurve):
                shape_keys.driver_remove(fcurve.data_path)

def delete_controller():
    remove_plugin_drivers()

    collection = bpy.data.collections.get(COLLECTION_NAME)

    if collection is None:
        return

    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    bpy.data.collections.remove(collection)

# ============================================================
# Scene 属性
# ============================================================

class MMD_FACE_Properties(PropertyGroup):
    character_armature: PointerProperty(
        name="角色 Armature",
        description="选择原始 MMD 模型的 Armature",
        type=bpy.types.Object,
    )

    follow_controller_object: PointerProperty(
        name="MMR 跟随控制器",
        description=(
            "选择 MMR 中用于移动角色的控制器对象。"
            "若对象是 Armature，可填写控制骨名称。"
        ),
        type=bpy.types.Object,
    )

    follow_controller_bone: StringProperty(
        name="控制器骨骼",
        description=(
            "仅当 MMR 跟随控制器为 Armature 时使用。"
            "留空则跟随整个 Armature 对象。"
        ),
        default="",
    )

    root_bone_name: StringProperty(
        name="备用根骨名称",
        description="自动识别失败时，手动指定原角色根骨名称",
        default="",
    )

    replace_existing_drivers: BoolProperty(
        name="替换已有驱动",
        description="允许覆盖嘴型 Shape Key 上已有的 Driver",
        default=False,
    )

    rebuild_controller: BoolProperty(
        name="重建已有控制器",
        description="删除旧面板及插件 Driver 后重新创建",
        default=False,
    )

# ============================================================
# Shape Key 关键帧操作
# ============================================================

class MMD_OT_KeyframeShapeKey(Operator):
    bl_idname = "mmd.keyframe_shape_key"
    bl_label = "插入关键帧"
    bl_description = "为当前形态键数值插入关键帧"

    shape_key_name: StringProperty()

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
        )

    def execute(self, context):
        obj = context.active_object

        if not has_shape_keys(obj):
            self.report({"WARNING"}, "当前对象没有形态键。")
            return {"CANCELLED"}

        key_block = obj.data.shape_keys.key_blocks.get(
            self.shape_key_name
        )

        if key_block is None:
            self.report(
                {"WARNING"},
                f"未找到形态键：{self.shape_key_name}",
            )
            return {"CANCELLED"}

        key_block.keyframe_insert(data_path="value")

        return {"FINISHED"}

# ============================================================
# 创建控制器
# ============================================================

class MMD_FACE_OT_build_controller(Operator):
    bl_idname = "mmd_face.build_controller"
    bl_label = "创建视图表情控制器"
    bl_description = "创建可通过 Child Of 跟随 MMR 控制器的表情面板"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.mmd_face_props
        armature = resolve_armature(context)

        if armature is None:
            self.report({"ERROR"}, "请选择角色 Armature。")
            return {"CANCELLED"}

        meshes = find_character_meshes(armature)

        if not meshes:
            self.report(
                {"ERROR"},
                "角色 Armature 子级中没有找到带 Shape Key 的网格。",
            )
            return {"CANCELLED"}

        root_bone = find_root_bone(
            armature,
            props.root_bone_name,
        )

        if root_bone is None:
            self.report({"ERROR"}, "没有找到角色根骨。")
            return {"CANCELLED"}

        old_controller = bpy.data.objects.get(
            CONTROLLER_ROOT_NAME
        )

        if old_controller is not None:
            if not props.rebuild_controller:
                self.report(
                    {"ERROR"},
                    "控制器已存在。请勾选“重建已有控制器”，或先删除旧控制器。",
                )
                return {"CANCELLED"}

            delete_controller()

        collection = get_or_create_collection()

        panel_root = create_empty(
            CONTROLLER_ROOT_NAME,
            collection,
            display_type="PLAIN_AXES",
            size=0.04 * CONTROLLER_SCALE,
        )

        try:
            # ------------------------------------------------
            # 计算最终世界矩阵：
            # - 使用角色根骨位置和旋转；
            # - 不使用根骨 / Armature Scale；
            # - PANEL_OFFSET_Y=0.7 不会缩为 0.036389。
            # ------------------------------------------------
            desired_world_matrix = build_initial_panel_world_matrix(
                armature,
                root_bone.name,
            )

            follow_object = props.follow_controller_object
            follow_bone_name = props.follow_controller_bone.strip()

            # ------------------------------------------------
            # 不使用 Object Parent / Bone Parent。
            #
            # 使用 Child Of 约束保持位置后跟随 MMR。
            # 因此 MMD_FaceControls 的 Location 不会因父级
            # Scale 被重算为 0.036389。
            # ------------------------------------------------
            constraint, follow_mode, used_bone_name = (
                add_follow_constraint(
                    panel_root,
                    follow_object,
                    follow_bone_name,
                    desired_world_matrix,
                )
            )

            if follow_object is None:
                panel_root.parent = None
                panel_root.matrix_world = desired_world_matrix
                follow_object_name = ""

            else:
                follow_object_name = follow_object.name

        except RuntimeError as error:
            bpy.data.objects.remove(panel_root, do_unlink=True)
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        panel_root["mmd_face_controller"] = True
        panel_root["character_armature"] = armature.name
        panel_root["root_bone"] = root_bone.name
        panel_root["follow_mode"] = follow_mode
        panel_root["follow_object"] = follow_object_name
        panel_root["follow_bone"] = used_bone_name
        panel_root["panel_offset_x"] = PANEL_OFFSET_X
        panel_root["panel_offset_y"] = PANEL_OFFSET_Y
        panel_root["panel_offset_z"] = PANEL_OFFSET_Z
        panel_root["panel_rotation_x"] = PANEL_ROTATION_X
        panel_root["panel_rotation_y"] = PANEL_ROTATION_Y
        panel_root["panel_rotation_z"] = PANEL_ROTATION_Z
        panel_root["controller_scale"] = CONTROLLER_SCALE

        # ----------------------------------------------------
        # 面板外框
        # ----------------------------------------------------
        create_wire(
            "MMD_Panel_Frame",
            [
                (-PANEL_HALF, -PANEL_HALF),
                (PANEL_HALF, -PANEL_HALF),
                (PANEL_HALF, PANEL_HALF),
                (-PANEL_HALF, PANEL_HALF),
                (-PANEL_HALF, -PANEL_HALF),
            ],
            collection,
            panel_root,
        )

        # ----------------------------------------------------
        # i / u / e / o 控制区
        # ----------------------------------------------------
        mouth_x = 0.055 * CONTROLLER_SCALE
        mouth_z = -0.035 * CONTROLLER_SCALE

        create_wire(
            "MMD_Mouth_Frame",
            [
                (
                    mouth_x - MOUTH_BOX_HALF,
                    mouth_z - MOUTH_BOX_HALF,
                ),
                (
                    mouth_x + MOUTH_BOX_HALF,
                    mouth_z - MOUTH_BOX_HALF,
                ),
                (
                    mouth_x + MOUTH_BOX_HALF,
                    mouth_z + MOUTH_BOX_HALF,
                ),
                (
                    mouth_x - MOUTH_BOX_HALF,
                    mouth_z + MOUTH_BOX_HALF,
                ),
                (
                    mouth_x - MOUTH_BOX_HALF,
                    mouth_z - MOUTH_BOX_HALF,
                ),
            ],
            collection,
            panel_root,
        )

        label_offset = 0.105 * CONTROLLER_SCALE

        create_text(
            "MMD_Label_I",
            "i",
            (mouth_x, 0.0, mouth_z + label_offset),
            LABEL_SIZE,
            collection,
            panel_root,
        )

        create_text(
            "MMD_Label_U",
            "u",
            (mouth_x, 0.0, mouth_z - label_offset),
            LABEL_SIZE,
            collection,
            panel_root,
        )

        create_text(
            "MMD_Label_O",
            "o",
            (mouth_x - label_offset, 0.0, mouth_z),
            LABEL_SIZE,
            collection,
            panel_root,
        )

        create_text(
            "MMD_Label_E",
            "e",
            (mouth_x + label_offset, 0.0, mouth_z),
            LABEL_SIZE,
            collection,
            panel_root,
        )

        # ----------------------------------------------------
        # a 滑块
        # ----------------------------------------------------
        a_slider_z = 0.175 * CONTROLLER_SCALE
        a_slider_left_x = 0.025 * CONTROLLER_SCALE
        a_slider_right_x = a_slider_left_x + A_SLIDER_LENGTH

        create_wire(
            "MMD_A_Slider",
            [
                (a_slider_left_x, a_slider_z),
                (a_slider_right_x, a_slider_z),
            ],
            collection,
            panel_root,
        )

        create_text(
            "MMD_Label_A",
            "a",
            (
                -0.075 * CONTROLLER_SCALE,
                0.0,
                a_slider_z,
            ),
            LABEL_SIZE,
            collection,
            panel_root,
        )

        # ----------------------------------------------------
        # i/u/e/o 控制方块
        # ----------------------------------------------------
        mouth_control = create_empty(
            MOUTH_CONTROL_NAME,
            collection,
            display_type="CUBE",
            size=0.018 * CONTROLLER_SCALE,
        )

        parent_to_object(
            mouth_control,
            panel_root,
            local_location=(mouth_x, 0.0, mouth_z),
        )

        mouth_control.color = (0.1, 0.8, 1.0, 1.0)

        add_xz_limits(
            mouth_control,
            mouth_x - MOUTH_BOX_HALF,
            mouth_x + MOUTH_BOX_HALF,
            mouth_z - MOUTH_BOX_HALF,
            mouth_z + MOUTH_BOX_HALF,
        )

        # ----------------------------------------------------
        # a 控制方块
        # ----------------------------------------------------
        a_control = create_empty(
            A_CONTROL_NAME,
            collection,
            display_type="CUBE",
            size=0.018 * CONTROLLER_SCALE,
        )

        parent_to_object(
            a_control,
            panel_root,
            local_location=(
                a_slider_left_x,
                0.0,
                a_slider_z,
            ),
        )

        a_control.color = (0.1, 0.8, 1.0, 1.0)

        add_xz_limits(
            a_control,
            a_slider_left_x,
            a_slider_right_x,
            a_slider_z,
            a_slider_z,
        )

        # ----------------------------------------------------
        # 创建 Shape Key Driver
        # ----------------------------------------------------
        vowel_directions = {
            "mouth_i": "i",
            "mouth_u": "u",
            "mouth_o": "o",
            "mouth_e": "e",
        }

        driver_count = 0
        skipped_count = 0
        missing_morphs = []

        for morph_id, direction in vowel_directions.items():
            key_blocks = get_shape_key_matches(
                meshes,
                morph_id,
            )

            if not key_blocks:
                missing_morphs.append(morph_id)

            for key_block in key_blocks:
                created = add_direction_driver(
                    key_block,
                    mouth_control,
                    mouth_x,
                    mouth_z,
                    direction,
                    MOUTH_TARGET_DISTANCE,
                    props.replace_existing_drivers,
                )

                if created:
                    driver_count += 1
                else:
                    skipped_count += 1

        a_key_blocks = get_shape_key_matches(
            meshes,
            "mouth_a",
        )

        if not a_key_blocks:
            missing_morphs.append("mouth_a")

        for key_block in a_key_blocks:
            created = add_a_driver(
                key_block,
                a_control,
                a_slider_left_x,
                A_SLIDER_LENGTH,
                props.replace_existing_drivers,
            )

            if created:
                driver_count += 1
            else:
                skipped_count += 1

        bpy.ops.object.select_all(action="DESELECT")
        panel_root.select_set(True)
        context.view_layer.objects.active = panel_root

        if follow_mode == "CONSTRAINT_BONE":
            follow_text = (
                f"已使用 Child Of 约束跟随控制骨“{used_bone_name}”。"
            )
        elif follow_mode == "CONSTRAINT_OBJECT":
            follow_text = (
                f"已使用 Child Of 约束跟随对象“{follow_object_name}”。"
            )
        else:
            follow_text = "未指定 MMR 跟随目标，面板保持在角色根骨附近。"

        message = (
            f"{follow_text} "
            f"已创建 {driver_count} 个嘴型 Driver。"
        )

        if skipped_count:
            message += f" 跳过 {skipped_count} 个已有 Driver。"

        if missing_morphs:
            message += (
                " 未匹配形态键："
                + "、".join(missing_morphs)
                + "。"
            )

        self.report({"INFO"}, message)

        return {"FINISHED"}

# ============================================================
# 重置与删除控制器
# ============================================================

class MMD_FACE_OT_reset_controller(Operator):
    bl_idname = "mmd_face.reset_controller"
    bl_label = "重置控制方块"
    bl_description = "重置嘴型控制方块"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mouth_control = bpy.data.objects.get(MOUTH_CONTROL_NAME)
        a_control = bpy.data.objects.get(A_CONTROL_NAME)

        if mouth_control is None or a_control is None:
            self.report({"WARNING"}, "没有找到表情控制器。")
            return {"CANCELLED"}

        mouth_control.location = (
            0.055 * CONTROLLER_SCALE,
            0.0,
            -0.035 * CONTROLLER_SCALE,
        )

        a_control.location = (
            0.025 * CONTROLLER_SCALE,
            0.0,
            0.175 * CONTROLLER_SCALE,
        )

        return {"FINISHED"}

class MMD_FACE_OT_delete_controller(Operator):
    bl_idname = "mmd_face.delete_controller"
    bl_label = "删除表情控制器"
    bl_description = "删除面板、控制方块和本插件创建的 Driver"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        delete_controller()

        self.report(
            {"INFO"},
            "已删除 MMD 表情控制器及其 Driver。",
        )

        return {"FINISHED"}

# ============================================================
# Shape Key N 面板
# ============================================================

class MMD_SHAPEKEY_PT_Panel(Panel):
    bl_label = "MMD 形态键"
    bl_idname = "MMD_SHAPEKEY_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD 形态键"

    @classmethod
    def poll(cls, context):
        return has_shape_keys(context.active_object)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        categorized = {
            category: []
            for category in CATEGORY_MAP
        }

        for key_block in obj.data.shape_keys.key_blocks:
            if key_block.name == "Basis":
                continue

            category = get_shape_key_category(key_block.name)
            categorized.setdefault(category, []).append(key_block)

        for category, key_blocks in categorized.items():
            if not key_blocks:
                continue

            box = layout.box()

            box.label(
                text=category,
                icon="SHAPEKEY_DATA",
            )

            for key_block in key_blocks:
                row = box.row(align=True)

                row.prop(
                    key_block,
                    "value",
                    text=get_display_name(key_block.name),
                    slider=True,
                )

                operator = row.operator(
                    "mmd.keyframe_shape_key",
                    text="",
                    icon="KEYFRAME",
                )

                operator.shape_key_name = key_block.name

# ============================================================
# 表情控制器 N 面板
# ============================================================

class MMD_FACE_PT_Panel(Panel):
    bl_label = "MMD 视图表情控制器"
    bl_idname = "MMD_FACE_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD 形态键"

    def draw(self, context):
        layout = self.layout
        props = context.scene.mmd_face_props

        layout.label(
            text="角色设置",
            icon="OUTLINER_OB_ARMATURE",
        )

        layout.prop(
            props,
            "character_armature",
            text="角色 Armature",
        )

        box = layout.box()

        box.label(
            text="MMR 跟随目标",
            icon="CONSTRAINT",
        )

        box.prop(
            props,
            "follow_controller_object",
            text="控制器对象",
        )

        box.prop(
            props,
            "follow_controller_bone",
            text="控制器骨骼",
        )

        layout.prop(
            props,
            "root_bone_name",
            text="备用根骨",
        )

        layout.separator()

        layout.prop(
            props,
            "replace_existing_drivers",
        )

        layout.prop(
            props,
            "rebuild_controller",
        )

        layout.separator()

        layout.operator(
            "mmd_face.build_controller",
            icon="EMPTY_AXIS",
        )

        row = layout.row(align=True)

        row.operator(
            "mmd_face.reset_controller",
            text="重置方块",
            icon="LOOP_BACK",
        )

        row.operator(
            "mmd_face.delete_controller",
            text="删除",
            icon="TRASH",
        )

# ============================================================
# 注册
# ============================================================

classes = (
    MMD_FACE_Properties,
    MMD_OT_KeyframeShapeKey,
    MMD_FACE_OT_build_controller,
    MMD_FACE_OT_reset_controller,
    MMD_FACE_OT_delete_controller,
    MMD_SHAPEKEY_PT_Panel,
    MMD_FACE_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mmd_face_props = PointerProperty(
        type=MMD_FACE_Properties,
    )

def unregister():
    if hasattr(bpy.types.Scene, "mmd_face_props"):
        del bpy.types.Scene.mmd_face_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()