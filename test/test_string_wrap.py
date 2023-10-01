# -*- coding: utf-8 -*-

import contextlib
import io
import unittest

from string_wrap import string_wrap
from string_wrap import string_unwrap
from string_wrap import string_rewrap
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
            buf.getvalue().rstrip("\n"),
            "[StringWrap] ERROR: String not on its own line. Preceding: some_function(",
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

    def test_unwrap_3(self):
        lines = [
            "            f\"CleverCSV requires version '{dependency.min_version}' or newer \"",
            "            f\"for optional dependency '{dependency.package_name}'. Please \"",
            '            "update the package or install CleverCSV with all its optional "',
            '            "dependencies using: pip install clevercsv[full]"',
        ]
        expected = [
            "            f\"CleverCSV requires version '{dependency.min_version}' or newer for optional dependency '{dependency.package_name}'. Please update the package or install CleverCSV with all its optional dependencies using: pip install clevercsv[full]\""
        ]
        out = string_unwrap(lines)
        self.assertEqual(out, expected)

    def test_round_trip_1(self):
        line = '        "The default behavior with multiple input columns is to plot each column as a separate line, and use a horizontal axis of sequential integer values. With this option, the user can specify that the first column in the input data stream should be used as the horizontal axis."'
        out = string_unwrap(string_wrap(line, 60))
        self.assertEqual(out, [line])

    def test_identify_1(self):
        line = '                "ERROR: version installed from TestPyPI doesn\'t match expected version."'
        info = identify_start_and_quote([line])
        # start, quote, is_fstring = identify_start_and_quote(line)
        self.assertEqual(info.start_pos, 16)
        self.assertEqual(info.quote_str, '"')
        self.assertFalse(info.is_fstring)

    def test_fstrings_1(self):
        line = '    f"aa bb {foo} cc dd ee"'
        out = string_wrap(line, 60)
        self.assertEqual(out, [line])

    def test_fstrings_2(self):
        expected = [
            '        f"\nOptional dependency {name} is missing. You can install it using "',
            '        "pip or conda, or you can install CleverCSV with all of its optional "',
            '        "dependencies by running: pip install clevercsv[full]"',
        ]
        line = '        f"\nOptional dependency {name} is missing. You can install it using pip or conda, or you can install CleverCSV with all of its optional dependencies by running: pip install clevercsv[full]"'
        out = string_wrap(line, 79)
        self.assertSequenceEqual(out, expected)

    def test_fstrings_3(self):
        expected = [
            '                    f"Description for action {action.dest} found in "',
            '                    f"{desc_source} attribute is not of type str (received "',
            '                    f"type: {type(desc)})."',
        ]
        line = '                    f"Description for action {action.dest} found in {desc_source} attribute is not of type str (received type: {type(desc)})."'
        out = string_wrap(line, 79)
        self.assertSequenceEqual(out, expected)

    def test_fstrings_4(self):
        line = '    f"{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}"'
        expected = [
            '    f"{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}{foo}{bar}"',
            '    f"{foo}{bar}"',
        ]
        out = string_wrap(line, 79)
        self.assertSequenceEqual(out, expected)

    def test_fstrings_5(self):
        expected = [
            '            f"CleverCSV requires version {dependency.min_version} or newer "',
            "            f\"for optional dependency {' '.join(['a', 'b'])}. Please update \"",
            '            "the package or install CleverCSV with all its optional "',
            '            "dependencies using: pip install clevercsv[full]"',
        ]
        line = "            f\"CleverCSV requires version {dependency.min_version} or newer for optional dependency {' '.join(['a', 'b'])}. Please update the package or install CleverCSV with all its optional dependencies using: pip install clevercsv[full]\""
        out = string_wrap(line, 79)
        self.assertSequenceEqual(out, expected)

    def test_fstrings_6(self):
        expected = [
            '    f"Lorem ipsum dolor sit amet {consectetur} adipiscing elit sed doo eiusmo "',
            '    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim foo "',
        ]
        line = '    f"Lorem ipsum dolor sit amet {consectetur} adipiscing elit sed doo eiusmo tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim foo "'
        out = string_wrap(line, 79)
        self.assertSequenceEqual(out, expected)

    def test_trailing_comma_1(self):
        expected = [
            '    f"Lorem ipsum dolor sit amet {consectetur} adipiscing elit sed doo eiusmo "',
            '    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim foo ",',
        ]
        line = '    f"Lorem ipsum dolor sit amet {consectetur} adipiscing elit sed doo eiusmo tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim foo ",'
        out = string_wrap(line, 79)
        self.assertSequenceEqual(out, expected)

    def test_trailing_comma_2(self):
        # TODO: Add a roundtrip test with a trailing comma to ensure it stays
        expected = [
            '    f"Lorem ipsum dolor sit amet {consectetur} adipiscing elit sed doo eiusmo "',
            '    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim foo ",',
        ]
        out = string_rewrap(expected, 79)
        self.assertSequenceEqual(out, expected)


if __name__ == "__main__":
    unittest.main()
