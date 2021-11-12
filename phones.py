from numpy.random import default_rng
from numpy.random import choice

rng = default_rng()

# Phonemic Inventory
consonants = ["p", "t", "k", "n", "r", "s", "x", "y", "w", "f", ""]
vowels = ["a", "e", "i", "u"]
# These I don't want shuffled
medials = ["", "y", "w"]
codas = ["", "n"]

# Rules
accept_medials = ["p", "t", "k", "n", "r"]
# Valid lengths of syllables
valid_lengths = [1, 2]

# Shuffle list for interesting words
rng.shuffle(consonants)
rng.shuffle(vowels)

# Print them in case we like it
print(f'Consonants List: {consonants}')
print(f'Vowels List: {vowels}')

'''
Zipfs Law:
	Frequency of element rank N =
		(1/k)/((1/n) for n in range(1, N+1))

Where k is the rank
Where N is the number of items
k and n can be raised to the power of s (any positive int) to change the distribution
'''

def getHarmonic(N):
	harmonic = 0
	for n in range(1, N+1):
		harmonic += (1/n)
	return harmonic

def getZipfFrequency(k, N):
	frequency = (1/k)
	frequency = frequency/getHarmonic(N)
	return frequency

def getZipfDistribution(N):
	distribution = []
	for k in range(1, N+1):
		distribution.append(getZipfFrequency(k, N))
	return distribution

# Get Zipf distribution for all elements
zipf_consonants = getZipfDistribution(len(consonants))
zipf_vowels = getZipfDistribution(len(vowels))
zipf_medials = getZipfDistribution(len(medials))
zipf_codas = getZipfDistribution(len(codas))
zipf_length = getZipfDistribution(len(valid_lengths))

'''
for consonant in consonants:
	for vowel in vowels:
		if consonant in ["p", "t", "k"]:
			for phone in clusterable:
				print(f'{consonant}{phone}{vowel}')
				print(f'{consonant}{phone}{vowel}n')
		elif consonant in ["n", "r"]:
			print(f'{consonant}y{vowel}')
			print(f'{consonant}y{vowel}n')
		print(f'{consonant}{vowel}')
		print(f'{consonant}{vowel}n')
'''
def getConsonant():
	return rng.choice(consonants, p=zipf_consonants, shuffle=False)

def getVowel():
	return rng.choice(vowels, p=zipf_vowels, shuffle=False)

def getMedial():
	return rng.choice(medials, p=zipf_medials, shuffle=False)

def getCoda():
	return rng.choice(codas, p=zipf_codas, shuffle=False)

def makeSyllable():
	onset = getConsonant()
	if onset in accept_medials:
		medial = getMedial()

		# Coding for an exception
		if medial == "w" and onset in ["n", "r"]:
			medial = ""

		onset = onset + medial

	nucleus = getVowel()

	coda = getCoda()

	return onset + nucleus + coda

def makeWord(length):
	word = ""
	for x in range(0, length):
		word += makeSyllable()
	return word

def getRandomLength():
	return rng.choice(valid_lengths, p=zipf_length, shuffle=False)	

def generateWordPool(word_count):
	pool = []

	while len(pool) < word_count:
		word = makeWord(getRandomLength())
		if word not in pool:
			pool.append(word)

	return pool

words = generateWordPool(50)
for position, word in enumerate(words, start=1):
	print(f'{position}. {word}')