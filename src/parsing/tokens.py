# Punctuation
LSQB = "LSQB"
RSQB = "RSQB"
LPAR = "LPAR"
RPAR = "RPAR"
COMMA = "COMMA"
DOT = "DOT"
COLON = "COLON"
NAME = "NAME"
RBRACE = "RBRACE"
LBRACE = "LBRACE"
AT = "AT"
BRACKET_MAP = {LPAR: RPAR, LSQB: RSQB, LBRACE: RBRACE}
OPENING_BRACKETS = set(BRACKET_MAP.keys())
CLOSING_BRACKETS = set(BRACKET_MAP.values())

# Formatting
INDENT = "_INDENT"
DEDENT = "_DEDENT"
NEWLINE = "_NEWLINE"
WHITESPACE = [INDENT, DEDENT, NEWLINE]

# Operations
BITAND = "_BITAND"
BITOR = "_BITOR"
BITXOR = "_BITXOR"
PLUS = "PLUS"
MINUS = "MINUS"
UNARY = {"usub", "uadd", "invert"}
ADD = "add"
SUB = "sub"
MUL = "mul"
MOD = "mod"
DIV = "div"
OPERATIONS = {ADD, SUB, MUL, MOD, DIV}
EQUAL = "EQUAL"
ASSIGN_OPERATORS = [ADD, SUB, DIV, MUL, MOD, BITOR, BITAND, BITXOR]
# 4 sets below still need adaptation to vyper
MATH_OPERATORS = {
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "VBAR",
    "AMPER",
    "PERCENT",
    "CIRCUMFLEX",
    "LEFTSHIFT",
    "RIGHTSHIFT",
    "DOUBLESTAR",
    "DOUBLESLASH",
}

LOGIC_OPERATORS = {"_AND", "_OR"}

COMPARATORS = {
    "LESS",
    "GREATER",
    "EQEQUAL",
    "NOTEQUAL",
    "LESSEQUAL",
    "GREATEREQUAL",
}

PRODUCT = "_PRODUCT"


# Imports
IMPORT_NAME = "_IMPORT"
IMPORT_FROM = "_FROM"
IMPORT = "import"

# Statements
PARAMETERS = "parameters"
ARGUMENTS = "arguments"
DECORATOR = "decorator"
FLOW_CONTROL = {"return", "break", "continue"}
INTERFACE_FUNCTION = "interface_function"
DECLARATIONS = {
    "_FUNC_DECL",
    "_EVENT_DECL",
    "_ENUM_DECL",
    "_STRUCT_DECL",
    "_INTERFACE_DECL",
}
BODY = "body"
MODULE = "module"
DEF_SUFFIX = "_def"
RETURN_TYPE = "_RETURN_TYPE"
FUNCTION_SIG = "function_sig"
CALL = "call"
EMPTY = "empty"
GET_ATTR = "get_attr"
LOG_STMT = "log_stmt"
GET_ITEM = "get_item"
VAR_GETTER = "variable_with_getter"
INDEXED_ARGS = "indexed_event_arg"

# Needs cleanup
COMMENT = "COMMENT"
STRING = "STRING"
STANDALONE_COMMENT = "STANDALONE_COMMENT"
