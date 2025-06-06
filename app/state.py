from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field


class InputState(BaseModel):
    prompt: str


class Router(BaseModel):
    logic: str
    type: Literal["more-info", "proceed"]


class GeneratedUserInput(BaseModel):
    generated_user_input: str


class AgentState(InputState, GeneratedUserInput, BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    generated_user_response: str
    router: Router = Field(default_factory=lambda: Router(type="proceed", logic=""))
    steps: list[str] = Field(default_factory=list)
