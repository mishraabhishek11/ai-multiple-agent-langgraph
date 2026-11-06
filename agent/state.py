from typing import TypedDict


class AgentState(TypedDict):

    user_request: str

    current_step: int

    max_steps: int

    actions: list

    observations: list

    action: str

    approval: str

    finished: bool

    final_answer: str

