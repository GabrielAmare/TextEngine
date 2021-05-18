"""
test to see how to table the unoptimized branchsets
"""
from collections import deque
from functools import reduce
from operator import or_
from typing import Deque, Dict, List
from .base import *
from .constants import ACTION


def _build_cases(origin, group_select):
    for group, action, target in origin.get_all_cases():
        if group in group_select:
            action_select = group_select[group]
        else:
            group_select[group] = action_select = {}

        if action in action_select:
            action_select[action] |= target
        else:
            action_select[action] = target


def _add_non_visited_origins(group_select, visited, queue):
    for action_select in group_select.values():
        for target in action_select.values():
            if not target.is_terminal:  # add to the queue only if the branch-set contains non-terminal instructions
                if target not in visited:
                    queue.append(target.only_non_terminals)  # we remove the terminal branches to avoid duplications


def _make_optimized(group_select, explicit_items):
    optimized = {}
    default = frozenset()

    for group, action_select in group_select.items():
        hashable_action_select = frozenset(action_select.items())

        for item in explicit_items:
            if item in group:
                optimized[item] = optimized.get(item, frozenset()).union(hashable_action_select)

            if group.inverted:
                default = default.union(hashable_action_select)

    return optimized, default


def _make_reverted(optimized):
    reverted = {}
    for item, hashable_action_select in optimized.items():
        if hashable_action_select in reverted:
            reverted[hashable_action_select] += item
        else:
            reverted[hashable_action_select] = item.as_group

    return reverted


def _merge_default(reverted, default, explicit_items):
    if default in reverted:
        # if there's an ItemSet[K] which maps to the default ItemSet[V]
        # (which is the map of all the non-explicit items)
        # then we revert the ItemSet[K] using all the explicit items
        reverted[default] = ~reduce(or_, [item.as_group for item in explicit_items if item not in reverted[default]])
    else:
        # else, it just revert the whole explicit (as default ItemSet[V] is mapped from no explicit item)
        reverted[default] = ~reduce(or_, [item.as_group for item in explicit_items])


def tableit(initial: BranchSet):
    visited: List[BranchSet] = []
    queue: Deque[BranchSet] = deque([initial])

    value_select: Dict[BranchSet, Dict[Group, Dict[ACTION, BranchSet]]] = {}

    while queue:
        origin = queue.popleft()
        visited.append(origin)

        group_select: Dict[Group, Dict[ACTION, BranchSet]] = {}

        # build all the cases
        _build_cases(origin, group_select)

        # seek for the non-terminal cases to be visited
        _add_non_visited_origins(group_select, visited, queue)

    # once the cases have been built, we reduce the complexity
    for origin, group_select in value_select.items():
        explicit_items = sorted(set(item for group in group_select.keys() for item in group.items))

        optimized, default = _make_optimized(group_select, explicit_items)

        reverted = _make_reverted(optimized)

        _merge_default(reverted, default, explicit_items)

        value_select[origin] = {
            group: dict(hashable_action_select)
            for hashable_action_select, group in reverted.items()
        }

    # from there, no item belongs to two different groups from the same origin
    # and now we can reduce the complexity of the branch-sets by removing errors when there is another possiblity
    for origin, group_select in value_select.items():
        for group, action_select in group_select.items():
            for action, target in action_select.items():
                valid_part = target.only_valids
                error_part = target.only_errors
                non_terminal_part = target.only_non_terminals

                if non_terminal_part:
                    action_select[action] = non_terminal_part
                elif valid_part:
                    action_select[action] = valid_part
                else:
                    action_select[action] = error_part
