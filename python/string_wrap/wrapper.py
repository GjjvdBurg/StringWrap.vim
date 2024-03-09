#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrap a long Python string in Vim.

Author: Gertjan van den Burg
Date: 2022-06-12
License: See LICENSE file

"""

import ast
import sys

from dataclasses import dataclass
from enum import Enum

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

if sys.version_info >= (3, 9):
    from ast import unparse as ast_unparse
else:
    from .ast_backports import unparse as ast_unparse


class UnsupportASTLiteralError(ValueError):
    pass


class TokenizeError(Exception):
    def __init__(self, source: str, reason: str) -> None:
        self._source = source
        self._reason = reason

    def __repr__(self) -> str:
        return (
            f"TokenizeError(source={self._source!r}, reason={self._reason!r})"
        )


class Kind(Enum):
    REGULAR = 0
    FORMAT = 1


@dataclass
class Token:
    kind: Kind
    value: str
    trailing_space: bool


@dataclass
class InputInfo:
    lines: List[str]
    start_pos: int
    quote_str: str
    is_fstring: bool
    trailing_comma: bool
    indent_len: int


def tokenize(source: str) -> List[Token]:
    """Tokenize the source string into Tokens that we can recombine"""
    module = ast.parse(source)
    body = module.body
    if len(body) > 1:
        raise TokenizeError(source, "no body")

    expr = body[0]
    if not hasattr(expr, "value"):
        raise TokenizeError(source, "no value")
    value = expr.value
    if isinstance(value, ast.JoinedStr):
        string_parts = value.values
    elif isinstance(value, ast.Constant):
        string_parts = [value]
    else:
        raise TokenizeError(source, "unsupported expression value")

    tokens = []
    for part in string_parts:
        if isinstance(part, ast.Constant):
            words = part.value.split(" ")
            if not words[-1]:
                words = words[:-1]
                last_trailing = True
            else:
                last_trailing = False

            for word in words[:-1]:
                # Attach space to last format token if possible, to avoid 
                # moving the space to the next sentence
                if not word and tokens[-1].kind == Kind.FORMAT:
                    tokens[-1].trailing_space = True
                    continue
                token = Token(Kind.REGULAR, word, trailing_space=True)
                tokens.append(token)

            tokens.append(
                Token(Kind.REGULAR, words[-1], trailing_space=last_trailing)
            )
        else:
            tokens.append(
                Token(Kind.FORMAT, ast_unparse(part), trailing_space=False)
            )
    return tokens


def make_sentences(source: str, width: int) -> Tuple[List[str], List[Kind]]:
    tokens = tokenize(source)

    sentences = []
    sentence_kinds = []
    sentence = ""
    sentence_kind = Kind.REGULAR

    for token in tokens:
        # Maximum width is reduced by one if the sentence is or could become an
        # f-string.
        max_width = (
            width - 1
            if (token.kind == Kind.FORMAT or sentence_kind == Kind.FORMAT)
            else width
        )
        combined_token = token.value + " " * token.trailing_space
        combined_width = len(combined_token)

        # If we'll overflow, create a new sentence
        if len(sentence) + combined_width > max_width:
            sentences.append(sentence)
            sentence_kinds.append(sentence_kind)

            sentence = ""
            sentence_kind = Kind.REGULAR

        sentence += combined_token
        sentence_kind = (
            Kind.FORMAT if token.kind == Kind.FORMAT else sentence_kind
        )

    # Don't forget to store the last sentence info
    if sentence:
        sentences.append(sentence)
        sentence_kinds.append(sentence_kind)

    return sentences, sentence_kinds


def wrap_text(
    source: str, width: int, table: Dict[int, str]
) -> Tuple[List[str], List[int]]:
    """Wrap text to multiple lines with specified maximum width

    This function wraps text in such a way that sentences always end with a
    space, which I prefer to the alternative of sentences occassionally
    starting with a space (which would happen when using textwrap.wrap).
    """
    # Source should be everything including the 'f' part and the quotes. It
    # should be one line.
    sentences, sentence_kinds = make_sentences(source, width)

    clean_sentences = untranslate_source(sentences, table)

    f_indices = [i for i, k in enumerate(sentence_kinds) if k == Kind.FORMAT]

    return clean_sentences, f_indices


def translate_source(source: str) -> Tuple[str, Dict[int, str]]:
    new_source = []
    translations = {
        "\a": "AA",
        "\b": "BB",
        "\f": "FF",
        "\n": "NN",
        "\r": "RR",
        "\t": "TT",
        # "\u": "UU", # TODO
        "\v": "VV",
        # "\x": "XX", # TODO
    }
    table: Dict[int, str] = {}
    is_fstring = source.startswith("f")
    quotechar = source[-1]
    line = source.lstrip("f")[1:-1]
    if is_fstring:
        new_source = ["f"]
    new_source.append(quotechar)

    for i, s in enumerate(line):
        if s in translations:
            c = translations[s]
            table[i] = s
        else:
            c = s
        new_source.append(c)

    new_source.append(quotechar)
    output = "".join(new_source)
    return output, table


def untranslate_source(lines: List[str], table: Dict[int, str]) -> List[str]:
    i = 0
    new_lines = []
    for line in lines:
        new_line = ""
        skip_next = False
        for s in line:
            if i in table:
                c = table[i]
                i += 1
                skip_next = True
                new_line += c
            else:
                if skip_next:
                    skip_next = False
                    continue
                c = s
                i += 1
                new_line += c
        new_lines.append(new_line)
    return new_lines


def string_wrap(line: str, text_width: int) -> Optional[List[str]]:
    # Figure out which quote mark the line is using
    info = identify_start_and_quote([line])
    if info is None or info.quote_str is None:
        return None

    indent = " " * info.indent_len

    source = line.rstrip(",").strip()
    tmp_source, table = translate_source(source)
    wrapped, f_indices = wrap_text(
        tmp_source,
        width=text_width - len(indent) - 2,
        table=table,
    )
    quoted = [info.quote_str + line + info.quote_str for line in wrapped]
    fstringed = []
    for i, line in enumerate(quoted):
        if i in f_indices:
            fstringed.append("f" + line)
        else:
            fstringed.append(line)
    indented = [indent + line for line in fstringed]
    if info.trailing_comma:
        indented[-1] += ","
    return indented


def string_unwrap(lines: List[str]) -> Optional[List[str]]:
    info = identify_start_and_quote(lines)
    # startpos, quotestr, is_fstring = identify_start_and_quote(lines[0])
    if info is None or info.quote_str is None:
        return None

    indent = " " * info.indent_len

    clean = [
        line.strip().lstrip("f").rstrip(",").strip(info.quote_str)
        for line in lines
    ]
    joined = "".join(clean)
    quoted = info.quote_str + joined + info.quote_str
    if info.is_fstring:
        quoted = "f" + quoted
    indented = indent + quoted
    if info.trailing_comma:
        indented += ","
    return [indented]


def string_rewrap(lines: List[str], text_width: int) -> Optional[List[str]]:
    unwrapped = string_unwrap(lines)
    if unwrapped is None:
        return None

    theline = unwrapped[0]
    return string_wrap(theline, text_width)


def identify_start_and_quote(lines: List[str]) -> Optional[InputInfo]:
    double_start = None
    single_start = None
    quote_str = None

    first_line = lines[0]
    last_line = lines[-1]

    trailing_comma = last_line.endswith(",")

    try:
        double_start = first_line.index('"')
    except ValueError:
        pass

    try:
        single_start = first_line.index("'")
    except ValueError:
        pass

    if double_start is None and single_start is None:
        print(
            "[StringWrap] ERROR: couldn't identify quote character.",
            file=sys.stderr,
        )
        return None
    elif single_start is None:
        assert double_start is not None
        start_pos = double_start
        quote_str = '"'
    elif double_start is None:
        assert single_start is not None
        start_pos = single_start
        quote_str = "'"
    else:
        start_pos = (
            double_start if double_start < single_start else single_start
        )
        quote_str = '"' if double_start < single_start else "'"

    if start_pos == 0:
        return InputInfo(
            lines=lines,
            start_pos=start_pos,
            quote_str=quote_str,
            is_fstring=False,
            trailing_comma=trailing_comma,
            indent_len=0,
        )

    # We get the indent length from the first line. If the first-line is an
    # f-string, the indent_len is one fewer than the position of the first
    # quote character, otherwise it is equal to that position.
    preceding = set(first_line[:start_pos])
    if preceding == set([" "]):
        info = InputInfo(
            lines=lines,
            start_pos=start_pos,
            quote_str=quote_str,
            is_fstring=False,
            trailing_comma=trailing_comma,
            indent_len=start_pos,
        )
    elif preceding == set([" ", "f"]):
        info = InputInfo(
            lines=lines,
            start_pos=start_pos,
            quote_str=quote_str,
            is_fstring=True,
            trailing_comma=trailing_comma,
            indent_len=start_pos - 1,
        )
    else:
        print(
            "[StringWrap] ERROR: String not on its own line. "
            f"Preceding: {first_line[:start_pos]}",
            file=sys.stderr,
        )
        return None

    for line in lines:
        if line.lstrip().startswith("f"):
            info.is_fstring = True
    return info
