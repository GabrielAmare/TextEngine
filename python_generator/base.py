from typing import List, Optional, Union, Any

NAME = str


def indent(s: str) -> str:
    return '\n'.join('    ' + l for l in s.split('\n'))


class STATEMENT:
    # statement: compound_stmt | small_stmt
    pass


class COMPOUND_STMT(STATEMENT):
    # compound_stmt:
    #     | function_def
    #     | if_stmt
    #     | class_def
    #     | with_stmt
    #     | for_stmt
    #     | try_stmt
    #     | while_stmt
    pass


class FUNC_TYPE_COMMENT:
    # func_type_comment:
    #     | NEWLINE TYPE_COMMENT &(NEWLINE INDENT)   # Must be followed by indented block
    #     | TYPE_COMMENT
    def __init__(self, comment: TYPE_COMMENT):
        self.comment: TYPE_COMMENT = comment


class PARAMS:
    # params:
    #     | parameters
    pass


class PARAMETERS(PARAMS):
    # parameters:
    #     | slash_no_default param_no_default* param_with_default* [star_etc]
    #     | slash_with_default param_with_default* [star_etc]
    #     | param_no_default+ param_with_default* [star_etc]
    #     | param_with_default+ [star_etc]
    #     | star_etc
    pass


class EXPRESSION:
    # expression:
    #     | disjunction 'if' disjunction 'else' expression
    #     | disjunction
    #     | lambdef
    pass


class COMPARISON:
    # comparison:
    #     | bitwise_or compare_op_bitwise_or_pair+
    #     | bitwise_or
    pass


class INVERSION:
    # inversion:
    #     | 'not' inversion
    #     | comparison
    def __init__(self, arg):
        assert isinstance(arg, (INVERSION, COMPARISON))
        self.arg = arg

    def __str__(self):
        return f"not {self.arg}"


class CONJUNCTION:
    # conjunction:
    #     | inversion ('and' inversion )+
    #     | inversion
    def __init__(self, inversions: List[INVERSION]):
        self.inversions: List[INVERSION] = inversions

    def __str__(self):
        return " and ".join(map(str, self.inversions))


class DISJUNCTION(EXPRESSION):
    # disjunction:
    #     | conjunction ('or' conjunction )+
    #     | conjunction
    def __init__(self, conjunctions: List[CONJUNCTION]):
        self.conjunctions: List[CONJUNCTION] = conjunctions

    def __str__(self):
        return " or ".join(map(str, self.conjunctions))


GRPS = [
    [COMPARISON],
    [INVERSION],
    [CONJUNCTION],
    [DISJUNCTION],
]


class LAMBDA_PARAMS:
    # lambda_params:
    #     | lambda_parameters
    pass


class LAMBDA_PARAMETERS(LAMBDA_PARAMS):
    # lambda_parameters:
    #     | lambda_slash_no_default lambda_param_no_default* lambda_param_with_default* [lambda_star_etc]
    #     | lambda_slash_with_default lambda_param_with_default* [lambda_star_etc]
    #     | lambda_param_no_default+ lambda_param_with_default* [lambda_star_etc]
    #     | lambda_param_with_default+ [lambda_star_etc]
    #     | lambda_star_etc
    pass


class LAMBDEF(EXPRESSION):
    # lambdef:
    #     | 'lambda' [lambda_params] ':' expression
    def __init__(self, params: Optional[LAMBDA_PARAMS], expr: EXPRESSION):
        self.params = params
        self.expr = expr

    def __str__(self):
        params = '' if self.params is None else f" {self.params!s}"
        return f"lambda{params}: {self.expr!s}"


class TERNARY(EXPRESSION):
    def __init__(self, do_: DISJUNCTION, if_: DISJUNCTION, else_: EXPRESSION):
        self.do_: DISJUNCTION = do_
        self.if_: DISJUNCTION = if_
        self.else_: EXPRESSION = else_

    def __repr__(self):
        return f"{self.do_!s} if {self.if_!s} else {self.else_!s}"


class NAMED_EXPRESSION:
    # named_expression:
    #     | NAME ':=' ~ expression
    #     | expression !':='
    def __init__(self, expr: EXPRESSION, name: Optional[NAME]):
        self.name: Optional[NAME] = name
        self.expr: EXPRESSION = expr

    def __str__(self):
        if self.name is None:
            return str(self.expr)
        else:
            return f"{self.name!s} := {self.expr}"


class DECORATORS:
    # decorators: ('@' named_expression NEWLINE )+
    def __init__(self, exprs: List[NAMED_EXPRESSION]):
        self.exprs: List[NAMED_EXPRESSION] = exprs

    def __str__(self):
        return "".join(f"@{expr!s}\n" for expr in self.exprs)


class BLOCK:
    # block:
    #     | NEWLINE INDENT statements DEDENT
    #     | simple_stmt
    # statements: statement+
    def __init__(self, statements: List[STATEMENT]):
        self.statements: List[STATEMENT] = statements

    def __str__(self):
        return indent('\n'.join(map(str, self.statements)))


class FUNCTION_DEF(COMPOUND_STMT):
    # function_def:
    #     | decorators function_def_raw
    #     | function_def_raw
    # function_def_raw:
    #     | 'def' NAME '(' [params] ')' ['->' expression ] ':' [func_type_comment] block
    #     | ASYNC 'def' NAME '(' [params] ')' ['->' expression ] ':' [func_type_comment] block

    def __init__(self,
                 name: NAME,
                 params: Optional[PARAMS],
                 rtype: Optional[EXPRESSION],
                 ftype_comment: Optional[FUNC_TYPE_COMMENT],
                 block: BLOCK,
                 decorators: DECORATORS,
                 is_async: bool = False
                 ):
        self.name: NAME = name
        self.params: Optional[PARAMS] = params
        self.rtype: Optional[EXPRESSION] = rtype
        self.ftype_comment: Optional[FUNC_TYPE_COMMENT] = ftype_comment
        self.block: BLOCK = block
        self.decorators: DECORATORS = decorators
        self.is_async: bool = is_async

    def __str__(self):
        decorators = '' if self.decorators is None else str(self.decorators) + '\n'
        async_kw = 'async ' if self.is_async else ''
        params = '' if self.params is None else str(self.params)
        rtype = '' if self.rtype is None else f' -> {self.rtype!s}'
        comment = '' if self.ftype_comment else f' {self.ftype_comment!s}'
        return f"{decorators}{async_kw}def {self.name!s}({params}){rtype}:{comment}\n" \
               f"{indent(str(self.block))}"


class IF_STMT(COMPOUND_STMT):
    # if_stmt:
    #     | 'if' named_expression ':' block elif_stmt
    #     | 'if' named_expression ':' block [else_block]
    def __init__(self, nmd: NAMED_EXPRESSION, block: BLOCK, after: Optional[Union[ELIF_STMT, ELSE_BLOCK]] = None):
        self.nmd: NAMED_EXPRESSION = nmd
        self.block: BLOCK = block
        self.after: Optional[Union[ELIF_STMT, ELSE_BLOCK]] = after

    def __str__(self):
        if self.after is None:
            return f"if {self.nmd!s}:\n" \
                   f"{indent(str(self.block))}"
        else:
            return f"if {self.nmd!s}:\n" \
                   f"{indent(str(self.block))}\n{self.after!s}"


class ELIF_STMT:
    # elif_stmt:
    #     | 'elif' named_expression ':' block elif_stmt
    #     | 'elif' named_expression ':' block [else_block]
    def __init__(self, nmd: NAMED_EXPRESSION, block: BLOCK, after: Optional[Any] = None):
        assert after is None or isinstance(after, ELIF_STMT, ELSE_BLOCK)
        self.nmd: NAMED_EXPRESSION = nmd
        self.block: BLOCK = block
        self.after: Optional[Union[ELIF_STMT, ELSE_BLOCK]] = after

    def __str__(self):
        if self.after is None:
            return f"elif {self.nmd!s}:\n" \
                   f"{indent(str(self.block))}"
        else:
            return f"elif {self.nmd!s}:\n" \
                   f"{indent(str(self.block))}\n{self.after!s}"


class ELSE_BLOCK:
    # else_block: 'else' ':' block
    def __init__(self, block: BLOCK):
        self.block: BLOCK = block

    def __str__(self):
        return f"else:\n" \
               f"{indent(str(self.block))}"


class CLASS_DEF(COMPOUND_STMT):
    # class_def:
    #     | decorators class_def_raw
    #     | class_def_raw
    # class_def_raw:
    #     | 'class' NAME ['(' [arguments] ')' ] ':' block
    def __init__(self, name: NAME, args: ARGUMENTS, block: BLOCK, decorators: Optional[DECORATORS] = None):
        self.name: NAME = name
        self.args: ARGUMENTS = args
        self.block: BLOCK = block
        self.decorators: Optional[DECORATORS] = decorators

    def __str__(self):
        decorators = '' if self.decorators is None else str(self.decorators) + '\n'
        arguments = '' if self.args is None else str(self.args)
        return f"{decorators}class {self.name!s}({arguments}):\n" \
               f"{indent(str(self.block))}"


class WITH_STMT(COMPOUND_STMT):
    # with_stmt:
    #     | 'with' '(' ','.with_item+ ','? ')' ':' block
    #     | 'with' ','.with_item+ ':' [TYPE_COMMENT] block
    #     | ASYNC 'with' '(' ','.with_item+ ','? ')' ':' block
    #     | ASYNC 'with' ','.with_item+ ':' [TYPE_COMMENT] block
    pass


class WITH_ITEM:
    # with_item:
    #     | expression 'as' star_target &(',' | ')' | ':')
    #     | expression
    pass


class EXCEPT_BLOCK:
    # except_block:
    #     | 'except' expression ['as' NAME ] ':' block
    #     | 'except' ':' block
    pass


class FINALLY_BLOCK:
    # finally_block: 'finally' ':' block
    pass


class FOR_STMT(COMPOUND_STMT):
    # for_stmt:
    #     | 'for' star_targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block]
    #     | ASYNC 'for' star_targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block]
    pass


class TRY_STMT(COMPOUND_STMT):
    # try_stmt:
    #     | 'try' ':' block finally_block
    #     | 'try' ':' block except_block+ [else_block] [finally_block]
    def __init__(self, block: BLOCK,
                 excepts: Optional[List[EXCEPT_BLOCK]] = None,
                 else_: Optional[ELSE_BLOCK] = None,
                 finally_: Optional[FINALLY_BLOCK] = None):
        assert excepts or (finally_ is not None)
        if excepts is None:
            excepts = []
        self.block: BLOCK = block
        self.excepts: List[EXCEPT_BLOCK] = excepts
        self.else_: Optional[ELSE_BLOCK] = else_
        self.finally_: Optional[FINALLY_BLOCK] = finally_

    def __str__(self):
        t = [f"try:{indent(str(self.block))}"] + list(map(str, self.excepts))

        if self.else_ is not None:
            t.append(str(self.else_))

        if self.finally_ is not None:
            t.append(str(self.finally_))

        return "\n".join(t)


class WHILE_STMT(COMPOUND_STMT):
    # while_stmt:
    #     | 'while' named_expression ':' block [else_block]
    def __init__(self, nmd: NAMED_EXPRESSION, block: BLOCK, after: Optional[ELSE_BLOCK] = None):
        self.nmd: NAMED_EXPRESSION = nmd
        self.block: BLOCK = block
        self.after: Optional[ELSE_BLOCK] = after

    def __str__(self):
        if self.after is None:
            return f"while {self.nmd!s}:\n" \
                   f"{indent(str(self.block))}"
        else:
            return f"while {self.nmd!s}:\n" \
                   f"{indent(str(self.block))}\n" \
                   f"{self.after!s}"


class SMALL_STMT(STATEMENT):
    # small_stmt:
    #     | assignment
    #     | star_expressions
    #     | return_stmt
    #     | import_stmt
    #     | raise_stmt
    #     | 'pass'
    #     | del_stmt
    #     | yield_stmt
    #     | assert_stmt
    #     | 'break'
    #     | 'continue'
    #     | global_stmt
    #     | nonlocal_stmt
    pass


class ASSIGNMENT(SMALL_STMT):
    # assignment:
    #     | NAME ':' expression ['=' annotated_rhs ]
    #     | ('(' single_target ')'
    #          | single_subscript_attribute_target) ':' expression ['=' annotated_rhs ]
    #     | (star_targets '=' )+ (yield_expr | star_expressions) !'=' [TYPE_COMMENT]
    #     | single_target augassign ~ (yield_expr | star_expressions)
    pass


class STAR_EXPRESSION:
    # star_expression:
    #     | '*' bitwise_or
    #     | expression
    pass


class STAR_EXPRESSIONS(SMALL_STMT):
    # star_expressions:
    #     | star_expression (',' star_expression )+ [',']
    #     | star_expression ','
    #     | star_expression
    def __init__(self, items: List[STAR_EXPRESSION]):
        self.items: List[STAR_EXPRESSION] = items

    def __str__(self, b0: bool = False):
        return ', '.join(map(str, self.items)) + (',' if b0 else '')


class RETURN_STMT(SMALL_STMT):
    # return_stmt:
    #     | 'return' [star_expressions]
    def __init__(self, item: Optional[STAR_EXPRESSIONS]):
        self.item = item

    def __str__(self):
        if self.item is None:
            return "return"
        else:
            return f"return {self.item!s}"


class IMPORT_STMT(SMALL_STMT):
    # import_stmt: import_name | import_from
    pass


class DOTTED_AS_NAME:
    # dotted_as_name:
    #     | dotted_name ['as' NAME ]
    # dotted_name:
    #     | dotted_name '.' NAME
    #     | NAME
    def __init__(self, names: List[NAME], as_: Optional[NAME] = None):
        self.names: List[NAME] = names
        self.as_: Optional[NAME] = as_

    def __str__(self):
        name = ".".join(map(str, self.names))
        if self.as_ is None:
            return name
        else:
            return f"{name} as {self.as_!s}"


class IMPORT_NAME(IMPORT_STMT):
    # import_name: 'import' dotted_as_names
    # dotted_as_names:
    #     | ','.dotted_as_name+
    def __init__(self, items: List[DOTTED_AS_NAME]):
        self.items = items

    def __str__(self):
        return "import " + ', '.join(map(str, self.items))


class IMPORT_FROM_AS_NAME:
    # import_from_as_name:
    #     | NAME ['as' NAME ]
    def __init__(self, name: NAME, as_: Optional[NAME] = None):
        self.name: NAME = name
        self.as_: NAME = as_

    def __str__(self):
        if self.as_ is None:
            return self.name
        else:
            return f"{self.name!s} as {self.as_}"


class IMPORT_FROM_AS_NAMES:
    # import_from_as_names:
    #     | ','.import_from_as_name+
    def __init__(self, items: List[IMPORT_FROM_AS_NAME]):
        self.items: List[IMPORT_FROM_AS_NAME] = items

    def __str__(self):
        return ', '.join(map(str, self.items))


class IMPORT_FROM_TARGETS:
    # import_from_targets:
    #     | '(' import_from_as_names [','] ')'
    #     | import_from_as_names !','
    #     | '*'
    def __init__(self, names: Optional[IMPORT_FROM_AS_NAMES]):
        self.names: IMPORT_FROM_AS_NAMES = names

    def __str__(self, b0: bool = False, b1: bool = False):
        assert not b0 or not b1
        if self.names is None:
            return '*'
        else:
            if b0:
                if b1:
                    return f"({self.names!s},)"
                else:
                    return f"({self.names!s})"
            else:
                return f"{self.names!s}"


class IMPORT_FROM(IMPORT_STMT):
    # import_from:
    #     | 'from' ('.' | '...')* dotted_name 'import' import_from_targets
    #     | 'from' ('.' | '...')+ 'import' import_from_targets
    def __init__(self, name: DOTTED_NAME, targets: IMPORT_FROM_TARGETS):
        self.name = name
        self.targets = targets

    def __str__(self):
        return f"from {self.name!s} import {self.targets!s}"


class RAISE_STMT(SMALL_STMT):
    # raise_stmt:
    #     | 'raise' expression ['from' expression ]
    #     | 'raise'
    def __init__(self, raise_: Optional[STAR_EXPRESSIONS], from_: Optional[STAR_EXPRESSIONS]):
        assert self.raise_ is not None or self.from_ is None
        self.raise_ = raise_
        self.from_ = from_

    def __str__(self):
        if self.raise_ is None:
            return "raise"
        elif self.from_ is None:
            return f"raise {self.raise_!s}"
        else:
            return f"raise {self.raise_!s} from {self.from_!s}"


class DEL_STMT(SMALL_STMT):
    # del_stmt:
    #     | 'del' del_targets &(';' | NEWLINE)
    pass


class YIELD_STMT(SMALL_STMT):
    # yield_stmt: yield_expr
    pass


class ASSERT_STMT(SMALL_STMT):
    # assert_stmt: 'assert' expression [',' expression ]
    def __init__(self, expr1: EXPRESSION, expr2: Optional[EXPRESSION] = None):
        self.expr1: EXPRESSION = expr1
        self.expr2: Optional[EXPRESSION] = expr2

    def __str__(self):
        if self.expr2 is None:
            return f"assert {self.expr1!s}"
        else:
            return f"assert {self.expr1!s}, {self.expr2!s}"


class PASS(SMALL_STMT):
    def __str__(self):
        return "pass"


class BREAK(SMALL_STMT):
    def __str__(self):
        return "break"


class CONTINUE(SMALL_STMT):
    def __str__(self):
        return "continue"


class GLOBAL_STMT(SMALL_STMT):
    # global_stmt: 'global' ','.NAME+
    def __init__(self, names: List[NAME]):
        self.names: List[NAME] = names

    def __str__(self):
        return "global " + ", ".join(map(str, self.names))


class NONLOCAL_STMT(SMALL_STMT):
    # nonlocal_stmt: 'nonlocal' ','.NAME+
    def __init__(self, names: List[NAME]):
        self.names: List[NAME] = names

    def __str__(self):
        return "nonlocal " + ", ".join(map(str, self.names))
