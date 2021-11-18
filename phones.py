from numpy.random import default_rng
from random import choice, randrange

class Phones():
	def __init__(self, definitions, structures, disallowed, max_syllables, required, delimiter):
		self.structures = list(structures)
		self.definitions = definitions
		self.disallowed = self.parseDisallowed(disallowed)
		self.required = self.parseRequired(required)
		self.min_syllables = 1
		self.max_syllables = max_syllables
		self.syllable_selection = False
		self.delimiter = delimiter
		
		self.rng = default_rng()

		print(self.required)

	def parseRequired(self, required):
		rule_dict = {"start" : [], "end" : []}

		for generic_rule in required:
			for rule in self.generatePermutationsList(generic_rule):
				if rule[0] == "?" and rule[-1] == "?":
					raise ValueError(f"Invalid value for rule {generic_rule}")
				elif rule[-1] == "?":
					location = "start"
				elif rule[0] == "?":
					location = "end"
				rule = rule.replace("?", "")
				rule_dict[location].append(rule)

		return rule_dict

	def parseDisallowed(self, disallowed):
		rule_dict = {"start": [], "middle": [], "end": [], "all": []}

		for rule in disallowed:
			for rule in self.generatePermutationsList(rule):
				if rule[0] == "?" and rule[-1] == "?":
					location = "middle"
				elif rule[0] == "?":
					location = "end"
				elif rule[-1] == "?":
					location = "start"
				else:
					location = "all"
				rule = rule.replace("?", "")			
				rule_dict[location].append(rule)

		return rule_dict

	def shuffleSounds(self, which_list):
		if which_list == "all":
			for key in list(self.definitions.keys()):
				self.rng.shuffle(self.definitions[key])
		else:
			self.rng.shuffle(self.definitions[which_list])

	def getHarmonic(self, N):
		harmonic = 0
		for n in range(1, N+1):
			harmonic += (1/n)
		return harmonic

	def getZipfFrequency(self, k, N):
		frequency = (1/k)
		frequency = frequency/self.getHarmonic(N)
		return frequency

	def getZipfDistribution(self, N):
		distribution = []
		for k in range(1, N+1):
			distribution.append(self.getZipfFrequency(k, N))
		return distribution

	def makeSyllable(self, structure, start=False, end=False):
		syllable = ""

		if start and structure[0] in list(self.definitions.keys()) and self.required["start"]:
			intersection = list(set(self.required["start"]).intersection(self.definitions[structure[0]]))
			if intersection:
				replacement = self.rng.choice(intersection, shuffle=False)
				structure = replacement + structure[1:]

		if end and structure[-1] in list(self.definitions.keys()) and self.required["end"]:
			intersection = list(set(self.required["end"]).intersection(self.definitions[structure[-1]]))
			if intersection:
				replacement = self.rng.choice(intersection, shuffle=False)
				structure = structure[:-1] + replacement

		for character in structure:
			if character in list(self.definitions.keys()):
				newChar = self.rng.choice(self.definitions[character], shuffle=False)
			else:
				newChar = character
			syllable += newChar

		return syllable

	def makeWord(self, length): #Structures may be a list or a single structure
		word = ""
		valid = False

		while not valid:
			word = ""
			for x in range(0, length):
				if word != "":
					word += self.delimiter

				start = False
				end = False

				if x == length-1:
					end = True
				if x == 0:
					start = True

				word += self.makeSyllable(self.getRandomStructure(), start=start, end=end)

			valid = self.checkValid(word, end=True)

		return word

	def getRandomStructure(self):
		# Picks a random element if structures is list, or returns it if it's str
		if isinstance(self.structures, list):
			return choice(self.structures)
		else:
			return self.structures

	def getRandomLength(self):
		if self.syllable_selection == False:
			return randrange(self.min_syllables, self.max_syllables)
		else:
			return choice(self.syllable_selection)

	def generatePermutationsList(self, rule):
		permutations = []
		special_chars = False
		for char in rule:
			if char in list(self.definitions.keys()):
				special_chars = True
				for perm in self.definitions[char]:
					permutations.append(rule.replace(char, perm))

		if special_chars:
			return permutations
		else:
			return [rule]

	def checkValid(self, string, end=False):
		string = string.replace(self.delimiter, "")

		for rule in self.disallowed["all"]:
			if rule in string:
				#print(f'{string} violates disallowed rule !{rule}')
				return False

		for rule in self.disallowed["start"]:
			if string.startswith(rule):
				#print(f'{string} violates disallowed start rule !{rule}')
				return False

		for rule in self.disallowed["middle"]:
			index = string.find(rule)
			if index != -1 and not string.startswith(rule) and not string.endswith(rule):
				#print(f'{string} violates disallowed middle !{rule}')
				return False
		
		required_match = False
		if self.required["start"]:
			for rule in self.required["start"]:
				if string.startswith(rule):
					required_match = True
			if not required_match:
				#print(f'{string} violates required start')
				return False

		if end:
			required_match = False

			if self.required["end"]:			
				for rule in self.required["end"]:
					if string.endswith(rule):
						required_match = True
				if not required_match:
					#print(f'{string} violates required end')
					return False

			for rule in self.disallowed["end"]:
				index = string.find(rule)
				if index != -1 and string.endswith(rule):
					#print(f'{string} violates end rule !{rule}')
					return False

		return True

	def generateWordPool(self, word_count):
		pool = []

		while len(pool) < word_count:
			word = self.makeWord(self.getRandomLength())
			if word not in pool:
				pool.append(word)

		return pool

if __name__ == "__main__":
	phones = Phones(["p", "t", "k"], ["i", "a", "o"], ["CVC"], ["?ng?", "?ng"], 5)
	print(phones.checkValid("strong", end=True)) # should be not valid
	print(phones.checkValid("strngo", end=True)) # should be not valid
	print(phones.checkValid("ng"))				 # should be valid
	print(phones.makeWord(2))