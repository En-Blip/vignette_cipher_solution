import random

cipher = "ynxzhseedbpebmjhkiyxesmmwnycrsxrgsmwhockalntdbsiygtovqmdqsimseozqibbsnobmidrxyletnrvabbqskfjglyaanpdmvzxzionbyxlptnrvnigybmsanrvwwepniwryueeevxkvhoboyuunrbigzwyesmdyovxgspznlfmdaigzseavrarifdnkktwjlskldnwlsbnhkxxdnckhqaosvkdhdyetvkrbsahonkvbavmhbyknozyhkcxcibztgnrnirzpoetcnpgwvgxckabrebmrjntlsbqicqvvvvvivglovehyywbzbxrmvciyutprckziiymvsanvinsmmeivqievqrklomiwhwkoinuxrtqbrctmaykedkhpdcvzwyllloizzsoymkelgscwqzyhkevgfiblzabfwbuspivhcojivaedqsiuvtoucidqxdixkolncgmqpmdrbiahyvgjgzvtqgmyveixcvcceimwskybrtqbrdpmngejtjrxrmgzhdiatsembmiuvcocegyvwdxoiabvsxasacxkezaedqsiuvrfnnmbasoboiwqfigmjvwotezgesvhdmkjtmetkaxobsekqakkvhhydyolfhslrjnziedrrdesmfnnazfjebymydyivxmxoqpmdgrmiixbavlc"

letters = list("abcdefghijklmnopqrstuvwxyz")
beginningLetter = ord("a")

words_4_letters = []
words_5_letters = []
words = []
# get some common words and store them in lists
with open("words.txt") as f:
   for word in f:
       if len(word.strip()) == 4:
        words_4_letters.append(word.strip().lower())
       elif len(word.strip()) == 5:
        words_5_letters.append(word.strip().lower())
       words.append(word.strip().lower())


# a function to decode the cipher once we have a good guess of the key
def decode(cipher, key):
    decoded_str = ""

    for i, letter in enumerate(cipher):
        index = ord(letter) - letters.index(key[i % len(key)])
        if index < beginningLetter: index += 26
        decoded_str += chr(index)

    return decoded_str

# function that calculates the key required to decode a length of the cipher to a certain length of text
# ex. if amd gets decoded to ala, the key would be abd
def calculate_key(snippet, guess): # snippet is a set of letters in the cipher
    key = ""

    if len(snippet) != len(guess):
        print("Snippet and guess must be the same length")
        return
    
    for i in range(len(snippet)):
        index = ord(snippet[i]) - ord(guess[i])
        if index < 0: index += 26 
        key += letters[index]

    return key

# given a set of words, this function first assumes the word is at position i, then using the encoded text and what that text would
# hypothetically be decoded as, it calculates the key for that position
# It does this for each word in the list and assuming that word is at each position, keeping track of how often a certain key is found
def generate_key_fragments(words):
    calculated_keys = {}

    # choose a word and calculate all the possible keys for that word
    for word in words:
        for i in range(len(cipher) - len(word)):
            test_key = calculate_key(cipher[i:i+len(word)], word)
            if test_key not in calculated_keys:
                calculated_keys[test_key] = 1
            else:
                calculated_keys[test_key] += 1


    return calculated_keys

# the next two functions attempt to remove "key fragments" that are more often a product of probability then 
# actually being a portion of the keyword
def calc_letter_frequency(guesses):
    letter_freq = {}
    for guess in guesses:
        for letter in guess:
            if letter not in letter_freq:
                letter_freq[letter] = 0
            else:
                letter_freq[letter] += 1
    
    top_10_letters = sorted(letter_freq, key=letter_freq.get, reverse=True)[:15]

    return top_10_letters
def remove_outliers(best_guesses, top_letters):
    guesses = best_guesses.copy()

    for guess in best_guesses:
        for letter in guess:
            if letter not in top_letters and guess in guesses:
                guesses.remove(guess)
                continue

    return guesses

# function to find similar sequences of strings among a list
# this helps concetenate the similar strings, which helps construct the word
def find_similar(guesses, min_sequence_length=3, max_sequence_length=5):
    similar = []
    sequences = []
    for sequence_length in range(min_sequence_length, max_sequence_length):
        for guess in guesses:
            for i in range(len(guess) -  sequence_length):
                sequence = guess[i:i+sequence_length]
                for similar_guess in guesses:
                    if similar_guess.endswith(sequence) and guess.startswith(sequence):
                        if (similar_guess + guess[sequence_length:]) not in similar: similar.append(similar_guess + guess[sequence_length:])

    return similar




def main():

    # get the best guesses for 4 and 5 letter words, taking the top 30 most frequent keys
    # choosing 4 and 5 letter words because average english word length is 4.7, so this length
    # of word will give the best results (if the key is at least 4 or 5 letters long)
    calculated_keys_4l = generate_key_fragments(words_4_letters)
    names = sorted(calculated_keys_4l, key=calculated_keys_4l.get, reverse=True)
    key_frags = names[:15]

    calculated_keys_5l = generate_key_fragments(words_5_letters)
    names = sorted(calculated_keys_5l, key=calculated_keys_5l.get, reverse=True)
    key_frags += names[:15]


    # remove outliers for keys (random keys that were found often often dont contain many of the most common letters)
    top_letters = calc_letter_frequency(key_frags)
    best_guesses = remove_outliers(key_frags, top_letters)

    # print the key fragments
    print(best_guesses)


    # loop through the best fragments and combine them into words
    # terminate the loop if they start growing in size because the key is likely repeating
    while len(best_guesses) > 1 and len(best_guesses[0]) < 20:
        together = find_similar(best_guesses, 3) # set the min sequence length to 2 for more accuracy (but longer computing time)

        # terminate if there are no more similar words
        if len(together) > 0:
            best_guesses = together
        else:
            print(best_guesses)
            break
    print(best_guesses)

main()


# output is krainekiev from which, it is quite easy to guess the key "kievukraine" in a couple of tries