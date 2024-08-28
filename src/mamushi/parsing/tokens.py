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
BITNOT = "invert"
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
FLOORDIV = "floordiv"
POW = "pow"
SHL = "shl"
SHR = "shr"
RIGHTSHIFT = "_SHR"
LEFTSHIFT = "_SHL"
DOUBLESTAR = "_POW"
SLASH = "SLASH"
STAR = "WILDCARD"
PERCENT = "PERCENT"
OPERATIONS = {ADD, SUB, MUL, MOD, DIV, FLOORDIV}
EQUAL = "EQUAL"
ASSIGN = "assign"
AUG_ASSIGN = "aug_assign"
MULTIPLE_ASSIGN = "multiple_assign"
ASSIGN_OPERATORS = [
    ADD,
    SUB,
    DIV,
    FLOORDIV,
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

BOOL_OR = "_OR"
BOOL_AND = "_AND"
BOOL_NOT = "_NOT"
LOGIC_OPERATORS = {"or", "and"}

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
KWARG = "kwarg"
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
DECLARATION = "declaration"
CONSTANT_DEF = "constant_def"
BODY = "body"
EVENT_BODY = "event_body"
ENUM_BODY = "enum_body"
MODULE = "module"
DEF_SUFFIX = "_def"
RETURN_TYPE = "_RETURN_TYPE"
FUNCTION_SIG = "function_sig"
ARRAY_DEF = "array_def"
DINARRAY_DEF = "dyn_array_def"
CALL = "call"
EXTERNAL_CALL = "external_call"
EMPTY = "empty"
ABI_DECODE = "abi_decode"
ATTRIBUTE = "attribute"
GET_VAR = "get_var"
LOG_STMT = "log_stmt"
SUBSCRIPT = "subscript"
GETTER_SUFIX = "_with_getter"
CONSTANT = "constant"
IMMUTABLE = "immutable"
IMPLEMENTS = "implements"
USES = "uses"
INDEXED_ARGS = "indexed_event_arg"
ATOM = "atom"

COND_EXEC = "cond_exec"
FOR_STMT = "for_stmt"
IF_STMT = "if_stmt"
TERNARY = "ternary"
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

VARIABLE_DEF = "variable_def"
RETURN_STMT = "return_stmt"
PASS_STMT = "pass_stmt"
BREAK_STMT = "break_stmt"
CONTINUE_STMT = "continue_stmt"
INITIALIZES_STMT = "initializes_stmt"
IMPORTED_TYPE = "imported_type"
RAISE = "raise"
RAISE_WITH_REASON = "raise_with_reason"
IMMUTABLE_DEF = "immutable_def"
INTERFACE_DEF = "interface_def"
IMPLEMENTS_DEF = "implements_def"
USES_DEF = "uses_def"
EXPORT = "export"
STRUCT_DEF = "struct_def"
ENUM_DEF = "enum_def"
EVENT_DEF = "event_def"
INDEXED_EVENT_ARG = "indexed_event_arg"
EVENT_MEMBER = "event_member"
ENUM_MEMBER = "enum_member"
STRUCT_MEMBER = "struct_member"

BODIES = {BODY, EVENT_BODY, ENUM_BODY, MODULE, STRUCT_DEF}

SIMPLE_STATEMENTS = {
    VARIABLE_DEF,
    RETURN_STMT,
    PASS_STMT,
    BREAK_STMT,
    CONTINUE_STMT,
    RAISE,
    RAISE_WITH_REASON,
    LOG_STMT,
    INITIALIZES_STMT,
    IMPLEMENTS_DEF,
    USES_DEF,
    EXPORT,
    CONSTANT_DEF,
    IMMUTABLE_DEF,
    INTERFACE_DEF,
    STRUCT_DEF,
    ENUM_DEF,
    EVENT_DEF,
    INDEXED_EVENT_ARG,
    EVENT_MEMBER,
    ENUM_MEMBER,
    STRUCT_MEMBER,
    ASSIGN,
    AUG_ASSIGN,
} | ASSERTS

ASSIGNMENTS_SIGNS = {"=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="}
