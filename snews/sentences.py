#! /usr/bin/env python3

"""Splitting a string into sentences.

There are libraries that do this, but I thought it might be interesting
to do it myself, and I don't want the common feature of trying to
compensate for grammatical errors in the text.  Besides, the library
that people recommend is for Python NLTK, which doesn't support Python 3
and seems quite big to install for just that one function.

This doesn't have to be perfect, since it's just used to insert pauses
in the audio.

"""

import unittest
import re
import sys
import util
import itertools


class TestSimple(unittest.TestCase):
    def test_simple_statement(self):
        self.assertEqual(sentences("I ate a sandwich."), ["I ate a sandwich."])

    def test_two_statements(self):
        self.assertEqual(sentences("I ate a sandwich.  It was good."),
                ["I ate a sandwich.", "It was good."])

    def test_question_statement(self):
        self.assertEqual(sentences("Who knows?  I don't."),
                ["Who knows?", "I don't."])

    def test_extra_punctuation(self):
        self.assertEqual(sentences("I asked him, \"How?\"  He didn't answer."),
                ["I asked him, \"How?\"",  "He didn't answer."])

    def test_abbreviation(self):
        self.assertEqual(sentences("The U.S.A. is a country."),
                ["The U.S.A. is a country."])

    def test_abbreviated_name(self):
        self.assertEqual(sentences("Mr. Smith ate a sandwich."),
                ["Mr. Smith ate a sandwich."])
        self.assertEqual(sentences("Brian P. Jaress is my name."),
                ["Brian P. Jaress is my name."])

    def test_proper_acronym(self):
        self.assertEqual(sentences("The U.S. Government collects taxes."),
                ["The U.S. Government collects taxes."])



class TestGoldenRules(unittest.TestCase):
    """ http://tech.grammarly.com/blog/posts/How-to-Split-Sentences.html
    """

    def test_abbreviated_title(self):
        self.assertEqual(len(sentences("""
            At some schools, even professionals boasting Ph.D. degrees
            are coming back to school for Master's degrees
            """)), 1)

    def skip_test_informal(self):
        """ Not supported (grammatical error).
        """
        self.assertEqual(len(sentences("""
            If Harvard doesn't come through, I 'll take the test to get
            into Yale. many parents set goals for their children, or
            maybe they don't set a goal.
            """)), 2)

    def test_abbreviation_name(self):
        self.assertEqual(len(sentences("""
            He adds, in a far less amused tone, that the government has
            been talking about making Mt. Kuanyin a national park for a
            long time, and has banned construction or use of the
            mountain.
            """)), 1)

    def skip_test_abbreviation_end(self):
        """No clue how to do this.  It's the hard case everyone else
        cites when saying the problem isn't completely solved.

        """

        self.assertEqual(len(sentences("""
            The luxury auto maker last year sold 1,214 cars in the U.S.
            Howard Mosher, president and chief executive officer, said
            he anticipates growth for the luxury auto maker in Britain
            and Europe, and in Far Eastern markets.
            """)), 2)

    def test_elipsis_end(self):
        """This test is altered from what's online because I actually
        think it's an error not to capitalize the start of a new
        sentence, but I do want to test ellipses.

        """

        self.assertEqual(len(sentences("""
            No, to my mind, the Journal did not "defend sleaze, fraud,
            waste, embezzlement, influence-peddling and abuse of the
            public trust..." It defended appropriate constitutional
            safeguards and practical common sense
            """)), 2)

    def skip_test_elipsis_omit(self):
        """Don't know how to distinguish that "I'll" isn't the start of
        a new sentence.
        """
        self.assertEqual(len(sentences("""
            After seeing the list of what would not be open and/or on
            duty... which I'm also quite sure is not complete... I 'll
            go out on a limb.... and predict... that this will not
            happen
            """)), 1)

    def test_initials(self):
        self.assertEqual(len(sentences("""
            Bharat Ratna Avul Pakir Jainulabdeen Abdul Kalam is also
            called as Dr. A.P.J Abdul Kalam.
            """)), 1)

    def skip_test_letter_end(self):
        """Not supported, don't see an easy way to do it.
        """
        self.assertEqual(len(sentences("""
            The agency said it confirmed American Continental's
            preferred stock rating at C. American Continental's thrift
            unit, Los Angeles-based Lincoln Savings & Loan Association,
            is in receivership and the parent company has filed for
            protection from creditor lawsuits under Chapter 11 of the
            federal Bankruptcy Code.
            """)), 2)

    def test_quote_end(self):
        self.assertEqual(len(sentences("""
            Wang first asked: "Are you sure you want the original
            inscription ground off?" Without thinking twice about it,
            Huang said yes.
            """)), 3)

    def skip_test_quote_middle(self):
        """It's actually better to get this one "wrong" because we're
        inserting pauses, not doing grammatical analysis.

        """

        self.assertEqual(len(sentences("""
            "It's too much, there's only us two, how are we going to eat
            this?" I asked young Zhao as I looked at him in surprise.
            """)), 1)

    def test_nonstandard(self):
        """I'm not even sure what the right answer is here.
        """
        self.assertEqual(len(sentences("""
            The JW considers itself THE kingdom of God on earth.
            ('Kindom Hall') So it is only to be expected that they do
            not see a reason to run to and report everything to the
            government.
            """)), 2)

    def test_url(self):
        self.assertEqual(len(sentences("""
            Google Search is at http://www.google.com.  It is a search engine.
            """)), 2)



def sentences(words):
    """Splits words into sentences.

    Everything else in the module is a helper or test for this function.
    """
    if isinstance(words, str):
        words = words.split()
    sentence_groups = [[]]
    prev = ""
    for word in words:
        #log(word)
        if len(prev) > 0 and ends_sentence(prev, word):
            sentence_groups.append([word])
        else:
            sentence_groups[-1].append(word)
        prev = word
    return [" ".join(group) for group in sentence_groups]


def ends_sentence(word, next_word):
    return (punctuated_as_end(word) and capitalized(next_word) and
            not (capitalized(word) and abbreviated_name(word)) and
            not acronym(word))

def log(word):
    print({
        "word": word,
        "punctuated_as_end": punctuated_as_end(word),
        "capitalized": capitalized(word),
        "abbreviated_name": abbreviated_name(word),
        "acronym": acronym(word),
        })

END_PUNCTUATION = frozenset(".?!:")

def punctuated_as_end(word):
    try:
        punct_suffix = re.findall("\W+$", word)[-1]
    except IndexError:
        return False
    return not END_PUNCTUATION.isdisjoint(frozenset(punct_suffix))

def capitalized(word):
    return re.match("[A-Z][^A-Z]*", letters(word))

def acronym(word):
    return re.match("[A-Z.]+\.$", word)

def abbreviated_name(word):
    ltrs = letters(word)
    if re.match("[A-Z]*$", ltrs):
        return True # initial
    return ltrs in ABBREVIATED_NAMES

def letters(word):
    return re.sub("\W", "", word)


ABBREVIATED_NAMES = frozenset(word for word in
        """

        Dr
        Esq
        Hon
        Hon
        Jr
        Messrs
        Mmes
        Mr
        Mrs
        Ms
        Msgr
        Prof
        Rev
        Rt
        Sr

        Ave
        Blvd
        Rd
        St
        Mt

        Col
        Gen
        Lt
        Pvt
        Sgt
        """.split())

if __name__ == '__main__':
    for paragraph in util.paragraph_words(sys.stdin):
        for sentence in sentences(paragraph):
            print(sentence)
        print()
