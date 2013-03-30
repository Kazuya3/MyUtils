
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
#									IMPORTS
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////

import mathutils

import bpy


# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
#								GLOBAL FUNCTIONS
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
#									CLASSES
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////

# -----------------------------------------------------------------------------
# **
# * This class provides Action Selection Function.
# * Use with bpy.types's Panel and Operator.
# * Custom Properties need this will be registered in "Scene".
class ActionSelectionComponent():
	
	
	# **
	# * コンストラクタ
	# * @param operatorId	type : string
	# *		UILayout の operator 関数の第一引数に指定する識別子。
	# *		Operator のサブクラスの bl_idname などを指定する。
	# * @param variableId	type : string
	# *		カスタムプロパティが他の利用者と競合しないようにするための識別子。
	# *		アドオン名など、独自性の高いものを指定する。
	# * @param modeIndices	type : tuple of string
	# *		Operator のサブクラスモードに指定する文字列のタプル。
	# *		利用側で競合しないようなら渡す必要はない。
	def __init__(self, operatorId, variableId, modeIndices =
				 ("addAction", "addAllActions", "removeAction", "emptyActions")):
		self.operatorId = operatorId
		self.modeIndices = modeIndices
		self.variableName_isAvailable = variableId + "_ActionSelection_isAvailable"
		self.variableName_targets = variableId + "_ActionSelection_targets"
		self.variableName_targetIndex = variableId + "_ActionSelection_targetIndex"
		attachedTarget = "bpy.types.Scene."
		self.variableFullName_isAvailable = \
				attachedTarget + self.variableName_isAvailable
		self.variableFullName_targets = \
				attachedTarget + self.variableName_targets
		self.variableFullName_targetIndex = \
				attachedTarget + self.variableName_targetIndex
		exec(self.variableFullName_isAvailable + \
			 " = bpy.props.BoolProperty(name = 'Select Action',"\
			 " description = 'Replace Selected Action Only if this is true.',"\
			 " default = False)")
		exec(self.variableFullName_targets + \
							" = bpy.props.CollectionProperty(type = "\
							"StringPropertyGroup)")
		exec(self.variableFullName_targetIndex + \
							" = bpy.props.IntProperty(min = -1, default = -1)")
	
	
	def __del__(self):
		exec("del " + self.variableFullName_isAvailable)
		exec("del " + self.variableFullName_targets)
		exec("del " + self.variableFullName_targetIndex)
	
	
	# **
	# * Accessor for custom property
	def isAvailable(self, data):
		return eval("data." + self.variableName_isAvailable)
	
	
	# **
	# * Accessor for custom property
	def targets(self, data):
		return eval("data." + self.variableName_targets)
	
	
	# **
	# * Accessor for custom property
	def targetIndex(self, data):
		return eval("data." + self.variableName_targetIndex)
	
	
	# **
	# * Examine whether the name already exist.
	# * @param name		Name of action
	# * @return			Return True if the name exist in targets.
	def isActionExistInTargets(self, data, name):
		isFound = False
		for item in self.targets(data):
			isFound = name == item.name
			if isFound:
				break
		
		return isFound
	
	
	# **
	# * アクションエディタで選択中のアクションをリストに追加
	def addAction(self, data):
		action = MyUtils.getSelectedAction()
		isAdded = False
		if not self.isActionExistInTargets(data, action.name):
			added = self.targets(data).add()
			added.name = action.name
			isAdded = True
		
		if not isAdded:
			raise ReportFactory.getWarningReport(
				"Selected Action already exists.")
		
		return ReportFactory.getInfoReport("Selected Action has added.")
	
	
	# **
	# * 全てのアクションをリストに追加する
	def addAllActions(self, data):
		isActionExist = 0 < len(bpy.data.actions)
		isAdded = False
		for action in bpy.data.actions:
			if not self.isActionExistInTargets(data, action.name):
				added = self.targets(data).add()
				added.name = action.name
				isAdded = True
		
		if not isActionExist:
			raise ReportFactory.getWarningReport("No Action.")
		if not isAdded:
			raise ReportFactory.getWarningReport(
				"All Actions already exists.")
		
		return ReportFactory.getInfoReport("Actions has been addes.")
	
	
	# **
	# * リストで選択中のアクションを削除
	def removeAction(self, data):
		index = self.targetIndex(data)
		targets = self.targets(data)
		if index < 0 or len(targets) <= index:
			raise ReportFactory.getWarningReport("A Action WASN'T selected.")
		
		targets.remove(index)
		if len(targets) <= index:
			exec("data." + self.variableName_targetIndex + " = len(targets) - 1")
		
		return ReportFactory.getInfoReport("Selected Action has removed.")
	
	
	# **
	# * リストを空にする
	def emptyActions(self, data):
		targets = self.targets(data)
		isTargetRemain = 0 < len(targets)
		if not isTargetRemain:
			raise ReportFactory.getWarningReport("Action not exists.")
		
		while isTargetRemain:
			targets.remove(0)
			isTargetRemain = 0 < len(targets)
		
		return ReportFactory.getInfoReport("Actions has been emptied")
	
	
	# **
	# * Panel の描画用関数
	def draw(self, data, layout):
		operatorId = self.operatorId
		layout.prop(data, self.variableName_isAvailable)
		modeIndices = self.modeIndices
		if self.isAvailable(data):
			row = layout.row()
			row.operator(operatorId, icon = "ZOOMIN", text = "").mode = \
					modeIndices[0]
			row.operator(operatorId, icon = "ZOOMOUT", text = "").mode = \
					modeIndices[1]
			row.operator(operatorId, icon = "MOD_ARRAY", text = "").mode = \
					modeIndices[2]
			row.operator(operatorId, icon = "CANCEL", text = "").mode = \
					modeIndices[3]
			row = layout.row()
			row.template_list(
				data, self.variableName_targets,
				data, self.variableName_targetIndex)
	
	
	# **
	# * Operator の実行用関数
	# * @operator	呼び出し元の Operator
	def execute(self, operator, data):
		result = None
		modeIndices = self.modeIndices
		commands = {
			modeIndices[0] : self.addAction,
			modeIndices[1] : self.removeAction,
			modeIndices[2] : self.addAllActions,
			modeIndices[3] : self.emptyActions}
		if operator.mode in commands:
			result = commands[operator.mode](data)
		
		return result


# -----------------------------------------------------------------------------
# **
# * Class for exception.
class ReportFactory(UserWarning):
	def __init__(self, type, message):
		self.type = type
		self.message = message
	
	@staticmethod
	def getInfoReport(message):
		return ReportFactory({"INFO"}, message)
	
	@staticmethod
	def getWarningReport(message):
		return ReportFactory({"WARNING"}, message)


# -----------------------------------------------------------------------------
# **
# * コレクション用クラス
class StringPropertyGroup(bpy.types.PropertyGroup):
	name = bpy.props.StringProperty()


# -----------------------------------------------------------------------------
# **
# * General Utility Class.
class MyUtils():
	# **
	# * シーンからアーマチュアを取得
	@staticmethod
	def getArmature():
		result = None
		for object in bpy.context.scene.objects:
			if object.type == "ARMATURE":
				if object.select:
					result = object
					break
		
		if not result:
			raise ReportFactory.getWarningReport(
				"Selected armature couldn't found!")
		
		return result
	
	
	# **
	# * 選択中のポーズボーンを取得
	@staticmethod
	def getSelectedPoseBone():
		return bpy.context.selected_pose_bones
	
	
	# **
	# * 選択中のアクションを取得
	@staticmethod
	def getSelectedAction():
		armature = MyUtils.getArmature()
		return armature.animation_data.action


# -----------------------------------------------------------------------------
# **
# * Utility for PoseBone.
# * Bone in this indicates PoseBone.
class PoseBoneUtils():
	
	# **
	# * location にベクターを加算代入する
	# * 詳細は howm のメモに記述してある。
	@staticmethod
	def addAssignVectorToLocation(bone, vector):
		identity = mathutils.Quaternion()
		identity.identity()
		vector = vector.copy()
		# ボーンの逆行列で移動させたいベクトルを回転させる
		matrix = bone.matrix.copy()
		matrix.invert()
		vector.rotate(matrix)
		# ボーンに回転がかかっている場合は、
		# その回転の逆行列でベクトルをさらに回転させる
		quaternion = bone.rotation_quaternion.copy()
		if not identity == quaternion:
			quaternion *= -1
			matrix = mathutils.Matrix().to_3x3()
			matrix.rotate(quaternion)
			vector.rotate(matrix)
		
		location = bone.location
		location.x += vector.x
		location.y += vector.y
		location.z += vector.z
	
	
	# **
	# * location にベクターを代入する
	@staticmethod
	def assignVectorToLocation(bone, vector):
		bone.location = (0, 0, 0)
		PoseBoneUtils.addAssignVectorToLocation(bone, vector)
	
	
	# **
	# * location ワールド空間に変換したものを取得する
	@staticmethod
	def getLocationAsWorld(bone):
		location = mathutils.Vector(bone.location)
		location.rotate(bone.matrix)
		identityQuaternion = mathutils.Quaternion()
		identityQuaternion.identity()
		quaternion = bone.rotation_quaternion.copy()
		if quaternion != identityQuaternion:
			quaternion.invert()
			matrix3 = mathutils.Matrix().to_3x3()
			matrix3.rotate(quaternion)
			location.rotate(matrix3)
		
		return location


# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
#								REGISTRATIONS
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////

bpy.utils.register_class(StringPropertyGroup)
