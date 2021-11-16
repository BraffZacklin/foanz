from random import choice
from structures import Structures

'''
def expandStructures(string):
	if if "(" not in string and if ")" not in string:
		return string

	expanded_structures = []
	more_structures = True
	while more_structures:
		if "(" in string and if ")" in string:

		elif "(" in string or if ")" in string:
			raise ValueError, "missing opening or closing bracket in structures directive"
		else:
			more_structures = False
	return expanded_structures
'''

class Reader():
	def __init__(self, textfile, outfile="./outfile.txt"):
		self.outfile = outfile
		self.textfile_list = []
		self.textfile = textfile
		self.consonants = []
		self.vowels = []
		self.structures = []
		self.disallowed = []
		self.reader_dictionary = {}
		self.max_syllables = False
		self.wordbank = []
		self.readDictionaryFile()

	def returnDirectives(self):
		return self.consonants, self.vowels, self.structures, self.disallowed, self.max_syllables

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
								self.structures = Structures().expandStructure(line.replace(self.findDirectiveName(line), ""))
							elif "DISALLOWED" in line:
								self.disallowed = self.processListDirective(line)
							elif "MAX_SYLLABLES" in line:
								self.max_syllables = line.replace(self.findDirectiveName(line), "")
								self.max_syllables.strip()
								self.max_syllables = int(self.max_syllables)
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

	def addWord(self, word):
		syllables = 1
		definition = ""
		key = ""

		for char in word:
			if char == ".":
				syllables = syllables+1
		syllables = str(syllables)
		
		if syllables in self.reader_dictionary:
			key = syllables
			definition = choice(self.reader_dictionary[syllables])
			#self.defineWord(word, definition)
			#self.reader_dictionary[syllables].remove(definition)
			#if not self.reader_dictionary[syllables]:
			#	del self.reader_dictionary[syllables]
			#match = True
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

if __name__ == "__main__":
	reader = Reader("./example.txt")
	reader.readDictionaryFile()
	print(reader.reader_dictionary)
	reader.defineWord("hi", "This word will be one syllable")
	reader.save()