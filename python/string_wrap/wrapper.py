#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrap a long Python string in Vim.

Author: Gertjan van den Burg
Date: 2022-06-12
License: See LICENSE file

"""

import sys

from typing import List
from typing import Optional
from typing import Tuple


def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to multiple lines with specified maximum width

    This function wraps text in such a way that sentences always end with a
    space, which I prefer to the alternative of sentences occassionally
    starting with a space (which would happen when using textwrap.wrap).
    """
    words = text.split(" ")
    sentences = []
    current_length = 0
    sentence = ""
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_length += len(word) + 1
            sentence += word + " "
        else:
            current_length = len(word) + 1
            sentences.append(sentence)
            sentence = word + " "
    if sentence:
        sentences.append(sentence.strip())
    return sentences


def string_wrap(line: str, text_width: int) -> Optional[List[str]]:
    # Figure out which quote mark the line is using
    startpos, quotestr = identify_start_and_quote(line)
    if quotestr is None:
        return None

    indent = " " * startpos
    clean = line.strip().strip(quotestr)
    wrapped = wrap_text(clean, width=text_width - len(indent) - 2)
    quoted = [quotestr + l + quotestr for l in wrapped]
    indented = [indent + l for l in quoted]
    return indented


def string_unwrap(lines: List[str]) -> Optional[List[str]]:
    startpos, quotestr = identify_start_and_quote(lines[0])
    if quotestr is None:
        return None

    indent = " " * startpos
    clean = [l.strip().strip(quotestr) for l in lines]
    joined = "".join(clean)
    quoted = quotestr + joined + quotestr
    indented = indent + quoted
    return [indented]


def identify_start_and_quote(line) -> Tuple[Optional[int], Optional[str]]:
    double_start = None
    single_start = None
    quote_str = None

    try:
        double_start = line.index('"')
    except ValueError:
        pass

    try:
        single_start = line.index("'")
    except ValueError:
        pass

    if double_start is None and single_start is None:
        print(
            "[StringWrap] ERROR: couldn't identify quote character.",
            file=sys.stderr,
        )
        return None, None
    elif single_start is None:
        start_pos = double_start
        quote_str = '"'
    elif double_start is None:
        start_pos = single_start
        quote_str = "'"
    else:
        start_pos = (
            double_start if double_start < single_start else single_start
        )
        quote_str = '"' if double_start < single_start else "'"

    if start_pos == 0:
        return start_pos, quote_str

    preceding = set(line[:start_pos])
    if not (len(preceding) == 1 and preceding.pop() == " "):
        print(
            "[StringWrap] ERROR: String not on its own line.",
            file=sys.stderr,
        )
        return None, None

    return start_pos, quote_str
