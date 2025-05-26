from utils import *
from data_models import *
import user_data

from langchain_core.tools import tool


@tool
def search_and_answer(query: str) -> str:
    """Searches for relevant information based on the provided query and retrieves the best possible response.

    This function uses a web search to extract the most relevant, up-to-date information regarding the query. The search results
    are analyzed, and the most accurate or informative response is returned.

    Args:
      query (str): The query or question for which the information is being sought.

    Returns:
      str: The most relevant and accurate response based on the web search results.

    Example:
      If a user asks, "What is the weather in New York today?", the function will search the web for the current weather in New York
      and return the answer accordingly.

    """
    client = genai.Client()
    model_id = "gemini-2.0-flash"

    google_search_tool = Tool(google_search=GoogleSearch())

    response = client.models.generate_content(
        model=model_id,
        contents=query,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )

    return "\n".join([x.text for x in response.candidates[0].content.parts])


@tool
def get_user_details() -> UserDetails:
    """
    Retrieves the user's essential personal and financial context details.

    This tool fetches fundamental information about the user necessary for
    providing personalized financial advice. The retrieved data includes the user's
    age, state and country of residence, country of citizenship, tax filing status,
    and their tax residency status within their country of residence. For privacy,
    the user's full name is anonymized in the returned data.

    Args:
        None

    Returns:
        UserDetails: An object containing the user's anonymized details.
                     Fields include: `name` (anonymized), `age`, `state`, `country`,
                     `citizen_of`, `tax_filing_status`, `is_tax_resident`.

    Usage Examples:
        - User asks: "What are the contribution limits for retirement accounts for someone my age?"
        - User asks: "Are there any state-specific tax benefits I should know about?"
        - Bot needs to understand the user's general context before providing tax or residency-related advice.
    """
    return anonymize_user_personal_details(USER_DETAILS)


# Manage Tickers


@tool
def get_tickers_info(tickers: list[str]) -> str:
    """
    Retrieves comprehensive, real-time financial data for a list of stock tickers.

    This tool fetches detailed, up-to-date market information for each specified stock
    ticker symbol using external, grounded web search. The information includes the
    company's full name, current price, daily/weekly/monthly/YTD price changes,
    50-day and 100-day moving averages (MA50, MA100), 52-week high and low prices,
    current day's trading volume, and a concise summary of recent market news relevant
    to the ticker. It might return zero in some fields if the data is not available. Please
    skip the fields of the response that are not available.

    Args:
        tickers (list[str]): A list of stock ticker symbols for which to retrieve
                             information (e.g., ["AAPL", "MSFT", "TSLA"]).

    Returns:
        str: Information regarding the given list of tickers. Each ticker informaiton
             contains the detailed financial metrics and news summary.

             Detailed data for one ticker includes:
                - ticker (str): Unique stock symbol (e.g., "AAPL").
                - company_name (str): Full name of the company (e.g., "Apple Inc.").
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Price change percentage since the previous market close.
                - weekly_price_change (float): Price change percentage over the last 7 days.
                - monthly_price_change (float): Price change percentage over the last 30 days.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average price.
                - MA100 (float): 100-day moving average price.
                - high_52_week (float): Highest price the stock reached in the last 52 weeks.
                - low_52_week (float): Lowest price the stock reached in the last 52 weeks.
                - volume (int): Number of shares traded on the current day.
                - summary_of_latest_market_news (str): A 1-2 paragraph summary of recent news relevant to the ticker.
            Returns an empty string if the input list is empty or tickers are invalid.

    Usage Examples:
        - User asks: "What is the current price and news for Google?" -> Call with `tickers=['GOOG']`.
        - User asks: "Show me the performance details for TSLA and F." -> Call with `tickers=['TSLA', 'F']`.
        - Bot needs to provide current market context after identifying user's holdings (e.g., after calling `extract_unique_tickers_investment_accounts`).
    """
    return "\n\n".join(
        [
            f"{ticker_info.ticker} : {str(ticker_info)}"
            for ticker_info in retrieve_tickers_info(tickers)
        ]
    )


@tool
def identify_better_tickers(prev_tickers: list[str], criteria: str) -> str:
    """
    Identifies and retrieves data for potentially better investment tickers based on criteria.

    This tool leverages an LLM analysis combined with grounded web search. It analyzes
    a list of potentially existing tickers (`prev_tickers`) against user-defined investment
    `criteria` to suggest alternative or new stock tickers that might be "better"
    according to those criteria. It then fetches comprehensive, real-time financial data
    (identical to `get_investment_tickers_info`) for these suggested tickers. If
    `prev_tickers` is empty, suggestions are based solely on the `criteria`.

    Args:
        prev_tickers (list[str]): A list of stock ticker symbols for context or comparison.
                                  Can be empty if no specific comparison is needed.
        criteria (str): A natural language description defining what constitutes a "better"
                        investment (e.g., "higher dividend yield", "stronger YTD growth in AI sector",
                        "undervalued renewable energy stocks").

    Returns:
        str: Information regarding the tickers
            identified as potentially "better" based on the provided
            criteria and context. Returns an empty string if no suitable tickers are found.

            Detailed data for one ticker includes:
                - ticker (str): Unique stock symbol (e.g., "AAPL").
                - company_name (str): Full name of the company (e.g., "Apple Inc.").
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Price change percentage since the previous market close.
                - weekly_price_change (float): Price change percentage over the last 7 days.
                - monthly_price_change (float): Price change percentage over the last 30 days.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average price.
                - MA100 (float): 100-day moving average price.
                - high_52_week (float): Highest price the stock reached in the last 52 weeks.
                - low_52_week (float): Lowest price the stock reached in the last 52 weeks.
                - volume (int): Number of shares traded on the current day.
                - summary_of_latest_market_news (str): A 1-2 paragraph summary of recent news relevant to the ticker.

    Examples of when to invoke:
        - "Find stocks similar to AAPL but with a higher dividend yield."
        - "Suggest some alternative tech stocks with lower volatility than TSLA."
        - "Are there better-performing stocks in the healthcare sector compared to JNJ?"
        - "Identify some growth stocks based on recent performance."
    """

    prompt = f"""
Objective: Identify and provide detailed information on potential alternative stock investments that meet specific financial criteria, potentially offering a better profile compared to a set of reference tickers.

Instructions:

1.  Analyze Criteria: Carefully examine the provided investment `criteria`. Understand the key metrics and desired characteristics (e.g., high growth, low P/E, specific dividend yield, low volatility, sector focus).
    * `Criteria: {criteria}`

2.  Reference Tickers (Context): Use the `prev_tickers` as a baseline or context for comparison, if provided and relevant to the criteria. The goal is to find alternatives that align better with the `criteria` than these reference points.
    * `Reference Tickers: {" ".join(prev_tickers)}`

3.  Identify Alternatives: Based *strictly* on the `criteria`, search for and identify up to three potential alternative stock tickers that represent compelling investment opportunities according to those criteria. Prioritize tickers demonstrating strong alignment. (The reasoning for selecting these should be based on the criteria, even if not explicitly stated in the final output fields).

4.  Gather Detailed Data: For *each* suggested alternative ticker, use grounded web search via available tools to find accurate, up-to-date values for *all* the fields listed below. Use reputable financial sources (e.g., major financial news sites, stock market data providers). Do not omit any fields. If precise data isn't available, provide the best reliable estimate and note if necessary. Ensure price data is current (as of {datetime.date.today().isoformat()}).

5.  Required Data Fields per Alternative:
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

    (tickers, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, list[TickerInformation]
    )

    return "\n\n".join(
        [f"{ticker_info.ticker} : {str(ticker_info)}" for ticker_info in tickers]
    )


# Investment Accounts


@tool
def extract_unique_tickers_investment_accounts(
    investment_account_ids: list[str],
) -> list[str]:
    """
    Extracts a unique list of stock ticker symbols from specified investment accounts.

    This tool scans the asset holdings within one or more specific taxable investment
    accounts, identified by their IDs, and returns a consolidated list of all unique
    stock ticker symbols found. Tickers are returned in uppercase. This is useful for
    identifying the user's holdings in specific accounts before fetching detailed
    market data.

    Args:
        investment_account_ids (list[str]): A list of unique identifiers for the
                                           investment accounts to be scanned.

    Returns:
        list[str]: A list of unique uppercase stock ticker symbols held within the
                   specified accounts (e.g., ["AAPL", "MSFT", "GOOG"]). Returns an
                   empty list if no tickers are found or the accounts are empty/invalid.

    Usage Examples:
        - User asks: "What stocks do I own in my 'Tech Portfolio' account (ID: inv-123)?"
        - Bot needs to know which specific tickers to look up market data for, based on holdings in certain accounts (e.g., "Get quotes for stocks in accounts inv-123 and inv-456").
    """
    tickers = set()

    for id_ in investment_account_ids:
        record = INVESTMENT_ACCOUNTS_DICT.get(id_)
        assets = record.asset_distribution

        tickers = tickers | {asset.ticker.upper() for asset in assets}

    return list(tickers)


@tool
def summary_of_investment_accounts() -> SummaryOfInvestmentAccounts:
    """
    Provides a consolidated summary of all the user's standard (non-retirement, non-HSA, non-tax-advantaged) investment accounts.

    This tool aggregates data across all general investment accounts (brokerage accounts)
    to give an overview of total uninvested cash and detailed information about the combined holdings.

    Args:
        None

    Returns:
        SummaryOfInvestmentAccounts: An object containing the aggregated summary:
            - total_uninvested_amount (float): The total sum of uninvested cash across all standard investment accounts.
            - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary where keys are ticker symbols (str)
              and values are TickerInformationInSummary objects. Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).

    Examples of when to invoke:
        - "Give me a summary of my investment portfolio."
        - "How are my overall investments performing?"
        - "What's the total cash available in my brokerage accounts?"
        - "Show me the performance of all my stock holdings combined."
    """

    return get_summary_of_investment_accounts()


@tool
def get_investment_account(
    account_id: str,
) -> SummaryOfInvestmentAccounts | Exception:
    """
    Retrieves the summary details for a single, specific investment account identified by its ID.

    Use this tool when the user asks about a particular investment account (e.g., by name or ID).

    Args:
        account_id (str): The unique identifier (ID) of the specific investment account to retrieve details for.

    Returns:
        SummaryOfInvestmentAccounts | Exception:
            - If successful: A SummaryOfInvestmentAccounts object containing the summary for *only* the specified account.
              The structure includes:
                - total_uninvested_amount (float): Uninvested cash in *this* account.
                - invested_securities_info (dict[str, TickerInformationInSummary]): Holdings summary for assets *in this account only*.
                 Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).
            - If unsuccessful (e.g., account ID not found): An Exception object indicating the error.

    Examples of when to invoke:
        - "Show me the details of my 'Robinhood Brokerage' account."
        - "What stocks are in account ID 'INV789' and how are they doing?"
        - "How much cash is available in my 'Growth Portfolio' investment account?"
        - User selects a specific account from a list provided by `get_all_investment_account_ids_and_names`.
    """

    account = INVESTMENT_ACCOUNTS_DICT.get(account_id, None)

    if not account:
        # Return a more specific exception or error message structure if preferred
        return Exception(f"Investment account with ID '{account_id}' not found.")

    # Assuming summary_of_assets works correctly for a single account list
    result = {
        "total_uninvested_amount": account.uninvested_amount,
        "invested_securities_info": summary_of_assets([account]),
    }

    return SummaryOfInvestmentAccounts(**result)


@tool
def get_all_investment_account_ids_and_names() -> list[dict[str, str]]:
    """
    Fetches a list of all standard (non-retirement, non-HSA) investment accounts belonging to the user, showing their IDs and names.

    This tool is useful when the user needs to identify or select a specific investment account
    before requesting detailed information about it (e.g., using `get_investment_account`).

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries. Each dictionary represents one investment account and contains:
            - id (str): The unique identifier for the investment account.
            - name (str): The user-friendly name assigned to the investment account.
            (e.g., [{'id': 'INV123', 'name': 'Brokerage Account'}, {'id': 'INV456', 'name': 'Growth Portfolio'}])

    Examples of when to invoke:
        - "Which investment accounts do I have?"
        - "List all my brokerage accounts."
        - "I want to check the balance of one of my investment accounts, what are they called?"
        - User asks a question about an investment account without specifying which one, and the agent needs to clarify.
    """
    return [
        {"id": account.id, "name": account.name}
        for account in user_data.INVESTMENT_ACCOUNTS
    ]


# Traditional IRAs


@tool
def extract_unique_tickers_traditional_ira(
    traditional_ira_account_ids: list[str],
) -> list[str]:
    """
    Extracts a list of unique stock ticker symbols from the holdings of specified Traditional IRA accounts.

    Scans the asset distribution of the provided Traditional IRA account IDs and returns a
    deduplicated list of all ticker symbols found within them.

    Args:
        traditional_ira_account_ids (list[str]): A list containing the unique identifiers (IDs)
                                                 of the Traditional IRA accounts to scan.

    Returns:
        list[str]: A list of unique, uppercase stock ticker symbols (e.g., ["VOO", "BND"])
                   found within the specified Traditional IRA assets.

    Examples of when to invoke:
        - (Often used internally before calling get_investment_tickers_info for IRA holdings)
        - User query: "What tickers are in my Traditional IRA accounts 'TIRA-1' and 'TIRA-2'?"
    """
    tickers = set()

    for id_ in traditional_ira_account_ids:
        record = TRADITIONAL_IRAS_DICT.get(id_)
        assets = record.asset_distribution

        tickers = tickers | {asset.ticker.upper() for asset in assets}

    return list(tickers)


@tool
def summary_of_traditional_ira_accounts() -> SummaryOfIRAAccounts:
    """
    Provides a consolidated summary of all the user's Traditional IRA accounts.

    Aggregates data across all Traditional IRAs to give an overview of total uninvested cash,
    total average monthly contributions, and detailed information about the combined holdings.

    Args:
        None

    Returns:
        SummaryOfIRAAccounts: An object containing the aggregated summary:
            - total_uninvested_amount (float): Total sum of uninvested cash across all Traditional IRAs.
            - total_average_monthly_contribution (float): Sum of the average monthly contributions across all Traditional IRAs.
            - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary summarizing combined holdings across all Traditional IRAs.
              Keys are ticker symbols (str), values are TickerInformationInSummary objects.
              A dictionary where keys are ticker symbols (str)
              and values are TickerInformationInSummary objects. Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).

    Examples of when to invoke:
        - "Summarize my Traditional IRA accounts."
        - "How much cash do I have in my Traditional IRAs combined?"
        - "What's the total monthly contribution to my Traditional IRAs?"
        - "Show the overall performance of my Traditional IRA holdings."
    """
    return get_summary_of_traditional_ira_accounts()


@tool
def get_traditional_ira_account(
    traditional_ira_account_id: str,
) -> SummaryOfIRAAccounts | Exception:
    """
    Retrieves the summary details for a single, specific Traditional IRA account identified by its ID.

    Args:
        traditional_ira_account_id (str): The unique identifier (ID) of the specific Traditional IRA account.

    Returns:
        SummaryOfIRAAccounts | Exception:
            - If successful: A SummaryOfIRAAccounts object containing the summary for *only* the specified account:
                - total_uninvested_amount (float): Uninvested cash in *this* IRA.
                - total_average_monthly_contribution (float): Average monthly contribution to *this* IRA.
                - invested_securities_info (dict[str, TickerInformationInSummary]): Holdings summary for assets *in this IRA only*.
                    Each TickerInformationInSummary object provides:
                        - total_quantity (float): Total shares owned across all accounts for this ticker.
                        - average_cost_basis (float): Weighted average purchase price per share.
                        - company_name (str): Full name of the company.
                        - current_price (float): Latest market price per share.
                        - daily_price_change (float): Today's price change percentage.
                        - weekly_price_change (float): 7-day price change percentage.
                        - monthly_price_change (float): 30-day price change percentage.
                        - ytd_price_change (float): Year-to-date price change percentage.
                        - MA50 (float): 50-day moving average.
                        - MA100 (float): 100-day moving average.
                        - high_52_week (float): Highest price in the last 52 weeks.
                        - low_52_week (float): Lowest price in the last 52 weeks.
                        - volume (int): Today's trading volume.
                        - summary_of_latest_market_news (str): Recent news summary.
                        - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).
            - If unsuccessful (e.g., account ID not found): An Exception object indicating the error.

    Examples of when to invoke:
        - "Show details for my Traditional IRA with ID 'TIRA-XYZ'."
        - "What's the contribution amount and holdings for my 'Vanguard Trad IRA'?"
        - User selects a specific Traditional IRA from a list.
    """

    account = TRADITIONAL_IRAS_DICT.get(traditional_ira_account_id, None)

    if not account:
        return Exception(
            f"Traditional IRA account with ID '{traditional_ira_account_id}' not found."
        )

    result = {
        "total_uninvested_amount": account.uninvested_amount,
        "total_average_monthly_contribution": account.average_monthly_contribution,
        "invested_securities_info": summary_of_assets([account]),
    }

    return SummaryOfIRAAccounts(**result)


@tool
def get_all_traditional_ira_account_ids_and_names() -> list[dict[str, str]]:
    """
    Fetches a list of all Traditional IRA accounts belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific Traditional IRA before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one Traditional IRA:
            - id (str): The unique identifier for the account.
            - name (str): The user-friendly name of the account.
            (e.g., [{'id': 'TIRA-123', 'name': 'My Trad IRA'}, {'id': 'TIRA-456', 'name': 'Spousal Trad IRA'}])

    Examples of when to invoke:
        - "List my Traditional IRA accounts."
        - "What are the names of my Traditional IRAs?"
        - User asks about a Traditional IRA without specifying which one.
    """
    return [{"id": ira.id, "name": ira.name} for ira in user_data.TRADITIONAL_IRAS]


# Roth IRAs


@tool
def extract_unique_tickers_roth_ira(
    roth_ira_account_ids: list[str],
) -> list[str]:
    """
    Extracts a list of unique stock ticker symbols from the holdings of specified Roth IRA accounts.

    Scans the asset distribution of the provided Roth IRA account IDs and returns a
    deduplicated list of all ticker symbols found within them.

    Args:
        roth_ira_account_ids (list[str]): A list containing the unique identifiers (IDs)
                                          of the Roth IRA accounts to scan.

    Returns:
        list[str]: A list of unique, uppercase stock ticker symbols (e.g., ["FZROX", "QQQ"])
                   found within the specified Roth IRA assets.

    Examples of when to invoke:
        - (Often used internally before calling get_investment_tickers_info for Roth IRA holdings)
        - User query: "What tickers are in my Roth IRA account 'RIRA-Main'?"
    """
    tickers = set()

    for id_ in roth_ira_account_ids:
        record = ROTH_IRAS_DICT.get(id_)
        assets = record.asset_distribution

        tickers = tickers | {asset.ticker.upper() for asset in assets}

    return list(tickers)


@tool
def summary_of_roth_ira_accounts() -> SummaryOfIRAAccounts:
    """
    Provides a consolidated summary of all the user's Roth IRA accounts.

    Aggregates data across all Roth IRAs to give an overview of total uninvested cash,
    total average monthly contributions, and detailed information about the combined holdings.

    Args:
        None

    Returns:
        SummaryOfIRAAccounts: An object containing the aggregated summary:
            - total_uninvested_amount (float): Total sum of uninvested cash across all Roth IRAs.
            - total_average_monthly_contribution (float): Sum of the average monthly contributions across all Roth IRAs.
            - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary summarizing combined holdings across all Roth IRAs.
              Keys are ticker symbols (str), values are TickerInformationInSummary objects.

              Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).

    Examples of when to invoke:
        - "Give me a summary of my Roth IRAs."
        - "How much have I contributed monthly to my Roth accounts in total?"
        - "Show the performance of all my Roth IRA investments together."
    """

    return get_summary_of_roth_ira_accounts()


@tool
def get_roth_ira_account(
    roth_ira_account_id: str,
) -> SummaryOfIRAAccounts | Exception:
    """
    Retrieves the summary details for a single, specific Roth IRA account identified by its ID.

    Args:
        roth_ira_account_id (str): The unique identifier (ID) of the specific Roth IRA account.

    Returns:
        SummaryOfIRAAccounts | Exception:
            - If successful: A SummaryOfIRAAccounts object containing the summary for *only* the specified account:
                - total_uninvested_amount (float): Uninvested cash in *this* Roth IRA.
                - total_average_monthly_contribution (float): Average monthly contribution to *this* Roth IRA.
                - invested_securities_info (dict[str, TickerInformationInSummary]): Holdings summary for assets *in this Roth IRA only*.
                Each TickerInformationInSummary object provides:
                    - total_quantity (float): Total shares owned across all accounts for this ticker.
                    - average_cost_basis (float): Weighted average purchase price per share.
                    - company_name (str): Full name of the company.
                    - current_price (float): Latest market price per share.
                    - daily_price_change (float): Today's price change percentage.
                    - weekly_price_change (float): 7-day price change percentage.
                    - monthly_price_change (float): 30-day price change percentage.
                    - ytd_price_change (float): Year-to-date price change percentage.
                    - MA50 (float): 50-day moving average.
                    - MA100 (float): 100-day moving average.
                    - high_52_week (float): Highest price in the last 52 weeks.
                    - low_52_week (float): Lowest price in the last 52 weeks.
                    - volume (int): Today's trading volume.
                    - summary_of_latest_market_news (str): Recent news summary.
                    - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).
            - If unsuccessful (e.g., account ID not found): An Exception object indicating the error.

    Examples of when to invoke:
        - "What are the holdings in my Roth IRA ID 'RIRA-GROWTH'?"
        - "Show the contribution and balance for my 'Fidelity Roth IRA'."
        - User selects a specific Roth IRA from a list.
    """

    account = ROTH_IRAS_DICT.get(roth_ira_account_id, None)

    if not account:
        return Exception(f"Roth IRA account with ID '{roth_ira_account_id}' not found.")

    result = {
        "total_uninvested_amount": account.uninvested_amount,
        "total_average_monthly_contribution": account.average_monthly_contribution,
        "invested_securities_info": summary_of_assets([account]),
    }

    return SummaryOfIRAAccounts(**result)


@tool
def get_all_roth_ira_account_ids_and_names() -> list[dict[str, str]]:
    """
    Fetches a list of all Roth IRA accounts belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific Roth IRA before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one Roth IRA:
            - id (str): The unique identifier for the account.
            - name (str): The user-friendly name of the account.
            (e.g., [{'id': 'RIRA-1', 'name': 'Primary Roth'}, {'id': 'RIRA-2', 'name': 'Old Roth Rollover'}])

    Examples of when to invoke:
        - "List my Roth IRA accounts."
        - "What Roth IRAs do I have?"
        - User asks about a Roth IRA without specifying which one.
    """
    return [
        {"id": roth_ira.id, "name": roth_ira.name} for roth_ira in user_data.ROTH_IRAS
    ]


# Retirement 401(k)s


@tool
def extract_unique_tickers_401k(
    retirment_401k_account_ids: list[str],
) -> list[str]:
    """
    Extracts a list of unique investment tickers (usually mutual funds or ETFs) from specified Traditional 401(k) accounts.

    Scans the asset distribution of the provided Traditional 401(k) account IDs and returns a
    deduplicated list of all ticker symbols found within them.

    Args:
        retirement_401k_account_ids (list[str]): A list containing the unique identifiers (IDs)
                                                  of the Traditional 401(k) accounts to scan.

    Returns:
        list[str]: A list of unique, uppercase investment ticker symbols (e.g., ["VFIAX", "VTSAX"])
                   found within the specified Traditional 401(k) assets.

    Examples of when to invoke:
        - (Often used internally before calling get_investment_tickers_info for 401(k) holdings)
        - User query: "What funds are in my main 401(k) account 'EMP401K-TRAD'?"
    """
    tickers = set()

    for id_ in retirment_401k_account_ids:
        record = RETIREMENT_401KS_DICT.get(id_)
        assets = record.asset_distribution

        tickers = tickers | {asset.ticker.upper() for asset in assets}

    return list(tickers)


@tool
def summary_of_401k_accounts() -> SummaryOf401kAccounts:
    """
    Provides a consolidated summary of all the user's Traditional 401(k) accounts.

    Aggregates data across all Traditional 401(k)s, including total uninvested cash, total contributions,
    employer match details, and combined investment holdings information.

    Args:
        None

    Returns:
        SummaryOf401kAccounts: An object containing the aggregated summary:
            - total_uninvested_amount (float): Total sum of uninvested cash across all Traditional 401(k)s.
            - total_average_monthly_contribution (float): Sum of the user's average monthly contributions across all Traditional 401(k)s.
            - employer_matches_summary (str): A combined summary of employer matching policies across all Traditional 401(k)s.
            - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary summarizing combined holdings (usually funds/ETFs) across all Traditional 401(k)s.
              Keys are ticker symbols (str), values are TickerInformationInSummary objects.

            Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).

    Examples of when to invoke:
        - "Summarize my 401(k) accounts."
        - "What's the total employer match I'm getting across my 401(k)s?"
        - "Show the overall performance of my 401(k) investments."
        - "How much cash is sitting uninvested in my 401(k)s?"
    """

    return get_summary_of_401k_accounts()


@tool
def get_401k_account(
    retirement_401k_account_id: str,
) -> SummaryOf401kAccounts | Exception:
    """
    Retrieves the summary details for a single, specific Traditional 401(k) account identified by its ID.

    Args:
        retirement_401k_account_id (str): The unique identifier (ID) of the specific Traditional 401(k) account.

    Returns:
        SummaryOf401kAccounts | Exception:
            - If successful: A SummaryOf401kAccounts object containing the summary for *only* the specified account:
                - total_uninvested_amount (float): Uninvested cash in *this* 401(k).
                - total_average_monthly_contribution (float): User's average monthly contribution to *this* 401(k).
                - employer_matches_summary (str): Employer matching policy for *this* 401(k).
                - invested_securities_info (dict[str, TickerInformationInSummary]): Holdings summary for assets *in this 401(k) only*.
            Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).
            - If unsuccessful (e.g., account ID not found): An Exception object indicating the error.

    Examples of when to invoke:
        - "Show details for my 401(k) with ID 'EMP401K-1'."
        - "What is the employer match for my 'Current Job 401k'?"
        - "List the funds and their performance in my main 401(k)."
        - User selects a specific 401(k) from a list.
    """

    account = RETIREMENT_401KS_DICT.get(retirement_401k_account_id, None)

    if not account:
        return Exception(
            f"Traditional 401(k) account with ID '{retirement_401k_account_id}' not found."
        )

    result = {
        "total_uninvested_amount": account.uninvested_amount,
        "total_average_monthly_contribution": account.average_monthly_contribution,
        "employer_matches_summary": account.employer_match,
        "invested_securities_info": summary_of_assets([account]),
    }

    return SummaryOf401kAccounts(**result)


@tool
def get_all_401k_account_ids_and_names() -> list[dict[str, str]]:
    """
    Fetches a list of all Traditional 401(k) accounts belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific Traditional 401(k) before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one Traditional 401(k):
            - id (str): The unique identifier for the account.
            - name (str): The user-friendly name of the account.
            (e.g., [{'id': 'EMP401K-1', 'name': 'Current Job 401k'}, {'id': 'OLD401K-2', 'name': 'Old Employer 401k'}])

    Examples of when to invoke:
        - "List my 401(k) accounts."
        - "What are the names of my Traditional 401(k)s?"
        - User asks about a 401(k) without specifying which one.
    """
    return [
        {"id": ret_401k.id, "name": ret_401k.name}
        for ret_401k in user_data.RETIREMENT_401KS
    ]


# Roth 401(k)s
@tool
def extract_unique_tickers_roth_401k(
    roth_401k_account_ids: list[str],
) -> list[str]:
    """
    Extracts a list of unique investment tickers (usually mutual funds or ETFs) from specified Roth 401(k) accounts.

    Scans the asset distribution of the provided Roth 401(k) account IDs and returns a
    deduplicated list of all ticker symbols found within them.

    Args:
        roth_401k_account_ids (list[str]): A list containing the unique identifiers (IDs)
                                           of the Roth 401(k) accounts to scan.

    Returns:
        list[str]: A list of unique, uppercase investment ticker symbols (e.g., ["FXAIX", "TARGETFUND2050"])
                   found within the specified Roth 401(k) assets.

    Examples of when to invoke:
        - (Often used internally before calling get_investment_tickers_info for Roth 401(k) holdings)
        - User query: "What funds are in my Roth 401(k) 'MyCompany-Roth'?"
    """
    tickers = set()

    for id_ in roth_401k_account_ids:
        record = ROTH_401KS_DICT.get(id_)
        assets = record.asset_distribution

        tickers = tickers | {asset.ticker.upper() for asset in assets}

    return list(tickers)


@tool
def summary_of_roth_401k_accounts() -> SummaryOf401kAccounts:
    """
    Provides a consolidated summary of all the user's Roth 401(k) accounts.

    Aggregates data across all Roth 401(k)s, including total uninvested cash, total contributions,
    employer match details (which typically apply to the total 401k contribution including Roth),
    and combined investment holdings information.

    Args:
        None

    Returns:
        SummaryOf401kAccounts: An object containing the aggregated summary:
            - total_uninvested_amount (float): Total sum of uninvested cash across all Roth 401(k)s.
            - total_average_monthly_contribution (float): Sum of the user's average monthly contributions to Roth 401(k)s.
            - employer_matches_summary (str): A combined summary of employer matching policies relevant to these accounts.
            - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary summarizing combined holdings across all Roth 401(k)s.
              Keys are ticker symbols (str), values are TickerInformationInSummary objects.

            Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).

    Examples of when to invoke:
        - "Summarize my Roth 401(k) accounts."
        - "How much am I contributing monthly to my Roth 401(k)s?"
        - "Show the performance of my Roth 401(k) investments."
    """

    return get_summary_of_roth_401k_accounts()


@tool
def get_roth_401k_account(
    roth_401k_account_id: str,
) -> SummaryOf401kAccounts | Exception:
    """
    Retrieves the summary details for a single, specific Roth 401(k) account identified by its ID.

    Args:
        roth_401k_account_id (str): The unique identifier (ID) of the specific Roth 401(k) account.

    Returns:
        SummaryOf401kAccounts | Exception:
            - If successful: A SummaryOf401kAccounts object containing the summary for *only* the specified account:
                - total_uninvested_amount (float): Uninvested cash in *this* Roth 401(k).
                - total_average_monthly_contribution (float): User's average monthly contribution to *this* Roth 401(k).
                - employer_matches_summary (str): Employer matching policy relevant to *this* account.
                - invested_securities_info (dict[str, TickerInformationInSummary]): Holdings summary for assets *in this Roth 401(k) only*.

                Each TickerInformationInSummary object provides:
                - total_quantity (float): Total shares owned across all accounts for this ticker.
                - average_cost_basis (float): Weighted average purchase price per share.
                - company_name (str): Full name of the company.
                - current_price (float): Latest market price per share.
                - daily_price_change (float): Today's price change percentage.
                - weekly_price_change (float): 7-day price change percentage.
                - monthly_price_change (float): 30-day price change percentage.
                - ytd_price_change (float): Year-to-date price change percentage.
                - MA50 (float): 50-day moving average.
                - MA100 (float): 100-day moving average.
                - high_52_week (float): Highest price in the last 52 weeks.
                - low_52_week (float): Lowest price in the last 52 weeks.
                - volume (int): Today's trading volume.
                - summary_of_latest_market_news (str): Recent news summary.
                - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).
            - If unsuccessful (e.g., account ID not found): An Exception object indicating the error.

    Examples of when to invoke:
        - "Show details for my Roth 401(k) ID 'ROTH401K-XYZ'."
        - "What funds are in my 'Company Roth 401k'?"
        - User selects a specific Roth 401(k) from a list.
    """

    account = ROTH_401KS_DICT.get(roth_401k_account_id, None)

    if not account:
        return Exception(
            f"Roth 401(k) account with ID '{roth_401k_account_id}' not found."
        )

    result = {
        "total_uninvested_amount": account.uninvested_amount,
        "total_average_monthly_contribution": account.average_monthly_contribution,
        "employer_matches_summary": account.employer_match,
        "invested_securities_info": summary_of_assets([account]),
    }

    return SummaryOf401kAccounts(**result)


@tool
def get_all_roth_401k_account_ids_and_names() -> list[dict[str, str]]:
    """
    Fetches a list of all Roth 401(k) accounts belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific Roth 401(k) before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one Roth 401(k):
            - id (str): The unique identifier for the account.
            - name (str): The user-friendly name of the account.
            (e.g., [{'id': 'ROTH401K-1', 'name': 'My Roth 401k Component'}])

    Examples of when to invoke:
        - "List my Roth 401(k) accounts."
        - "Do I have a Roth 401(k)?"
        - User asks about a Roth 401(k) without specifying which one.
    """
    return [
        {"id": roth_401k.id, "name": roth_401k.name}
        for roth_401k in user_data.ROTH_401KS
    ]


# Credit Cards


@tool
def summary_of_credit_cards() -> SummaryOfCreditCards:
    """
    Provides a consolidated summary of all the user's credit card accounts.

    Aggregates data across all credit cards held by the user, offering a high-level view of their
    overall credit situation, spending patterns, debt levels, and rewards potential.

    Args:
        None

    Returns:
        SummaryOfCreditCards: An object containing the aggregated summary:
            - total_limit (float): The sum of credit limits across all cards.
            - available_credit (float): The total credit currently available (sum of limits minus outstanding balances).
            - outstanding_debt (float): The total amount currently owed across all cards.
            - apr_range (list[float]): A list containing the minimum and maximum Annual Percentage Rates (APRs) among the user's cards [min_apr, max_apr].
            - spending_by_category (dict[str, float]): A dictionary showing total spending (negative values) or credits (positive values)
                                                      per category across all cards in the current billing cycle. Keys are categories (str), values are amounts (float).
            - weighted_average_interest_rate_applied_on_debt (float): The average interest rate the user is paying, weighted by the amount of debt on each card carrying a balance.
            - rewards_summary (str): A combined textual summary of the rewards programs for all the user's cards.
            - total_annual_fees (float): The total annual fees for all cards combined.

    Examples of when to invoke:
        - "Give me a summary of my credit cards."
        - "What's my total credit card debt and available credit?"
        - "Show my credit card spending by category for this month."
        - "What's the average interest rate I'm paying on my credit card debt?"
    """
    return get_summary_of_credit_cards()


@tool
def get_all_credit_cards():
    """
    Retrieves a list of all credit cards belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific credit card before requesting detailed information about it (e.g., using `get_credit_card`).

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one credit card:
            - id (str): The unique identifier for the credit card account.
            - name (str): The user-friendly name or type of the credit card (e.g., "Visa Signature", "Amex Gold").
            (e.g., [{'id': 'CC1', 'name': 'Chase Sapphire Preferred'}, {'id': 'CC2', 'name': 'Citi Double Cash'}])

    Examples of when to invoke:
        - "List all my credit cards."
        - "What credit cards do I have with you?"
        - User asks about a specific card's balance or limit without specifying which card.
    """
    return [{"id": card.id, "name": card.name} for card in user_data.CREDIT_CARDS]


@tool
def get_credit_card(card_id: str) -> CreditCard | Exception:
    """
    Retrieves detailed information for a single, specific credit card identified by its ID.

    Args:
        card_id (str): The unique identifier (ID) of the specific credit card to retrieve details for.

    Returns:
        CreditCard | str:
            - If successful: A CreditCard object containing detailed information about the specified card:
                - id (str): Unique identifier for the card.
                - name (str): Name of the card.
                - type (str): Type of card (e.g., "Visa", "Mastercard").
                - total_limit (float): The total credit limit for this card.
                - current_limit (float): The currently available credit on this card.
                - rewards_summary (str): Description of the rewards program for this specific card.
                - interest (float): The Annual Percentage Rate (APR) for this card.
                - outstanding_debt (float): The current balance or debt owed on this card.
                - current_billing_cycle_transactions (list[BillingCycleTransaction]): A list of transactions for the current cycle. Each transaction includes:
                    - amount (float): Transaction amount (positive for credit/payment, negative for debit/purchase).
                    - category (str): Spending category assigned to the transaction.
                - annual_fee (float): The annual fee for this card.
            - If unsuccessful (e.g., card ID not found): A string indicating "Card not found".

    Examples of when to invoke:
        - "Show me the details for my Chase Sapphire card (ID CC1)."
        - "What is the current balance and limit on my Citi card (ID CC2)?"
        - "List the recent transactions for my Amex Gold card."
        - User selects a specific card from the list provided by `get_all_credit_cards`.
    """

    card = CREDIT_CARDS_DICT.get(card_id, None)

    if not card:
        return Exception(f"Credit Card with ID: {card_id} not found")

    return card


@tool
def optimize_spending_in_a_category(
    open_to_new_cards: bool, category: str
) -> OptimalCreditCardSpending:
    """
    Analyzes user's spending in a specific category and suggests optimal credit card usage, potentially including new card recommendations, using grounded web search.

    This tool reviews the user's current credit cards and spending patterns within the specified category.
    Based on whether the user is open to new cards, it provides a plan to maximize rewards or minimize costs
    for that category, possibly suggesting better-suited cards available in the market.

    Args:
        open_to_new_cards (bool): Indicates if the user is willing to apply for new credit cards (True) or
                                  prefers to optimize using their existing cards (False).
        category (str): The spending category to optimize (e.g., "Groceries", "Travel", "Gas", "Dining").

    Returns:
        OptimalCreditCardSpending: An object containing suggestions:
            - better_credit_cards (list[BasicCreditCardDetails]): A list of recommended credit cards (can be empty if optimizing with existing cards or no better options found). Each object includes:
                - name (str): The name of the suggested credit card.
                - annual_fee (float): The annual fee of the card.
                - rewards_summary (str): A summary of the card's rewards structure, especially for the target category.
            - plan_for_optimization (str): A textual description of the recommended strategy. This might involve using a specific existing card, applying for a new card, or a combination.

    Examples of when to invoke:
        - "How can I maximize rewards on my grocery spending? I'm open to new cards."
        - "Which of my current cards is best for travel purchases?"
        - "Suggest the best card for gas, I don't want a new one right now."
        - "Optimize my dining expenses."
    """

    user_intent_on_new_cards = (
        "The user is open to applying for new credit cards if they offer significant benefits for this category."
        if open_to_new_cards
        else "The user wants to optimize spending using only their existing credit cards."
    )

    summary_of_user_cc = get_summary_of_credit_cards()

    category_spending = "".join(
        f"${amount} is being spent on {category}\n"
        for category, amount in summary_of_user_cc.spending_by_category.items()
    )

    current_cc = [
        BasicCreditCardDetails(
            name=cc.name,
            annual_fee=cc.annual_fee,
            rewards_summary=cc.rewards_summary,
        )
        for cc in user_data.CREDIT_CARDS
    ]

    prompt = f"""
**Context:**
* User's current credit cards details:
{"".join(f"- {str(cc)} " for cc in current_cc)}
* User's stance on new cards: {user_intent_on_new_cards}
* User's spending context (e.g., recent category spending): {category_spending}
* Optimization Focus Category: '{category}'

**Your Task:** Generate a credit card optimization plan focused on the '{category}' spending category, strictly respecting the user's stated stance on acquiring new cards.

**Instructions:**

1.  **Analyze Existing Cards:** Review the user's current cards (`current_cc_details`). Identify which existing card(s) offer the best rewards (cash back, points, miles) or benefits specifically for the '{category}' spending category. Note their relevant reward rates or terms.

2.  **Consider New Cards (Conditionally based on User Stance):**
    * **Check User Intent:** Evaluate the value of `User's stance on new cards`.
    * **IF** the user's stance indicates they **ARE OPEN** or willing to consider new cards:
        * Search for potentially better credit cards currently available in the market (use grounded search). Focus on cards offering demonstrably superior rewards or benefits *specifically* for '{category}' spending compared to the user's *best existing card* for this category.
        * Identify only 1 or 2 top alternatives if strong candidates exist. Keep the list concise.
    * **ELSE (IF** the user's stance indicates they **ARE NOT OPEN** or unwilling to consider new cards):
        * **DO NOT** search for, suggest, or mention any new credit cards in the plan or the output list. The analysis should focus *exclusively* on optimizing with existing cards.

3.  **Develop Optimization Plan (`plan_for_optimization`):** Create a clear, actionable plan.
    * The plan **MUST** first state which **EXISTING** card(s) should be prioritized for '{category}' purchases and explain why (mentioning the relevant reward rate or benefit). This is the primary recommendation.
    * **ONLY IF** the user is open to new cards AND you identified a superior new card in Step 2, the plan MAY *additionally* suggest considering that specific new card. Clearly state its name, key benefit for the category (e.g., reward rate), and annual fee. Contrast its benefit against the best existing card for context.

"""

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, OptimalCreditCardSpending
    )

    return structured_response


@tool
def optimize_spending_with_cc_all_categories(
    open_to_new_cards: bool,
) -> OptimalCreditCardSpending:
    """
    Analyzes user's overall credit card spending across all categories and suggests an optimal usage strategy, potentially including new card recommendations, using grounded web search.

    Reviews the user's complete spending profile (from credit card summaries) and current cards.
    Provides a holistic plan to maximize rewards or benefits across all spending, considering whether the user
    is open to new cards. It identifies which cards (existing or new) are best suited for the user's main spending categories.

    Args:
        open_to_new_cards (bool): Indicates if the user is willing to apply for new credit cards (True) or
                                  prefers to optimize using their existing cards (False).

    Returns:
        OptimalCreditCardSpending: An object containing suggestions:
            - better_credit_cards (list[BasicCreditCardDetails]): A list of recommended new credit cards based on overall spending (can be empty). Each object includes:
                - name (str): Card name.
                - annual_fee (float): Annual fee.
                - rewards_summary (str): Overview of rewards structure, highlighting benefits for user's top categories.
            - plan_for_optimization (str): A textual description of the overall strategy, detailing which card to use for which major spending category (e.g., "Use Card A for travel, Card B for groceries, consider new Card C for general spending...").

    Examples of when to invoke:
        - "Analyze my credit card spending and suggest how I can optimize my rewards overall."
        - "Are my current credit cards the best fit for my spending habits? I'm open to suggestions."
        - "Help me create a strategy to use my existing cards more effectively across different categories."
        - "Recommend a credit card setup for maximizing cash back based on my spending."
    """
    user_intent_on_new_cards = (
        "User is open to new cards"
        if open_to_new_cards
        else "User is not open to new cards"
    )

    summary_of_user_cc = get_summary_of_credit_cards()

    category_spending = "".join(
        f"${amount} is being spent on {category}\n"
        for category, amount in summary_of_user_cc.spending_by_category.items()
    )

    current_cc = [
        BasicCreditCardDetails(
            name=cc.name,
            annual_fee=cc.annual_fee,
            rewards_summary=cc.rewards_summary,
        )
        for cc in user_data.CREDIT_CARDS
    ]

    current_cc_details_str = "\n".join(f"- {str(cc)} " for cc in current_cc)

    prompt = f"""
Context:
- User's current credit cards and their rewards:
{current_cc_details_str}
- User's stance on new cards: {user_intent_on_new_cards}
- User's spending summary (by category, showing money spent):
{category_spending}
- Current Date for data freshness reference: {datetime.date.today().isoformat()}

Task: Create a holistic credit card optimization strategy based on the user's spending across their major categories. The strategy MUST strictly respect the user's stated preference regarding new cards.

Instructions:

1. Analyze Spending and Existing Cards: Review the user's spending summary to identify the top 3-5 spending categories (highest absolute spending). For these top categories, determine which of the user's CURRENT cards offer the best rewards (e.g., highest cash back percentage, best points value) based on their rewards summary.

2. Consider New Cards (Conditionally based on User Stance):
   CHECK USER INTENT: Is the user open to new cards? Refer to 'User's stance on new cards' above.
   IF the user IS OPEN to new cards:
     Use grounded search to find 1 or 2 potential new credit cards available now that could SIGNIFICANTLY improve rewards in the user's top spending categories where existing cards are weak OR offer superior overall value/cash back based on the total spending pattern. Focus on cards with clear benefits over existing ones.
   ELSE (the user IS NOT OPEN to new cards):
     DO NOT search for, suggest, or include any new credit cards in the output. The optimization plan MUST rely solely on the user's existing cards.

3. Develop Optimization Plan (`plan_for_optimization`): Create a clear, actionable strategy string. This plan MUST detail:
   - Which EXISTING card to use for each of the user's top 3-5 spending categories identified in step 1 to maximize current rewards. Mention the card name and the relevant reward.
   - ONLY IF the user is open to new cards AND a suitable new card was identified in step 2: Suggest considering that specific new card. Explain clearly which spending category(ies) it would benefit most, mention its name, annual fee, and the specific reward rate/benefit that makes it better than the existing options for that spending.

"""

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, OptimalCreditCardSpending
    )

    return structured_response


@tool
def get_better_cards_for_category(category: str, criteria: str) -> str:
    """
    Retrieves a list of credit cards available in the market that are well-suited for a specific spending category based on given criteria, using grounded web search.

    This tool searches for and lists credit cards (not necessarily held by the user) that excel in the specified category according to the user's criteria (e.g., highest cash back, no annual fee).

    Args:
        category (str): The spending category of interest (e.g., "Travel", "Online Shopping", "Restaurants").
        criteria (str): The specific features or criteria the user is looking for in a card for this category
                        (e.g., "highest cash back rate", "no annual fee", "travel points transferable to partners", "introductory 0% APR offer").

    Returns:
        str : A list of credit card options matching the criteria. Each object includes:
            - name (str): The name of the credit card.
            - annual_fee (float): The card's annual fee.
            - rewards_summary (str): A summary of the card's rewards structure, highlighting its relevance to the specified category and criteria.
            (The list might contain 5 or more options if available).

    Examples of when to invoke:
        - "List the top 5 cash back cards for groceries with no annual fee."
        - "Find travel credit cards that offer airport lounge access."
        - "What are some good credit cards for online shopping rewards?"
        - "Show me restaurant cards with the highest reward points."
    """

    prompt = f"""
Context:
- Search Focus Category: '{category}'
- Desired Card Criteria: '{criteria}'
- Current Date for data freshness reference: {datetime.date.today().isoformat()}

Task: Search the general credit card market for currently available cards that are strong matches for the specified '{category}' based on the '{criteria}'.

Instructions:

1. Understand Requirements: Analyze the '{category}' and the desired '{criteria}' (e.g., highest rate, no fee, specific perks).

2. Market Search: Use grounded search to identify several (aiming for about 3-5, if available) generally available credit cards that excel in the '{category}' according to the '{criteria}'. Prioritize cards with clear and strong alignment currently offered to new applicants.

3. Gather Key Details: For each identified card, retrieve the following details accurately:
   - Name (Card's official name)
   - Annual Fee (Use 0.0 if none)
   - Rewards Summary (Provide a concise summary focusing on how its rewards/benefits apply to the '{category}' and meet the '{criteria}'. Mention specific rates or point multipliers for the category if possible.)
"""

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, list[BasicCreditCardDetails]
    )

    return "\n".join([str(card) for card in structured_response])


# Checking Accounts


@tool
def summary_of_cheking_accounts() -> SummaryOfCheckingOrSavingsAccounts:
    """
    Provides a consolidated summary of all the user's checking accounts.

    Aggregates data across all checking accounts, offering insights into total balance, cash flow,
    spending patterns, interest earned (if any), and common fees.

    Args:
        None

    Returns:
        SummaryOfCheckingOrSavingsAccounts: An object containing the aggregated summary:
            - total_balance (float): The sum of current balances across all checking accounts.
            - rewards_summary (str): A combined textual summary of any rewards or benefits associated with the checking accounts.
            - net_flow_current_cycle (float): The net change in total balance across all checking accounts during the current billing cycle (Total Inflows - Total Outflows).
            - category_spending (dict[str, float]): A dictionary showing total spending (negative values) or credits (positive values) per category originating from all checking accounts in the current cycle.
            - interest_range (list[float]): A list containing the minimum and maximum interest rates (APY) offered across the checking accounts [min_apy, max_apy]. Often [0.0, 0.0] for checking.
            - fees_summary (dict[str, float]): A dictionary summarizing average fees across the accounts (e.g., {'monthly_fee_avg': 5.00, 'atm_fee_avg': 2.50, ...}). Keys include:
                - no_minimum_balance_fee_avg
                - monthly_fee_avg
                - atm_fee_avg
                - overdraft_fee_avg

    Examples of when to invoke:
        - "Summarize my checking accounts."
        - "What's the total balance in my checking?"
        - "How much did I spend from my checking accounts this month by category?"
        - "What's the net cash flow in my checking accounts recently?"
    """

    return get_summary_of_checking_or_savings_accounts(is_checking=True)


@tool
def get_all_checking_accounts() -> list[dict[str, str]]:
    """
    Retrieves a list of all checking accounts belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific checking account before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one checking account:
            - id (str): The unique identifier for the checking account.
            - name (str): The user-friendly name of the account (e.g., "Primary Checking", "Joint Checking").
            (e.g., [{'id': 'CHK1', 'name': 'Wells Fargo Checking'}, {'id': 'CHK2', 'name': 'Ally Spending Account'}])

    Examples of when to invoke:
        - "List my checking accounts."
        - "What are the names of my checking accounts?"
        - User asks about a transaction or balance without specifying which checking account.
    """
    return [
        {"id": account.id, "name": account.name}
        for account in user_data.CHECKING_ACCOUNTS
    ]


@tool
def get_checking_account(account_id: str) -> CheckingOrSavingsAccount | Exception:
    """
    Retrieves detailed information for a single, specific checking account identified by its ID.

    Args:
        account_id (str): The unique identifier (ID) of the specific checking account.

    Returns:
        CheckingOrSavingsAccount | Exception:
            - If successful: A CheckingOrSavingsAccount object containing details for the specified account:
                - id (str): Unique account identifier.
                - name (str): Name of the account.
                - type (str): Account type (should be "Checking").
                - rewards_summary (str): Description of any rewards/benefits for this account.
                - current_amount (float): The current balance in this account.
                - interest (float): The Annual Percentage Yield (APY) on the balance (if applicable).
                - overdraft_protection (str): Description of overdraft protection status/settings.
                - minimum_balance_requirement (float): Minimum balance required to avoid fees.
                - fee (CheckingOrSavingsAccountFee): An object detailing specific fees for this account:
                    - no_minimum_balance_fee (float)
                    - monthly_fee (float)
                    - ATM_fee (float)
                    - overdraft_fee (float)
                - current_billing_cycle_transactions (list[BillingCycleTransaction]): Recent transactions for this account.
            - If unsuccessful (e.g., account ID not found): An Exception indicating "Account not found".

    Examples of when to invoke:
        - "Show the details for my Wells Fargo checking account (ID CHK1)."
        - "What is the current balance and interest rate on my Ally spending account (ID CHK2)?"
        - "List the recent transactions for my primary checking account."
        - "What are the fees associated with checking account CHK1?"
        - User selects a specific checking account from the list.
    """
    account = CHECKING_ACCOUNTS_DICT.get(account_id, None)

    if not account:
        return Exception(f"Checking Account with ID: {account_id} not found")

    return account


# Saving Accounts


@tool
def summary_of_saving_accounts() -> SummaryOfCheckingOrSavingsAccounts:
    """
    Provides a consolidated summary of all the user's savings accounts.

    Aggregates data across all savings accounts, offering insights into total balance, net flow,
    interest earnings, and associated fees.

    Args:
        None

    Returns:
        SummaryOfCheckingOrSavingsAccounts: An object containing the aggregated summary:
            - total_balance (float): The sum of current balances across all savings accounts.
            - rewards_summary (str): Combined summary of rewards or benefits (less common for savings).
            - net_flow_current_cycle (float): Net change in total balance across savings accounts this cycle.
            - category_spending (dict[str, float]): Spending/credits per category originating from savings accounts (usually minimal spending expected).
            - interest_range (list[float]): Minimum and maximum interest rates (APY) across savings accounts [min_apy, max_apy].
            - fees_summary (dict[str, float]): Summary of average fees (e.g., monthly fees if applicable). Keys include:
                - no_minimum_balance_fee_avg
                - monthly_fee_avg
                - atm_fee_avg (less common for savings)
                - overdraft_fee_avg (less common for savings)

    Examples of when to invoke:
        - "Summarize my savings accounts."
        - "What's the total amount I have in savings?"
        - "What interest rates are my savings accounts earning?"
        - "Show the net change in my savings balance recently."
    """
    return get_summary_of_checking_or_savings_accounts(is_checking=False)


@tool
def get_all_saving_accounts() -> list[dict[str, str]]:
    """
    Retrieves a list of all savings accounts belonging to the user, showing their IDs and names.

    Useful when the user needs to identify or select a specific savings account before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one savings account:
            - id (str): The unique identifier for the savings account.
            - name (str): The user-friendly name of the account (e.g., "Emergency Fund", "High Yield Savings").
            (e.g., [{'id': 'SAV1', 'name': 'Ally Savings'}, {'id': 'SAV2', 'name': 'Marcus Savings'}])

    Examples of when to invoke:
        - "List my savings accounts."
        - "What are the names of my savings accounts?"
        - User asks about interest rate or balance without specifying which savings account.
    """
    return [
        {"id": account.id, "name": account.name}
        for account in user_data.SAVING_ACCOUNTS
    ]


@tool
def get_saving_account(account_id: str) -> CheckingOrSavingsAccount | Exception:
    """
    Retrieves detailed information for a single, specific savings account identified by its ID.

    Args:
        account_id (str): The unique identifier (ID) of the specific savings account.

    Returns:
        CheckingOrSavingsAccount | Exception:
            - If successful: A CheckingOrSavingsAccount object containing details for the specified account:
                - id (str): Unique account identifier.
                - name (str): Name of the account.
                - type (str): Account type (should be "Savings").
                - rewards_summary (str): Description of any rewards/benefits.
                - current_amount (float): The current balance.
                - interest (float): The Annual Percentage Yield (APY).
                - overdraft_protection (str): Overdraft settings (less common for savings).
                - minimum_balance_requirement (float): Minimum balance to avoid fees.
                - fee (CheckingOrSavingsAccountFee): Object detailing specific fees.
                - current_billing_cycle_transactions (list[BillingCycleTransaction]): Recent transactions (usually deposits/interest).
            - If unsuccessful (e.g., account ID not found): An Exception indicating "Account not found".

    Examples of when to invoke:
        - "Show details for my Ally savings account (ID SAV1)."
        - "What is the current balance and APY on my Marcus savings (ID SAV2)?"
        - "List recent interest payments to my emergency fund account."
        - User selects a specific savings account from the list.
    """
    account = SAVING_ACCOUNTS_DICT.get(account_id, None)

    if not account:
        return Exception(f"Savings Account with ID: {account_id} not found")

    return account


# Loans


# Need to include Payment History?
@tool
def summary_of_loan_accounts() -> SummaryOfLoanAccounts:
    """
    Provides a consolidated summary of all the user's loan accounts (e.g., mortgage, auto, student, personal loans).

    Aggregates data across all loans to give an overview of total debt, principal remaining,
    interest rates, terms, and associated fees.

    Args:
        None

    Returns:
        SummaryOfLoanAccounts: An object containing the aggregated summary:
            - total_loans (int): The total number of loan accounts the user has.
            - total_outstanding_balance (float): The sum of current outstanding balances across all loans.
            - total_paid (float): The total amount paid towards all loans so far (principal + interest).
            - total_principal_remaining (float): The sum of the remaining principal amounts across all loans.
            - loan_types (list[str]): A list of the different types of loans the user has (e.g., ["mortgage", "auto", "student"]).
            - active_loans (int): The number of loans that are currently active (not fully paid off).
            - upcoming_due_dates (list[str]): A list of upcoming payment due dates for active loans.
            - interest_rate_range (list[float]): A list containing the minimum and maximum interest rates across all loans [min_rate, max_rate].
            - loan_term_range_years (list[int]): A list containing the minimum and maximum original loan terms in years [min_term, max_term].
            - loans_with_late_fees (int): The number of loans currently incurring late fees.
            - loans_with_prepayment_penalties (int): The number of loans that have prepayment penalties.
            - total_fees_summary (dict[str, float]): A dictionary summarizing the total outstanding fees across all loans by type (e.g., {'late_fees': 50.00, 'prepayment_penalties': 0.00, ...}). Keys include:
                - late_fees
                - prepayment_penalties
                - origination_fees (less likely to be currently outstanding, might be total incurred)
                - other_fees
            - collaterals_info (str): A summary string listing any collateral associated with the loans (e.g., "Mortgage: 123 Main St, Auto Loan: 2022 Honda Civic").


    Examples of when to invoke:
        - "Summarize all my loans."
        - "What's my total outstanding loan balance?"
        - "Which loans have upcoming payments?"
        - "What types of loans do I have?"
        - "Are any of my loans incurring late fees?"
    """
    return get_summary_of_loan_accounts()


@tool
def get_all_loans() -> list[dict[str, str]]:
    """
    Retrieves a list of all loan accounts belonging to the user, showing their IDs and names/types.

    Useful when the user needs to identify or select a specific loan before requesting detailed information.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one loan:
            - id (str): The unique identifier for the loan account.
            - name (str): The user-friendly name or type of the loan (e.g., "Mortgage", "Car Loan - Honda").
            (e.g., [{'id': 'LN1', 'name': 'Home Mortgage'}, {'id': 'LN2', 'name': 'Student Loan - Navient'}])

    Examples of when to invoke:
        - "List all my loans."
        - "What loans am I currently paying off?"
        - User asks about interest rate or balance without specifying which loan.
    """

    return [{"id": loan.id, "name": loan.name} for loan in user_data.LOANS]


@tool
def get_loan(loan_id: str) -> Loan | Exception:
    """
    Retrieves detailed information for a single, specific loan account identified by its ID.

    Args:
        loan_id (str): The unique identifier (ID) of the specific loan.

    Returns:
        Loan | Exception:
            - If successful: A Loan object containing details for the specified loan:
                - id (str): Unique loan identifier.
                - name (str): Name/type of the loan.
                - type (str): Loan type (e.g., "Mortgage", "Auto"). (Note: `loan_type` also exists, clarify which is primary).
                - principal_left (float): Remaining principal amount.
                - interest_rate (float): Annual interest rate (APR).
                - monthly_contribution (float): Regular monthly payment amount.
                - loan_term (str): Original term of the loan (e.g., "30 years", "60 months").
                - loan_start_date (str): Date the loan originated.
                - loan_end_date (str): Expected payoff date.
                - outstanding_balance (float): Current total balance including principal and accrued interest/fees.
                - total_paid (float): Total amount paid towards the loan so far.
                - payment_due_date (str): Next payment due date.
                - payment_history (list[dict]): List of recent payments, each dict containing 'amount_paid' (float) and 'payment_date' (str).
                - loan_type (str): Specific type of loan (e.g., "Fixed-Rate Mortgage").
                - collateral (Optional[str]): Description of any collateral securing the loan.
                - current_outstanding_fees (LoanFee): Object detailing currently owed fees:
                    - late_fee (float)
                    - prepayment_penalty (float) (Note: this usually applies if paid off early, might not be 'outstanding')
                    - origination_fee (float) (Usually paid at start, less likely 'outstanding')
                    - other_fees (float)
                - other_payments (list[dict[str, str | float]]): List of additional/non-standard payments made.
            - If unsuccessful (e.g., loan ID not found): An Exception indicating "Loan not found".

    Examples of when to invoke:
        - "Show the details for my mortgage (ID LN1)."
        - "What is the interest rate and remaining balance on my student loan (ID LN2)?"
        - "When is the next payment due for my car loan?"
        - "List the payment history for loan LN1."
        - User selects a specific loan from the list.
    """

    loan = LOANS_DICT.get(loan_id, None)

    if not loan:
        return Exception(f"Loan with ID: {loan_id} not found")

    return loan


# Payrolls


@tool
def summary_of_payroll_accounts() -> SummaryOfPayrollAccounts:
    """
    Provides a consolidated summary of all the user's payroll information entries.

    Aggregates data across all recorded payrolls (e.g., from different jobs or pay periods)
    to give an overview of total income, withholdings, pay frequencies, and benefits.

    Args:
        None

    Returns:
        SummaryOfPayrollAccounts: An object containing the aggregated summary:
            - total_entries (int): The total number of payroll records available.
            - total_annual_income (float): Sum of annual incomes from all payroll records (might need clarification if records overlap).
            - total_net_income (float): Sum of net incomes across the most recent pay periods recorded.
            - total_bonus_income (float): Sum of bonus incomes recorded.
            - total_withheld (SummaryOfPayrollWithholdings): An object summarizing total withholdings across relevant periods:
                - federal (float): Total federal tax withheld.
                - state (float): Total state tax withheld.
                - social_security (float): Total Social Security withheld.
                - medicare (float): Total Medicare withheld.
                - other (float): Total other deductions withheld.
            - withheld_by_state (dict[str, float]): Dictionary showing total state tax withheld per state.
            - pay_frequencies (dict[str, int]): Dictionary showing the count of records for each pay frequency (e.g., {'bi-weekly': 2, 'monthly': 1}).
            - most_recent_ytd_income (float): The highest year-to-date income figure found across the payroll records.
            - benefits_summary (str): A combined textual summary of benefits mentioned across payroll records.

    Examples of when to invoke:
        - "Summarize my payroll information."
        - "What's my total estimated annual income based on my payrolls?"
        - "Show my total tax withholdings."
        - "What benefits are listed in my payroll data?"
    """
    return get_summary_of_payroll_accounts()


@tool
def get_all_payrolls() -> list[dict[str, str]]:
    """
    Retrieves a list of all payroll records available for the user, showing their IDs and names/sources.

    Useful when the user has multiple jobs or payroll entries and needs to select a specific one.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one payroll entry:
            - id (str): The unique identifier for the payroll record.
            - name (str): A descriptive name for the payroll entry (e.g., "Current Job - Acme Corp", "Previous Job - XYZ Inc").
            (e.g., [{'id': 'PAY1', 'name': 'Acme Corp Payroll'}, {'id': 'PAY2', 'name': 'Side Gig Consulting'}])

    Examples of when to invoke:
        - "List all my payroll sources."
        - "Which payroll records do you have for me?"
        - User asks about deductions or income without specifying which job/payroll.
    """
    return [{"id": payroll.id, "name": payroll.name} for payroll in user_data.PAYROLLS]


@tool
def get_payroll(payroll_id: str) -> Payroll | Exception:
    """
    Retrieves detailed information for a single, specific payroll record identified by its ID.

    Args:
        payroll_id (str): The unique identifier (ID) of the specific payroll record.

    Returns:
        Payroll | Exception:
            - If successful: A Payroll object containing details for the specified record:
                - id (str): Unique record identifier.
                - name (str): Name/source of the payroll.
                - type (str): Type classification (e.g., "W2", "1099").
                - annual_income (float): Stated annual income for this source.
                - federal_taxes_withheld (float): Federal tax withheld for the relevant pay period.
                - state (str): State for tax withholding.
                - state_taxes_withheld (float): State tax withheld for the relevant pay period.
                - social_security_withheld (float): Social Security withheld for the relevant pay period.
                - medicare_withheld (float): Medicare withheld for the relevant pay period.
                - other_deductions (float): Other deductions (e.g., 401k, health insurance) for the relevant pay period.
                - net_income (float): Net pay (take-home) for the relevant pay period.
                - pay_period_start_date (str): Start date of the pay period covered by this record.
                - pay_period_end_date (str): End date of the pay period covered by this record.
                - pay_frequency (str): How often the user is paid (e.g., "bi-weekly", "monthly").
                - benefits (str): Description of benefits associated with this employment.
                - bonus_income (float): Any bonus income included in this record/period.
                - year_to_date_income (float): Year-to-date gross income reported on this record.
            - If unsuccessful (e.g., payroll ID not found): A string indicating "Payroll not found".

    Examples of when to invoke:
        - "Show the details for my Acme Corp payroll (ID PAY1)."
        - "What were my deductions on my last paycheck from Side Gig Consulting (ID PAY2)?"
        - "What is the pay frequency for my main job?"
        - User selects a specific payroll record from the list.
    """
    payroll = PAYROLLS_DICT.get(payroll_id, None)

    if not payroll:
        return Exception(f"Payroll with ID: {payroll_id} not found")

    return payroll


# HSA Accounts


@tool
def summary_of_hsa_accounts() -> SummaryOfHSAAccounts:
    """
    Provides a consolidated summary of all the user's Health Savings Accounts (HSAs).

    Aggregates data across all HSAs, focusing on contributions, uninvested cash, and investment holdings within these tax-advantaged accounts.

    Args:
        None

    Returns:
        SummaryOfHSAAccounts: An object containing the aggregated summary:
            - total_uninvested_amount (float): Total sum of uninvested cash across all HSAs.
            - total_average_monthly_contribution (float): Sum of the average monthly contributions across all HSAs (from user and potentially employer).
            - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary summarizing combined investment holdings across all HSAs.
              Keys are ticker symbols (str), values are TickerInformationInSummary objects (see `summary_of_investment_accounts` for details).

    Examples of when to invoke:
        - "Summarize my HSA accounts."
        - "How much cash is available in my HSAs?"
        - "What's the total monthly contribution going into my HSAs?"
        - "Show the investment performance within my HSAs."
    """

    return get_summary_of_hsa_accounts()


@tool
def get_all_hsa_accounts() -> list[dict[str, str]]:
    """
    Retrieves a list of all Health Savings Accounts (HSAs) belonging to the user, showing their IDs and names.

    Useful when the user has multiple HSAs or needs to select a specific one.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one HSA:
            - id (str): The unique identifier for the HSA.
            - name (str): The user-friendly name of the account (e.g., "Optum Bank HSA", "Fidelity HSA").
            (e.g., [{'id': 'HSA1', 'name': 'My Primary HSA'}])

    Examples of when to invoke:
        - "List my HSA accounts."
        - "What HSAs do I have?"
        - User asks about contributions or investments without specifying which HSA.
    """
    return [
        {"id": account.id, "name": account.name} for account in user_data.HSA_ACCOUNTS
    ]


@tool
def get_hsa_account(account_id: str) -> SummaryOfHSAAccounts | Exception:
    """
    Retrieves detailed information for a single, specific Health Savings Account (HSA) identified by its ID.

    Args:
        account_id (str): The unique identifier (ID) of the specific HSA.

    Returns:
        HSAAccount | Exception:
            - If successful:
                SummaryOfHSAAccounts: An object containing the aggregated summary:
                - total_uninvested_amount (float): Uninvested cash in the Health Savings Account.
                - total_average_monthly_contribution (float): Average monthly contributions in the Health Savings Account.
                - invested_securities_info (dict[str, TickerInformationInSummary]): A dictionary summarizing combined holdings in the Health Savings Account.
                Keys are ticker symbols (str), values are TickerInformationInSummary objects.
                A dictionary where keys are ticker symbols (str)
                and values are TickerInformationInSummary objects. Each TickerInformationInSummary object provides:
                    - total_quantity (float): Total shares owned across all accounts for this ticker.
                    - average_cost_basis (float): Weighted average purchase price per share.
                    - company_name (str): Full name of the company.
                    - current_price (float): Latest market price per share.
                    - daily_price_change (float): Today's price change percentage.
                    - weekly_price_change (float): 7-day price change percentage.
                    - monthly_price_change (float): 30-day price change percentage.
                    - ytd_price_change (float): Year-to-date price change percentage.
                    - MA50 (float): 50-day moving average.
                    - MA100 (float): 100-day moving average.
                    - high_52_week (float): Highest price in the last 52 weeks.
                    - low_52_week (float): Lowest price in the last 52 weeks.
                    - volume (int): Today's trading volume.
                    - summary_of_latest_market_news (str): Recent news summary.
                    - total_value_change (float): Total unrealized gain or loss for this holding across accounts (Current Value - Total Cost Basis).
            - If unsuccessful (e.g., account ID not found): An Exception indicating "HSA Account not found".

    Examples of when to invoke:
        - "Show the details for my Optum Bank HSA (ID HSA1)."
        - "What investments are in my Fidelity HSA?"
        - "How much cash do I have in HSA account HSA1?"
        - User selects a specific HSA from the list.
    """
    account = HSA_ACCOUNTS_DICT.get(account_id, None)

    if not account:
        return Exception(f"HSA Account with ID: {account_id} not found")

    result = {
        "total_uninvested_amount": account.uninvested_amount,
        "total_average_monthly_contribution": account.average_monthly_contribution,
        "invested_securities_info": summary_of_assets([account]),
    }

    return result


# Other Accounts


@tool
def summary_of_other_accounts() -> SummaryOfOtherAccounts:
    """
    Provides a consolidated summary of all accounts categorized as 'Other'.

    Aggregates the total income and debt figures associated with miscellaneous accounts
    that don't fit into standard categories like checking, savings, investment, or loans.

    Args:
        None

    Returns:
        SummaryOfOtherAccounts: An object containing the aggregated summary:
            - total_income (float): The sum of total income figures reported across all 'Other' accounts.
            - total_debt (float): The sum of total debt figures reported across all 'Other' accounts.

    Examples of when to invoke:
        - "Summarize my 'other' accounts."
        - "What's the total income listed in my miscellaneous accounts?"
        - "Is there any debt recorded in my 'other' accounts category?"
    """

    return get_summary_of_other_accounts()


@tool
def get_all_other_accounts() -> list[dict[str, str]]:
    """
    Retrieves a list of all accounts categorized as 'Other', showing their IDs and names.

    Useful for identifying specific miscellaneous accounts before requesting details.

    Args:
        None

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing one 'Other' account:
            - id (str): The unique identifier for the account.
            - name (str): The user-friendly name of the account (e.g., "PayPal Balance", "Venmo Account").
            (e.g., [{'id': 'OTH1', 'name': 'Business Petty Cash'}])

    Examples of when to invoke:
        - "List my 'other' accounts."
        - "What accounts are in the 'other' category?"
    """
    return [
        {"id": account.id, "name": account.name} for account in user_data.OTHER_ACCOUNTS
    ]


@tool
def get_other_account(account_id: str) -> OtherAccount | Exception:
    """
    Retrieves detailed information for a single, specific account categorized as 'Other', identified by its ID.

    Args:
        account_id (str): The unique identifier (ID) of the specific 'Other' account.

    Returns:
        OtherAccount | Exception:
            - If successful: An OtherAccount object containing details for the specified account:
                - id (str): Unique account identifier.
                - name (str): Name of the account.
                - type (str): Account type (should be "Other" or more specific if available).
                - total_income (float): Income figure associated with this account.
                - total_debt (float): Debt figure associated with this account.
            - If unsuccessful (e.g., account ID not found): An Exception indicating "Other Account not found".

    Examples of when to invoke:
        - "Show details for my 'Business Petty Cash' account (ID OTH1)."
        - "What's the balance reported for my PayPal account?"
        - User selects a specific account from the 'other' list.
    """
    account = OTHER_ACCOUNTS_DICT.get(account_id, None)

    if not account:
        return Exception(f"Other Account with ID: {account_id} not found")

    return account


# Overall Financial Plan


@tool
def optimize_financial_plan(criteria: str) -> FinancialPlan:
    """
    Generates a personalized financial plan aimed at optimizing the user's finances based on a specific goal or criteria, using grounded web search and the user's overall financial summary.

    This tool analyzes the user's complete financial picture (summaries of accounts, debts, income)
    and creates actionable steps towards achieving the user-defined optimization criteria. It considers realism and may adjust ambitious goals.

    Args:
        criteria (str): A description of the user's financial goal or the area they want to optimize
                        (e.g., "maximize retirement savings", "pay down high-interest debt faster",
                        "build an emergency fund", "improve investment diversification").

    Returns:
        FinancialPlan: An object containing the generated plan:
            - plan_summary (str): A high-level overview of the proposed financial strategy.
            - instructions (str): A string outlining instructions regarding the actions the user can take.

    Examples of when to invoke:
        - "Help me create a plan to reach financial independence."
        - "How can I optimize my finances to buy a house in 5 years?"
        - "Give me a strategy to balance debt repayment and investing."
        - "Develop a plan to improve my overall financial health."
    """

    prompt = f"""
Context:
- User Details:
{anonymize_user_personal_details(USER_DETAILS)}
- User's Comprehensive Financial Summary:
{get_user_financial_summary()}
- User's Stated Financial Goal/Optimization Criteria: {criteria}

Task: Develop a personalized and actionable financial plan to help the user achieve their stated goal or optimize based on their criteria, using their provided financial summary. The plan MUST be realistic given their situation.

Instructions:

1. Analyze Financial Situation: Thoroughly review the user's entire financial summary provided in the context - including income sources (payrolls), spending patterns (inferred from checking/credit card summaries), assets (investments, savings, retirement accounts), liabilities (loans, credit card debt), and savings/contribution rates (retirement/HSA summaries). Consider user details like age, location, and tax status if available in the summary.

2. Evaluate Goal vs. Situation: Assess the user's goal (`criteria`) in light of their current financial situation (analyzed in step 1). Determine if the goal seems realistic within any implied timeframe. If the goal appears overly ambitious given the summary (e.g., retiring very early with low savings rate), acknowledge this respectfully in the plan summary and propose either a more achievable version of the goal OR break the original goal down into concrete, sequential phases with realistic milestones.

3. Formulate Strategy (`plan_summary`): Create a concise summary (typically 1-3 sentences) of the overall recommended financial strategy. This summary should explain the core approach (e.g., "The plan focuses on accelerating high-interest debt payoff while building an emergency fund, followed by increasing retirement contributions.").

4. Develop Actionable Steps (instructions): Create specific, actionable steps the user can take, derived primarily from their financial summary. Format these steps into a single, well-structured string intended for the instructions field. Use clear Markdown formatting within this string (such as headings like ## Financial Area or ## Phase 1, and numbered 1. or bulleted - lists) to organize the steps logically for readability. Ensure the entire plan's steps are contained within this single string. Use grounded search ONLY if external general financial information (e.g., current retirement contribution limits for the year 2025, standard financial benchmarks) is necessary to make the plan realistic or informative. Do NOT give specific investment advice (e.g., "buy stock X").
"""

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, FinancialPlan
    )

    return structured_response


@tool
def how_can_I_make_X_money_in_Y_months(
    amount: float, months: int, criteria: str
) -> FinancialPlan:
    """
    Generates a financial plan focused on achieving a specific monetary gain target within a defined timeframe, using grounded web search and the user's financial summary.

    Analyzes the user's financial situation to suggest realistic strategies (like side hustles, investment adjustments,
    or aggressive saving/cost-cutting) to reach the target income or gain. Will assess if the goal is feasible.

    Args:
        amount (float): The target amount of additional money the user wants to make (net gain).
        months (int): The number of months the user has to achieve this goal.
        criteria (str): Additional context regarding how to structure the plan (e.g., "focus on side hustles", "invest in stocks", "cut expenses").

    Returns:
        FinancialPlan: An object containing the generated plan:
            - plan_summary (str): High-level overview of the strategy to make the target amount.
            - instructions (str): Step-by-step actions, potentially including income generation ideas,
                                   investment strategies, or spending adjustments.

    Examples of when to invoke:
        - "How can I make an extra $5,000 in the next 6 months?"
        - "I need a plan to earn $10,000 in 1 year for a down payment."
        - "What steps can I take to generate $1,000 more income per month?"
    """
    # Format amount for clarity in the prompt
    formatted_amount = f"${amount:,.2f}"
    # Calculate required monthly gain for feasibility check
    monthly_gain_needed = amount / months if months > 0 else amount
    formatted_monthly_gain = f"${monthly_gain_needed:,.2f}"

    prompt = (
        f"User's Financial Summary Context:\n{get_user_financial_summary()}\n\n"
        f"Additional context regarding how to structure the financial plan, given by the user: {criteria}\n\n"
        f"User's Goal: To make an additional {formatted_amount} within {months} months.\n\n"
        f"Required average monthly gain: {formatted_monthly_gain} per month.\n\n"
        "Task: Generate a detailed, actionable, and personalized financial plan to help the user achieve this monetary gain goal. Use grounded web search where necessary for market context or specific opportunities (e.g., investment ideas, side hustle platforms), but tailor suggestions primarily to the user's provided summary.\n\n"
        "Instructions for Plan Generation:\n"
        "1. Analyze the User's Summary: Thoroughly review their income (payrolls), expenses (checking/CC summaries), assets (investments, savings balances, uninvested cash), and debts (loans). Identify potential resources (e.g., available capital, existing skills suggested by job type if available) and constraints (e.g., high debt payments, low savings).\n"
        "2. Propose Specific Strategies: Based on the analysis, suggest concrete actions focused on MAKING money. Prioritize relevance and potential impact. Categories to consider:\n"
        "    - Increasing Income: Suggest ways like negotiating raises, finding part-time work, freelance opportunities, or starting a side hustle (consider low-startup options if capital is low).\n"
        "    - Investment Strategies: If the user has capital (check uninvested amounts, savings), suggest potential investment adjustments or new investments aimed at generating returns within the timeframe. CLEARLY STATE THE RISKS involved and that returns are not guaranteed. Do not suggest overly speculative or complex strategies unless explicitly asked and qualified. Avoid specific ticker recommendations (e.g., 'buy stock X').\n"
        "    - Capital Optimization: Suggest ways to free up capital specifically for income-generating activities (e.g., targeted cost-cutting to fund a side business investment, potentially selling specific underperforming assets if analysis supports it).\n"
        f"3. Assess Feasibility & Manage Expectations: Critically evaluate if making {formatted_amount} in {months} months ({formatted_monthly_gain} per month) is realistic given their financial picture. State your assessment clearly in the plan summary. If the goal seems highly ambitious or unlikely:\n"
        "    - Explicitly mention this.\n"
        "    - Either propose a more achievable target/timeframe OR focus the plan on the most impactful first steps towards the goal, emphasizing that the full amount might not be reachable in the specified time.\n"
        "4. Develop Actionable Steps (`instructions` string): Create specific, actionable steps based primarily on the user's financial summary. Combine all these steps into a single string value for the `instructions` field. Ensure the entire output for the plan's steps is one continuous string. Use grounded search ONLY if external general financial information (e.g., current {datetime.date.today().year} retirement contribution limits, standard financial benchmarks) is necessary for context or realism. Do NOT give specific investment advice.\n"  # Updated instruction #4
    )

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, FinancialPlan
    )

    return structured_response


@tool
def how_can_save_X_money_in_Y_months(
    amount: float, months: int, criteria: str
) -> FinancialPlan:
    """
    Generates a financial plan focused on achieving a specific savings target within a defined timeframe, using grounded web search and the user's financial summary.

    Analyzes the user's income, expenses (derived from summaries), and existing savings potential to create
    a realistic plan involving budget adjustments, identifying savings opportunities, and potentially
    suggesting suitable savings vehicles. Will assess if the goal is feasible.

    Args:
        amount (float): The target amount of money the user wants to save.
        months (int): The number of months the user has to achieve this savings goal.
        criteria (str): Additional context regarding how to structure the plan (e.g., "focus on budgeting", "invest in a high-yield savings account", "cut unnecessary expenses").

    Returns:
        FinancialPlan: An object containing the generated plan:
            - plan_summary (str): High-level overview of the strategy to save the target amount.
            - instructions (str): Step-by-step actions, focusing on budgeting, expense reduction,
                                   automating savings, and potentially where to keep the saved money.

    Examples of when to invoke:
        - "Help me save $10,000 in 12 months for a vacation."
        - "What's the best way to save $2,000 in the next 3 months for an emergency fund?"
        - "I want to save $500 per month, give me a plan."
    """

    prompt = f"""
You are a financial planning assistant. The user wants to save ${amount:,.2f} in {months} months.

Use the following financial summary to assess their situation:
{get_user_financial_summary()}

Additional context regarding how to structure the financial plan, given by the user: {criteria}

Your job is to create a personalized savings plan that is realistic and actionable based on the user's income, spending habits, and current financial obligations.

Your response must include:

Plan Summary: a high-level overview of how the user can reach their goal.
Step-by-Step Instructions: specific actions the user can take, such as:

Adjusting or creating a budget

Reducing specific expenses

Automating monthly savings

Choosing the right savings account (e.g., high-yield savings, CD, etc.)

This is how much the user needs to save per month: ${amount / months:,.2f}/month.
First assess whether this is realistic given their net income and expenses.

If achievable: provide a detailed plan.

If unrealistic: clearly state why and suggest either a revised savings goal or a longer timeline, with tips to gradually improve savings habits.

Be practical, grounded, and solution-focused.
"""

    (structured_response, _, _) = get_structured_output_with_grounding(
        "gemini-2.0-flash", prompt, FinancialPlan
    )

    return structured_response
