class Structures():
	def __init__(self):
		pass

	def expandStructure(self, structure):
		valid_structures = [""]
		structure_list = self.structureToList(structure)

		for group in structure_list:
			optional = False
			if "(" in group and ")" in group:
				optional = True
				group = group.replace("(", "")
				group = group.replace(")", "")
			elif "(" in group or ")" in group:
				assert ValueError, "foanz: malfomred structures directive entry {structure}"

			if "/" in group:
				options_list = group.split("/")
				new_structures = []
				for option in options_list:
					new_structures += [entry+option for entry in valid_structures] + valid_structures
				valid_structures = new_structures
			else:
				if optional:
					new_structures = [entry+group for entry in valid_structures] + valid_structures
				else:
					new_structures = [entry+group for entry in valid_structures]
				valid_structures = new_structures
		
		valid_structures = set(valid_structures)
		return valid_structures 

	def structureToList(self, structure):
		structure_list = []

		group_hit = False
		group_start = 0
		for index, char in enumerate(structure):
			if char == "(":
				group_hit = True
				group_start = index
			elif char == ")":
				group_hit = False
				structure_list.append(structure[group_start:index+1])
			elif char.isspace():
				continue
			elif group_hit == False:
				structure_list.append(char)
		return structure_list


	def returnNextCharacters(self, string):
		pass

if __name__ == "__main__":
	structures = Structures()
	print(structures.expandStructure("(C)V(C/n/j)"))
	print(structures.structureToList("(C)V(C/n)"))