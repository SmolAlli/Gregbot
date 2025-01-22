import re

ALPHABET = r"a-zA-Z"
LETTERS_REGEX = r"[" + ALPHABET + r"]"
PUNCTUATION_REGEX = r"[^" + ALPHABET + r"\s]+"


def fix_re_escape(string: str):
    """Fixes the \\ being messed up from re.escape"""
    return re.sub(r'\\(.)', r'\1', string)


def is_punctuation(string: str):
    return bool(re.search(PUNCTUATION_REGEX, string))
