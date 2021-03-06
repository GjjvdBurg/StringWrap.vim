# -*- coding: utf-8 -*-

import contextlib
import io
import unittest

from string_wrap import string_wrap
from string_wrap import string_unwrap
from string_wrap.wrapper import identify_start_and_quote


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
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            out = string_wrap(line, 79)
        self.assertIsNone(out)
        self.assertEqual(
            buf.getvalue().rstrip('\n'), "[StringWrap] ERROR: String not on its own line."
        )

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

    def test_unwrap_2(self):
        lines = [
            '\'{\n\t"test_statistic": 7.001209,\n\t"degrees_of_freedom": 9,\n\t\'',
            '\'"p_value": 6.316304505558843e-05,\n\t"reject_H0_at_0.05: true,\n\t\'',
            '\'"mean_difference": 0.5425054110364441,\n\t"std_difference": \'',
            "'0.23246217185411072,\n\t\"count\": 10}'",
        ]
        expected = [
            '\'{\n\t"test_statistic": 7.001209,\n\t"degrees_of_freedom": 9,\n\t"p_value": 6.316304505558843e-05,\n\t"reject_H0_at_0.05: true,\n\t"mean_difference": 0.5425054110364441,\n\t"std_difference": 0.23246217185411072,\n\t"count": 10}\'',
        ]
        out = string_unwrap(lines)
        self.assertEqual(out, expected)

    def test_round_trip(self):
        line = '        "The default behavior with multiple input columns is to plot each column as a separate line, and use a horizontal axis of sequential integer values. With this option, the user can specify that the first column in the input data stream should be used as the horizontal axis."'
        out = string_unwrap(string_wrap(line, 60))
        self.assertEqual(out, [line])

    def test_identify_1(self):
        line = '                "ERROR: version installed from TestPyPI doesn\'t match expected version."'
        start, quote = identify_start_and_quote(line)
        self.assertEqual(start, 16)
        self.assertEqual(quote, '"')


if __name__ == "__main__":
    unittest.main()
