from random import choice

class Reader():
	def __init__(self, textfile, outfile="./outfile.txt"):
		self.outfile = outfile
		self.textfile_list = []
		self.textfile = textfile
		self.consonants = []
		self.vowels = []
		self.structures = []
		self.disallowed = []
		self.required = []
		self.reader_dictionary = {}
		self.max_syllables = False
		self.wordbank = []
		self.readDictionaryFile()

	def returnDirectives(self):
		return self.consonants, self.vowels, self.structures, self.disallowed, self.max_syllables, self.required

	def removeComments(self, string):
		if "//" in string:
			return string[:string.index("//")]
		return string

	def findDirectiveName(self, line):
		return line.split()[0]

	def processListDirective(self, line):
		line = line.replace(self.findDirectiveName(line), "")
		#return [(self.removeComments(n).strip()) for n in line.split(",")]
		return [(n.strip()) for n in line.split(",")]

	def readDictionaryFile(self):
		try:
			with open(self.textfile, "r") as file:
				self.textfile_list = file.readlines()
				for index, line in enumerate([line.strip() for line in self.textfile_list if line.strip() != ""], start=1):
					if line[0:2] == "//":
						continue
					line = self.removeComments(line)

					if line[0] == "#":
						try:
							if "CONSONANTS" in line:
								self.consonants = self.processListDirective(line)
							elif "VOWELS" in line:
								self.vowels = self.processListDirective(line)
							elif "STRUCTURE" in line:
								self.structures = self.expandStructure(line.replace(self.findDirectiveName(line), ""))
							elif "DISALLOWED" in line:
								self.disallowed = self.processListDirective(line)
							elif "MAX_SYLLABLES" in line:
								self.max_syllables = line.replace(self.findDirectiveName(line), "")
								self.max_syllables.strip()
								self.max_syllables = int(self.max_syllables)+1
							elif "REQUIRED" in line:
								self.required = self.processListDirective(line)
							elif "DUPLICATES" in line:
								self.duplicates = lower(line.replace(self.findDirectiveName(line), "").strip())
								if self.duplicates not in ["allow", "deny", "warn"]:
									raise ValueError
							else:
								raise ValueError
						except ValueError as e:
							print(e)
							print(f'foanz: mangled directive on line {index}')
							print(f'\t"{line}"')
							quit()
					elif ":" in line:
						if line[0].isdigit() or line[0] == "?":
							line = [line.strip() for line in line.split(":")]
							if "(" in line and ")" in line:
								continue
							elif line[0] == "?" and self.max_syllables == False:
								print(f'foanz: MAX_SYLLABLES not defined but wildcard is used on line {index}')
								print(f'\t{line}')
								quit()

							if line[0] in self.reader_dictionary:
								if line[1] not in self.reader_dictionary[line[0]]:
									self.reader_dictionary[line[0]].append(line[1])
							else:
								self.reader_dictionary[line[0]] = [line[1]]

						elif line[0:5] == "bank:":
							line = line.replace("bank:", "")
							line = line.strip()
							if line not in self.wordbank:
								self.wordbank.append(line)
			
			self.removeBankedFromTextfileList()
							
			return self.reader_dictionary
		except FileNotFoundError as e:
			print(e)
			print("foanz: default or user input file not found,")
			print("\tone will need to be manually loaded with 'reload [file]'")
			return False

	def removeBankedFromTextfileList(self):
		bank_lines = []
		for line in self.textfile_list:
			if "bank: " in line:
				bank_lines.append(line)
		for line in bank_lines:
			self.textfile_list.remove(line)

	def defineWord(self, word, definition):
		if "." in word:
			word = word.replace(".", "")
		for index, line in enumerate(self.textfile_list):
			if definition in line:
				line_list = line.split(":")
				line_list[0] = f'{word} ({line_list[0]})'
				line_list = ":".join(line_list)
				self.textfile_list[index] = line_list

	def guessSyllables(self, word):
		if word[0] in self.vowels:
			vowel_cluster = True
			syllables = 1
		else:
			vowel_cluster = False
			syllables = 0

		for char in word:
			if char in self.vowels and vowel_cluster == False:
				syllables += 1
				vowel_cluster = True
			elif char not in self.vowels and vowel_cluster == True:
				vowel_cluster = False

		return syllables

	def checkDuplicates(self, word):
		if self.duplicates:
			if self.duplicates == "allow":
				return word
			else:
				for line in self.textfile_list:
					line_list = [segment.strip() for segment in line.split(":")]
					if line_list[0] == word:
						if self.duplicates == "warn":
							print(f'foanz: duplicate word {word}')
						else:
							return False

	def addWord(self, word):
		check = self.checkDuplicates(word)
		if check == False:
			return word

		syllables = 1
		definition = ""
		key = ""

		syllables = 0
		if "." not in word:
			syllables = self.guessSyllables(word)
		else:			
			for char in word:
				if char == ".":
					syllables = syllables+1
			syllables = str(syllables)
		
		if syllables in self.reader_dictionary:
			key = syllables
			definition = choice(self.reader_dictionary[syllables])
		elif "?" in self.reader_dictionary:
			key = "?"
			definition = choice(self.reader_dictionary["?"])
		else:
			for key in list(self.reader_dictionary.keys()):
				if "-" in key:
					syllables = int(syllables)
					syllable_range = [int(value.strip()) for value in key.split("-")]
					if syllables in list(range(syllable_range[0], syllable_range[1]+1)):
						definition = choice(self.reader_dictionary[key])

		if definition and key:
			self.defineWord(word, definition)
			self.reader_dictionary[key].remove(definition)
			if not self.reader_dictionary[key]:
				del self.reader_dictionary[key]
		else:
			return word

	def save(self, wordbank):
		with open(self.outfile, "w+") as file:
			for line in self.textfile_list:
				file.write(line)

			if self.textfile_list[-1].strip() != "":
				file.write("\n\n")

			for line in self.wordbank:
				file.write(f'bank: {line}\n')

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
				raise Exception(f"foanz: malformed structures directive entry {structure}")

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

if __name__ == "__main__":
	reader = Reader("./example.txt")
	print(reader.guessSyllables("a"))
	print(reader.guessSyllables("hi"))
	print(reader.guessSyllables("ahhh"))
	print(reader.guessSyllables("aha"))
	print(reader.guessSyllables("othelo"))