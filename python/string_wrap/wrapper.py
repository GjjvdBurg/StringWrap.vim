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
    startpos = None
    quotestr = None
    try:
        startpos = line.index('"')
        quotestr = '"'
    except ValueError:
        pass

    if startpos is None:
        try:
            startpos = line.index("'")
            quotestr = "'"
        except ValueError:
            pass

    if startpos is None:
        print(
            "[StringWrap] ERROR: couldn't identify quote character.",
            file=sys.stderr,
        )
        return None, None

    preceding = set(line[:startpos])
    if not (len(preceding) == 1 and preceding.pop() == " "):
        print(
            f"[StringWrap] ERROR: String not on its own line (preceding chars: {preceding}).",
            file=sys.stderr,
        )
        return None, None

    return startpos, quotestr
