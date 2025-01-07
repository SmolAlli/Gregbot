import pyphen

s = pyphen.Pyphen(lang='en')


def syllables_split(sentence):
    words = sentence.split()
    syllable_list = []

    for word in words:
        syllables = s.inserted(word).split('-')
        print('word', word)
        if word == '\U000e0000':
            continue
        syllable_list.append(syllables)

    return syllable_list


def syllables_to_sentence(syllable_lists):
    # Join each list of syllables back into words
    words = [''.join(syllables) for syllables in syllable_lists]
    sentence = ' '.join(words)  # Join words into a complete sentence
    return sentence
