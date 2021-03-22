from ...core import *
from .Optimized_Match import Optimized_Match
from .Optimized_Pattern import Optimized_Pattern


def _optimize_match(engine, match: Match):
    patterns = tuple(engine.lexer.get_all_matching_patterns(match.identifier))
    builders = tuple(engine.parser.get_all_matching_builders(match.identifier))
    return Optimized_Match(identifier=match.identifier, patterns=patterns, builders=builders)


def _optimize_rule(engine, rule):
    if isinstance(rule, Match):
        return _optimize_match(engine, rule)
    elif isinstance(rule, All):
        return All(*(_optimize_rule(engine, sub_rule) for sub_rule in rule.rules))
    elif isinstance(rule, Any):
        return Any(*(_optimize_rule(engine, sub_rule) for sub_rule in rule.rules))
    elif isinstance(rule, As):
        return As(rule.key, _optimize_rule(engine, rule.rule))
    elif isinstance(rule, In):
        return In(rule.key, _optimize_rule(engine, rule.rule))
    elif isinstance(rule, Builder):
        return Builder(rule.identifier, _optimize_rule(engine, rule.rule))
    elif isinstance(rule, Routine):
        return Routine(rule.identifier, _optimize_rule(engine, rule.rule))
    elif isinstance(rule, Repeat):
        return Repeat(_optimize_rule(engine, rule.rule))
    elif isinstance(rule, Optional):
        return Optional(_optimize_rule(engine, rule.rule))
    else:
        raise Exception(type(rule))


def optimize(engine):
    mapper = []
    for pattern in sorted(engine.lexer.patterns, key=lambda pattern: pattern.priority):
        o_pattern = Optimized_Pattern(
            identifier=pattern.identifier,
            mode=pattern.mode,
            expr=pattern.expr,
            flag=pattern.flag,
            ignore=pattern.ignore,
            value=pattern.value,
            priority=pattern.priority
        )

        mapper.append((pattern, o_pattern))

    parser = Parser(*(_optimize_rule(engine, builder) for builder in engine.parser.builders))

    engine = Engine(engine.lexer, parser, engine.astb)

    return engine
