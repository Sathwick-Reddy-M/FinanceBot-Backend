from data_models import *

# Personal Details:

USER_DETAILS = {
    "name": "Jhon Doe",
    "age": 25,
    "state": "California",
    "country": "USA",
    "citizen_of": "USA",
    "tax_filing_status": "single",
    "is_tax_resident": True,
}

USER_DETAILS = UserDetails(**USER_DETAILS)

# Investment / Brokerage Accounts
INVESTMENT_ACCOUNTS = [
    {
        "id": "ACCT-789456123",
        "name": "Tech Portfolio",
        "type": "Investment",
        "uninvested_amount": 1000.00,
        "asset_distribution": [
            {"ticker": "AAPL", "quantity": 50, "average_cost_basis": 145.00},
            {"ticker": "VTI", "quantity": 30, "average_cost_basis": 210.00},
            {"ticker": "TSLA", "quantity": 10, "average_cost_basis": 230.00},
            {"ticker": "JNJ", "quantity": 20, "average_cost_basis": 145.50},
        ],
    },
    {
        "id": "ACCT-456123789",
        "name": "Growth & Income Portfolio",
        "type": "Investment",
        "uninvested_amount": 100.00,
        "asset_distribution": [
            {"ticker": "MSFT", "quantity": 25, "average_cost_basis": 365.00},
            {"ticker": "VOO", "quantity": 15, "average_cost_basis": 400.00},
            {"ticker": "AMZN", "quantity": 40, "average_cost_basis": 135.00},
            {"ticker": "KO", "quantity": 100, "average_cost_basis": 62.00},
            {"ticker": "BND", "quantity": 50, "average_cost_basis": 76.50},
        ],
    },
]

CREDIT_CARDS = [
    {
        "id": "cc001",
        "name": "Chase Sapphire Preferred",
        "type": "Credit Card",
        "total_limit": 15000,
        "current_limit": 8200,
        "rewards_summary": "Earn 3% cashback on dining, including takeout and eligible delivery services, 2% on travel including flights, hotels, and transit, and 1% on all other purchases. Points can be redeemed for travel, gift cards, cash back, or transferred to travel partners for greater value.",
        "interest": 19.99,
        "outstanding_debt": 6800.45,
        "current_billing_cycle_transactions": [
            {"amount": -75.32, "category": "dining"},
            {"amount": -215.67, "category": "travel"},
            {"amount": 500.25, "category": "payment"},
        ],
        "annual_fee": 95,
    },
    {
        "id": "cc002",
        "name": "Capital One Quicksilver",
        "type": "Credit Card",
        "total_limit": 10000,
        "current_limit": 9950,
        "rewards_summary": "Earn unlimited 1.5% cash back on every purchase, every day with no rotating categories or limits to how much you can earn. Includes no foreign transaction fees and access to travel and shopping protection benefits.",
        "interest": 17.49,
        "outstanding_debt": 49.85,
        "current_billing_cycle_transactions": [
            {"amount": -25.12, "category": "utilities"},
            {"amount": -24.73, "category": "groceries"},
        ],
        "annual_fee": 0,
    },
    {
        "id": "cc003",
        "name": "American Express Gold Card",
        "type": "Credit Card",
        "total_limit": 20000,
        "current_limit": 14200,
        "rewards_summary": "Earn 4X Membership Rewards points at restaurants, including takeout and delivery, and at U.S. supermarkets (up to $25,000 per year), 3X points on flights booked directly with airlines or on amextravel.com, and 1X on all other purchases. Additional benefits include monthly dining credits and no foreign transaction fees.",
        "interest": 20.74,
        "outstanding_debt": 5800.91,
        "current_billing_cycle_transactions": [
            {"amount": -100.88, "category": "groceries"},
            {"amount": -300.56, "category": "flights"},
            {"amount": -200.49, "category": "dining"},
            {"amount": 200.15, "category": "payment"},
        ],
        "annual_fee": 250,
    },
    {
        "id": "cc004",
        "name": "Wells Fargo Active Cash",
        "type": "Credit Card",
        "total_limit": 12000,
        "current_limit": 9650,
        "rewards_summary": "Earn unlimited 2% cash rewards on purchases with no category restrictions or annual fee. Cardholders also benefit from cell phone protection when the bill is paid with this card, and access to Visa Signature Concierge services and travel protections.",
        "interest": 18.74,
        "outstanding_debt": 2350.20,
        "current_billing_cycle_transactions": [
            {"amount": -150.75, "category": "electronics"},
            {"amount": -200.33, "category": "subscriptions"},
            {"amount": 300.00, "category": "payment"},
        ],
        "annual_fee": 0,
    },
    {
        "id": "cc005",
        "name": "Citi Custom Cash Card",
        "type": "Credit Card",
        "total_limit": 8000,
        "current_limit": 7940,
        "rewards_summary": "Automatically earn 5% cash back on your top eligible spend category each billing cycle (up to $500), including restaurants, gas stations, groceries, and more. Earn 1% on all other purchases, with rewards automatically adjusted based on your spending habits.",
        "interest": 16.99,
        "outstanding_debt": 60.00,
        "current_billing_cycle_transactions": [{"amount": -60.00, "category": "gas"}],
        "annual_fee": 0,
    },
    {
        "id": "cc006",
        "name": "Discover it Cash Back",
        "type": "Credit Card",
        "total_limit": 9500,
        "current_limit": 8125,
        "rewards_summary": "Earn 5% cash back on everyday purchases at different places each quarter like Amazon.com, grocery stores, restaurants, and gas stations—up to the quarterly maximum when activated. Plus, 1% unlimited cash back on all other purchases and a dollar-for-dollar cash back match at the end of the first year.",
        "interest": 21.49,
        "outstanding_debt": 1375.00,
        "current_billing_cycle_transactions": [
            {"amount": -125.45, "category": "groceries"},
            {"amount": -150.00, "category": "online shopping"},
            {"amount": 200.00, "category": "payment"},
        ],
        "annual_fee": 0,
    },
]

CHECKING_ACCOUNTS = [
    {
        "id": "chk001",
        "name": "Everyday Checking",
        "type": "Checking",
        "rewards_summary": "ATM fee reimbursement up to $10 per month, plus cashback on debit card purchases when enrolled in qualifying programs.",
        "current_amount": 1543.65,
        "interest": 0.01,
        "overdraft_protection": "Linked to primary savings account for automatic overdraft coverage up to $500.",
        "minimum_balance_requirement": 500.00,
        "fee": {
            "no_minimum_balance_fee": 12.00,
            "monthly_fee": 6.95,
            "ATM_fee": 3.00,
            "overdraft_fee": 35.00,
        },
        "current_billing_cycle_transactions": [
            {"amount": -45.87, "category": "groceries"},
            {"amount": -120.00, "category": "subscriptions"},
            {"amount": 2200.00, "category": "salary"},
        ],
    },
    {
        "id": "chk002",
        "name": "SmartSpend Account",
        "type": "Checking",
        "rewards_summary": "No monthly maintenance fees with direct deposit; free online bill pay and mobile check deposits. Earn 0.25% cashback on select debit card purchases.",
        "current_amount": -75.40,
        "interest": 0.00,
        "overdraft_protection": "Linked to credit card for up to $1000 overdraft coverage with interest.",
        "minimum_balance_requirement": 0.00,
        "fee": {
            "no_minimum_balance_fee": 0.00,
            "monthly_fee": 0.00,
            "ATM_fee": 2.50,
            "overdraft_fee": 34.00,
        },
        "current_billing_cycle_transactions": [
            {"amount": -55.00, "category": "transportation"},
            {"amount": -150.00, "category": "groceries"},
            {"amount": 100.00, "category": "refund"},
        ],
    },
]

SAVING_ACCOUNTS = [
    {
        "id": "sav001",
        "name": "High Yield Savings",
        "type": "Savings",
        "rewards_summary": "Earn up to 4.00% APY on balances above $5,000. Free transfers to linked checking. No maintenance fees with $1,000 minimum balance.",
        "current_amount": 12450.78,
        "interest": 4.00,
        "overdraft_protection": "Linked to checking account for overdraft protection up to $1000 with no transfer fees.",
        "minimum_balance_requirement": 1000.00,
        "fee": {
            "no_minimum_balance_fee": 10.00,
            "monthly_fee": 0.00,
            "ATM_fee": 0.00,
            "overdraft_fee": 0.00,
        },
        "current_billing_cycle_transactions": [
            {"amount": -200.00, "category": "emergency fund"},
            {"amount": 500.00, "category": "interest earned"},
        ],
    },
    {
        "id": "sav002",
        "name": "Student Saver",
        "type": "Savings",
        "rewards_summary": "0.25% APY, no monthly maintenance fees for students under 24. Automatic savings transfers from linked debit purchases.",
        "current_amount": 825.32,
        "interest": 0.25,
        "overdraft_protection": "Overdraft coverage available through overdraft line of credit if linked to checking.",
        "minimum_balance_requirement": 0.00,
        "fee": {
            "no_minimum_balance_fee": 0.00,
            "monthly_fee": 0.00,
            "ATM_fee": 2.00,
            "overdraft_fee": 32.00,
        },
        "current_billing_cycle_transactions": [
            {"amount": 50.00, "category": "round-up deposit"},
            {"amount": -75.00, "category": "tuition"},
        ],
    },
    {
        "id": "sav003",
        "name": "Emergency Reserve",
        "type": "Savings",
        "rewards_summary": "Tiered interest rates starting at 1.50% APY. Up to 6 free withdrawals per month. ATM fee refunds up to $20 annually.",
        "current_amount": 7025.10,
        "interest": 1.50,
        "overdraft_protection": "Covers checking overdrafts up to $250 with no interest if paid back within 5 days.",
        "minimum_balance_requirement": 500.00,
        "fee": {
            "no_minimum_balance_fee": 5.00,
            "monthly_fee": 2.50,
            "ATM_fee": 3.00,
            "overdraft_fee": 30.00,
        },
        "current_billing_cycle_transactions": [
            {"amount": -600.00, "category": "car repair"},
            {"amount": 300.00, "category": "paycheck allocation"},
        ],
    },
]

LOANS = [
    {
        "id": "loan001",
        "name": "Personal Loan - Debt Consolidation",
        "type": "Loan",
        "principal_left": 12500.75,
        "interest_rate": 6.75,
        "monthly_contribution": 300.00,
        "loan_term": "5 years",
        "loan_start_date": "2022-05-10",
        "loan_end_date": "2027-05-10",
        "outstanding_balance": 13250.40,
        "total_paid": 4700.60,
        "payment_due_date": "2025-04-20",
        "payment_history": [
            {
                "payment_date": "2025-03-20",
                "amount_paid": 300.00,
                "remaining_balance": 13250.40,
            },
            {
                "payment_date": "2025-02-20",
                "amount_paid": 300.00,
                "remaining_balance": 13550.40,
            },
            {
                "payment_date": "2025-01-20",
                "amount_paid": 300.00,
                "remaining_balance": 13850.40,
            },
        ],
        "loan_type": "personal loan",
        "collateral": "None",
        "current_outstanding_fees": {
            "late_fee": 25.00,
            "prepayment_penalty": 0.00,
            "origination_fee": 150.00,
            "other_fees": 0.00,
        },
        "other_payments": [
            {
                "payment_date": "2024-12-15",
                "payment_amount": 1000.00,
                "payment_type": "prepayment",
                "description": "End-of-year bonus used for early repayment",
            },
            {
                "payment_date": "2023-06-10",
                "payment_amount": 50.00,
                "payment_type": "penalty",
                "description": "Late fee payment",
            },
        ],
    }
]

PAYROLLS = [
    {
        "id": "payroll001",
        "name": "John Doe - Payroll",
        "type": "Payroll",
        "annual_income": 98000.00,
        "federal_taxes_withheld": 820.45,
        "state": "CA",
        "state_taxes_withheld": 320.30,
        "social_security_withheld": 250.00,
        "medicare_withheld": 145.00,
        "other_deductions": 110.00,
        "net_income": 2354.25,
        "pay_period_start_date": "2025-03-24",
        "pay_period_end_date": "2025-04-06",
        "pay_frequency": "biweekly",
        "benefits": "401(k) contribution, Health Insurance (PPO), Dental, Vision",
        "bonus_income": 0.00,
        "year_to_date_income": 24500.00,
    }
]

TRADITIONAL_IRAS = [
    {
        "id": "ira001",
        "name": "John Doe's Traditional IRA",
        "type": "Traditional IRA",
        "uninvested_amount": 1000.00,
        "average_monthly_contribution": 500.00,
        "asset_distribution": [
            {"ticker": "AAPL", "quantity": 50, "average_cost_basis": 145.30},
            {"ticker": "MSFT", "quantity": 30, "average_cost_basis": 310.20},
        ],
    },
    {
        "id": "ira002",
        "name": "Ava Smith's Traditional IRA",
        "type": "Traditional IRA",
        "uninvested_amount": 121.00,
        "average_monthly_contribution": 350.00,
        "asset_distribution": [
            {"ticker": "VTI", "quantity": 100, "average_cost_basis": 210.00},
            {"ticker": "BND", "quantity": 50, "average_cost_basis": 80.00},
        ],
    },
]

ROTH_IRAS = [
    {
        "id": "roth001",
        "name": "Emily Johnson's Roth IRA",
        "type": "Roth IRA",
        "uninvested_amount": 0,
        "average_monthly_contribution": 450.00,
        "asset_distribution": [
            {"ticker": "TSLA", "quantity": 40, "average_cost_basis": 550.00},
            {"ticker": "JNJ", "quantity": 50, "average_cost_basis": 155.00},
            {"ticker": "VIG", "quantity": 30, "average_cost_basis": 150.00},
        ],
    }
]

RETIREMENT_401KS = [
    {
        "id": "k401001",
        "name": "Mark Taylor's 401(k)",
        "type": "Retirement 401k",
        "average_monthly_contribution": 800.00,
        "uninvested_amount": 0,
        "asset_distribution": [
            {"ticker": "GOOGL", "quantity": 25, "average_cost_basis": 2600.00},
            {"ticker": "VZ", "quantity": 150, "average_cost_basis": 50.00},
            {"ticker": "SPY", "quantity": 30, "average_cost_basis": 440.00},
        ],
        "employer_match": "The employer contributes 100% of the first 5% of the employee's salary, meaning if Mark contributes 5% of his salary towards the 401(k), his employer matches it dollar-for-dollar. If he contributes 6%, only the first 5% gets matched. This employer match is automatically deposited monthly.",
    },
    {
        "id": "k401002",
        "name": "Sophia Green's 401(k)",
        "type": "Retirement 401k",
        "average_monthly_contribution": 1200.00,
        "uninvested_amount": 0,
        "asset_distribution": [
            {"ticker": "VTI", "quantity": 80, "average_cost_basis": 210.00},
            {"ticker": "BND", "quantity": 50, "average_cost_basis": 82.00},
        ],
        "employer_match": "The employer offers a 50% match on employee contributions up to 8% of their annual salary. This means if Sophia contributes 8%, her employer will match 4% of her salary. The match is deposited quarterly into her 401(k) account.",
    },
    {
        "id": "k401003",
        "name": "James Wilson's 401(k)",
        "type": "Retirement 401k",
        "average_monthly_contribution": 1500.00,
        "uninvested_amount": 1000.00,
        "asset_distribution": [
            {"ticker": "MSFT", "quantity": 40, "average_cost_basis": 310.00},
            {"ticker": "VEU", "quantity": 100, "average_cost_basis": 57.00},
            {"ticker": "VIG", "quantity": 70, "average_cost_basis": 150.00},
        ],
        "employer_match": "James' employer offers a 3% employer match contribution for all employees. If James contributes at least 3% of his salary into his 401(k), his employer will match his contributions at a 3% rate, which is automatically deposited into his 401(k) account every month.",
    },
]

ROTH_401KS = [
    {
        "id": "k401004",
        "name": "Emma Davis's Roth 401(k)",
        "type": "Roth 401k",
        "average_monthly_contribution": 1000.00,
        "uninvested_amount": 1000.00,
        "asset_distribution": [
            {"ticker": "VTI", "quantity": 60, "average_cost_basis": 220.00},
            {"ticker": "QCOM", "quantity": 45, "average_cost_basis": 130.00},
        ],
        "employer_match": "Emma's employer offers a 100% match on employee contributions up to 6% of their annual salary. If Emma contributes at least 6% of her salary towards her Roth 401(k), the employer will match this 100%. The matching contribution is made on a monthly basis.",
    }
]

HSA_ACCOUNTS = [
    {
        "id": "hsa001",
        "name": "John Doe's HSA",
        "type": "HSA",
        "average_monthly_contribution": 300.00,
        "uninvested_amount": 0,
        "asset_distribution": [
            {"ticker": "VHT", "quantity": 100, "average_cost_basis": 235.00},
            {"ticker": "SCHD", "quantity": 50, "average_cost_basis": 70.00},
        ],
    }
]

OTHER_ACCOUNTS = [
    {
        "id": "other001",
        "name": "Freelance Income",
        "type": "other",
        "total_income": 4500.00,
        "total_debt": 1500.00,
    },
    {
        "id": "other002",
        "name": "Side Business Income",
        "type": "Other",
        "total_income": 2200.50,
        "total_debt": 800.00,
    },
    {
        "id": "other003",
        "name": "Rental Property Income",
        "type": "Other",
        "total_income": 3500.00,
        "total_debt": 20000.00,
    },
]

# Dictionaries for faster access

INVESTMENT_ACCOUNTS = [InvestmentAccount(**account) for account in INVESTMENT_ACCOUNTS]
CREDIT_CARDS = [CreditCard(**card) for card in CREDIT_CARDS]
CHECKING_ACCOUNTS = [
    CheckingOrSavingsAccount(**account) for account in CHECKING_ACCOUNTS
]
SAVING_ACCOUNTS = [CheckingOrSavingsAccount(**account) for account in SAVING_ACCOUNTS]
LOANS = [Loan(**loan) for loan in LOANS]
PAYROLLS = [Payroll(**payroll) for payroll in PAYROLLS]
TRADITIONAL_IRAS = [TraditionalIRA(**ira) for ira in TRADITIONAL_IRAS]
ROTH_IRAS = [RothIRA(**ira) for ira in ROTH_IRAS]
RETIREMENT_401KS = [Retirement401K(**account) for account in RETIREMENT_401KS]
ROTH_401KS = [Roth401K(**account) for account in ROTH_401KS]
HSA_ACCOUNTS = [HSAAccount(**account) for account in HSA_ACCOUNTS]
OTHER_ACCOUNTS = [OtherAccount(**account) for account in OTHER_ACCOUNTS]

INVESTMENT_ACCOUNTS_DICT = {account.id: account for account in INVESTMENT_ACCOUNTS}
CREDIT_CARDS_DICT = {card.id: card for card in CREDIT_CARDS}
CHECKING_ACCOUNTS_DICT = {account.id: account for account in CHECKING_ACCOUNTS}
SAVING_ACCOUNTS_DICT = {account.id: account for account in SAVING_ACCOUNTS}
LOANS_DICT = {loan.id: loan for loan in LOANS}
PAYROLLS_DICT = {payroll.id: payroll for payroll in PAYROLLS}
TRADITIONAL_IRAS_DICT = {ira.id: ira for ira in TRADITIONAL_IRAS}
ROTH_IRAS_DICT = {ira.id: ira for ira in ROTH_IRAS}
RETIREMENT_401KS_DICT = {account.id: account for account in RETIREMENT_401KS}
ROTH_401KS_DICT = {account.id: account for account in ROTH_401KS}
HSA_ACCOUNTS_DICT = {account.id: account for account in HSA_ACCOUNTS}
OTHER_ACCOUNTS_DICT = {account.id: account for account in OTHER_ACCOUNTS}
