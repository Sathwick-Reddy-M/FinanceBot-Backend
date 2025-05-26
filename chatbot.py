from google import genai
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.ai import AIMessage
from google.api_core import retry
from typing import Annotated, Literal
from typing_extensions import TypedDict
from tools import *
from utils import *
from data_models import *


# Define a retry policy. The model might make multiple consecutive calls automatically
# for a complex query, this ensures the client retries if it hits quota limits.

is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

if not hasattr(genai.models.Models.generate_content, "__wrapped__"):
    genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
        genai.models.Models.generate_content
    )


class ChatState(TypedDict):
    """State"""

    messages: Annotated[list, add_messages]
    finished: bool


FINANCEBOT_SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "You are finance bot and you will help users make better financial decisions",
)

WELCOME_MSG = "Welcome to your personal financial advisor. Type `q` to quit. How can I help you today?"

from typing import Literal


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
    if state.get("finished", False):
        return END

    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages in state")

    last_msg = messages[-1]

    # If the last message has tool calls, route to tool node
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        for tool_call in last_msg.tool_calls:
            if tool_call["name"] in tool_node.tools_by_name:
                return "tools"

    return "human"


def chatbot_with_tools(state: ChatState) -> ChatState:
    messages = state["messages"]
    new_output = llm_with_tools.invoke([FINANCEBOT_SYSINT] + messages)

    # If current model response does NOT have tool_calls → it's a final message
    is_final_response = not (
        hasattr(new_output, "tool_calls") and new_output.tool_calls
    )

    return state | {
        "messages": messages + [new_output],
        "finished": is_final_response,  # Only end if no more tool calls needed
    }


def human_node(state: ChatState) -> ChatState:
    """Display the last model message to the user, and receive the user's input."""

    user_input = state["messages"][-1].content

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}


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

# Chatbot -> {tools, human, END}
graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
# Human -> {chatbot, END}
graph_builder.add_conditional_edges("human", maybe_exit_human_node)

# Tools (both kinds) always route back to chat afterwards.
graph_builder.add_edge("tools", "chatbot")

graph_builder.add_edge(START, "chatbot")
graph_with_tools = graph_builder.compile()
