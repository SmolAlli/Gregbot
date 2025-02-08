import re
import inflect
from regex_funcs import LETTERS_REGEX

inf = inflect.engine()


def check_if_plural(word: str):
    """Check if the given word is a plural or not"""
    try:
        pl = inf.singular_noun(word) is not False
    except Exception as e:
        print(f"Errored in check_if_plural: {e}")
        pl = False
    return pl


def get_plural_of_word(word: str):
    """Gets the plural form of a specific word"""
    return inf.plural(word)


def get_syllables_no_punctuation(syllables: list[str]):
    """
    Gets all the syllables in a list and replaces all punctuation with an empty string
    Note: will leave apostrophes in the middle of words as is
    """
    syllables_no_punctuation = []
    for i, syllable in enumerate(syllables):
        # Special case: if it's a apostrophe in the middle of a word
        if 0 < i < len(syllables) and syllable == "'":
            # Keep this
            syllables_no_punctuation.append(syllable)

        else:
            if re.match(LETTERS_REGEX + r"+", syllable):
                syllables_no_punctuation.append(syllable)
            else:
                syllables_no_punctuation.append("")

    return syllables_no_punctuation


def get_reverse_index(li: list[str], elem: str):
    """Gets the last index of an element in a list"""
    return next((i for i in reversed(range(len(li))) if li[i] == elem), 0)


def check_if_should_be_plural(syllables: list[str], index: int):
    """
    Check if the syllable in a list should be considered as a plural or not.
    Will return true only when the word it finds is a plural AND if the index given is for the last part of the word
    """
    # Find the start of the word part in syllables
    start_pos = get_reverse_index(syllables[:index+1], "")

    # Find the end of the word part in syllables
    end_pos = 0
    try:
        end_pos = syllables.index("", index)
    except ValueError:
        end_pos = len(syllables)

    # Make the word to be tested
    word = "".join(syllables[start_pos:end_pos])

    # If the word is a plural and the chosen index is for the last part of the word, butts
    if check_if_plural(word) and end_pos - 1 == index:
        return True

    return False


def get_buttword_plural(word: str, li: list[str], index: int):
    plural = get_plural_of_word(word) if check_if_should_be_plural(
        get_syllables_no_punctuation(li), index) else word
    return plural
