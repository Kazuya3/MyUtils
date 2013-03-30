bl_info = {
    'name': 'ActionSelection Sample',
    'author': 'John Doe',
    'version': (2, 0),
    "blender": (2, 62, 0),
    'location': '3D View',
    'description': 'ActionSelection Sample.',
    'category': '3D View'
	}


"""
"""


import bpy

import myutils


class SamplePanel(bpy.types.Panel):
	bl_idname = "object.pt.SamplePanel"
	bl_label = "ActionSelection Sample"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.operator(SampleButton.bl_idname,
						icon = "QUESTION", text = "").mode = "sample"
		g_ActionSelectionComponent.draw(context.scene, self.layout)


class SampleButton(bpy.types.Operator):
	bl_label = "Sample Button"
	bl_idname = "sample.button"
	mode = bpy.props.StringProperty()
	
	
	def sample(self, context):
		self.report({"INFO"}, "SampleButton::sample had been called.")
	
	
	def execute(self, context):
		actionSelection = g_ActionSelectionComponent
		try:
			actionSelectionResult = \
					actionSelection.execute(self, context.scene)
			if actionSelectionResult:
				self.report(actionSelectionResult.type,
							actionSelectionResult.message)
			else:
				command = {
					"sample" : self.sample
					}[self.mode]
				command(context)
		except myutils.ReportFactory as report:
			self.report(report.type, report.message)
		
		return {"FINISHED"}


def register():
	global g_ActionSelectionComponent
	bpy.utils.register_module(__name__)
	g_ActionSelectionComponent = myutils.ActionSelectionComponent(
		SampleButton.bl_idname, "Sample")


def unregister():
	global g_ActionSelectionComponent
	bpy.utils.unregister_module(__name__)
	del g_ActionSelectionComponent


if __name__ == "__main__":
	register()


g_ActionSelectionComponent = None
