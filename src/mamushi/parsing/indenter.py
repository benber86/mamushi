"Provides Indentation services for languages with indentation similar to Python"

from abc import ABC, abstractmethod
from typing import List, Iterator, Tuple
from mamushi.parsing.tokens import (
    OPENING_BRACKETS,
    CLOSING_BRACKETS,
    NEWLINE,
    INDENT,
    DEDENT,
)

from lark.exceptions import LarkError
from lark.lark import PostLex
from lark.lexer import Token


class DedentError(LarkError):
    pass


class Indenter(PostLex, ABC):
    paren_level: int
    indent_level: List[int]
    processed_newlines: List[Token]

    def __init__(self) -> None:
        self.paren_level = 0
        self.indent_level = [0]
        self.processed_newlines = []
        assert self.tab_len > 0

    @staticmethod
    def create_dent_on_next_line(
        type: str, value: str, newline: Token, lines: int
    ):
        return Token(
            type,
            value,
            newline.start_pos,
            newline.end_line + lines,
            0,
            newline.end_line + lines,
            0,
            0,
        )

    def split_into_dedents(self, line: str) -> List[str]:
        res = []
        prev_tab_len = self.indent_level[-1]
        for i, element in enumerate(line.split("\n")[1:]):
            cur_tab_len = (
                element.count(" ") + element.count("\t") * self.tab_len
            )
            if cur_tab_len < prev_tab_len or i == 0:
                res.append("\n" + element)
                prev_tab_len = cur_tab_len
            else:
                res[-1] += "\n" + element
        return res

    @staticmethod
    def split_into_indents(line: str) -> Tuple[str, str]:
        if "#" not in line:
            return "", line
        nl, ind = line.split("#", 1)
        return nl, "#" + ind

    def handle_NL(self, token: Token) -> Iterator[Token]:
        if self.paren_level > 0:
            return

        self.processed_newlines.append(token)
        indent_str = token.rsplit("\n", 1)[1]  # Tabs and spaces
        indent = indent_str.count(" ") + indent_str.count("\t") * self.tab_len

        if indent > self.indent_level[-1]:
            # nl, ind = self.split_into_indents(token.value)
            yield Token.new_borrow_pos(self.NL_type, "", token)
            yield self.create_dent_on_next_line(
                self.INDENT_type, token.value, token, 1
            )
            self.indent_level.append(indent)
        elif indent < self.indent_level[-1]:
            dedent_captions = self.split_into_dedents(token)
            index = 0
            yield Token.new_borrow_pos(self.NL_type, "", token)
            while indent < self.indent_level[-1]:
                self.indent_level.pop()
                caption = (
                    dedent_captions[index]
                    if index < len(dedent_captions)
                    else ""
                )
                yield self.create_dent_on_next_line(
                    self.DEDENT_type, caption, token, 1
                )
                index += 1

            if indent != self.indent_level[-1]:
                raise DedentError(
                    "Unexpected dedent to column %s. Expected dedent to %s"
                    % (indent, self.indent_level[-1])
                )
        else:
            yield token

    def _process(self, stream):
        for token in stream:
            if token.type == self.NL_type:
                yield from self.handle_NL(token)
            else:
                yield token

            if token.type in self.OPEN_PAREN_types:
                self.paren_level += 1
            elif token.type in self.CLOSE_PAREN_types:
                self.paren_level -= 1
                assert self.paren_level >= 0

        while len(self.indent_level) > 1:
            self.indent_level.pop()
            yield Token(self.DEDENT_type, "")

        assert self.indent_level == [0], self.indent_level

    def process(self, stream):
        self.paren_level = 0
        self.indent_level = [0]
        self.processed_newlines = []
        return self._process(stream)

    # XXX Hack for ContextualLexer. Maybe there's a more elegant solution?
    @property
    def always_accept(self):
        return (self.NL_type,)

    @property
    @abstractmethod
    def NL_type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def OPEN_PAREN_types(self) -> List[str]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def CLOSE_PAREN_types(self) -> List[str]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def INDENT_type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def DEDENT_type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def tab_len(self) -> int:
        raise NotImplementedError()


class PythonIndenter(Indenter):
    NL_type = NEWLINE
    OPEN_PAREN_types = list(OPENING_BRACKETS)
    CLOSE_PAREN_types = list(CLOSING_BRACKETS)
    INDENT_type = INDENT
    DEDENT_type = DEDENT
    tab_len = 4