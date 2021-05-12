from __future__ import annotations
import typing as t

TypeComment = str


class TypeExpressions:
    def __init__(self, expressions: t.List[Expression], args: Expression = None, kwargs: Expression = None):
        assert expressions or args or kwargs
        self.expressions: t.List[Expression] = expressions
        self.args: t.Optional[Expression] = args
        self.kwargs: t.Optional[Expression] = kwargs

    def __str__(self):
        l = list(map(str, self.expressions))

        if self.args:
            l.append("*" + str(self.args))

        if self.kwargs:
            l.append("**" + str(self.kwargs))

        return ", ".join(l)


class Statements:
    def __init__(self, statements: t.List[Statement]):
        self.statements: t.List[Statement] = statements

    def __str__(self):
        return " ".join(map(str, self.statements))


class Statement:
    pass


class StatementNewline:
    """
statement_newline:
    | compound_stmt NEWLINE
    | simple_stmt
    | NEWLINE
    | ENDMARKER
    """


class SimpleStmt(Statement):
    """
simple_stmt:
    | small_stmt !';' NEWLINE  # Not needed, there for speedup
    | ';'.small_stmt+ [';'] NEWLINE
    """


class CompoundStmt(Statement):
    pass


class SmallStmt:
    pass


class Pass(SmallStmt):
    def __str__(self):
        return "pass"


class Break(SmallStmt):
    def __str__(self):
        return "break"


class Continue(SmallStmt):
    def __str__(self):
        return "continue"


class Assignment(SmallStmt):
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


class GlobalStmt(SmallStmt):
    def __init__(self, names: t.List[str]):
        assert all(name.isidentifier() for name in names)
        self.names: t.List[str] = names

    def __str__(self):
        return "global " + ", ".join(self.names)


class NonLocalStmt(SmallStmt):
    def __init__(self, names: t.List[str]):
        assert all(name.isidentifier() for name in names)
        self.names: t.List[str] = names

    def __str__(self):
        return "nonlocal " + ", ".join(self.names)


class YieldStmt(SmallStmt):
    pass


class AssertStmt(SmallStmt):
    def __init__(self, expr1: Expression, expr2: Expression = None):
        self.expr1: Expression = expr1
        self.expr2: t.Optional[Expression] = expr2

    def __str__(self):
        if self.expr2 is None:
            return f"assert {self.expr1!s}"
        else:
            return f"assert {self.expr1!s}, {self.expr2!s}"


class DelStmt(SmallStmt):
    """
del_stmt:
    | 'del' del_targets &(';' | NEWLINE)
    """


class ImportStmt(SmallStmt):
    pass


class ImportName(ImportStmt):
    """
import_name: 'import' dotted_as_names
    """


class ImportFrom(ImportStmt):
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

    def __init__(self, items: t.List[ImportFromAsName]):
        self.items: t.List[ImportFromAsName] = items

    def __str__(self):
        return ", ".join(map(str, self.items))


class ImportFromAsName:
    def __init__(self, import_: str, as_: str = None):
        assert import_.isidentifier()
        assert as_ is None or as_.isidentifier()
        self.import_: str = import_
        self.as_: t.Optional[str] = as_

    def __str__(self):
        if self.as_ is None:
            return f"{self.import_!s}"
        else:
            return f"{self.import_!s} as {self.as_!s}"


class DottedAsNames:
    def __init__(self, items: t.List[DottedAsName]):
        self.items: t.List[DottedAsName] = items

    def __str__(self):
        return ", ".join(map(str, self.items))


class DottedAsName:
    def __init__(self, name: DottedName, as_: str = None):
        assert as_ is None or as_.isidentifier()
        self.name: DottedName = name
        self.as_: t.Optional[str] = as_

    def __str__(self):
        if self.as_ is None:
            return f"{self.name!s}"
        else:
            return f"{self.name!s} as {self.as_!s}"


class DottedName:
    def __init__(self, names: t.List[str]):
        assert all(name.isidentifier() for name in names)
        self.names: t.List[str] = names

    def __str__(self):
        return ".".join(self.names)


class IfStmt(CompoundStmt):
    def __init__(self, expr: NamedExpression, block: Block, alt: t.Union[ElifStmt, ElseBlock] = None):
        self.expr: NamedExpression = expr
        self.block: Block = block
        self.alt: t.Optional[t.Union[ElifStmt, ElseBlock]] = alt

    def __str__(self):
        if self.alt is None:
            return f"if {self.expr!s}:{self.block!s}"
        else:
            return f"if {self.expr!s}:{self.block!s}{self.alt!s}"


class ElifStmt:
    def __init__(self, expr: NamedExpression, block: Block, alt: t.Union[ElifStmt, ElseBlock] = None):
        self.expr: NamedExpression = expr
        self.block: Block = block
        self.alt: t.Optional[t.Union[ElifStmt, ElseBlock]] = alt

    def __str__(self):
        if self.alt is None:
            return f"elif {self.expr!s}:{self.block!s}"
        else:
            return f"elif {self.expr!s}:{self.block!s}{self.alt!s}"


class ElseBlock:
    def __init__(self, block: Block):
        self.block: Block = block

    def __str__(self):
        return f"else:{self.block!s}"


class WhileStmt(CompoundStmt):
    def __init__(self, expr: NamedExpression, block: Block, alt: ElseBlock = None):
        self.expr: NamedExpression = expr
        self.block: Block = block
        self.alt: t.Optional[ElseBlock] = alt

    def __str__(self):
        if self.alt is None:
            return f"while {self.expr!s}:{self.block!s}"
        else:
            return f"while {self.expr!s}:{self.block!s}{self.alt!s}"


class ForStmt(CompoundStmt):
    def __init__(self,
                 star_targets: StarTargets,
                 star_expressions: StarExpressions,
                 block: Block,
                 comment: TypeComment = None,
                 alt: Block = None,
                 is_async: bool = False):
        self.star_targets: StarTargets = star_targets
        self.star_expressions: StarExpressions = star_expressions
        self.block: Block = block
        self.comment: t.Optional[TypeComment] = comment
        self.alt: t.Optional[Block] = alt
        self.is_async: bool = is_async

    def __str__(self):
        return f"{'async ' if self.is_async else ''}" \
               f"for {self.star_targets!s} in {self.star_expressions!s}:" \
               f"{' ' + str(self.comment) if self.comment else ''}" \
               f"{self.block!s}" \
               f"{str(self.alt) if self.alt else ''}"


class WithStmt(CompoundStmt):
    def __init__(self, items: t.List[WithItem], block: Block, comment: TypeComment = None, is_async: bool = False):
        self.items: t.List[WithItem] = items
        self.block: Block = block
        self.comment: t.Optional[TypeComment] = comment
        self.is_async: bool = is_async

    def __str__(self, b0: bool = False, b1: bool = False):
        assert b0 or not b1
        return f"{'async ' if self.is_async else ''}" \
               f"with " \
               f"{'(' if b0 else ''}" \
               f"{', '.join(map(str, self.items))}" \
               f"{',' if b1 else ''}" \
               f"{')' if b0 else ''}:" \
               f"{' ' + str(self.comment) if self.comment else ''}" \
               f"{self.block!s}"


class WithItem:
    """
with_item:
    | expression 'as' star_target &(',' | ')' | ':')
    | expression
    """


class TryStmt(CompoundStmt):
    def __init__(self,
                 block: Block,
                 excepts: t.List[ExceptBlock] = None,
                 else_: ElseBlock = None,
                 finally_: FinallyBlock = None):
        assert not else_ or excepts or finally_
        if excepts is None:
            excepts = []
        self.block = block
        self.excepts: t.List[ExceptBlock] = excepts
        self.else_: t.Optional[ElseBlock] = else_
        self.finally_: t.Optional[FinallyBlock] = finally_

    def __str__(self):
        return f"try:{self.block!s}" + \
               "".join(map(str, self.excepts)) + \
               (str(self.else_) if self.else_ else "") + \
               (str(self.finally_) if self.finally_ else "")


class ExceptBlock:
    def __init__(self, block: Block, expr: Expression = None, as_: str = None):
        assert expr is not None or as_ is None
        assert as_ is None or as_.isidentifier()
        self.block: Block = block
        self.expr: t.Optional[Expression] = expr
        self.as_: t.Optional[str] = as_

    def __str__(self):
        if self.expr is None:
            return f"except:{self.block!s}"
        elif self.as_ is None:
            return f"except {self.expr!s}:{self.block!s}"
        else:
            return f"except {self.expr!s} as {self.as_}:{self.block!s}"


class FinallyBlock:
    def __init__(self, block: Block):
        self.block: Block = block

    def __str__(self):
        return f"finally:{self.block!s}"


class ReturnStmt(SmallStmt):
    def __init__(self, star_expressions: StarExpressions):
        self.star_expressions: StarExpressions = star_expressions

    def __str__(self):
        return f"return {self.star_expressions!s}"


class RaiseStmt(SmallStmt):
    def __init__(self, raise_: Expression, from_: Expression = None):
        self.raise_: Expression = raise_
        self.from_: t.Optional[Expression] = from_

    def __str__(self):
        if self.from_ is None:
            return f"raise {self.raise_!s}"
        else:
            return f"raise {self.raise_!s} from {self.from_!s}"


class FunctionDef(CompoundStmt):
    def __init__(self,
                 name: str,
                 block: Block,
                 params: Params = None,
                 rtype: Expression = None,
                 comment: TypeComment = None,
                 decorators: Decorators = None,
                 is_async: bool = False):
        assert name.isidentifier()
        self.name: str = name
        self.block: Block = block
        self.params: t.Optional[Params] = params
        self.rtype: t.Optional[Expression] = rtype
        self.comment: t.Optional[TypeComment] = comment
        self.decorators: t.Optional[Decorators] = decorators
        self.is_async: bool = is_async

    def __str__(self):
        decorators = str(self.decorators) if self.decorators else ''
        is_async = 'async ' if self.is_async else ''
        rtype = f' -> {self.rtype!s}' if self.rtype else ''
        comment = f'\n{self.comment!s}' if self.comment else ''
        return f"{decorators}{is_async}def {self.name}({self.params!s}){rtype}:{comment}{self.block!s}"


class Params:
    pass


class Parameters(Params):
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


class ClassDef(CompoundStmt):
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


class StarExpressions(SmallStmt):
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


class YieldExpr(YieldStmt):
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
