from .base import *
from .core import *
from typing import Union


def add_pattern(lexer, identifier, mode, expr, flag=0, ignore=False, value=None, priority=0):
    pattern = Pattern(identifier, mode, expr, flag, ignore, value, priority)
    lexer.patterns.append(pattern)
    return pattern


Lexer.add_pattern = add_pattern


def add_builder(parser, identifier, rule):
    builder = Builder(identifier, rule)
    parser.builders.append(builder)
    return builder


Parser.add_builder = add_builder


def add_routine(parser, identifier, rule):
    builder = Routine(identifier, rule)
    parser.builders.append(builder)
    return builder


Parser.add_routine = add_routine

Rule.__and__ = lambda rule, other: All(rule, *(other.rules if isinstance(other, All) else [other]))
All.__and__ = lambda rule, other: All(*rule.rules, *(other.rules if isinstance(other, All) else [other]))

Rule.__or__ = lambda rule, other: Any(rule, *(other.rules if isinstance(other, Any) else [other]))
Any.__or__ = lambda rule, other: Any(*rule.rules, *(other.rules if isinstance(other, Any) else [other]))

Pattern.__and__ = lambda pattern, other: pattern.match & other
Pattern.__or__ = lambda pattern, other: pattern.match | other


def match(obj: Union[Match, Pattern, str]):
    if isinstance(obj, Match):
        return obj
    elif isinstance(obj, Pattern):
        return Match(obj.identifier)
    elif isinstance(obj, str):
        return Match(obj)
    else:
        raise TypeError(obj)


def sep_by(rule, sep):
    return All(rule, Repeat(All(match(sep), rule)))


def wrapped_by(rule, prefix, suffix):
    return All(match(prefix), rule, match(suffix))


Rule.sep_by = sep_by
Rule.wrapped_by = wrapped_by

Rule.repeat = property(lambda rule: Repeat(rule))
Rule.optional = property(lambda rule: Optional(rule))
Rule.and_repeat = property(lambda rule: All(rule, Repeat(rule)))

Rule.as_ = lambda rule, key: As(key, rule)
Rule.in_ = lambda rule, key: In(key, rule)

Rule.builder = lambda rule, identifier: Builder(identifier, rule)
Rule.routine = lambda rule, identifier: Routine(identifier, rule)

Pattern.match = property(lambda pattern: Match(pattern.identifier))

Pattern.as_ = lambda pattern, key: pattern.match.as_(key)
Pattern.in_ = lambda pattern, key: pattern.match.in_(key)
