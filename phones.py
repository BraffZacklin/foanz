from numpy.random import default_rng
from random import choice, randrange

class Phones():
	def __init__(self, definitions, structures, disallowed, max_syllables, required, delimiter):
		self.definitions = definitions
		self.structures = list(structures)
		self.disallowed = self.parseDisallowed(disallowed)
		self.min_syllables = 1
		self.max_syllables = max_syllables
		self.syllable_selection = False
		self.delimiter = delimiter
		self.definitions = {"C": [], "V": []}
		
		self.rng = default_rng()

	def parseDisallowed(self, disallowed):
		rule_dict = {"start": [], "middle": [], "end": [], "all": []}

		for rule in disallowed:
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
		for character in structure:
			if character in self.definitions.keys():
				newChar = self.rng.choice(self.definitions[character], p=self.getZipfDistribution(len(self.definitions[character])), shuffle=False)
			else:
				newChar = character
			syllable += newChar

		return syllable

	def makeWord(self, length): #Structures may be a list or a single structure
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

			valid = False
			newSyllable = ""
			while not valid:
				newSyllable = self.makeSyllable(self.getRandomStructure(), end=end, start=start)
				valid = self.checkValid(word + newSyllable, end=end)
			word += newSyllable

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

	def checkValid(self, string, end=False):
		string = string.replace(self.delimiter, "")
		for rule in self.disallowed["all"]:
			if rule in string:
				return False
		for rule in self.disallowed["start"]:
			rule_length = len(rule)
			if string[0:rule_length] == rule:
				return False
		for rule in self.disallowed["middle"]:
			index = string.find(rule)
			if index != -1:
				if index == 0:
					continue
				if end and index == len(string) - len(rule):
					continue
				return False
		if end:
			for rule in self.disallowed["end"]:
				index = string.find(rule)
				if index != -1:
					if index == len(string) - len(rule):
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