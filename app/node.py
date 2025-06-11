from typing import cast, Literal
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from app.llm import load_model
from app.state import AgentState, Router, GeneratedUserInput
from app.prompt import (
    ANALYZER_PROMPT,
    PLANNER_PROMPT,
    MORE_INFO_PROMPT,
    EVALUATION_PROMPT,
    GENERATED_USER_INPUT_INSTRUCTION,
)

model = load_model()


def analyzer(state: AgentState, *, config: RunnableConfig) -> dict[str, Router]:
    messages = [
        SystemMessage(content=ANALYZER_PROMPT),
        HumanMessage(content=state.prompt),
    ]
    response = model.with_structured_output(Router).invoke(messages)
    return {"router": response}


def router(state: AgentState) -> Literal["ask_for_more_info", "planner"]:
    type = state.router.type
    if type == "more-info":
        return "ask_for_more_info"
    if type == "proceed":
        return "planner"


def ask_for_more_info(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    messages = [
        SystemMessage(content=MORE_INFO_PROMPT.format(logic=state.router.logic))
    ] + state.messages
    response = model.invoke(messages)
    return {"messages": [response]}


def planner(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    messages = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=state.prompt),
    ]
    response = model.invoke(messages)
    return {"messages": [response]}


def executor(state: AgentState, *, config: RunnableConfig) -> dict[str, str]:
    # 1. 사용자의 가상 요청 생성
    generated_user_input_messages = [
        SystemMessage(
            content=GENERATED_USER_INPUT_INSTRUCTION.format(prompt=state.prompt)
        ),
    ]
    generated_user_input_response = model.with_structured_output(
        GeneratedUserInput
    ).invoke(generated_user_input_messages)

    # 2. 사용자의 가상 요청 실행
    executor_messages = [
        SystemMessage(content=state.prompt),
        HumanMessage(content=generated_user_input_response.generated_user_input),
    ]
    executor_response = model.invoke(executor_messages)

    return {
        "generated_user_input": generated_user_input_response.generated_user_input,
        "generated_user_response": executor_response.content,
    }


def evaluator(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    messages = [
        SystemMessage(
            content=EVALUATION_PROMPT.format(
                evaluation_criteria=state.messages[0].content,
                input_prompt_result=state.generated_user_response,
            )
        )
    ] + state.messages
    response = model.invoke(messages)
    return {"messages": [response]}
