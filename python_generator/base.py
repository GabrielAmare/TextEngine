class TypeExpressions:
    """
# type_expressions allow */** but ignore them
type_expressions:
    | ','.expression+ ',' '*' expression ',' '**' expression
    | ','.expression+ ',' '*' expression
    | ','.expression+ ',' '**' expression
    | '*' expression ',' '**' expression
    | '*' expression
    | '**' expression
    | ','.expression+
    """


class Statements:
    """
statements: statement+
    """


class Statement:
    """
statement: compound_stmt  | simple_stmt
    """


class StatementNewline:
    """
statement_newline:
    | compound_stmt NEWLINE
    | simple_stmt
    | NEWLINE
    | ENDMARKER
    """


class SimpleStmt:
    """
simple_stmt:
    | small_stmt !';' NEWLINE  # Not needed, there for speedup
    | ';'.small_stmt+ [';'] NEWLINE
    """


class SmallStmt:
    """
# NOTE: assignment MUST precede expression, else parsing a simple assignment
# will throw a SyntaxError.
small_stmt:
    | assignment
    | star_expressions
    | return_stmt
    | import_stmt
    | raise_stmt
    | 'pass'
    | del_stmt
    | yield_stmt
    | assert_stmt
    | 'break'
    | 'continue'
    | global_stmt
    | nonlocal_stmt
    """


class CompoundStmt:
    """
compound_stmt:
    | function_def
    | if_stmt
    | class_def
    | with_stmt
    | for_stmt
    | try_stmt
    | while_stmt
    """


class Assignment:
    """
# NOTE: annotated_rhs may start with 'yield'; yield_expr must start with 'yield'
assignment:
    | NAME ':' expression ['=' annotated_rhs ]
    | ('(' single_target ')'
         | single_subscript_attribute_target) ':' expression ['=' annotated_rhs ]
    | (star_targets '=' )+ (yield_expr | star_expressions) !'=' [TYPE_COMMENT]
    | single_target augassign ~ (yield_expr | star_expressions)
    """


class AugAssign:
    """
augassign:
    | '+='
    | '-='
    | '*='
    | '@='
    | '/='
    | '%='
    | '&='
    | '|='
    | '^='
    | '<<='
    | '>>='
    | '**='
    | '//='
    """


class GlobalStmt:
    """
global_stmt: 'global' ','.NAME+
    """


class NonLocalStmt:
    """
nonlocal_stmt: 'nonlocal' ','.NAME+
    """


class YieldStmt:
    """
yield_stmt: yield_expr
    """


class AssertStmt:
    """
assert_stmt: 'assert' expression [',' expression ]
    """


class DelStmt:
    """
del_stmt:
    | 'del' del_targets &(';' | NEWLINE)
    """


class ImportStmt:
    """
import_stmt: import_name | import_from
    """


class ImportName:
    """
import_name: 'import' dotted_as_names
    """


class ImportFrom:
    """
# note below: the ('.' | '...') is necessary because '...' is tokenized as ELLIPSIS
import_from:
    | 'from' ('.' | '...')* dotted_name 'import' import_from_targets
    | 'from' ('.' | '...')+ 'import' import_from_targets
    """


class ImportFromTargets:
    """
import_from_targets:
    | '(' import_from_as_names [','] ')'
    | import_from_as_names !','
    | '*'
    """


class ImportFromAsNames:
    """
import_from_as_names:
    | ','.import_from_as_name+
    """


class ImportFromAsName:
    """
import_from_as_name:
    | NAME ['as' NAME ]
    """


class DottedAsNames:
    """
dotted_as_names:
    | ','.dotted_as_name+
    """


class DottedAsName:
    """
dotted_as_name:
    | dotted_name ['as' NAME ]
    """


class DottedName:
    """
dotted_name:
    | dotted_name '.' NAME
    | NAME
    """


class IfStmt:
    """
if_stmt:
    | 'if' named_expression ':' block elif_stmt
    | 'if' named_expression ':' block [else_block]
    """


class ElifStmt:
    """
elif_stmt:
    | 'elif' named_expression ':' block elif_stmt
    | 'elif' named_expression ':' block [else_block]
    """


class ElseBlock:
    """
else_block: 'else' ':' block
    """


class WhileStmt:
    """
while_stmt:
    | 'while' named_expression ':' block [else_block]
    """


class ForStmt:
    """
for_stmt:
    | 'for' star_targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block]
    | ASYNC 'for' star_targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block]
    """


class WithStmt:
    """
with_stmt:
    | 'with' '(' ','.with_item+ ','? ')' ':' block
    | 'with' ','.with_item+ ':' [TYPE_COMMENT] block
    | ASYNC 'with' '(' ','.with_item+ ','? ')' ':' block
    | ASYNC 'with' ','.with_item+ ':' [TYPE_COMMENT] block
    """


class WithItem:
    """
with_item:
    | expression 'as' star_target &(',' | ')' | ':')
    | expression
    """


class TryStmt:
    """
try_stmt:
    | 'try' ':' block finally_block
    | 'try' ':' block except_block+ [else_block] [finally_block]
    """


class ExceptBlock:
    """
except_block:
    | 'except' expression ['as' NAME ] ':' block
    | 'except' ':' block
    """


class FinallyBlock:
    """
finally_block: 'finally' ':' block
    """


class ReturnStmt:
    """
return_stmt:
    | 'return' [star_expressions]
    """


class RaiseStmt:
    """
raise_stmt:
    | 'raise' expression ['from' expression ]
    | 'raise'
    """


class FunctionDef:
    """
function_def:
    | decorators function_def_raw
    | function_def_raw
    """


class FunctionDefRaw:
    """
function_def_raw:
    | 'def' NAME '(' [params] ')' ['->' expression ] ':' [func_type_comment] block
    | ASYNC 'def' NAME '(' [params] ')' ['->' expression ] ':' [func_type_comment] block
    """


class FuncTypeComment:
    """
func_type_comment:
    | NEWLINE TYPE_COMMENT &(NEWLINE INDENT)   # Must be followed by indented block
    | TYPE_COMMENT
    """


class Params:
    """
params:
    | parameters
    """


class Parameters:
    """
parameters:
    | slash_no_default param_no_default* param_with_default* [star_etc]
    | slash_with_default param_with_default* [star_etc]
    | param_no_default+ param_with_default* [star_etc]
    | param_with_default+ [star_etc]
    | star_etc
    """


class SlashNoDefault:
    """
slash_no_default:
    | param_no_default+ '/' ','
    | param_no_default+ '/' &')'
    """


class SlashWithDefault:
    """
# Some duplication here because we can't write (',' | &')'),
# which is because we don't support empty alternatives (yet).
#
slash_with_default:
    | param_no_default* param_with_default+ '/' ','
    | param_no_default* param_with_default+ '/' &')'
    """


class StarEtc:
    """
star_etc:
    | '*' param_no_default param_maybe_default* [kwds]
    | '*' ',' param_maybe_default+ [kwds]
    | kwds
    """


class Kwds:
    """
kwds: '**' param_no_default
    """


class ParamNoDefault:
    """
# One parameter.  This *includes* a following comma and type comment.
#
# There are three styles:
# - No default
# - With default
# - Maybe with default
#
# There are two alternative forms of each, to deal with type comments:
# - Ends in a comma followed by an optional type comment
# - No comma, optional type comment, must be followed by close paren
# The latter form is for a final parameter without trailing comma.
#
param_no_default:
    | param ',' TYPE_COMMENT?
    | param TYPE_COMMENT? &')'
    """


class ParamWithDefault:
    """
param_with_default:
    | param default ',' TYPE_COMMENT?
    | param default TYPE_COMMENT? &')'
    """


class ParamMaybeDefault:
    """
param_maybe_default:
    | param default? ',' TYPE_COMMENT?
    | param default? TYPE_COMMENT? &')'
    """


class Param:
    """
param: NAME annotation?
    """


class Annotation:
    """
annotation: ':' expression
    """


class Default:
    """
default: '=' expression
    """


class Decorators:
    """
decorators: ('@' named_expression NEWLINE )+
    """


class ClassDef:
    """
class_def:
    | decorators class_def_raw
    | class_def_raw
    """


class ClassDefRaw:
    """
class_def_raw:
    | 'class' NAME ['(' [arguments] ')' ] ':' block
    """


class Block:
    """
block:
    | NEWLINE INDENT statements DEDENT
    | simple_stmt
    """


class StarExpressions:
    """
star_expressions:
    | star_expression (',' star_expression )+ [',']
    | star_expression ','
    | star_expression
    """


class StarExpression:
    """
star_expression:
    | '*' bitwise_or
    | expression
    """


class StarNamedExpressions:
    """
star_named_expressions: ','.star_named_expression+ [',']
    """


class StarNamedExpression:
    """
star_named_expression:
    | '*' bitwise_or
    | named_expression
    """


class NamedExpression:
    """
named_expression:
    | NAME ':=' ~ expression
    | expression !':='
    """


class AnnotatedRHS:
    """
annotated_rhs: yield_expr | star_expressions
    """


class Expressions:
    """
expressions:
    | expression (',' expression )+ [',']
    | expression ','
    | expression
    """


class Expression:
    """
expression:
    | disjunction 'if' disjunction 'else' expression
    | disjunction
    | lambdef
    """


class LambDef:
    """
lambdef:
    | 'lambda' [lambda_params] ':' expression
    """


class LambdaParams:
    """
lambda_params:
    | lambda_parameters
    """


class LambdaParameters:
    """
# lambda_parameters etc. duplicates parameters but without annotations
# or type comments, and if there's no comma after a parameter, we expect
# a colon, not a close parenthesis.  (For more, see parameters above.)
#
lambda_parameters:
    | lambda_slash_no_default lambda_param_no_default* lambda_param_with_default* [lambda_star_etc]
    | lambda_slash_with_default lambda_param_with_default* [lambda_star_etc]
    | lambda_param_no_default+ lambda_param_with_default* [lambda_star_etc]
    | lambda_param_with_default+ [lambda_star_etc]
    | lambda_star_etc
    """


class LambdaSlashNoDefault:
    """
lambda_slash_no_default:
    | lambda_param_no_default+ '/' ','
    | lambda_param_no_default+ '/' &':'
    """


class LambdaSlashWithDefault:
    """
lambda_slash_with_default:
    | lambda_param_no_default* lambda_param_with_default+ '/' ','
    | lambda_param_no_default* lambda_param_with_default+ '/' &':'
    """


class LambdaStarEtc:
    """
lambda_star_etc:
    | '*' lambda_param_no_default lambda_param_maybe_default* [lambda_kwds]
    | '*' ',' lambda_param_maybe_default+ [lambda_kwds]
    | lambda_kwds
    """


class LambdaKwds:
    """
lambda_kwds: '**' lambda_param_no_default
    """


class LambdaParamNoDefault:
    """
lambda_param_no_default:
    | lambda_param ','
    | lambda_param &':'
    """


class LambdaParamWithDefault:
    """
lambda_param_with_default:
    | lambda_param default ','
    | lambda_param default &':'
    """


class LambdaParamMaybeDefault:
    """
lambda_param_maybe_default:
    | lambda_param default? ','
    | lambda_param default? &':'
    """


class LambdaParam:
    """
lambda_param: NAME
    """


class Disjunction:
    """
disjunction:
    | conjunction ('or' conjunction )+
    | conjunction
    """


class Conjunction:
    """
conjunction:
    | inversion ('and' inversion )+
    | inversion
    """


class Inversion:
    """
inversion:
    | 'not' inversion
    | comparison
    """


class Comparison:
    """
comparison:
    | bitwise_or compare_op_bitwise_or_pair+
    | bitwise_or
    """


class CompareOpBitwiseOrPair:
    """
compare_op_bitwise_or_pair:
    | eq_bitwise_or
    | noteq_bitwise_or
    | lte_bitwise_or
    | lt_bitwise_or
    | gte_bitwise_or
    | gt_bitwise_or
    | notin_bitwise_or
    | in_bitwise_or
    | isnot_bitwise_or
    | is_bitwise_or
    """


class EqBitwiseOr:
    """
eq_bitwise_or: '==' bitwise_or
    """


class NotEqBitwiseOr:
    """
noteq_bitwise_or:
    | ('!=' ) bitwise_or
    """


class LteBitwiseOr:
    """
lte_bitwise_or: '<=' bitwise_or
    """


class LtBitwiseOr:
    """
lt_bitwise_or: '<' bitwise_or
    """


class GteBitwiseOr:
    """
gte_bitwise_or: '>=' bitwise_or
    """


class GtBitwiseOr:
    """
gt_bitwise_or: '>' bitwise_or
    """


class NotInBitwiseOr:
    """
notin_bitwise_or: 'not' 'in' bitwise_or
    """


class InBitwiseOr:
    """
in_bitwise_or: 'in' bitwise_or
    """


class IsNotBitwiseOr:
    """
isnot_bitwise_or: 'is' 'not' bitwise_or
    """


class IsBitwiseOr:
    """
is_bitwise_or: 'is' bitwise_or
    """


class BitwiseOr:
    """
bitwise_or:
    | bitwise_or '|' bitwise_xor
    | bitwise_xor
    """


class BitwiseXor:
    """
bitwise_xor:
    | bitwise_xor '^' bitwise_and
    | bitwise_and
    """


class BitwiseAnd:
    """
bitwise_and:
    | bitwise_and '&' shift_expr
    | shift_expr
    """


class ShiftExpr:
    """
shift_expr:
    | shift_expr '<<' sum
    | shift_expr '>>' sum
    | sum
    """


class Sum:
    """
sum:
    | sum '+' term
    | sum '-' term
    | term
    """


class Term:
    """
term:
    | term '*' factor
    | term '/' factor
    | term '//' factor
    | term '%' factor
    | term '@' factor
    | factor
    """


class Factor:
    """
factor:
    | '+' factor
    | '-' factor
    | '~' factor
    | power
    """


class Power:
    """
power:
    | await_primary '**' factor
    | await_primary
    """


class AwaitPrimary:
    """
await_primary:
    | AWAIT primary
    | primary
    """


class Primary:
    """
primary:
    | invalid_primary  # must be before 'primay genexp' because of invalid_genexp
    | primary '.' NAME
    | primary genexp
    | primary '(' [arguments] ')'
    | primary '[' slices ']'
    | atom
    """


class Slices:
    """
slices:
    | slice !','
    | ','.slice+ [',']
    """


class Slice:
    """
slice:
    | [expression] ':' [expression] [':' [expression] ]
    | expression
    """


class Atom:
    """
atom:
    | NAME
    | 'True'
    | 'False'
    | 'None'
    | '__peg_parser__'
    | strings
    | NUMBER
    | (tuple | group | genexp)
    | (list | listcomp)
    | (dict | set | dictcomp | setcomp)
    | '...'
    """


class Strings:
    """
strings: STRING+
    """


class List:
    """
list:
    | '[' [star_named_expressions] ']'
    """


class ListComp:
    """
listcomp:
    | '[' named_expression ~ for_if_clauses ']'
    """


class Tuple:
    """
tuple:
    | '(' [star_named_expression ',' [star_named_expressions]  ] ')'
    """


class Group:
    """
group:
    | '(' (yield_expr | named_expression) ')'
    """


class GenExp:
    """
genexp:
    | '(' named_expression ~ for_if_clauses ')'
    """


class Set:
    """
set: '{' star_named_expressions '}'
    """


class SetComp:
    """
setcomp:
    | '{' named_expression ~ for_if_clauses '}'
    """


class Dict:
    """
dict:
    | '{' [double_starred_kvpairs] '}'
    """


class DictComp:
    """
dictcomp:
    | '{' kvpair for_if_clauses '}'
    """


class DoubleStarredKVPairs:
    """
double_starred_kvpairs: ','.double_starred_kvpair+ [',']
    """


class DoubleStarredKVPair:
    """
double_starred_kvpair:
    | '**' bitwise_or
    | kvpair
    """


class KVPair:
    """
kvpair: expression ':' expression
    """


class ForIfClauses:
    """
for_if_clauses:
    | for_if_clause+
    """


class ForIfClause:
    """
for_if_clause:
    | ASYNC 'for' star_targets 'in' ~ disjunction ('if' disjunction )*
    | 'for' star_targets 'in' ~ disjunction ('if' disjunction )*
    """


class YieldExpr:
    """
yield_expr:
    | 'yield' 'from' expression
    | 'yield' [star_expressions]
    """


class Arguments:
    """
arguments:
    | args [','] &')'
    """


class Args:
    """
args:
    | ','.(starred_expression | named_expression !'=')+ [',' kwargs ]
    | kwargs
    """


class Kwargs:
    """
kwargs:
    | ','.kwarg_or_starred+ ',' ','.kwarg_or_double_starred+
    | ','.kwarg_or_starred+
    | ','.kwarg_or_double_starred+
    """


class StarredExpression:
    """
starred_expression:
    | '*' expression
    """


class KwargOrStarred:
    """
kwarg_or_starred:
    | NAME '=' expression
    | starred_expression
    """


class KwargsOrDoubleStarred:
    """
kwarg_or_double_starred:
    | NAME '=' expression
    | '**' expression
    """


class StarTargets:
    """
# NOTE: star_targets may contain *bitwise_or, targets may not.
star_targets:
    | star_target !','
    | star_target (',' star_target )* [',']
    """


class StarTargetsListSeq:
    """
star_targets_list_seq: ','.star_target+ [',']
    """


class StarTargetTupleSeq:
    """
star_targets_tuple_seq:
    | star_target (',' star_target )+ [',']
    | star_target ','
    """


class StarTarget:
    """
star_target:
    | '*' (!'*' star_target)
    | target_with_star_atom
    """


class TargetWithStarAtom:
    """
target_with_star_atom:
    | t_primary '.' NAME !t_lookahead
    | t_primary '[' slices ']' !t_lookahead
    | star_atom
    """


class StarAtom:
    """
star_atom:
    | NAME
    | '(' target_with_star_atom ')'
    | '(' [star_targets_tuple_seq] ')'
    | '[' [star_targets_list_seq] ']'
    """


class SingleTarget:
    """
single_target:
    | single_subscript_attribute_target
    | NAME
    | '(' single_target ')'
    """


class SingleSubscriptAttributeTarget:
    """
single_subscript_attribute_target:
    | t_primary '.' NAME !t_lookahead
    | t_primary '[' slices ']' !t_lookahead
    """


class DelTargets:
    """
del_targets: ','.del_target+ [',']
    """


class DelTarget:
    """
del_target:
    | t_primary '.' NAME !t_lookahead
    | t_primary '[' slices ']' !t_lookahead
    | del_t_atom
    """


class DelTAtom:
    """
del_t_atom:
    | NAME
    | '(' del_target ')'
    | '(' [del_targets] ')'
    | '[' [del_targets] ']'
    """


class Targets:
    """
targets: ','.target+ [',']
    """


class Target:
    """
target:
    | t_primary '.' NAME !t_lookahead
    | t_primary '[' slices ']' !t_lookahead
    | t_atom
    """


class TPrimary:
    """
t_primary:
    | t_primary '.' NAME &t_lookahead
    | t_primary '[' slices ']' &t_lookahead
    | t_primary genexp &t_lookahead
    | t_primary '(' [arguments] ')' &t_lookahead
    | atom &t_lookahead
    """


class TLookAhead:
    """
t_lookahead: '(' | '[' | '.'
    """


class TAtom:
    """
t_atom:
    | NAME
    | '(' target ')'
    | '(' [targets] ')'
    | '[' [targets] ']'
    """


"""
# PEG grammar for Python
file: [statements] ENDMARKER
interactive: statement_newline
eval: expressions NEWLINE* ENDMARKER
func_type: '(' [type_expressions] ')' '->' expression NEWLINE* ENDMARKER
fstring: star_expressions
"""
