#! /usr/bin/env python3

import unittest
import itertools

def listify(iterable):
    """For testing nested iterators."""
    return [list(sub_iter) for sub_iter in iterable]

class TestIterSplit(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
                listify(iter_split(lambda x: x % 3 == 0, range(11))),
                [[1, 2], [4, 5], [7, 8], [10]])

    def test_string_equiv(self):
        text = "one two three"
        self.assertEqual(
                [list(chars) for chars in text.split(' ')],
                listify(iter_split(lambda char: char == ' ', text)))


def iter_split(pred, seq):
    """Split iterable.

    Same idea as string splitting, but instead of splitting a string
    into a list of strings, it splits an iterable into an iterable of
    iterables.

    """
    not_pred = lambda x: not pred(x)
    iterator = iter(seq)

    def cons(first, rest):
        yield first
        yield from rest

    while True:
        iterator = itertools.dropwhile(pred, iterator)
        first = next(iterator) # break out if empty
        yield cons(first, itertools.takewhile(not_pred, iterator))



class TestParagraphWords(unittest.TestCase):
    def test_short(self):
        lines = [ "one two", "three four" ]
        self.assertEqual(
                listify(paragraph_words(lines)),
                [[ "one", "two", "three", "four" ]])

    def test_extended(self):
        lines = [ "one two", "three four" , "", "five six" ]
        self.assertEqual(
                listify(paragraph_words(lines)),
                [ [ "one", "two", "three", "four" ], ["five", "six"] ])


def paragraph_words(lines):
    """Turn a sequence of lines into an iterable of paragraphs, each of
    which is an iterable of words.
    """
    split_lines = (line.split() for line in lines)
    line_paragraphs = iter_split(lambda line: not len(line), split_lines)
    word_paragraphs = map(itertools.chain.from_iterable, line_paragraphs)
    return word_paragraphs

