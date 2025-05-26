import os
import threading

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import graph_with_tools
from data_models import *
import user_data
from utils import parse_messages_for_langgraph
from langchain_core.messages.ai import AIMessage


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(
        app,
        resources={
            r"/chat": {
                "origins": "https://9000-firebase-studio-1748025806552.cluster-f4iwdviaqvc2ct6pgytzw4xqy4.cloudworkstations.dev/",
                "methods": ["POST", "OPTIONS"],
                "allow_headers": ["Content-Type"],
            },
        },
        supports_credentials=True,
    )

    # CONFIGURATION
    env = os.environ.get("FLASK_ENV", "production").lower()
    if env == "development":
        app.config.update(DEBUG=True)
    else:
        app.config.update(DEBUG=False)

    _account_setup_lock = threading.Lock()

    @app.route("/chat", methods=["POST"])
    def chat():
        """Chat with the finance bot."""

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        with _account_setup_lock:
            user_data.USER_DETAILS = UserDetails(**data["user_details"])

            accounts = data["accounts"]
            user_data.INVESTMENT_ACCOUNTS = []
            user_data.CREDIT_CARDS = []
            user_data.CHECKING_ACCOUNTS = []
            user_data.SAVING_ACCOUNTS = []
            user_data.LOANS = []
            user_data.PAYROLLS = []
            user_data.TRADITIONAL_IRAS = []
            user_data.ROTH_IRAS = []
            user_data.RETIREMENT_401KS = []
            user_data.ROTH_401KS = []
            user_data.HSA_ACCOUNTS = []
            user_data.OTHER_ACCOUNTS = []

            for account in accounts:
                account_type = account["type"]
                if account_type == "Investment":
                    user_data.INVESTMENT_ACCOUNTS.append(InvestmentAccount(**account))
                elif account_type == "Credit Card":
                    user_data.CREDIT_CARDS.append(CreditCard(**account))
                elif account_type == "Checking":
                    user_data.CHECKING_ACCOUNTS.append(
                        CheckingOrSavingsAccount(**account)
                    )
                elif account_type == "Savings":
                    user_data.SAVING_ACCOUNTS.append(
                        CheckingOrSavingsAccount(**account)
                    )
                elif account_type == "Loan":
                    user_data.LOANS.append(Loan(**account))
                elif account_type == "Payroll":
                    user_data.PAYROLLS.append(Payroll(**account))
                elif account_type == "Traditional IRA":
                    user_data.TRADITIONAL_IRAS.append(TraditionalIRA(**account))
                elif account_type == "Roth IRA":
                    user_data.ROTH_IRAS.append(RothIRA(**account))
                elif account_type == "Retirement 401k":
                    user_data.RETIREMENT_401KS.append(Retirement401K(**account))
                elif account_type == "Roth 401k":
                    user_data.ROTH_401KS.append(Roth401K(**account))
                elif account_type == "HSA":
                    user_data.HSA_ACCOUNTS.append(HSAAccount(**account))
                elif account_type == "Other":
                    user_data.OTHER_ACCOUNTS.append(OtherAccount(**account))

            user_data.INVESTMENT_ACCOUNTS_DICT = {
                account.id: account for account in user_data.INVESTMENT_ACCOUNTS
            }
            user_data.CREDIT_CARDS_DICT = {
                card.id: card for card in user_data.CREDIT_CARDS
            }
            user_data.CHECKING_ACCOUNTS_DICT = {
                account.id: account for account in user_data.CHECKING_ACCOUNTS
            }
            user_data.SAVING_ACCOUNTS_DICT = {
                account.id: account for account in user_data.SAVING_ACCOUNTS
            }
            user_data.LOANS_DICT = {loan.id: loan for loan in user_data.LOANS}
            user_data.PAYROLLS_DICT = {
                payroll.id: payroll for payroll in user_data.PAYROLLS
            }
            user_data.TRADITIONAL_IRAS_DICT = {
                ira.id: ira for ira in user_data.TRADITIONAL_IRAS
            }
            user_data.ROTH_IRAS_DICT = {ira.id: ira for ira in user_data.ROTH_IRAS}
            user_data.RETIREMENT_401KS_DICT = {
                account.id: account for account in user_data.RETIREMENT_401KS
            }
            user_data.ROTH_401KS_DICT = {
                account.id: account for account in user_data.ROTH_401KS
            }
            user_data.HSA_ACCOUNTS_DICT = {
                account.id: account for account in user_data.HSA_ACCOUNTS
            }
            user_data.OTHER_ACCOUNTS_DICT = {
                account.id: account for account in user_data.OTHER_ACCOUNTS
            }

        # Messages
        config = {"recursion_limit": 5}

        processed_messages = parse_messages_for_langgraph(data["chatMessages"])

        state = graph_with_tools.invoke({"messages": processed_messages}, config=config)

        # Get the latest chatbot message
        chatbot_messages = state.get("messages", [])
        last_message = chatbot_messages[-1] if chatbot_messages else None

        if isinstance(last_message, AIMessage):
            return jsonify({"response": last_message.content})
        return jsonify({"error": "No valid response"}), 500

    return app


app = create_app()
