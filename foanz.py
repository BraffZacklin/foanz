from reader import Reader
from phones import Phones

'''
	for key in list(dictionary.keys()):
		if "-" in key:
			syllable_range = key.split("-")
			phones.getRandomLength(start=)
'''

#phones.makeWord()
#phones.getRandomLength()

global reader
global phones
global dictionary
global wordbank
global current_set
global next_set

def help():
	print("Commands:")
	print("\thelp")
	print("\t\tShows this whole spiel")
	print()
	print("\tnew [x]")
	print("\t\tby default, will provide 10 randomly generated words with a shuffled phoneme distribution")
	print("\t\tif provided a given number x, it will generate x words instead")
	print()
	print("\tmore [x]")
	print("\t\tby default, will provide 10 randomly generated words with the same phoneme distribution")
	print("\t\tas in your original dictionary file, or the last generated batch of words")
	print("\t\tif provided a given number x, it will generate x words instead")
	print()
	print("\tshuffle [consonants/vowels]")
	print("\t\twill shuffle both consonants and vowels, unless only one is specified")
	print()
	print("\tsyllables [x[.y.z]/x-y]")
	print("\t\twill restrict generated words to a single length, or given range or dotted list of syllables")
	print("\t\tnull-argument will reset it back to using your defined max_syllables directive")
	print()
	print("\tapply [filename]")
	print("\t\twill apply your existing updates and write it to 'filename'")
	print("\t\tif you leave filename blank, it will use your last-used filename")
	print("\t\tor it will default to default.txt")
	print()
	print("\texit")
	print("\t\twill exit without updating words")
	print()
	print("When given a list of words, entering their indexes in a comma-separated list")
	print("will auto-fill blank entries in your dictionary file as directed")
	print("Alternatively, new words can be added by typing your own in, but syllable boundaries")
	print("Will need to be indicated with full stops and single quotes (') used")
	print("TIP: Multiple commands can be issued with a comma-separated list and they will be processed one-by-one")
	print()

def getInput(message):
	while True:
		user_input = input(message).strip()
		if user_input != "":
			return user_input

def processCommand(command):
	new = False
	more = False
	shuffle_consonants = False
	shuffle_vowels = False
	apply_words = False
	exit = False
	syllables = False
	indexes = []
	new_words = []

	command_list = [n.strip() for n in command.split(",") if n.strip() != ""]
	for command in command_list:
		if "new" in command:
			if command == "new":
				new = 10
			else:
				new = command.split()[1]
		elif "more" in command:
			if command == "more":
				more = 10
			else:
				more = command.split()[1]
		elif "shuffle" in command:
			if command == "shuffle":
				shuffle_vowels = True
				shuffle_consonants = True
			elif "vowels" in command:
				shuffle_vowels = True
			elif "consonants" in command:
				shuffle_consonants = True
		elif "apply" in command:
			if command == "apply":
				apply_words = True
			else:
				command_list = command.split()
				reader.outfile = command_list[1]
		elif command == "exit":
			exit = True
		elif "'" in command:
			new_words.append(command.replace("'", ""))
		elif command.isdigit():
			indexes.append(int(command))
		elif "syllables" in command:
			if command == "syllables":
				syllables = "Reset"
			else:
				command_list = command.split()
				try:
					if "." in command_list[1]:
						syllables = [int(number.strip()) for number in command_list[1].split(".")]
					elif "-" in command_list[1]:
						syllables_list = syllables.strip("-")
						syllables = list(range(syllables_list[0], syllables_list[1]+1))
					else:
						syllables = int(command_list[1].strip())
				except ValueError:
					print("Warning: non-number supplied where number was expected")
		elif "help" in command:
			help()

	return {"new": new, "more": more, "shuffle_consonants": shuffle_consonants, "shuffle_vowels": shuffle_vowels,
			"apply_words": apply_words, "exit": exit, "indexes": indexes, "new_words": new_words, "syllables": syllables}

def exit():
	reader.save()
	quit()

reader = Reader("./example.txt")
consonants, vowels, structures, disallowed, max_syllables = reader.returnDirectives()
print(consonants, vowels, structures, disallowed, max_syllables)
phones = Phones(consonants, vowels, structures, disallowed, max_syllables)
dictionary = reader.readDictionaryFile()
wordbank = []
current_set = []
next_set = []

def main():
	global reader
	global phones
	global dictionary
	global wordbank
	global current_set
	global next_set

	print("Welcome to Foanz")
	print("Type 'help' to see commands")
	print()
	exit = False
	while True:
		if exit == True:
			exit()
		
		if next_set:
			current_set = next_set
			next_set = []
		if current_set:
			for index, word in enumerate(current_set):
				print(f'{index}.) {word}')

		user_input = getInput(": ")
		command_dict = processCommand(user_input)

		if command_dict["new"] != False and command_dict["more"] != False:
			print("New and more commands entered; more will be favoured")
		
		if command_dict["more"]:
			if command_dict["shuffle_consonants"]:
				phones.shuffleConsonants()
			if command_dict["shuffle_vowels"]:
				phones.shuffleVowels()
			next_set = phones.generateWordPool(int(command_dict["more"]))
		elif command_dict["new"]:
			phones.shuffleVowels()
			phones.shuffleConsonants()
			next_set = phones.generateWordPool(int(command_dict["new"]))

		if command_dict["apply_words"]:
			for word in wordbank:
				return_val = reader.addWord(word)
				if return_val == None:
					wordbank.remove(word)

		if command_dict["exit"]:
			exit = True

		if len(command_dict["indexes"]) != 0:
			for index in command_dict["indexes"]:
				try:
					wordbank.append(current_set[index])
				except IndexError:
					print("ERROR: index not in a valid range")

		if len(command_dict["new_words"]) != 0:
			for word in command_dict["new_words"]:
				wordbank.append(word)

		if command_dict["syllables"]:
			if isinstance(command_dict["syllables"], str):
				if command_dict["syllables"] == "Reset":
					phones.syllable_selection = False
					phones.min_syllables = 1
					phones.max_syllables = reader.max_syllables
			elif isinstance(command_dict["syllables"], int):
				phones.syllable_selection = False
				phones.min_syllables = 1
				phones.max_syllables = command_dict["syllables"]
			elif isinstance(command_dict["syllables"], list):
				phones.syllable_selection = command_dict["syllables"]
			else:
				print("foanz: unexpected input for syllables")

if __name__ == "__main__":
	main()