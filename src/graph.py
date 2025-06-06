from src.state import AgentState, InputState
from langgraph.graph import StateGraph, START, END
from src.node import analyzer, router, planner, ask_for_more_info, evaluator, executor


builder = StateGraph(state_schema=AgentState, input=InputState)
builder.add_node(analyzer)
builder.add_node(ask_for_more_info)
builder.add_node(planner)
builder.add_node(executor)
builder.add_node(evaluator)

builder.add_edge(START, "analyzer")
builder.add_conditional_edges("analyzer", router)
builder.add_edge("planner", "executor")
builder.add_edge("executor", "evaluator")
builder.add_edge("evaluator", END)
builder.add_edge("ask_for_more_info", "__end__")

graph = builder.compile(interrupt_before=["evaluator"])
