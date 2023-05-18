import Levenshtein

CUTOFF = 0.6

# https://maxbachmann.github.io/Levenshtein/levenshtein.html
# https://en.m.wikipedia.org/wiki/Levenshtein_distance
# Normalized similarity is documented as (1 - normalized distance).
# Normalized distance seems to be (raw_distance / combined length) * 2
def is_similar(string_a, string_b):
    if string_a == string_b:  # shortcut
        return True
    return Levenshtein.ratio(string_a, string_b, score_cutoff=CUTOFF) > CUTOFF


def first_unknown(consider, history, match=is_similar):
    for candidate in consider:
        for past in history:
            if match(candidate, past):
                break  # out of inner for loop
        else:  # executed after loop if no break
            return candidate
