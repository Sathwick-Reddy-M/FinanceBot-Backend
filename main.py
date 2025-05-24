import os

from flask import Flask

app = Flask(__name__)

from google import genai
from langchain_core.tools import tool
from tools import *
from utils import *
from data_models import *

# Define a retry policy. The model might make multiple consecutive calls automatically
# for a complex query, this ensures the client retries if it hits quota limits.
from google.api_core import retry

is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

if not hasattr(genai.models.Models.generate_content, "__wrapped__"):
    genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
        genai.models.Models.generate_content
    )

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """State"""

    messages: Annotated[list, add_messages]
    finished: bool


FINANCEBOT_SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "You are finance bot and you will help users make better financial decisions",
)

WELCOME_MSG = "Welcome to your personal financial advisor. Type `q` to quit. How can I help you today?"

from collections.abc import Iterable
from random import randint
from typing import Literal


from langchain_core.messages.tool import ToolMessage

# These functions have no body; LangGraph does not allow @tools to update
# the conversation state, so you will implement a separate node to handle
# state updates. Using @tools is still very convenient for defining the tool
# schema, so empty functions have been defined that will be bound to the LLM
# but their implementation is deferred to the actual node.


def maybe_exit_human_node(state: ChatState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        return "chatbot"


def maybe_route_to_tools(state: ChatState) -> str:
    """Route between chat and tool nodes if a tool call is made."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    msg = msgs[-1]

    if state.get("finished", False):
        # When an order is placed, exit the app. The system instruction indicates
        # that the chatbot should say thanks and goodbye at this point, so we can exit
        # cleanly.
        return END

    elif hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Route to `tools` node for any automated tool calls first.
        if any(
            tool["name"] in tool_node.tools_by_name.keys() for tool in msg.tool_calls
        ):
            return "tools"
        else:
            return "ordering"

    else:
        return "human"


def chatbot_with_tools(state: ChatState) -> ChatState:
    """The chatbot with tools. A simple wrapper around the model's own chat interface."""
    defaults = {"order": [], "finished": False}

    if state["messages"]:
        new_output = llm_with_tools.invoke([FINANCEBOT_SYSINT] + state["messages"])
    else:
        new_output = AIMessage(content=WELCOME_MSG)

    # Set up some defaults if not already set, then pass through the provided state,
    # overriding only the "messages" field.
    return defaults | state | {"messages": [new_output]}


def human_node(state: ChatState) -> ChatState:
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    print("Model:", last_msg.content)

    user_input = input("User: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}


from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.ai import AIMessage


# Auto-tools will be invoked automatically by the ToolNode
auto_tools = [
    search_and_answer,
    get_user_details,
    get_tickers_info,
    identify_better_tickers,
    extract_unique_tickers_investment_accounts,
    summary_of_investment_accounts,
    get_investment_account,
    get_all_investment_account_ids_and_names,
    extract_unique_tickers_traditional_ira,
    summary_of_traditional_ira_accounts,
    get_traditional_ira_account,
    get_all_traditional_ira_account_ids_and_names,
    extract_unique_tickers_roth_ira,
    summary_of_roth_ira_accounts,
    get_roth_ira_account,
    get_all_roth_ira_account_ids_and_names,
    extract_unique_tickers_401k,
    summary_of_401k_accounts,
    get_401k_account,
    get_all_401k_account_ids_and_names,
    extract_unique_tickers_roth_401k,
    summary_of_roth_401k_accounts,
    get_roth_401k_account,
    get_all_roth_401k_account_ids_and_names,
    summary_of_credit_cards,
    get_all_credit_cards,
    get_credit_card,
    optimize_spending_in_a_category,
    optimize_spending_with_cc_all_categories,
    get_better_cards_for_category,
    summary_of_cheking_accounts,
    get_all_checking_accounts,
    get_checking_account,
    summary_of_saving_accounts,
    get_all_saving_accounts,
    get_saving_account,
    summary_of_loan_accounts,
    get_all_loans,
    get_loan,
    summary_of_payroll_accounts,
    get_all_payrolls,
    get_payroll,
    summary_of_hsa_accounts,
    get_all_hsa_accounts,
    get_hsa_account,
    summary_of_other_accounts,
    get_all_other_accounts,
    get_other_account,
    optimize_financial_plan,
    how_can_I_make_X_money_in_Y_months,
    how_can_save_X_money_in_Y_months,
]

tool_node = ToolNode(auto_tools)


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# The LLM needs to know about all of the tools, so specify everything here.
llm_with_tools = llm.bind_tools(auto_tools)

graph_builder = StateGraph(ChatState)

# Nodes
graph_builder.add_node("chatbot", chatbot_with_tools)
graph_builder.add_node("human", human_node)
graph_builder.add_node("tools", tool_node)

# Chatbot -> {ordering, tools, human, END}
graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
# Human -> {chatbot, END}
graph_builder.add_conditional_edges("human", maybe_exit_human_node)

# Tools (both kinds) always route back to chat afterwards.
graph_builder.add_edge("tools", "chatbot")

graph_builder.add_edge(START, "chatbot")
graph_with_tools = graph_builder.compile()

config = {"recursion_limit": 100}


state = graph_with_tools.invoke({"messages": []}, config)


@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the finance bot."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
