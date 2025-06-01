# =========
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def load_model():
    return ChatOpenAI(model="gpt-4o-mini")


# =========
from dataclasses import dataclass, field
from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import add_messages
from typing import Annotated, Literal, cast, Optional


@dataclass
class InputState:
    messages: Annotated[list[AnyMessage], add_messages]


@dataclass
class Router:
    logic: str
    type: Literal["more-info", "proceed"]


@dataclass
class AgentState(InputState):
    prompt: Optional[str] = ""
    result: Optional[str] = None
    router: Router = field(default_factory=lambda: Router(type="proceed", logic=""))
    steps: list[str] = field(default_factory=list)


# =========
ANALYZER_PROMPT = """
당신은 프롬프트가 적절한지 평가하는 전문가입니다. 당신의 역할은 프롬프트를 작성하는 사람들이 겪는 문제를 해결할 수 있도록 돕는 것입니다. 한국어로 작성하세요.

사용자가 프롬프트를 입력하면, 먼저 해당 프롬프트가 평가에 적절한지 분류해야 합니다. 분류할 수 있는 유형은 다음과 같습니다:

## `more-info`
프롬프트를 평가하기 위해 추가 정보가 필요한 경우 이 유형으로 분류합니다. 예를 들어:
- 프롬프트에 목적, 규칙 등이 명확하지 않아서 평가기준을 도출하기 어려운 경우
- 프롬프트가 지나치게 짧아서 평가기준을 도출하기 어려운 경우

## `proceed`
프롬프트로부터 평가 기준을 도출하여 답변할 수 있는 경우 이 유형으로 분류합니다.
프롬프트로부터 구체적인 평가 기준을 도출하고, 각 항목 별로 평가하게 됩니다.
"""

PLANNER_PROMPT = """
당신은 LLM 프롬프트 평가 전문가이자 세계적인 연구자로서, LLM 프롬프트의 평가 요소와 관련된 모든 질문과 문제를 해결하는 데 도움을 줄 수 있습니다. 사용자는 다양한 질문이나 문제를 가지고 찾아올 수 있습니다. 한국어로 작성하세요.

아래 대화를 기반으로, 사용자의 프롬프트를 평가하기 위한 평가 항목을 구체적으로 생성하세요.
평가항목은 반드시 프롬프트의 내용을 인용하여 구체적으로 작성해야 합니다.
평가항목은 일반적으로 5단계를 넘지 않아야 하며, 2단계로도 충분할 수 있습니다. 평가 항목의 갯수와 길이는 프롬프트의 복잡성에 따라 달라집니다.
"""

MORE_INFO_PROMPT = """
당신은 프롬프트가 적절한지 평가하는 전문가입니다. 당신의 역할은 프롬프트를 작성하는 사람들이 겪는 문제를 해결할 수 있도록 돕는 것입니다. 한국어로 작성하세요.

당신의 상사는 사용자를 대신하여 조사를 진행하기 전에 추가 정보가 필요하다고 판단했습니다. 그들의 논리는 다음과 같습니다:

<logic>
{logic}
</logic>

사용자에게 추가 정보를 요청하세요. 하지만 너무 많은 질문을 하지 마세요! 친절하게 접근하고, 단 하나의 후속 질문만 하세요.
"""

EVALUATION_PROMPT = """
당신은 LLM 프롬프트에 관하여, 주어지는 평가 항목에 따라 평가를 수행하는, 전문 프로그래머이자 문제 해결사입니다. 당신은 LLM 프롬프트의 평가 항목에 따라서 프롬프트 실행결과를 평가해야 합니다.

각 평가 항목 마다 1에서 5점 사이의 점수를 평가하고, 평가의 이유를 상세하게 설명해주세요.

한국어로 작성하세요.


<평가 항목>
{evaluation_criteria}
</평가 항목>


<프롬프트 실행결과>
{input_prompt_result}
</프롬프트 실행결과>
"""

# 주어지는 평가 항목에 적절한 도구를 사용해야 합니다. 사용할 수 있는 도구 유형은 아래와 같습니다.

# ## 반환기
# "안녕" 이라고 말합니다.

# ## 반환기
# "안녕" 이라고 말합니다.

# ## 반환기
# "안녕" 이라고 말합니다.

# =========
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig


def analyzer(state: AgentState, *, config: RunnableConfig) -> dict[str, Router]:
    model = load_model()
    messages = [{"role": "system", "content": PLANNER_PROMPT}] + state.messages
    response = cast(Router, model.with_structured_output(Router).invoke(messages))
    return {"router": response, "prompt": state.messages[0].content}


def router(state: AgentState) -> Literal["ask_for_more_info", "planner"]:
    type = state.router["type"]
    if type == "more-info":
        return "ask_for_more_info"
    if type == "proceed":
        return "planner"


def ask_for_more_info(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    model = load_model()
    system_prompt = MORE_INFO_PROMPT.format(logic=state.router["logic"])
    messages = [{"role": "system", "content": system_prompt}] + state.messages
    response = model.invoke(messages)
    return {"messages": [response]}


def planner(state: AgentState, *, config: RunnableConfig) -> dict[str, Router]:
    model = load_model()
    messages = [{"role": "system", "content": PLANNER_PROMPT}] + state.messages
    response = cast(Router, model.invoke(messages))
    return {"messages": [response]}


def evaluator(
    state: AgentState, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    model = load_model()
    input_prompt_response = model.invoke([HumanMessage(content=state.prompt)])

    messages = [
        SystemMessage(
            content=EVALUATION_PROMPT.format(
                evaluation_criteria=state.messages[0].content,
                input_prompt_result=input_prompt_response.content,
            )
        )
    ] + state.messages
    print(messages[0])

    response = model.invoke(messages)
    return {"messages": [response], "result": input_prompt_response}


builder = StateGraph(state_schema=AgentState)
builder.add_node(analyzer)
builder.add_node(planner)
builder.add_node(ask_for_more_info)
builder.add_node(evaluator)

builder.add_edge(START, "analyzer")
builder.add_conditional_edges("analyzer", router)
builder.add_edge("planner", "evaluator")
builder.add_edge("evaluator", END)
builder.add_edge("ask_for_more_info", "__end__")

graph = builder.compile(interrupt_before=["evaluator"])
