bl_info = {
    "name": "MMD Shape Key Panel (CN Display)",
    "author": "Your Name",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "View3D > N Panel > MMD 形态键",
    "description": "精确分类并显示中文名称，支持滑条和小图标K帧",
    "category": "Animation",
}

import bpy

# ------------------------------------------------------------
# 分类集合（匹配日文原名）
# ------------------------------------------------------------
EYE_KEYS = {
    "まばたき", "笑い", "ウィンク", "ウィンク右", "ウィンク２", "ウィンク２右",
    "なごみ", "なごみ左", "なごみ右", "びっくり", "じと目", "悲しむ", "怒り目",
    "ジト目", "眼角上", "眼角下", "下眼上", "星目", "じと目2", "はちゅ目"
}

MOUTH_KEYS = {
    "あ", "い", "う", "え", "お", "にやり", "ワ", "ん", "い１", "い２",
    "あ２", "お２", "にやり２", "にやり３", "ω", "てへぺ", "ぺろっ",
    "口角上げ", "口横広げ", "口横狭め", "舌広げ", "もぐもぐ口"
}

BROW_KEYS = {
    "真面目", "困る", "にこり", "怒り", "恥ずかしい", "上", "下", "前",
    "困る左", "困る右", "にこり左", "にこり右", "怒り左", "怒り右",
    "恥ずかしい左", "恥ずかしい右", "上左", "上右", "下左", "下右",
    "前左", "前右"
}

OTHER_KEYS = {
    "噛む", "もぐもぐ"
}

CATEGORY_MAP = {
    "眼睛": EYE_KEYS,
    "嘴": MOUTH_KEYS,
    "眉毛": BROW_KEYS,
    "其他": OTHER_KEYS,
}

# ------------------------------------------------------------
# 日文 → 中文显示名映射（依据表格）
# ------------------------------------------------------------
DISPLAY_NAME_MAP = {
    # 眼睛
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
    # 嘴
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
    "ω": "抿嘴成w",
    "てへぺ": "向上吐舌头",
    "ぺろっ": "中间吐舌头",
    "口角上げ": "嘴角上扬",
    "口横広げ": "嘴角下扬",
    "口横狭め": "嘴变小",
    "舌広げ": "舌头变宽",
    "もぐもぐ口": "生气（可爱版）",
    # 眉毛
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
    # 其他
    "噛む": "下巴变长",
    "もぐもぐ": "鼓腮帮子",
}

def get_shape_key_category(name):
    for category, keys_set in CATEGORY_MAP.items():
        if name in keys_set:
            return category
    return "其他"

def get_display_name(name):
    return DISPLAY_NAME_MAP.get(name, name)


class MMD_SHAPEKEY_PT_Panel(bpy.types.Panel):
    bl_label = "MMD 形态键"
    bl_idname = "MMD_SHAPEKEY_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMD 形态键"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if not obj or not obj.data.shape_keys:
            layout.label(text="请选择一个带有形态键的网格物体")
            return

        shape_keys = obj.data.shape_keys.key_blocks
        categorized = {cat: [] for cat in CATEGORY_MAP.keys()}
        for key in shape_keys:
            if key.name == "Basis":
                continue
            cat = get_shape_key_category(key.name)
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(key)

        for category, keys in categorized.items():
            if not keys:
                continue
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.label(text=category, icon='SHAPEKEY_DATA')
            for key in keys:
                row = col.row(align=True)
                display_name = get_display_name(key.name)
                row.prop(key, "value", text=display_name, slider=True)
                op = row.operator("mmd.keyframe_shape_key", text="", icon='KEYFRAME')
                op.shape_key_name = key.name


class MMD_OT_KeyframeShapeKey(bpy.types.Operator):
    bl_idname = "mmd.keyframe_shape_key"
    bl_label = "K关键帧"
    bl_description = "为当前形态键的值插入关键帧"
    
    shape_key_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data.shape_keys:
            self.report({'WARNING'}, "没有找到形态键")
            return {'CANCELLED'}
        
        key = obj.data.shape_keys.key_blocks.get(self.shape_key_name)
        if not key:
            self.report({'WARNING'}, f"未找到形态键: {self.shape_key_name}")
            return {'CANCELLED'}
        
        key.keyframe_insert(data_path="value")
        self.report({'INFO'}, f"为 '{self.shape_key_name}' 插入关键帧")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MMD_SHAPEKEY_PT_Panel)
    bpy.utils.register_class(MMD_OT_KeyframeShapeKey)

def unregister():
    bpy.utils.unregister_class(MMD_SHAPEKEY_PT_Panel)
    bpy.utils.unregister_class(MMD_OT_KeyframeShapeKey)

if __name__ == "__main__":
    register()