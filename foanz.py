#!/usr/bin/python3

from reader import Reader
from phones import Phones
from sys import argv

def printHelp():
	print("Commands:")
	print("\t(h)elp")
	print("\t\tShows this whole spiel")
	print()
	print("\t(r)ead [FILEPATH]")
	print("\t\tload the file at the absolute or relative directory FILEPATH as new dictionary/directives file")
	print("\t\twithout any filepath it reloads the dictionary file given")
	print()
	print("\t(n)ew [x]")
	print("\t\tby default, will provide 10 randomly generated words with a shuffled phoneme distribution")
	print("\t\tif provided a given number x, it will generate x words instead")
	print()
	print("\t(m)ore [x]")
	print("\t\tby default, will provide 10 randomly generated words with the same phoneme distribution")
	print("\t\tas in your original dictionary file, or the last generated batch of words")
	print("\t\tif provided a given number x, it will generate x words instead")
	print()
	print("\t(sh)uffle [consonants/vowels]")
	print("\t\twill shuffle both consonants and vowels, unless only one is specified")
	print()
	print("\t(s)yllables [x[.y.z]/x-y]")
	print("\t\twill restrict generated words to a single length, or given range or dotted list of syllables")
	print("\t\tnull-argument will reset it back to using your defined max_syllables directive")
	print()
	print("\t(a)pply [filename]")
	print("\t\twill apply your existing updates and write it to 'filename'")
	print("\t\tif you leave filename blank, it will use your last-used filename")
	print("\t\tor it will default to default.txt")
	print()
	print("\t(e)xit")
	print("\t\twill exit without updating words")
	print()
	print("When given a list of words, entering their indexes in a comma-separated list")
	print("\twill auto-fill blank entries in your dictionary file as directed")
	print("Alternatively, new words can be added by typing your own in; syllable boundaries")
	print("\tmay need to be indicated with full stops (foanz will attempt to guess based")
	print("\ton the number of vowel clusters), and single quotes (') MUST wrap your words")
	print("TIP: Multiple commands can be issued with a comma-separated list and they will be processed one-by-one")
	print()
	print("PROTIP: You can launch foanz with:")
	print("\tfoanz.py [input_textfile] [output.textfile]")
	print("\t(with only one filepath it is assumed to be input)")
	print()

def getInput(message):
	while True:
		user_input = input(message).strip()
		if user_input != "":
			return user_input

def processCommand(command):
	global reader

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
		if "'" in command:
			new_words.append(command.replace("'", ""))
			continue
		elif command.isdigit():
			indexes.append(int(command))
			continue

		elif command.startswith("n"):
			if command == "new" or command == "n":
				new = 10
			else:
				try:
					new = int(command.split()[1])
				except Exception as e:
					print(e)
					print("foanz: unexpected argument")
			continue

		elif command.startswith("m"):
			if command == "more" or command == "m":
				more = 10
			else:
				try:
					more = int(command.split()[1])
				except Exception as e:
					print(e)
					print("foanz: unexpected argument")
			continue

		elif command.startswith("sh"):
			if command == "shuffle" or command == "sh":
				shuffle_vowels = True
				shuffle_consonants = True
			elif "vowels" in command:
				shuffle_vowels = True
			elif "consonants" in command:
				shuffle_consonants = True
			else:
				print("foanz: unexpected argument")
			continue

		elif command.startswith("a"):
			apply_words = True
			command_list = command.split()
			if len(command_list) > 1:
				reader.outfile = command_list[1]
			continue

		elif command == "exit" or command == "e":
			exit = True
			continue

		elif command.startswith("s"):
			if command == "syllables" or command == "s":
				syllables = "Reset"
			else:
				command_list = command.split()
				try:
					if reader.delimiter in command_list[1]:
						syllables = [int(number.strip()) for number in command_list[1].split(reader.delimiter)]
					elif "-" in command_list[1]:
						syllables_list = [int(n.strip()) for n in command_list[1].split("-")]
						syllables = list(range(syllables_list[0], syllables_list[1]+1))
					else:
						syllables = int(command_list[1].strip())
				except ValueError:
					print("foanz: non-number supplied where number was expected")
			continue

		elif command.startswith("h"):
			printHelp()
			continue

		elif command.startswith("r"):
			command_list = command.split()
			old_file = reader.textfile
			if len(command_list) > 1:
				reader.textfile = command_list[1]
			try:
				reader.readDictionaryFile()
			except Exception as e:
				print(e)
				print("foanz: bad filepath")
				reader.textfile = old_file

	return {"new": new, "more": more, "shuffle_consonants": shuffle_consonants, "shuffle_vowels": shuffle_vowels,
			"apply_words": apply_words, "exit": exit, "indexes": indexes, "new_words": new_words, "syllables": syllables}

def exitFoanz():
	global wordbank

	reader.save(wordbank)
	quit()

def printSettings():
	global reader
	global phones
	syllables = phones.syllable_selection if phones.syllable_selection else list(range(phones.min_syllables, phones.max_syllables)) 
	print(f'input_file: {reader.textfile}\noutput_file: {reader.outfile}\nvowels: {phones.vowels}\nconsonants: {phones.consonants}\nsyllables: {syllables}')

def main():
	global reader
	global phones
	global wordbank
	global current_set
	global next_set

	print("Welcome to Foanz")
	print("Type 'help' to see commands")
	print()
	exit = False
	reprint = False

	while True:
		if exit == True:
			exitFoanz()
		
		printSettings()

		if next_set:
			current_set = next_set
			next_set = []
		if current_set and reprint:
			for index, word in enumerate(current_set):
				print(f'{index}.) {word} ({word.replace(reader.delimiter, "")})')
			reprint = False

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
			reprint = True
		elif command_dict["new"]:
			phones.shuffleVowels()
			phones.shuffleConsonants()
			next_set = phones.generateWordPool(int(command_dict["new"]))
			reprint = True

		if command_dict["apply_words"]:
			for word in wordbank:
				return_val = reader.addWord(word)
				if return_val == None:
					wordbank.remove(word)
			reader.save(wordbank)

		if command_dict["exit"]:
			exit = True

		if len(command_dict["indexes"]) != 0:
			for index in command_dict["indexes"]:
				try:
					wordbank.append(current_set[index])
				except IndexError:
					print("foanz: index not in a valid range")

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
				phones.max_syllables = command_dict["syllables"] + 1
			elif isinstance(command_dict["syllables"], list):
				phones.syllable_selection = command_dict["syllables"]
			else:
				print("foanz: unexpected input for syllables")

if __name__ == "__main__":
	global reader
	global consonants
	global phones
	global wordbank
	global current_set
	global next_set

	infile = "./example.txt"
	outfile = "./outfile.txt"

	argc = len(argv)
	if argc > 1:
		if argc == 2:
			infile = argv[1]
		elif argc == 3:
			infile = argv[1]
			outfile = argv[2]
		else:
			print("foanz: too many arguments")
			printHelp()
			quit()

	reader = Reader(infile, outfile=outfile)
	
	consonants, vowels, structures, disallowed, max_syllables, required, delimiter = reader.returnDirectives()
	phones = Phones(consonants, vowels, structures, disallowed, max_syllables, required, delimiter)
	wordbank = reader.wordbank
	current_set = []
	next_set = []

	main()