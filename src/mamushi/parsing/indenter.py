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
        endline = newline.end_line if newline.end_line else 0
        return Token(
            type,
            value,
            newline.start_pos,
            endline + lines,
            0,
            endline + lines,
            0,
            0,
        )

    def split_into_dedents(self, line: str) -> List[str]:
        res = []
        prev_tab_len = self.indent_level[-1]
        for i, element in enumerate(line.split("\n")[1:]):
            pre_comment = element.split("#")[0]
            cur_tab_len = (
                pre_comment.count(" ") + pre_comment.count("\t") * self.tab_len
            )
            if (cur_tab_len < prev_tab_len) or i == 0:
                res.append("\n" + element)
                if len(element.strip()) > 0:
                    prev_tab_len = cur_tab_len
                else:
                    prev_tab_len = prev_tab_len - self.tab_len
                    # the newline will get added to a newline token and is gone
                    # need to add it back as prefix to next comment
                    res[-1] += "\n"
            else:
                res[-1] += "\n" + element
        # if the final element is whitespace, merge it with penultimate
        if not res[-1].strip() and len(res) > 1:
            res[-2] += res[-1]
            res.pop()

        return res

    @staticmethod
    def split_into_indents(line: str) -> Tuple[str, str]:
        if "#" not in line:
            return "", line
        nl, ind = line.split("#", 1)
        return nl, "#" + ind

    def _get_indent(self, token):
        indent_str = token.rsplit("\n", 1)[1]  # Tabs and spaces
        return indent_str.count(" ") + indent_str.count("\t") * self.tab_len

    def handle_NL(self, token: Token) -> Iterator[Token]:
        if self.paren_level > 0:
            return

        self.processed_newlines.append(token)  # Tabs and spaces
        indent = self._get_indent(token)

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
            newline = False  # whether we've created the leading newline or not
            newline_caption = ""
            while indent < self.indent_level[-1]:
                caption = (
                    dedent_captions[index]
                    if index < len(dedent_captions)
                    else ""
                )
                index += 1

                if not newline:
                    # as long as we haven't hit the dedent, we add the comments
                    # to the newline
                    cmt_indent = (
                        self._get_indent(caption.split("#")[0])
                        if "#" in caption
                        else indent
                    )
                    if cmt_indent >= self.indent_level[-1]:
                        newline_caption += caption
                        continue

                    yield Token.new_borrow_pos(
                        self.NL_type, newline_caption.rstrip(), token
                    )
                    newline = True
                self.indent_level.pop()
                yield self.create_dent_on_next_line(
                    self.DEDENT_type, caption, token, 1
                )

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
