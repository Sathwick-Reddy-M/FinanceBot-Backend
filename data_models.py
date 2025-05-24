from pydantic import BaseModel, Field
from typing import Optional, Any


class UserDetails(BaseModel):
    name: str = Field(..., description="Full name of the user")
    age: int = Field(..., description="Age of the user")
    state: str = Field(..., description="State of residence")
    country: str = Field(..., description="Country of residence")
    citizen_of: str = Field(..., description="Country of citizenship")
    tax_filing_status: str = Field(..., description="Tax filing status")
    is_tax_resident: bool = Field(..., description="Is the user a tax resident")

    def __str__(self):
        return (
            f"The user is {self.name}, aged {self.age}, living in {self.state}, {self.country}. "
            f"They are a citizen of {self.citizen_of}. "
            f"Their tax filing status is {self.tax_filing_status}, and they are "
            f"{'a tax resident' if self.is_tax_resident else 'not a tax resident'} of {self.country}."
        )


class TickerInformation(BaseModel):
    ticker: str = Field(..., description="Unique stock symbol")
    company_name: str = Field(..., description="Full name of the company")
    current_price: float = Field(..., description="Latest market price per share")
    daily_price_change: float = Field(
        ..., description="Price change from previous close"
    )
    weekly_price_change: float = Field(
        ..., description="Price change over the last 7 days"
    )
    monthly_price_change: float = Field(
        ..., description="Price change over the last 30 days"
    )
    ytd_price_change: float = Field(..., description="Year-to-date percentage change")
    MA50: float = Field(..., description="50 day moving average")
    MA100: float = Field(..., description="100 day moving average")
    high_52_week: float = Field(..., description="Highest price in the last 52 weeks")
    low_52_week: float = Field(..., description="Lowest price in the last 52 weeks")
    volume: int = Field(..., description="Number of shares traded today")
    summary_of_latest_market_news: str = Field(
        ...,
        description="1 or 2 paragraphs summary of latest market news related to this ticker",
    )

    def __str__(self):
        # Return the information in a readable sentences format
        return (
            f"The current price of {self.ticker} ({self.company_name}) is "
            f"{f'${self.current_price:.2f}' if self.current_price != 0 else 'NOT_AVAILABLE'}. "
            f"Daily price change is "
            f"{f'{self.daily_price_change:.2f}%' if self.daily_price_change != 0 else 'NOT_AVAILABLE'}. "
            f"Weekly price change is "
            f"{f'{self.weekly_price_change:.2f}%' if self.weekly_price_change != 0 else 'NOT_AVAILABLE'}. "
            f"Monthly price change is "
            f"{f'{self.monthly_price_change:.2f}%' if self.monthly_price_change != 0 else 'NOT_AVAILABLE'}. "
            f"Year-to-date price change is "
            f"{f'{self.ytd_price_change:.2f}%' if self.ytd_price_change != 0 else 'NOT_AVAILABLE'}. "
            f"The 50-day moving average is "
            f"{f'${self.MA50:.2f}' if self.MA50 != 0 else 'NOT_AVAILABLE'}. "
            f"The 100-day moving average is "
            f"{f'${self.MA100:.2f}' if self.MA100 != 0 else 'NOT_AVAILABLE'}. "
            f"The highest price in the last 52 weeks was "
            f"{f'${self.high_52_week:.2f}' if self.high_52_week != 0 else 'NOT_AVAILABLE'}. "
            f"The lowest price in the last 52 weeks was "
            f"{f'${self.low_52_week:.2f}' if self.low_52_week != 0 else 'NOT_AVAILABLE'}. "
            f"Today's trading volume is {self.volume}. "
            f"Latest market news: {self.summary_of_latest_market_news}"
        )


class AssetDistribution(BaseModel):
    ticker: str = Field(..., description="Unique security symbol")
    quantity: float = Field(..., description="Number of shares owned")
    average_cost_basis: float = Field(..., description="Average cost basis per share")

    def __str__(self):
        return f"{self.quantity} shares of {self.ticker} at an average cost basis of ${self.average_cost_basis:.2f}"


class InvestmentAccount(BaseModel):
    id: str = Field(..., description="Unique identifier for the investment account")
    name: str = Field(..., description="Name of the investment account")
    type: str = Field(..., description="Type of investment account")
    uninvested_amount: float = Field(
        ..., description="Amount of uninvested cash in the account"
    )
    asset_distribution: list[AssetDistribution] = Field(
        ..., description="List of asset distributions in the account"
    )

    def __str__(self):
        return (
            f"Investment Account of ID {self.id} named {self.name} with uninvested amount of ${self.uninvested_amount:.2f} "
            f"Asset Distribution of this account is as follows: {', '.join(str(asset) for asset in self.asset_distribution)}"
        )


class TickerInformationInSummary(BaseModel):
    total_quantity: float = Field(..., description="Total quantity of shares owned")
    average_cost_basis: float = Field(..., description="Average cost basis per share")
    company_name: str = Field(..., description="Full name of the company")
    current_price: float = Field(..., description="Latest market price per share")
    daily_price_change: float = Field(..., description="Price change from previous day")
    weekly_price_change: float = Field(
        ..., description="Price change over the last 7 days at this time"
    )
    monthly_price_change: float = Field(
        ..., description="Price change over the last 30 days at this time"
    )
    ytd_price_change: float = Field(..., description="Year-to-date percentage change")
    MA50: float = Field(..., description="50 day moving average")
    MA100: float = Field(..., description="100 day moving average")
    high_52_week: float = Field(..., description="Highest price in the last 52 weeks")
    low_52_week: float = Field(..., description="Lowest price in the last 52 weeks")
    volume: int = Field(..., description="Number of shares traded today")
    summary_of_latest_market_news: str = Field(
        ...,
        description="1 or 2 paragraphs summary of latest market news related to this ticker",
    )
    total_value_change: float = Field(
        ...,
        description="Total value change of the asset in the account. Positive for gain, negative for loss",
    )

    def __str__(self):
        return (
            f"The person has a total of {self.total_quantity} shares owned for the company {self.company_name}, "
            f"with an average cost basis of ${self.average_cost_basis:.2f} per share. "
            f"The current market price is ${self.current_price:.2f}, with a daily price change of {self.daily_price_change:.2f}%. "
            f"Over the last week, the price changed by {self.weekly_price_change:.2f}%, and over the last month, it changed by {self.monthly_price_change:.2f}%. "
            f"The year-to-date price change is {self.ytd_price_change:.2f}%. "
            f"The 50-day moving average is ${self.MA50:.2f}, and the 100-day moving average is ${self.MA100:.2f}. "
            f"The highest price in the last 52 weeks was ${self.high_52_week:.2f}, while the lowest was ${self.low_52_week:.2f}. "
            f"Today's trading volume is {self.volume} shares. "
            f"The total value change of the asset is ${self.total_value_change:.2f}. "
            f"Here is a summary of the latest market news regarding this security: {self.summary_of_latest_market_news}"
        )


class SummaryOfInvestmentAccounts(BaseModel):
    total_uninvested_amount: float = Field(
        ...,
        description="Total univested amount across all of the investment accounts of the user",
    )
    invested_securities_info: dict[str, TickerInformationInSummary] = Field(
        ..., description="Invested Securities Information"
    )

    def __str__(self):
        invested_securities_details = "\n".join(
            f"{ticker}: {str(info)}"
            for ticker, info in self.invested_securities_info.items()
        )
        return (
            f"The total uninvested amount across the given investment accounts is ${self.total_uninvested_amount:.2f}. "
            f"The details of the invested securities are as follows:\n{invested_securities_details}"
        )


class SummaryOfIRAAccounts(BaseModel):
    total_uninvested_amount: float = Field(
        ...,
        description="Total univested amount across all of the investment accounts of the user",
    )
    total_average_monthly_contribution: float = Field(
        ...,
        description="Total average monthly contribution across all of the investment accounts of the user",
    )
    invested_securities_info: dict[str, TickerInformationInSummary] = Field(
        ..., description="Invested Securities Information"
    )

    def __str__(self):
        invested_securities_details = "\n".join(
            f"{ticker}: {str(info)}"
            for ticker, info in self.invested_securities_info.items()
        )
        return (
            f"The total uninvested amount across the given accounts is ${self.total_uninvested_amount:.2f}. "
            f"The total average monthly contribution across the given accounts is ${self.total_average_monthly_contribution:.2f}. "
            f"The details of the invested securities are as follows:\n{invested_securities_details}"
        )


class SummaryOfHSAAccounts(BaseModel):
    total_uninvested_amount: float = Field(
        ...,
        description="Total univested amount across all of the investment accounts of the user",
    )
    total_average_monthly_contribution: float = Field(
        ...,
        description="Total average monthly contribution across all of the investment accounts of the user",
    )
    invested_securities_info: dict[str, TickerInformationInSummary] = Field(
        ..., description="Invested Securities Information"
    )

    def __str__(self):
        invested_securities_details = "\n".join(
            f"{ticker}: {str(info)}"
            for ticker, info in self.invested_securities_info.items()
        )
        return (
            f"The total uninvested amount across the given accounts is ${self.total_uninvested_amount:.2f}. "
            f"The total average monthly contribution across the given accounts is ${self.total_average_monthly_contribution:.2f}. "
            f"The details of the invested securities are as follows:\n{invested_securities_details}"
        )


class HSAAccount(BaseModel):
    id: str
    name: str
    type: str
    average_monthly_contribution: float
    uninvested_amount: float
    asset_distribution: list[AssetDistribution]

    def __str__(self):
        return (
            f"HSA Account of ID {self.id} named {self.name} with uninvested amount of ${self.uninvested_amount:.2f} "
            f"Average monthly contribution is ${self.average_monthly_contribution:.2f}. "
            f"Asset Distribution of this account is as follows: {', '.join(str(asset) for asset in self.asset_distribution)}"
        )


class SummaryOf401kAccounts(BaseModel):
    total_uninvested_amount: float = Field(
        ...,
        description="Total univested amount across all of the investment accounts of the user",
    )
    total_average_monthly_contribution: float = Field(
        ...,
        description="Total average monthly contribution across all of the investment accounts of the user",
    )
    employer_matches_summary: str = Field(
        ..., description="Summary of employer matches across all accounts"
    )
    invested_securities_info: dict[str, TickerInformationInSummary] = Field(
        ..., description="Invested Securities Information"
    )

    def __str__(self):
        invested_securities_details = "\n".join(
            f"{ticker}: {str(info)}"
            for ticker, info in self.invested_securities_info.items()
        )
        return (
            f"The total uninvested amount across the given accounts is ${self.total_uninvested_amount:.2f}. "
            f"The total average monthly contribution across the given accounts is ${self.total_average_monthly_contribution:.2f}. "
            f"The details of the invested securities are as follows:\n{invested_securities_details}"
        )


class TraditionalIRA(BaseModel):
    id: str
    name: str
    type: str
    uninvested_amount: float
    average_monthly_contribution: float
    asset_distribution: list[AssetDistribution]

    def __str__(self):
        return (
            f"Traditional IRA of ID {self.id} named {self.name} with uninvested amount of ${self.uninvested_amount:.2f} "
            f"Average monthly contribution is ${self.average_monthly_contribution:.2f}. "
            f"Asset Distribution of this account is as follows: {', '.join(str(asset) for asset in self.asset_distribution)} "
        )


class RothIRA(BaseModel):
    id: str
    name: str
    type: str
    uninvested_amount: float
    average_monthly_contribution: float
    asset_distribution: list[AssetDistribution]

    def __str__(self):
        return (
            f"Roth IRA of ID {self.id} named {self.name} with uninvested amount of ${self.uninvested_amount:.2f} "
            f"Average monthly contribution is ${self.average_monthly_contribution:.2f}. "
            f"Asset Distribution of this account is as follows: {', '.join(str(asset) for asset in self.asset_distribution)} "
        )


class Retirement401K(BaseModel):
    id: str
    name: str
    type: str
    average_monthly_contribution: float
    uninvested_amount: float
    asset_distribution: list[AssetDistribution]
    employer_match: str

    def __self__(self):
        return (
            f"401(k) of ID {self.id} named {self.name} with uninvested amount of ${self.uninvested_amount:.2f} "
            f"Average monthly contribution is ${self.average_monthly_contribution:.2f}. "
            f"Asset Distribution of this account is as follows: {', '.join(str(asset) for asset in self.asset_distribution)} "
            f"Employer match details: {self.employer_match}"
        )


class Roth401K(BaseModel):
    id: str
    name: str
    type: str
    average_monthly_contribution: float
    uninvested_amount: float
    asset_distribution: list[AssetDistribution]
    employer_match: str

    def __self__(self):
        return (
            f"Roth 401(k) of ID {self.id} named {self.name} with uninvested amount of ${self.uninvested_amount:.2f} "
            f"Average monthly contribution is ${self.average_monthly_contribution:.2f}. "
            f"Asset Distribution of this account is as follows: {', '.join(str(asset) for asset in self.asset_distribution)} "
            f"Employer match details: {self.employer_match}"
        )


class BillingCycleTransaction(BaseModel):
    amount: float
    category: str

    def __str__(self):
        return f'{"Credit" if self.amount > 0 else "Debit"} of ${abs(self.amount):.2f} in category {self.category}'


class CreditCard(BaseModel):
    id: str
    name: str
    type: str
    total_limit: float
    current_limit: float
    rewards_summary: str
    interest: float
    outstanding_debt: float
    current_billing_cycle_transactions: list[BillingCycleTransaction]
    annual_fee: Optional[float] = 0.0

    def __str__(self):
        return (
            f"Credit Card of ID {self.id} named {self.name} with total limit of ${self.total_limit:.2f} and outstanding debt of ${self.outstanding_debt:.2f} "
            f"Interest rate on is {self.interest}% APY. "
            f"Rewards of card are as follows: {self.rewards_summary} "
            f"Current billing cycle transactions: {', '.join(str(txn) for txn in self.current_billing_cycle_transactions)} "
            f"Annual Fee: ${self.annual_fee:.2f}"
        )


class SummaryOfCreditCards(BaseModel):
    total_limit: float
    available_credit: float
    outstanding_debt: float
    apr_range: list[float]
    spending_by_category: dict[str, float]
    weighted_average_interest_rate_applied_on_debt: float
    rewards_summary: str
    total_annual_fees: float

    def __str__(self):
        return (
            f"Summary of Credit Cards: "
            f"Total Limit across all the credit cards available is: ${self.total_limit:.2f} "
            f"Available Credit is: ${self.available_credit:.2f} "
            f"Outstanding Debt is: ${self.outstanding_debt:.2f} "
            f"APR Range is: {self.apr_range} "
            f"Spending by Category: {', '.join([f'${abs(amount):.2f} spent on {cat}' if amount < 0 else f'${amount:.2f} credited under {cat}' for cat, amount in self.spending_by_category.items()])} "
            f"Weighted Average Interest Rate Applied on the outstanding debt is: {self.weighted_average_interest_rate_applied_on_debt:.2f}% "
            f"Rewards Summary: {self.rewards_summary}"
        )


class CheckingOrSavingsAccountFee(BaseModel):
    no_minimum_balance_fee: float
    monthly_fee: float
    ATM_fee: float
    overdraft_fee: float

    def __str__(self):
        return (
            f"No minimum balance fee is ${self.no_minimum_balance_fee:.2f}, "
            f"Monthly fee is ${self.monthly_fee:.2f}, "
            f"ATM fee is ${self.ATM_fee:.2f}, "
            f"Overdraft fee is ${self.overdraft_fee:.2f}."
        )


# Need to include properties like prev month transcations to get an idea of spending habits


class CheckingOrSavingsAccount(BaseModel):
    id: str
    name: str
    type: str
    rewards_summary: str
    current_amount: float
    interest: float
    overdraft_protection: str
    minimum_balance_requirement: float
    fee: CheckingOrSavingsAccountFee
    current_billing_cycle_transactions: list[BillingCycleTransaction]

    def __str__(self):
        # Sometimes it might not be possible to send all of the transactions of the billing cycle. Need to send the latest N.
        return (
            f"{self.type} Account of ID {self.id} named {self.name} with current amount of ${self.current_amount:.2f} "
            f"Interest rate on the current amount (if positive) available is {self.interest} APY%. "
            f"Rewards of account are as follows: {self.rewards_summary} "
            f"Overdraft protection is {self.overdraft_protection}. "
            f"Minimum balance requirement is ${self.minimum_balance_requirement:.2f}. "
            f"Fees: {str(self.fee)} "
            f"Current billing cycle transactions: {', '.join(str(txn) for txn in self.current_billing_cycle_transactions)}"
        )


class SummaryOfCheckingOrSavingsAccounts(BaseModel):
    total_balance: float
    rewards_summary: str
    net_flow_current_cycle: float
    category_spending: dict[str, float]
    interest_range: list[float]
    fees_summary: dict[str, float]

    def __str__(self):
        return (
            f"Summary of Checking/Savings Accounts: "
            f"Total Balance across all the accounts is: ${self.total_balance:.2f} "
            f"Rewards Summary: {self.rewards_summary} "
            f"Net Flow in the current cycle is: ${self.net_flow_current_cycle:.2f} "
            f"Category Spending: {', '.join([f'${abs(amount):.2f} spent on {cat}' if amount < 0 else f'${amount:.2f} credited under {cat}' for cat, amount in self.category_spending.items()])} "
            f"Interest Range: {self.interest_range} "
            f"Fees Summary: {', '.join([f'{key}: ${value:.2f}' for key, value in self.fees_summary.items()])}"
        )


class LoanFee(BaseModel):
    late_fee: float
    prepayment_penalty: float
    origination_fee: float
    other_fees: float

    def __str__(self):
        return (
            f"Late fee is ${self.late_fee:.2f}, "
            f"Prepayment penalty is ${self.prepayment_penalty:.2f}, "
            f"Origination fee is ${self.origination_fee:.2f}, "
            f"Other fees are ${self.other_fees:.2f}."
        )


class Loan(BaseModel):
    id: str
    name: str
    type: str
    principal_left: float
    interest_rate: float
    monthly_contribution: float
    loan_term: str
    loan_start_date: str
    loan_end_date: str
    outstanding_balance: float
    total_paid: float
    payment_due_date: str
    payment_history: list[dict]
    loan_type: str
    collateral: Optional[str] = None
    current_outstanding_fees: LoanFee
    other_payments: list[dict[str, str | float]]

    def __str__(self):
        payment_history_str = ", ".join(
            [
                f"${payment['amount_paid']:.2f} on {payment['payment_date']}"
                for payment in self.payment_history
            ]
        )
        other_payments_str = ", ".join(
            [
                f"${payment['payment_amount']:.2f} on {payment['payment_date']} under type {payment['payment_type']} ({payment['description']})"
                for payment in self.other_payments
            ]
        )

        return (
            f"Loan of ID {self.id} named {self.name} with principal left of ${self.principal_left:.2f} "
            f"Interest rate is {self.interest_rate}% APY. "
            f"Monthly contribution is ${self.monthly_contribution:.2f}. "
            f"Loan term is {self.loan_term} starting from {self.loan_start_date} to {self.loan_end_date}. "
            f"Outstanding balance is ${self.outstanding_balance:.2f}. "
            f"Total paid so far is ${self.total_paid:.2f}. "
            f"Payment due date is {self.payment_due_date}. "
            f"Payment history: {payment_history_str} "
            f"Current outstanding fees: {str(self.current_outstanding_fees)} "
            f"Other payments: {other_payments_str}"
        )


class SummaryOfLoanAccounts(BaseModel):
    total_loans: int
    total_outstanding_balance: float
    total_paid: float
    total_principal_remaining: float
    loan_types: list[str]
    active_loans: int
    upcoming_due_dates: list[str]
    interest_rate_range: list[float]
    loan_term_range_years: list[int]
    loans_with_late_fees: int
    loans_with_prepayment_penalties: int
    total_fees_summary: dict[str, float]
    collaterals_info: str

    def __str__(self):
        return (
            f"Summary of Loan Accounts: "
            f"Total Loans: {self.total_loans}, "
            f"Total Outstanding Balance: ${self.total_outstanding_balance:.2f}, "
            f"Total Paid: ${self.total_paid:.2f}, "
            f"Total Principal Remaining: ${self.total_principal_remaining:.2f}, "
            f"Collaterals Info: {self.collaterals_info}, "
            f"Loan Types: {', '.join(self.loan_types)}, "
            f"Active Loans: {self.active_loans}, "
            f"Upcoming Due Dates: {', '.join(self.upcoming_due_dates)}, "
            f"Interest Rate Range: {self.interest_rate_range}, "
            f"Loan Term Range (Years): {self.loan_term_range_years}, "
            f"Loans with Late Fees: {self.loans_with_late_fees}, "
            f"Loans with Prepayment Penalties: {self.loans_with_prepayment_penalties}, "
            f"Total Fees Summary: {', '.join([f'{key}: ${value:.2f}' for key, value in self.total_fees_summary.items()])}"
        )


class Payroll(BaseModel):
    id: str
    name: str
    type: str
    annual_income: float
    federal_taxes_withheld: float
    state: str
    state_taxes_withheld: float
    social_security_withheld: float
    medicare_withheld: float
    other_deductions: float
    net_income: float
    pay_period_start_date: str
    pay_period_end_date: str
    pay_frequency: str
    benefits: str
    bonus_income: float
    year_to_date_income: float

    def __str__(self):
        return (
            f"Payroll of ID {self.id} named {self.name} with annual income of ${self.annual_income:.2f}. "
            f"Federal taxes withheld: ${self.federal_taxes_withheld:.2f}, "
            f"State: {self.state}, State taxes withheld: ${self.state_taxes_withheld:.2f}. "
            f"Social Security withheld: ${self.social_security_withheld:.2f}, "
            f"Medicare withheld: ${self.medicare_withheld:.2f}, "
            f"Other deductions: ${self.other_deductions:.2f}. "
            f"Net income for the pay period is ${self.net_income:.2f}. "
            f"Pay period from {self.pay_period_start_date} to {self.pay_period_end_date}. "
            f"Pay frequency is {self.pay_frequency}. "
            f"Benefits include: {self.benefits}. "
            f"Bonus income is ${self.bonus_income:.2f}. "
            f"Year-to-date income is ${self.year_to_date_income:.2f}."
        )


class SummaryOfPayrollWithholdings(BaseModel):
    federal: float
    state: float
    social_security: float
    medicare: float
    other: float

    def __str__(self):
        return (
            f"Federal: ${self.federal:.2f}, "
            f"State: ${self.state:.2f}, "
            f"Social Security: ${self.social_security:.2f}, "
            f"Medicare: ${self.medicare:.2f}, "
            f"Other: ${self.other:.2f}."
        )


class SummaryOfPayrollAccounts(BaseModel):
    total_entries: int
    total_annual_income: float
    total_net_income: float
    total_bonus_income: float
    total_withheld: SummaryOfPayrollWithholdings
    withheld_by_state: dict[str, float]
    pay_frequencies: dict[str, int]
    most_recent_ytd_income: float
    benefits_summary: str

    def __str__(self):
        return (
            f"Summary of Payroll Accounts: "
            f"Total Entries: {self.total_entries}, "
            f"Total Annual Income: ${self.total_annual_income:.2f}, "
            f"Total Net Income: ${self.total_net_income:.2f}, "
            f"Total Bonus Income: ${self.total_bonus_income:.2f}, "
            f"Total Withheld: {str(self.total_withheld)}, "
            f"Withheld by State: {', '.join([f'{key}: ${value:.2f}' for key, value in self.withheld_by_state.items()])}, "
            f"Pay Frequencies: {', '.join([f'{key}: {value}' for key, value in self.pay_frequencies.items()])}, "
            f"Most Recent Year-to-Date Income: ${self.most_recent_ytd_income:.2f}, "
            f"Benefits Summary: {self.benefits_summary}, "
        )


class OtherAccount(BaseModel):
    id: str
    name: str
    type: str
    total_income: float
    total_debt: float

    def __str__(self):
        return (
            f"Other Account of ID {self.id} named {self.name} with total income of ${self.total_income:.2f} "
            f"and total debt of ${self.total_debt:.2f}."
        )


class SummaryOfOtherAccounts(BaseModel):
    total_income: float
    total_debt: float

    def __str__(self):
        return (
            f"Summary of Other Accounts: "
            f"Total Income across all of the other accounts is: ${self.total_income:.2f} "
            f"Total Debt across all of the other accounts is: ${self.total_debt:.2f} "
        )


class BasicCreditCardDetails(BaseModel):
    """
    A model representing a better credit card option.
    """

    name: str = Field(..., description="The name of the credit card.")
    annual_fee: float = Field(..., description="The annual fee for the credit card.")
    rewards_summary: str = Field(
        ...,
        description="The rewards summary including the cash back rates for the credit card.",
    )

    def __str__(self):
        return f"{self.name} credit card - Annual Fee: {self.annual_fee}, Rewards: {self.rewards_summary}"


class OptimalCreditCardSpending(BaseModel):
    """
    A model representing the optimal credit card spending.
    """

    better_credit_cards: list[BasicCreditCardDetails] = Field(
        ..., description="The better credit cards available for the user."
    )
    plan_for_optimization: str = Field(
        ..., description="The plan for optimizing credit card spending."
    )


class UserFinancialSummary(BaseModel):
    """
    A model representing a summary of the user's accounts.
    """

    user_details: UserDetails = Field(..., description="The user's personal details.")
    investment_summary: SummaryOfInvestmentAccounts = Field(
        ..., description="The summary of the user's investment accounts."
    )
    credit_card_summary: SummaryOfCreditCards = Field(
        ..., description="The summary of the user's credit cards."
    )
    checking_summary: SummaryOfCheckingOrSavingsAccounts = Field(
        ..., description="The summary of the user's checking accounts."
    )
    saving_summary: SummaryOfCheckingOrSavingsAccounts = Field(
        ..., description="The summary of the user's saving accounts."
    )
    loans_summary: SummaryOfLoanAccounts = Field(
        ..., description="The summary of the user's loans."
    )
    payrolls_summary: SummaryOfPayrollAccounts = Field(
        ..., description="The summary of the user's payroll accounts."
    )
    traditional_ira_summary: SummaryOfIRAAccounts = Field(
        ..., description="The summary of the user's traditional IRA accounts."
    )
    roth_ira_summary: SummaryOfIRAAccounts = Field(
        ..., description="The summary of the user's Roth IRA accounts."
    )
    retirement_401k_summary: SummaryOf401kAccounts = Field(
        ..., description="The summary of the user's retirement 401(k) accounts."
    )
    roth_401k_summary: SummaryOf401kAccounts = Field(
        ..., description="The summary of the user's Roth 401(k) accounts."
    )
    hsa_summary: SummaryOfHSAAccounts = Field(
        ..., description="The summary of the user's HSA accounts."
    )
    other_accounts_summary: SummaryOfOtherAccounts = Field(
        ..., description="The summary of the user's other accounts."
    )

    def __str__(self):
        return (
            f"User Details: {self.user_details} "
            f"Here is the investment account details {self.investment_summary} "
            f"Here is the credit card details {self.credit_card_summary} "
            f"Here is the checking account details {self.checking_summary} and the saving account details {self.saving_summary} "
            f"Here is the loans details {self.loans_summary} "
            f"Here is the payrolls details {self.payrolls_summary} "
            f"Here is the traditional ira account details {self.traditional_ira_summary} "
            f"Here is the roth ira account details {self.roth_ira_summary} "
            f"Here is the retirement 401k account details {self.retirement_401k_summary} "
            f"Here is the roth 401k account details {self.roth_401k_summary} "
            f"Here is the hsa account details {self.hsa_summary} "
            f"Here is the other accounts details {self.other_accounts_summary}"
        )


class FinancialPlan(BaseModel):
    """
    A model representing a financial plan.
    """

    plan_summary: str = Field(..., description="The summary of the financial plan.")
    instructions: str = Field(
        ..., description="The step by step instructions to follow."
    )

    def __str__(self):
        return f"Financial Plan Summary: {self.plan_summary} - Step by Step Instructions: {self.instructions}"
