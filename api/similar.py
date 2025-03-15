import Levenshtein
import logging

CUTOFF = 0.8


# https://maxbachmann.github.io/Levenshtein/levenshtein.html
# https://en.m.wikipedia.org/wiki/Levenshtein_distance
# Normalized similarity is documented as (1 - normalized distance).
# Normalized distance seems to be (raw_distance / combined length) * 2
def is_similar(string_a, string_b):
    if string_a == string_b:  # shortcut
        return True
    ratio = Levenshtein.ratio(string_a, string_b, score_cutoff=CUTOFF)
    if ratio > CUTOFF:
        logging.debug(f"'{string_a}' matches '{string_b}' {ratio}")
        return True
    return False


def score(string_a, string_b):
    return Levenshtein.ratio(string_a, string_b)


def unknowns(consider, history, match=is_similar):
    for candidate in consider:
        for past in history:
            if match(candidate, past):
                break  # out of inner for loop
        else:  # executed after inner loop if no break
            yield candidate
