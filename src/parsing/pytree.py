# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""
Python parse tree definitions.

This is a very concrete parse tree; we need to keep every token and
even the comments and whitespace between tokens.

There's also a pattern matching implementation here.
"""

# mypy: allow-untyped-defs, allow-incomplete-defs

from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Text,
    Tuple,
    TypeVar,
    Union,
    Set,
    Iterable,
)
from lark import Tree, Token

__author__ = "Guido van Rossum <guido@python.org>"

import sys
from io import StringIO

HUGE: int = 0x7FFFFFFF  # maximum repeat count, default max

_type_reprs: Dict[int, Union[Text, int]] = {}


_P = TypeVar("_P", bound="Base")

NL = Union["Node", "Leaf"]
Context = Tuple[Text, Tuple[int, int]]
RawNode = Tuple[int, Optional[Text], Optional[Context], Optional[List[NL]]]


class Base(object):

    """
    Abstract base class for Node and Leaf.

    This provides some default functionality and boilerplate using the
    template pattern.

    A node may be a subnode of at most one parent.
    """

    # Default values for instance variables
    type: str
    parent: Optional["Node"] = None  # Parent node pointer, or None
    children: List[NL]  # List of subnodes
    was_changed: bool = False
    was_checked: bool = False

    def __new__(cls, *args, **kwds):
        """Constructor that prevents Base from being instantiated."""
        assert cls is not Base, "Cannot instantiate Base"
        return object.__new__(cls)

    def __eq__(self, other: Any) -> bool:
        """
        Compare two nodes for equality.

        This calls the method _eq().
        """
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self._eq(other)

    @property
    def prefix(self) -> Text:
        raise NotImplementedError

    def _eq(self: _P, other: _P) -> bool:
        """
        Compare two nodes for equality.

        This is called by __eq__ and __ne__.  It is only called if the two nodes
        have the same type.  This must be implemented by the concrete subclass.
        Nodes should be considered equal if they have the same structure,
        ignoring the prefix string and other context information.
        """
        raise NotImplementedError

    def __deepcopy__(self: _P, memo: Any) -> _P:
        return self.clone()

    def clone(self: _P) -> _P:
        """
        Return a cloned (deep) copy of self.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    def post_order(self) -> Iterator[NL]:
        """
        Return a post-order iterator for the tree.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    def pre_order(self) -> Iterator[NL]:
        """
        Return a pre-order iterator for the tree.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    def replace(self, new: Union[NL, List[NL]]) -> None:
        """Replace this node with a new one in the parent."""
        assert self.parent is not None, str(self)
        assert new is not None
        if not isinstance(new, list):
            new = [new]
        l_children = []
        found = False
        for ch in self.parent.children:
            if ch is self:
                assert not found, (self.parent.children, self, new)
                if new is not None:
                    l_children.extend(new)
                found = True
            else:
                l_children.append(ch)
        assert found, (self.children, self, new)
        self.parent.children = l_children
        self.parent.changed()
        self.parent.invalidate_sibling_maps()
        for x in new:
            x.parent = self.parent
        self.parent = None

    def get_lineno(self) -> Optional[int]:
        """Return the line number which generated the invocant node."""
        node = self
        while not isinstance(node, Leaf):
            if not node.children:
                return None
            node = node.children[0]
        return node.lineno

    def changed(self) -> None:
        if self.was_changed:
            return
        if self.parent:
            self.parent.changed()
        self.was_changed = True

    def remove(self) -> Optional[int]:
        """
        Remove the node from the tree. Returns the position of the node in its
        parent's children before it was removed.
        """
        if self.parent:
            for i, node in enumerate(self.parent.children):
                if node is self:
                    del self.parent.children[i]
                    self.parent.changed()
                    self.parent.invalidate_sibling_maps()
                    self.parent = None
                    return i
        return None

    @property
    def next_sibling(self) -> Optional[NL]:
        """
        The node immediately following the invocant in their parent's children
        list. If the invocant does not have a next sibling, it is None
        """
        if self.parent is None:
            return None

        if self.parent.next_sibling_map is None:
            self.parent.update_sibling_maps()
        assert self.parent.next_sibling_map is not None
        return self.parent.next_sibling_map[id(self)]

    @property
    def prev_sibling(self) -> Optional[NL]:
        """
        The node immediately preceding the invocant in their parent's children
        list. If the invocant does not have a previous sibling, it is None.
        """
        if self.parent is None:
            return None

        if self.parent.prev_sibling_map is None:
            self.parent.update_sibling_maps()
        assert self.parent.prev_sibling_map is not None
        return self.parent.prev_sibling_map[id(self)]

    def leaves(self) -> Iterator["Leaf"]:
        for child in self.children:
            yield from child.leaves()

    def depth(self) -> int:
        if self.parent is None:
            return 0
        return 1 + self.parent.depth()

    def get_suffix(self) -> Text:
        """
        Return the string immediately following the invocant node. This is
        effectively equivalent to node.next_sibling.prefix
        """
        next_sib = self.next_sibling
        if next_sib is None:
            return ""
        prefix = next_sib.prefix
        return prefix


class Node(Base):

    """Concrete implementation for interior nodes."""

    fixers_applied: Optional[List[Any]]
    used_names: Optional[Set[Text]]

    def __init__(
        self,
        type: str,
        children: List[NL],
        context: Optional[Any] = None,
        prefix: Optional[Text] = None,
        fixers_applied: Optional[List[Any]] = None,
    ) -> None:
        """
        Initializer.

        Takes a type constant, a sequence of
        child nodes, and an optional context keyword argument.

        As a side effect, the parent pointers of the children are updated.
        """
        self.type = type
        self.children = list(children)
        for ch in self.children:
            assert ch.parent is None, repr(ch)
            ch.parent = self
        self.invalidate_sibling_maps()
        if prefix is not None:
            self.prefix = prefix
        if fixers_applied:
            self.fixers_applied = fixers_applied[:]
        else:
            self.fixers_applied = None

    def __repr__(self) -> Text:
        """Return a canonical string representation."""
        assert self.type is not None
        return "%s(%s, %r)" % (
            self.__class__.__name__,
            self.type,
            self.children,
        )

    def __str__(self) -> Text:
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        return "".join(map(str, self.children))

    def _eq(self, other: Base) -> bool:
        """Compare two nodes for equality."""
        return (self.type, self.children) == (other.type, other.children)

    def clone(self) -> "Node":
        assert self.type is not None
        """Return a cloned (deep) copy of self."""
        return Node(
            self.type,
            [ch.clone() for ch in self.children],
            fixers_applied=self.fixers_applied,
        )

    def post_order(self) -> Iterator[NL]:
        """Return a post-order iterator for the tree."""
        for child in self.children:
            yield from child.post_order()
        yield self

    def pre_order(self) -> Iterator[NL]:
        """Return a pre-order iterator for the tree."""
        yield self
        for child in self.children:
            yield from child.pre_order()

    @property
    def prefix(self) -> Text:
        """
        The whitespace and comments preceding this node in the input.
        """
        if not self.children:
            return ""
        return self.children[0].prefix

    @prefix.setter
    def prefix(self, prefix: Text) -> None:
        if self.children:
            self.children[0].prefix = prefix

    def set_child(self, i: int, child: NL) -> None:
        """
        Equivalent to 'node.children[i] = child'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children[i].parent = None
        self.children[i] = child
        self.changed()
        self.invalidate_sibling_maps()

    def insert_child(self, i: int, child: NL) -> None:
        """
        Equivalent to 'node.children.insert(i, child)'. This method also sets
        the child's parent attribute appropriately.
        """
        child.parent = self
        self.children.insert(i, child)
        self.changed()
        self.invalidate_sibling_maps()

    def append_child(self, child: NL) -> None:
        """
        Equivalent to 'node.children.append(child)'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children.append(child)
        self.changed()
        self.invalidate_sibling_maps()

    def invalidate_sibling_maps(self) -> None:
        self.prev_sibling_map: Optional[Dict[int, Optional[NL]]] = None
        self.next_sibling_map: Optional[Dict[int, Optional[NL]]] = None

    def update_sibling_maps(self) -> None:
        _prev: Dict[int, Optional[NL]] = {}
        _next: Dict[int, Optional[NL]] = {}
        self.prev_sibling_map = _prev
        self.next_sibling_map = _next
        previous: Optional[NL] = None
        for current in self.children:
            _prev[id(current)] = previous
            _next[id(previous)] = current
            previous = current
        _next[id(current)] = None


class Leaf(Base):

    """Concrete implementation for leaf nodes."""

    # Default values for instance variables
    value: Text
    fixers_applied: List[Any]
    bracket_depth: int
    # Changed later in brackets.py
    opening_bracket: Optional["Leaf"] = None
    used_names: Optional[Set[Text]]
    _prefix = ""  # Whitespace and comments preceding this token in the input
    lineno: int = 0  # Line where this token starts in the input
    column: int = 0  # Column where this token starts in the input

    def __init__(
        self,
        type: str,
        value: Text,
        context: Optional[Context] = None,
        prefix: Optional[Text] = None,
        fixers_applied: List[Any] = [],
        opening_bracket: Optional["Leaf"] = None,
    ) -> None:
        """
        Initializer.

        Takes a type constant, a string value, and an
        optional context keyword argument.
        """

        if context is not None:
            self._prefix, (self.lineno, self.column) = context
        self.type = type
        self.value = value
        if prefix is not None:
            self._prefix = prefix
        self.fixers_applied: Optional[List[Any]] = fixers_applied[:]
        self.children = []
        self.opening_bracket = opening_bracket

    def __repr__(self) -> str:
        """Return a canonical string representation."""

        assert self.type is not None
        return "%s(%s, %r)" % (
            self.__class__.__name__,
            self.type,
            self.value,
        )

    def __str__(self) -> Text:
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        return self._prefix + str(self.value)

    def _eq(self, other: "Leaf") -> bool:
        """Compare two nodes for equality."""
        return (self.type, self.value) == (other.type, other.value)

    def clone(self) -> "Leaf":
        assert self.type is not None
        """Return a cloned (deep) copy of self."""
        return Leaf(
            self.type,
            self.value,
            (self.prefix, (self.lineno, self.column)),
            fixers_applied=self.fixers_applied,
        )

    def leaves(self) -> Iterator["Leaf"]:
        yield self

    def post_order(self) -> Iterator["Leaf"]:
        """Return a post-order iterator for the tree."""
        yield self

    def pre_order(self) -> Iterator["Leaf"]:
        """Return a pre-order iterator for the tree."""
        yield self

    @property
    def prefix(self) -> Text:
        """
        The whitespace and comments preceding this token in the input.
        """
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: Text) -> None:
        self.changed()
        self._prefix = prefix
