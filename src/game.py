"""
TODO: 
1) Finish adding some code comment sections
2) Scoring could be improved massively I am sure
3) What is the convention to underscore the start of methods
4) Is there convention to order methods within a class?
"""

import os
import logging
import string
from collections import defaultdict
import sys

class Wordlesolver():
    def __init__(self):
        self.remaining_turns = 5
        self.create_logger()
        self.letter_info ={letter: None for letter in string.ascii_lowercase}
        self.get_word_list()
        self.logger.info(f"Number of total possible words is {len(self.possible_solutions)}")


    def play(self):        
        self.score_words()
        while self.remaining_turns >= 0:
            self.game_round()
            self.remaining_turns -= 1

    def get_word_list(self):
        # Go up one directory from this file (from src/ to project root)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "valid-wordle-words.txt")


        with open(file_path, "r") as file:
            self.words = [line.strip() for line in file]

        self.possible_solutions = self.words.copy()

        

    def game_round(self):
        while True:
            word_input = input("(Enter 'xxxxx' to quit) Enter your 5-letter word: ").strip().lower()
            if word_input == 'xxxxx':
                self.logger.info("Quitting game, thanks!")
                sys.exit(0)
            if len(word_input) != 5:
                print("Word must be exactly 5 letters.")
                continue

            if not word_input.isalpha():
                print("Word must contain only letters (no numbers or symbols).")
                continue

            break  # valid input


        self.logger.info(f"You have entered '{word_input}'. Now please enter the response in the format 'YBGYG' for the three options of black,yellow and green.")


        while True:
            response_input = input("(Enter 'xxxxx' to quit) Enter your 5-letter response: ").strip().lower()
            if response_input == 'xxxxx':
                self.logger.info("Quitting game, thanks!")
                sys.exit(0)
            if len(response_input) != 5:
                print("Word must be exactly 5 letters.")
                continue

            if not response_input.isalpha():
                print("Word must contain only letters (no numbers or symbols).")
                continue

            break  # valid input



        word_letters = list(word_input)
        response_letters = list(response_input)

        self.refresh_possible_solutions(word_letters=word_letters
                                        ,response_letters=response_letters)
        
        self.score_words()



    def create_logger(self):
        """
        Creates and configures a logger.

        This function initializes a logger, sets its level to INFO,
        and configures a StreamHandler to output log messages to stdout with a specific format.

        Returns:
            self.logger
        """
        self.logger = logging.getLogger("WordleHelper")
        self.logger.setLevel(logging.INFO)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.info(f"Logger initalised")








    def __black_letter(self,letter):
        """
            Removes words from the possible solution pile that contain the provided letter
        """
        letter = letter.strip().lower()
        pre_vol = len(self.possible_solutions)
        self.possible_solutions = [word for word in self.possible_solutions if letter not in word]
        post_vol = len(self.possible_solutions)
        self.logger.info(f"Removed {pre_vol-post_vol} words from the solution pile due to having '{letter}' in the word.")


    def __yellow_letter(self, letter, position):
        """
        Removes words from the possible solution pile that:
        - contain the letter in the specified position (bad),
        - or do not contain the letter at all in any other position (also bad).
        """
        python_position = position - 1  # Adjust for 0-based indexing
        letter = letter.strip().lower()

        # e.g for word[:python_position] + word[python_position + 1:]
        # word = "apple"
        # word[:1] + word[2:] == "a" + "ple" == "aple"
        
        pre_vol = len(self.possible_solutions)
        self.possible_solutions = [
            word for word in self.possible_solutions
            if len(word) > python_position
            and word[python_position].lower() != letter
            and letter in (word[:python_position] + word[python_position + 1:]).lower()
        ] 
        post_vol = len(self.possible_solutions)

        self.logger.info(
            f"Removed {pre_vol - post_vol} words due to yellow '{letter}' in position {position}."
        )

    def __green_letter(self,letter,position):
        """
            Removes words from the possible solution pile that do not contain the provided letter in that position
        """
        python_position = position-1 # Fixing the player index vs Python index 0
        letter = letter.strip().lower()

        pre_vol = len(self.possible_solutions)
        # Filter words where the letter at 'python_position' is the letter
        self.possible_solutions = [
            word for word in self.possible_solutions
            if len(word) > python_position and word[python_position].lower() == letter
        ]
        post_vol = len(self.possible_solutions)
        self.logger.info(f"Removed {pre_vol-post_vol} words from the solution pile due to not having '{letter}' in position {position}.")



    def refresh_possible_solutions(self,word_letters,response_letters):

        position = 1

        for item1, item2 in zip(word_letters, response_letters):
            self.logger.info(f"Letter {item1} in position {position} is {item2}...")
            
            if item2 == 'b':
                self.__black_letter(letter=item1)
            if item2 == 'y':
                self.__yellow_letter(letter=item1
                                   ,position=position)
            if item2 == 'g':
                self.__green_letter(letter=item1
                                  ,position=position)
            position += 1

        self.logger.info(f"There are now {len(self.possible_solutions)} possible solutions remaining.")

        # Either the wrong entry or something has gone wrong!
        if len(self.possible_solutions) == 0:
            self.logger.info("No found solutions...")
            sys.exit(0)


    def __calculate_positional_frequency(self) -> list[dict]:
        pos_freq = [defaultdict(int) for _ in range(5)]  # assuming 5-letter words
        for word in self.possible_solutions:
            for i, ch in enumerate(word):
                pos_freq[i][ch] += 1
        self.positional_frequency = pos_freq


    def score_words(self):
        scored = []
        self.__calculate_positional_frequency()
        for word in self.possible_solutions:
            # Sum the frequency of each letter in its position
            score = sum(self.positional_frequency[i].get(ch, 0) for i, ch in enumerate(word))
            scored.append((word, score))
        scored.sort(key=lambda x: x[1], reverse=True)

        # Format the top 20 into a readable string
        top_words_str = "\n".join(f"'{word}' has a score of {score}" for word, score in scored[:20])
        self.logger.info(f"Here are some good words:\n{top_words_str}")