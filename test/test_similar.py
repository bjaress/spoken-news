import unittest
import operator as op
import hypothesis as hy
import hypothesis.strategies as st

from api.similar import is_similar, first_unknown


class TestFirstUnknown(unittest.TestCase):
    def test_single_known(self):
        consider = [1]
        history = [1]
        assert first_unknown(consider, history, match=op.eq) is None

    def test_single_unknown(self):
        consider = [2]
        history = [1]
        assert first_unknown(consider, history, match=op.eq) == 2

    def test_skips(self):
        consider = [1, 2, 3, 4, 5, 6]
        history = [1, 1, 2, 3, 5, 8]
        assert first_unknown(consider, history, match=op.eq) == 4

    @hy.given(st.lists(st.integers()), st.lists(st.integers()))
    def test_knownness(self, consider, history):
        result = first_unknown(consider, history, match=op.eq)
        consider_set = set(consider)
        history_set = set(history)

        assert result not in history_set, (result, consider, history)
        if result is not None:
            assert result in consider_set, (result, consider, history)
        else:
            assert consider_set.issubset(history_set), (result, consider, history)


class TestSimple(unittest.TestCase):
    def test_kitten_sitting(self):
        assert is_similar("kitten", "sitting")

    def test_flaw_lawn(self):
        assert is_similar("flaw", "lawn")

    def test_flaw_lawn(self):
        assert not is_similar("flawed", "lawn")


class TestFake(unittest.TestCase):
    def setUp(self):
        self.frog = " ".join(
            [
                "An incident involving frogs occurred. For a variety",
                "of reasons, it takes Wikipedia many characters to",
                "form a headline about it, but this ...",
            ]
        )
        self.toad = " ".join(
            [
                "An incident involving toads occurred. For a variety",
                "of reasons, it takes Wikipedia many characters to",
                "form a headline about it, but this ...",
            ]
        )
        self.early_report_toad = " ".join(["An incident involving toads occurred."])

    def test_frog_toad(self):
        assert is_similar(self.frog, self.toad)

    def test_toad_early_toad(self):
        assert not is_similar(self.early_report_toad, self.toad)

    def test_frog_early_toad(self):
        assert not is_similar(self.early_report_toad, self.frog)


class TestRealistic(unittest.TestCase):
    def test_death_total_mocha(self):
        assert is_similar(
            " ".join(
                [
                    "Cyclone Mocha strikes Myanmar and Bangladesh,",
                    "killing more than 400 people.",
                ]
            ),
            " ".join(
                [
                    "Cyclone Mocha strikes Myanmar and Bangladesh,",
                    "killing more than 85 people.",
                ]
            ),
        )

    def test_more_info_kivandya(self):
        assert not is_similar(
            " ".join(
                [
                    "Three people are killed and three others are injured",
                    "after an armed ambush on a convoy near the Kivandya",
                    "village, North Kivu, Democratic Republic of the",
                    "Congo. One person is also reported missing.",
                ]
            ),
            " ".join(
                [
                    "An armed ambush occurs on a convoy",
                    "in the Democratic Republic of the Congo.",
                ]
            ),
        )
