from typing import Dict, TypeVar, Generic, Tuple
import python_generator as pg

State = TypeVar("State")
Event = TypeVar("Event")
Check = TypeVar("Check")
Action = TypeVar("Action")


class BAS(Generic[Action, State]):
    @property
    def code(self) -> pg.BLOCK:
        raise NotImplementedError


class SAS(BAS[Action, State], Generic[Action, State]):
    def __init__(self, action: Action, state: State):
        self.action: Action = action
        self.state: State = state

    @property
    def code(self) -> pg.BLOCK:
        return pg.ARGS(self.action, self.state).RETURN().BLOCK()


class MAS(BAS[Action, State], Generic[Action, State]):
    def __init__(self, data: Dict[Action, State] = None):
        self.data: Dict[Action, State] = data or {}

    @property
    def code(self) -> pg.BLOCK:
        return pg.BLOCK(*[pg.ARGS(action, state).YIELD() for action, state in self.data.items()])


ActionState = TypeVar("ActionState", bound=BAS)


class BCS(Generic[Check, ActionState]):
    @property
    def code(self) -> pg.BLOCK:
        raise NotImplementedError


class MCS(BCS[Check, ActionState], Generic[Check, ActionState]):
    def __init__(self, cases, default):
        self.cases: Dict[Check, ActionState] = cases
        self.default: ActionState = default

    @property
    def code(self) -> pg.BLOCK:
        return pg.SWITCH(
            cases=[(check.code, action_state.code) for check, action_state in self.cases.items()],
            default=self.default.code
        ).BLOCK()


class SCS(BCS[Check, ActionState], Generic[Check, ActionState]):
    def __init__(self, check: Check, action_state: ActionState):
        self.check: Check = check
        self.action_state: ActionState = action_state

    @property
    def code(self) -> pg.BLOCK:
        return pg.IF(
            self.check.code,
            self.action_state.code,
            pg.EXCEPTION("check not passed").RAISE()
        ).BLOCK()


class StateMachine(Generic[State, Check, Action, ActionState]):
    """
        A State machine works as follow :
        When given an input state and an event,
        if the event triggers a validator, then it will return an action and an output state
    """

    def __init__(self, data: Dict[State, BCS]):
        self.data: Dict[State, BCS] = data
    
    @property
    def code(self):
        return 
