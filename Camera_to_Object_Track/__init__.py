import bpy

bl_info = {
	"name": "Camera to Object Track",
	"description": "Automatically animates object movements based on reference objects.",
	"author": "DShot92",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"category": "Animation",
}

class ObjectAnimationOperator(bpy.types.Operator):
	"""Operator to animate object movements based on reference objects"""
	bl_idname = "camera_to_object_track.duplicate_and_convert"
	bl_label = "Duplicate and convert"

	def execute(self, context):
		scene = context.scene
		frame_start = scene.frame_start
		frame_end = scene.frame_end

		bpy.context.scene.frame_set(bpy.context.scene.frame_start)

		# Get the selected objects and their copies
		a = context.scene.object_picker_1  # Represents the camera
		b = context.scene.object_picker_2  # Represents the reference points

		# Duplicate the selected objects
		if a is not None and b is not None:
			# Duplicate Object 1 (Camera)
			c = a.copy()
			c.data = a.data.copy()
			c.name = "Static_" + a.name
			context.collection.objects.link(c)
			c.animation_data_clear()

			# Duplicate Object 2 (Reference points)
			d = b.copy()
			d.data = b.data.copy()
			d.name = "Static_" + b.name
			context.collection.objects.link(d)

		# Store the location and rotation of the duplicated objects
		crfLoc = c.location
		crfRot = c.rotation_euler
		drfLoc = d.location
		drfRot = d.rotation_euler

		# Loop through each frame and perform the animation
		for frame in range(frame_start, frame_end + 1):
			bpy.ops.object.select_all(action='DESELECT')
			b.select_set(True)

			# Set the location and rotation of the reference points
			b.location = drfLoc
			b.rotation_euler = drfRot

			bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')

			bpy.ops.object.select_all(action='DESELECT')
			a.select_set(True)
			b.select_set(True)
			bpy.context.view_layer.objects.active = a

			# Set the camera as the parent of the reference points
			bpy.ops.object.parent_set()

			# Set the location and rotation of the camera
			a.location = crfLoc
			a.rotation_euler = crfRot

			bpy.ops.object.select_all(action='DESELECT')
			b.select_set(True)

			bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')

			# Clear the parent-child relationship
			bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

			bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')

			bpy.ops.object.select_all(action='DESELECT')
			bpy.context.scene.frame_set(frame)
			
			### END FOR LOOP

		# Set Original Object Invisible in viewport
		a.hide_render = True
		a.hide_viewport = True
		a.hide_set(True)
		
		b.hide_render = True
		b.hide_viewport = True
		b.hide_set(True)
		
		return {'FINISHED'}

class ObjectAnimationPanel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_camera_to_object_track"
	bl_label = "Cam 2 O-Track"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Cam 2 O-Track'

	def draw(self, context):
		layout = self.layout

		# Object Picker 1: Camera
		layout.prop_search(context.scene, "object_picker_1", bpy.data, "objects", text="Camera")

		# Object Picker 2: Reference Points
		layout.prop_search(context.scene, "object_picker_2", bpy.data, "objects", text="Points")

		layout.separator()

		# Duplicate Button
		layout.operator("camera_to_object_track.duplicate_and_convert")


classes = [
	ObjectAnimationOperator,
	ObjectAnimationPanel,
]

def register():
	# Register the add-on classes
	for cls in classes:
		bpy.utils.register_class(cls)

	# Create custom properties for storing selected objects
	bpy.types.Scene.object_picker_1 = bpy.props.PointerProperty(
		type=bpy.types.Object,
		name="Object Picker 1"
	)

	bpy.types.Scene.object_picker_2 = bpy.props.PointerProperty(
		type=bpy.types.Object,
		name="Object Picker 2"
	)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.object_picker_1
	del bpy.types.Scene.object_picker_2