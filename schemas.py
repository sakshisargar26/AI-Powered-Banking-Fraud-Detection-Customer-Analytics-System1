from pydantic import BaseModel
from typing import Optional, Union, Any

# Credit Prediction Schema
class CreditInput(BaseModel):
    Age: int
    Gender: Union[int, str]
    Annual_Income: float
    Employment_Years: float
    Monthly_Income: float
    Existing_Loan: float
    EMI: float
    Credit_Card_Utilization: float
    Missed_Payments: int
    Savings: float
    Loan_History: Union[int, str]

# Loan Prediction Schema
class LoanInput(BaseModel):
    Age: int
    Income: float
    Loan_Amount: float
    EMI: float
    Employment_Years: float
    Credit_Score: int
    Previous_Defaults: int
    Debt_to_Income: float

# Fraud Detection Schema
class FraudInput(BaseModel):
    Amount: float
    Transaction_Type: Union[int, str] = "IMPS"
    Location: Union[int, str] = "Mumbai"
    Device: Union[int, str] = "Mobile"
    Hour: int
    Merchant_Category: Union[int, str] = "Retail"
    International: int = 0

# Customer Recommendation Schema
class CustomerInput(BaseModel):
    Age: int
    Income: float
    Savings: float
    Credit_Score: int
    Loan_Amount: float
    Spending_Score: int

# Contact Form Schema
class ContactInput(BaseModel):
    name: str
    email: str
    department: Optional[str] = "General"
    message: str