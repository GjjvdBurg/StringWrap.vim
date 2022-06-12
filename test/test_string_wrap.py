# -*- coding: utf-8 -*-

import unittest

from string_wrap import string_wrap
from string_wrap import string_unwrap


class StringWrapTestCase(unittest.TestCase):

    maxDiff = None

    def test_wrap_1(self):
        line = '                "The default behavior with multiple input columns is to plot each column as a separate line, and use a horizontal axis of sequential integer values. With this option, the user can specify that the first column in the input data stream should be used as the horizontal axis."'
        expected = [
            '                "The default behavior with multiple input columns is to plot "',
            '                "each column as a separate line, and use a horizontal axis of "',
            '                "sequential integer values. With this option, the user can "',
            '                "specify that the first column in the input data stream "',
            '                "should be used as the horizontal axis."',
        ]
        out = string_wrap(line, 79)
        self.assertEqual(out, expected)

    def test_wrap_2(self):
        line = 'some_function("text here")'
        expected = ['some_function("text here")']
        out = string_wrap(line, 79)
        self.assertEqual(out, expected)

    def test_unwrap_1(self):
        lines = [
            '                "The default behavior with multiple input columns is to plot "',
            '                "each column as a separate line, and use a horizontal axis of "',
            '                "sequential integer values. With this option, the user can "',
            '                "specify that the first column in the input data stream "',
            '                "should be used as the horizontal axis."',
        ]
        expected = [
            '                "The default behavior with multiple input columns is to plot each column as a separate line, and use a horizontal axis of sequential integer values. With this option, the user can specify that the first column in the input data stream should be used as the horizontal axis."'
        ]
        out = string_unwrap(lines)
        self.assertEqual(out, expected)

    def test_round_trip(self):
        line = '        "The default behavior with multiple input columns is to plot each column as a separate line, and use a horizontal axis of sequential integer values. With this option, the user can specify that the first column in the input data stream should be used as the horizontal axis."'
        out = string_unwrap(string_wrap(line, 60))
        self.assertEqual(out, [line])



if __name__ == "__main__":
    unittest.main()
