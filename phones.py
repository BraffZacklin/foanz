from numpy.random import default_rng
from random import choice, randrange

class Phones():
	def __init__(self, consonants, vowels, structures, disallowed, max_syllables):
		self.consonants = consonants
		self.vowels = vowels
		self.structures = structures
		self.disallowed = disallowed
		self.min_syllables = 1
		self.max_syllables = max_syllables
		self.syllable_selection = False
		
		self.rng = default_rng()
		self.zipf_consonants = self.getZipfDistribution(len(consonants))
		self.zipf_vowels = self.getZipfDistribution(len(vowels))

	def shuffleConsonants(self):
		self.rng.shuffle(self.consonants)

	def shuffleVowels(self):
		self.rng.shuffle(self.vowels)

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

	def makeSyllable(self, structure):
		syllable = ""
		for character in structure:
			valid = False
			while not valid:
				if character == "C":
					newChar = self.rng.choice(self.consonants, p=self.zipf_consonants, shuffle=False)
				elif character == "V":
					newChar = self.rng.choice(self.vowels, p=self.zipf_vowels, shuffle=False)
				else:
					newChar = character

				valid = self.checkValid(syllable + newChar)
				if valid:
					syllable += newChar

		return syllable

	def makeWord(self, length): #Structures may be a list or a single structure
		word = ""
		for x in range(0, length):
			if word != "":
				word += '.'
			valid = False
			while not valid:
				newSyllable = self.makeSyllable(self.getRandomStructure())
				
				valid = self.checkValid(word + newSyllable)
				if valid:
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

	def checkValid(self, string):
		for combo in self.disallowed:
			if combo in string:
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
	phones = Phones(["p", "t", "k"], ["i", "a", "o"], ["CVC"], [], 5)
	print(phones.makeWord(2))