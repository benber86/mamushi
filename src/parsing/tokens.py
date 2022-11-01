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
DEC_NUMBER = "DEC_NUMBER"
HEX_NUMBER = "HEX_NUMBER"
BIN_NUMBER = "BIN_NUMBER"
OCT_NUMBER = "OCT_NUMBER"
NUMBERS = {DEC_NUMBER, HEX_NUMBER, BIN_NUMBER, OCT_NUMBER}
AT = "AT"
BRACKET_MAP = {LPAR: RPAR, LSQB: RSQB, LBRACE: RBRACE}
OPENING_BRACKETS = set(BRACKET_MAP.keys())
CLOSING_BRACKETS = set(BRACKET_MAP.values())
BRACKETS = OPENING_BRACKETS | CLOSING_BRACKETS

# Formatting
INDENT = "_INDENT"
DEDENT = "_DEDENT"
NEWLINE = "_NEWLINE"
WHITESPACE = [INDENT, DEDENT, NEWLINE]

# Operations
AMPERSAND = "_BITAND"
VBAR = "_BITOR"
CARET = "_BITXOR"
BITAND = "bitand"
BITOR = "bitor"
BITXOR = "bitxor"
PLUS = "PLUS"
MINUS = "MINUS"
PRODUCT = "_PRODUCT"
TILDE = "TILDE"
UNARY = {"usub", "uadd", "invert"}
ADD = "add"
SUB = "sub"
MUL = "mul"
MOD = "mod"
DIV = "div"
POW = "pow"
SHL = "shl"
SHR = "shr"
RIGHTSHIFT = "_SHR"
LEFTSHIFT = "_SHL"
DOUBLESTAR = "_POW"
SLASH = "SLASH"
STAR = "WILDCARD"
PERCENT = "PERCENT"
OPERATIONS = {ADD, SUB, MUL, MOD, DIV}
EQUAL = "EQUAL"
AUG_ASSIGN = "aug_assign"
MULTIPLE_ASSIGN = "multiple_assign"
ASSIGN_OPERATORS = [
    ADD,
    SUB,
    DIV,
    MUL,
    MOD,
    POW,
    BITOR,
    BITXOR,
    BITAND,
    SHR,
    SHL,
]
MATH_OPERATORS = {
    PLUS,
    MINUS,
    STAR,
    SLASH,
    VBAR,
    AMPERSAND,
    CARET,
    PERCENT,
    LEFTSHIFT,
    RIGHTSHIFT,
    DOUBLESTAR,
}

LOGIC_OPERATORS = {"_AND", "_OR"}

COMPARATORS = {
    "LESSTHAN",
    "MORETHAN",
    "_EQ",
    "_NE",
    "_LE",
    "_GE",
}

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
EVENT_BODY = "event_body"
ENUM_BODY = "enum_body"
MODULE = "module"
BODIES = {BODY, EVENT_BODY, ENUM_BODY, MODULE}
DEF_SUFFIX = "_def"
RETURN_TYPE = "_RETURN_TYPE"
FUNCTION_SIG = "function_sig"
ARRAY_DEF = "array_def"
DINARRAY_DEF = "dyn_array_def"
CALL = "call"
EMPTY = "empty"
GET_ATTR = "get_attr"
GET_VAR = "get_var"
LOG_STMT = "log_stmt"
GET_ITEM = "get_item"
GETTER_SUFIX = "_with_getter"
CONSTANT = "constant"
IMMUTABLE = "immutable"
INDEXED_ARGS = "indexed_event_arg"
ATOM = "atom"

COND_EXEC = "cond_exec"
FOR_STMT = "for_stmt"
IF_STMT = "if_stmt"
FOR = "FOR"
IF = "IF"
IN = "_IN"
ELSE = "ELSE"
ELIF = "ELIF"

PRAGMA = "PRAGMA"
COMMENT = "COMMENT"
STRING = "STRING"
DOCSTRING = "DOCSTRING"
STANDALONE_COMMENT = "STANDALONE_COMMENT"

ASSERT = "assert"
ASSERT_TOKEN = "_ASSERT"
ASSERT_WITH_REASON = "assert_with_reason"
ASSERT_UNREACHABLE = "assert_unreachable"
ASSERTS = {ASSERT, ASSERT_WITH_REASON, ASSERT_UNREACHABLE}
