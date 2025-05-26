from data_models import *
import user_data

from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from collections import defaultdict
import datetime
import os


def parse_messages_for_langgraph(messages_input):
    """
    Parses a list of raw message dictionaries into a list of LangGraph-compatible
    BaseMessage objects (HumanMessage, AIMessage).

    Args:
        messages_input: A list of dictionaries, where each dictionary represents a message
                        and is expected to have "sender" and "text" keys.

    Returns:
        A list of BaseMessage objects (HumanMessage or AIMessage).
    """
    processed_messages = []
    for msg_data in messages_input:
        sender = msg_data.get("sender")
        text = msg_data.get("text")

        if sender is None or text is None:
            print(
                f"Warning: Skipping message due to missing sender or text: {msg_data}"
            )
            continue

        if sender == "user":
            processed_messages.append(HumanMessage(content=text))
        elif sender == "bot":
            # LangGraph typically uses AIMessage for bot/assistant responses
            processed_messages.append(AIMessage(content=text))
        else:
            print(f"Warning: Unknown sender type '{sender}' in message: {msg_data}")
            # Optionally, you could raise an error or handle other sender types
            # For now, we'll just skip unknown senders.
            # To include them as generic messages, you might use:
            # from langchain_core.messages import ChatMessage
            # processed_messages.append(ChatMessage(role=sender, content=text))

    return processed_messages


def get_structured_output_with_grounding(model, prompt, response_schema):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    google_search_tool = Tool(google_search=GoogleSearch())

    grounding_response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool], response_modalities=["TEXT"]
        ),
    )

    response_text = "\n".join(
        [x.text for x in grounding_response.candidates[0].content.parts]
    )
    grounding_chunks = grounding_response.candidates[
        0
    ].grounding_metadata.grounding_chunks
    entry_point_rendered = grounding_response.candidates[
        0
    ].grounding_metadata.search_entry_point.rendered_content

    structured_prompt = (
        f"{response_text}" "Convert the above into the respective JSON structure"
    )

    structured_response = client.models.generate_content(
        model=model,
        contents=structured_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": response_schema,
        },
    )

    return structured_response.parsed, grounding_chunks, entry_point_rendered


# Personal Details
def anonymize_user_personal_details(user_details) -> UserDetails:
    user_details_copy = user_details.copy()
    user_details_copy.name = "<ANONYMIZED>"
    return user_details_copy


# Investment Accounts


def retrieve_tickers_info(tickers: list[str]) -> list[TickerInformation]:
    prompt = f"""
Objective: Retrieve detailed, current financial information for each specified stock ticker using grounded web search.

Instructions:

1.  Identify Tickers: Process the following list of stock tickers:
    * `Tickers: {', '.join(tickers)}`

2.  Gather Detailed Data: For *each* ticker in the list, use grounded web search via available tools to find accurate, up-to-date values for *all* the fields listed below. Use reputable financial sources (e.g., major financial news sites, stock market data providers). Do not omit any fields. If precise real-time data isn't available for a specific field (like moving averages which might update slightly delayed), provide the latest reliable value or estimate from your sources. Ensure price data is as current as possible (as of {datetime.date.today().isoformat()}).

3.  Required Data Fields per Ticker:
    * `Ticker Symbol` (Map this to 'ticker' in the final JSON object)
    * `Company Name` (Map to 'company_name')
    * `Current Price` (Map to 'current_price', specify currency if not USD)
    * `Daily Price Change` (% - Map to 'daily_price_change')
    * `Weekly Price Change` (% - Map to 'weekly_price_change')
    * `Monthly Price Change` (% - Map to 'monthly_price_change')
    * `Year-to-Date Price Change` (% - Map to 'ytd_price_change')
    * `50-day Moving Average (MA50)` (Map to 'MA50')
    * `100-day Moving Average (MA100)` (Map to 'MA100')
    * `52 Week High` (Map to 'high_52_week')
    * `52 Week Low` (Map to 'low_52_week')
    * `Volume` (Shares traded today - Map to 'volume')
    * `Summary of latest market news` (1-2 relevant paragraphs - Map to 'summary_of_latest_market_news')
"""

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, list[TickerInformation]
    )

    return structured_response


def summary_of_assets(
    accounts: (
        list[InvestmentAccount]
        | list[TraditionalIRA]
        | list[RothIRA]
        | list[Retirement401K]
        | list[Roth401K]
        | list[HSAAccount]
    ),
) -> dict[str, TickerInformationInSummary]:
    """
    Provides a summary of all assets in the investment accounts.

    Returns:
        dict: Dictionary containing summarized information for each asset.
    """
    summary = defaultdict(
        lambda: {"total_quantity": 0, "weighted_cost_basis": 0, "count": 0}
    )

    for portfolio in accounts:
        for asset in portfolio.asset_distribution:
            ticker = asset.ticker.upper()
            quantity = float(asset.quantity)
            cost_basis = float(asset.average_cost_basis)

            s = summary[ticker]
            s["total_quantity"] += quantity
            s["weighted_cost_basis"] += cost_basis * quantity
            s["count"] += 1

    # Finalize averages and cost basis
    for ticker, data in summary.items():
        if data["total_quantity"] > 0:
            data["average_cost_basis"] = round(
                data["weighted_cost_basis"] / data["total_quantity"], 2
            )
        else:
            data["average_cost_basis"] = 0

        del data["weighted_cost_basis"]
        del data["count"]

    tickers = sorted(summary.keys())
    tickers_info = retrieve_tickers_info(tickers)

    for ticker_info in tickers_info:
        ticker = ticker_info.ticker.upper()
        if ticker in summary:
            summary[ticker].update(
                {
                    "company_name": ticker_info.company_name,
                    "current_price": ticker_info.current_price,
                    "daily_price_change": ticker_info.daily_price_change,
                    "weekly_price_change": ticker_info.weekly_price_change,
                    "monthly_price_change": ticker_info.monthly_price_change,
                    "ytd_price_change": ticker_info.ytd_price_change,
                    "MA50": ticker_info.MA50,
                    "MA100": ticker_info.MA100,
                    "high_52_week": ticker_info.high_52_week,
                    "low_52_week": ticker_info.low_52_week,
                    "volume": ticker_info.volume,
                    "summary_of_latest_market_news": ticker_info.summary_of_latest_market_news,
                }
            )

    for ticker, summary_item in summary.items():
        summary_item["total_value_change"] = round(
            summary_item["total_quantity"]
            * (summary_item["current_price"] - summary_item["average_cost_basis"]),
            2,
        )

        summary[ticker] = TickerInformationInSummary(**summary_item)

    return dict(summary)


def get_summary_of_investment_accounts() -> SummaryOfInvestmentAccounts:
    """
    Provides a summary of all investment accounts.
    """
    result = {
        "total_uninvested_amount": sum(
            account.uninvested_amount for account in user_data.INVESTMENT_ACCOUNTS
        ),
        "invested_securities_info": summary_of_assets(user_data.INVESTMENT_ACCOUNTS),
    }

    return SummaryOfInvestmentAccounts(**result)


def get_summary_of_credit_cards() -> SummaryOfCreditCards:
    """
    Provides a summary of all credit cards.
    """
    total_limit = 0
    available_credit = 0
    outstanding_debt = 0
    category_spending = defaultdict(float)
    rewards_summary = ""
    aprs = []
    weighted_average_interest_rate_applied_on_debt = 0
    weighted_apr = 0
    total_annual_fees = 0

    for card in user_data.CREDIT_CARDS:
        total_limit += float(card.total_limit)
        available_credit += float(card.current_limit)
        outstanding_debt += float(card.outstanding_debt)
        total_annual_fees += float(card.annual_fee)

        apr = float(card.interest)
        aprs.append(apr)

        if card.outstanding_debt > 0:
            weighted_average_interest_rate_applied_on_debt += (
                apr * card.outstanding_debt
            )

        for txn in card.current_billing_cycle_transactions:
            amount = float(txn.amount)
            category = txn.category.lower()
            category_spending[category] += amount

        rewards_summary += f"{card.name}: {card.rewards_summary}\n"

    if weighted_average_interest_rate_applied_on_debt > 0 and weighted_apr > 0:
        weighted_average_interest_rate_applied_on_debt = (
            weighted_average_interest_rate_applied_on_debt / weighted_apr
        )

    result = {
        "total_limit": round(total_limit, 2),
        "available_credit": round(available_credit, 2),
        "outstanding_debt": round(outstanding_debt, 2),
        "apr_range": [min(aprs), max(aprs)] if aprs else [0, 0],
        "spending_by_category": dict(category_spending),
        "weighted_average_interest_rate_applied_on_debt": round(
            weighted_average_interest_rate_applied_on_debt, 2
        ),
        "rewards_summary": rewards_summary,
        "total_annual_fees": round(total_annual_fees, 2),
    }

    return SummaryOfCreditCards(**result)


def get_summary_of_checking_or_savings_accounts(
    is_checking: bool,
) -> SummaryOfCheckingOrSavingsAccounts:
    """
    Provides a summary of all checking or savings accounts.
    """
    accounts = user_data.CHECKING_ACCOUNTS if is_checking else user_data.SAVING_ACCOUNTS

    total_balance = 0.0
    net_flow = 0.0
    interest_rates = []
    fee_totals = defaultdict(float)
    fee_counts = defaultdict(int)
    category_spending = defaultdict(float)
    rewards_summary = ""

    for acc in accounts:
        # Total Balance
        total_balance += acc.current_amount

        # Rewards Summary
        rewards_summary += acc.rewards_summary + "\n, "

        # Interest Ranges
        interest = acc.interest
        if interest is not None:
            interest_rates.append(interest)

        # Transaction Flow (Current Cycle)
        for txn in acc.current_billing_cycle_transactions:
            amount = float(txn.amount)
            category = txn.category.lower()
            category_spending[category] += amount
            net_flow += amount

        # Fee Aggregation
        fees = acc.fee

        fee_totals["monthly_fee"] += fees.monthly_fee
        fee_counts["monthly_fee"] += 1

        fee_totals["ATM_fee"] += fees.ATM_fee
        fee_counts["ATM_fee"] += 1

        fee_totals["overdraft_fee"] += fees.overdraft_fee
        fee_counts["overdraft_fee"] += 1

        fee_totals["no_minimum_balance_fee"] += fees.overdraft_fee
        fee_counts["no_minimum_balance_fee"] += 1

    def safe_avg(totals, counts, key):
        return round(totals[key] / counts[key], 2) if counts[key] else 0.0

    result = {
        "total_balance": round(total_balance, 2),
        "rewards_summary": rewards_summary,
        "net_flow_current_cycle": round(net_flow, 2),
        "category_spending": dict(category_spending),
        "interest_range": (
            [min(interest_rates), max(interest_rates)] if interest_rates else [0.0, 0.0]
        ),
        "fees_summary": {
            "no_minimum_balance_fee": safe_avg(
                fee_totals, fee_counts, "no_minimum_balance_fee"
            ),
            "monthly_fee_avg": safe_avg(fee_totals, fee_counts, "monthly_fee"),
            "atm_fee_avg": safe_avg(fee_totals, fee_counts, "ATM_fee"),
            "overdraft_fee_avg": safe_avg(fee_totals, fee_counts, "overdraft_fee"),
        },
    }

    return SummaryOfCheckingOrSavingsAccounts(**result)


def get_summary_of_traditional_ira_accounts() -> SummaryOfIRAAccounts:
    """
    Provides a summary of all of the traditional ira accounts.

    Returns:
        list: List of dictionaries containing summarized information for each of the traditional ira account.
    """
    result = {
        "total_uninvested_amount": sum(
            account.uninvested_amount for account in user_data.TRADITIONAL_IRAS
        ),
        "total_average_monthly_contribution": sum(
            account.average_monthly_contribution
            for account in user_data.TRADITIONAL_IRAS
        ),
        "invested_securities_info": summary_of_assets(user_data.TRADITIONAL_IRAS),
    }

    return SummaryOfIRAAccounts(**result)


def get_summary_of_roth_ira_accounts() -> SummaryOfIRAAccounts:
    """
    Provides a summary of all of the roth ira accounts.

    Returns:
        list: List of dictionaries containing summarized information for each of the roth ira account.
    """
    result = {
        "total_uninvested_amount": sum(
            account.uninvested_amount for account in user_data.ROTH_IRAS
        ),
        "total_average_monthly_contribution": sum(
            account.average_monthly_contribution for account in user_data.ROTH_IRAS
        ),
        "invested_securities_info": summary_of_assets(user_data.ROTH_IRAS),
    }

    return SummaryOfIRAAccounts(**result)


def get_summary_of_401k_accounts() -> SummaryOf401kAccounts:
    """
    Provides a summary of all of the 401(k) accounts.
    """
    result = {
        "total_uninvested_amount": sum(
            account.uninvested_amount for account in user_data.RETIREMENT_401KS
        ),
        "total_average_monthly_contribution": sum(
            account.average_monthly_contribution
            for account in user_data.RETIREMENT_401KS
        ),
        "employer_matches_summary": ", \n".join(
            account.employer_match for account in user_data.RETIREMENT_401KS
        ),
        "invested_securities_info": summary_of_assets(user_data.RETIREMENT_401KS),
    }

    return SummaryOf401kAccounts(**result)


def get_summary_of_roth_401k_accounts() -> SummaryOf401kAccounts:
    """
    Provides a summary of all of the Roth 401(k) accounts.
    """
    result = {
        "total_uninvested_amount": sum(
            account.uninvested_amount for account in user_data.ROTH_401KS
        ),
        "total_average_monthly_contribution": sum(
            account.average_monthly_contribution for account in user_data.ROTH_401KS
        ),
        "employer_matches_summary": ", \n".join(
            account.employer_match for account in user_data.ROTH_401KS
        ),
        "invested_securities_info": summary_of_assets(user_data.ROTH_401KS),
    }

    return SummaryOf401kAccounts(**result)


def get_summary_of_loan_accounts() -> SummaryOfLoanAccounts:
    """
    Provides a summary of all of the loan accounts.
    """
    total_loans = len(user_data.LOANS)
    total_outstanding = 0.0
    total_paid = 0.0
    total_principal = 0.0
    interest_rates = []
    loan_terms = []
    due_dates = []
    loan_types = set()
    collaterals_info = ""
    fee_totals = defaultdict(float)
    loans_with_late_fees = 0
    loans_with_prepay_penalty = 0
    active_loans = 0

    for loan in user_data.LOANS:
        # Basic financials
        outstanding = loan.outstanding_balance
        paid = loan.total_paid
        principal = loan.principal_left
        total_outstanding += outstanding
        total_paid += paid
        total_principal += principal
        collaterals_info += f"{loan.name}: {loan.collateral}\n "

        # Term & Interest
        try:
            term = int(loan.loan_term.split()[0])
            loan_terms.append(term)
        except:
            pass

        interest_rates.append(loan.interest_rate)

        # Loan types
        loan_types.add(loan.loan_type.lower())

        # Due Dates
        due_date = loan.payment_due_date
        if due_date:
            due_dates.append(due_date)

        # Fee Info
        fees = loan.current_outstanding_fees
        if fees.late_fee > 0:
            loans_with_late_fees += 1
        if fees.prepayment_penalty > 0:
            loans_with_prepay_penalty += 1

        fee_totals["late_fee"] = fees.late_fee
        fee_totals["prepayment_penalty"] = fees.prepayment_penalty
        fee_totals["origination_fee"] = fees.origination_fee
        fee_totals["other_fees"] = fees.other_fees

        # Determine if loan is still active
        end_date_str = loan.loan_end_date
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                if end_date > datetime.today():
                    active_loans += 1
            except:
                pass

    result = {
        "total_loans": total_loans,
        "total_outstanding_balance": round(total_outstanding, 2),
        "total_paid": round(total_paid, 2),
        "total_principal_remaining": round(total_principal, 2),
        "collaterals_info": collaterals_info,
        "loan_types": sorted(list(loan_types)),
        "active_loans": active_loans,
        "upcoming_due_dates": due_dates,
        "interest_rate_range": (
            [min(interest_rates), max(interest_rates)] if interest_rates else [0.0, 0.0]
        ),
        "loan_term_range_years": (
            [min(loan_terms), max(loan_terms)] if loan_terms else [0, 0]
        ),
        "loans_with_late_fees": loans_with_late_fees,
        "loans_with_prepayment_penalties": loans_with_prepay_penalty,
        "total_fees_summary": {
            "late_fees": round(fee_totals["late_fee"], 2),
            "prepayment_penalties": round(fee_totals["prepayment_penalty"], 2),
            "origination_fees": round(fee_totals["origination_fee"], 2),
            "other_fees": round(fee_totals["other_fees"], 2),
        },
    }

    return SummaryOfLoanAccounts(**result)


def get_summary_of_payroll_accounts() -> SummaryOfPayrollAccounts:
    """
    Provides a summary of all of the payroll accounts.
    """
    total_gross = 0.0
    total_net = 0.0
    total_bonus = 0.0
    total_federal = 0.0
    total_state = 0.0
    total_ss = 0.0
    total_medicare = 0.0
    total_other = 0.0
    ytd_max = 0.0

    states = defaultdict(float)
    frequencies = defaultdict(int)
    all_benefits = ""

    for record in user_data.PAYROLLS:
        total_gross += record.annual_income
        total_net += record.net_income
        total_bonus += record.bonus_income
        total_federal += record.federal_taxes_withheld
        total_state += record.state_taxes_withheld
        total_ss += record.social_security_withheld
        total_medicare += record.medicare_withheld
        total_other += record.other_deductions

        state = record.state.lower()
        states[state] += record.state_taxes_withheld

        freq = record.pay_frequency.lower()
        frequencies[freq] += 1

        all_benefits += record.benefits

        ytd = record.year_to_date_income
        if ytd > ytd_max:
            ytd_max = ytd

    result = {
        "total_entries": len(user_data.PAYROLLS),
        "total_annual_income": round(total_gross, 2),
        "total_net_income": round(total_net, 2),
        "total_bonus_income": round(total_bonus, 2),
        "total_withheld": {
            "federal": round(total_federal, 2),
            "state": round(total_state, 2),
            "social_security": round(total_ss, 2),
            "medicare": round(total_medicare, 2),
            "other": round(total_other, 2),
        },
        "withheld_by_state": {k: round(v, 2) for k, v in states.items()},
        "pay_frequencies": dict(frequencies),
        "most_recent_ytd_income": round(ytd_max, 2),
        "benefits_summary": all_benefits,
    }

    return SummaryOfPayrollAccounts(**result)


def get_summary_of_other_accounts() -> SummaryOfOtherAccounts:
    """
    Provides a summary of all of the other accounts.

    """
    return SummaryOfOtherAccounts(
        total_income=sum(account.total_income for account in user_data.OTHER_ACCOUNTS),
        total_debt=sum(account.total_debt for account in user_data.OTHER_ACCOUNTS),
    )


def get_summary_of_hsa_accounts() -> SummaryOfHSAAccounts:
    """
    Provides a summary of all of the HSA accounts.
    """
    result = {
        "total_uninvested_amount": sum(
            account.uninvested_amount for account in user_data.HSA_ACCOUNTS
        ),
        "total_average_monthly_contribution": sum(
            account.average_monthly_contribution for account in user_data.HSA_ACCOUNTS
        ),
        "invested_securities_info": summary_of_assets(user_data.HSA_ACCOUNTS),
    }

    return SummaryOfHSAAccounts(**result)


def get_user_financial_summary():
    """
    Provides a summary of the user's financial situation.
    """

    return {
        "user_details": str(anonymize_user_personal_details(user_data.USER_DETAILS)),
        "investment_summary": (
            str(get_summary_of_investment_accounts())
            if user_data.INVESTMENT_ACCOUNTS
            else "NO INVESTMENT ACCOUNTS"
        ),
        "credit_card_summary": (
            str(get_summary_of_credit_cards())
            if user_data.CREDIT_CARDS
            else "NO CREDIT CARDS"
        ),
        "checking_summary": (
            str(get_summary_of_checking_or_savings_accounts(is_checking=True))
            if user_data.CHECKING_ACCOUNTS
            else "NO CHECKING ACCOUNTS"
        ),
        "saving_summary": (
            str(get_summary_of_checking_or_savings_accounts(is_checking=False))
            if user_data.SAVING_ACCOUNTS
            else "NO SAVING ACCOUNTS"
        ),
        "loans_summary": (
            str(get_summary_of_loan_accounts()) if user_data.LOANS else "NO LOANS"
        ),
        "payrolls_summary": (
            str(get_summary_of_payroll_accounts())
            if user_data.PAYROLLS
            else "NO PAYROLLS"
        ),
        "traditional_ira_summary": (
            str(get_summary_of_traditional_ira_accounts())
            if user_data.TRADITIONAL_IRAS
            else "NO TRADITIONAL IRAS"
        ),
        "roth_ira_summary": (
            str(get_summary_of_roth_ira_accounts())
            if user_data.ROTH_IRAS
            else "NO ROTH IRAS"
        ),
        "retirement_401k_summary": (
            str(get_summary_of_401k_accounts())
            if user_data.RETIREMENT_401KS
            else "NO RETIREMENT 401K"
        ),
        "roth_401k_summary": (
            str(get_summary_of_roth_401k_accounts())
            if user_data.ROTH_401KS
            else "NO ROTH 401K"
        ),
        "hsa_summary": (
            str(get_summary_of_hsa_accounts())
            if user_data.HSA_ACCOUNTS
            else "NO HSA ACCOUNTS"
        ),
        "other_accounts_summary": (
            str(get_summary_of_other_accounts())
            if user_data.OTHER_ACCOUNTS
            else "NO OTHER ACCOUNTS"
        ),
    }
