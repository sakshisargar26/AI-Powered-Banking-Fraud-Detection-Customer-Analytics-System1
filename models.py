from sqlalchemy import Column, Integer, Float, String, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class CreditPrediction(Base):
    __tablename__ = "credit_predictions"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(Integer)
    annual_income = Column(Integer)
    employment_years = Column(Integer)
    monthly_income = Column(Integer)
    existing_loan = Column(Integer)
    emi = Column(Integer)
    credit_card_utilization = Column(Integer)
    missed_payments = Column(Integer)
    savings = Column(Integer)
    loan_history = Column(Integer)
    predicted_credit_score = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())

class LoanPrediction(Base):
    __tablename__ = "loan_predictions"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    income = Column(Integer)
    loan_amount = Column(Integer)
    emi = Column(Integer)
    employment_years = Column(Integer)
    credit_score = Column(Integer)
    previous_defaults = Column(Integer)
    debt_to_income = Column(Integer)
    prediction = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

class FraudPrediction(Base):
    __tablename__ = "fraud_predictions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    transaction_type = Column(Integer)
    location = Column(Integer)
    device = Column(Integer)
    hour = Column(Integer)
    merchant_category = Column(Integer)
    international = Column(Integer)
    prediction = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

class CustomerPrediction(Base):
    __tablename__ = "customer_predictions"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    income = Column(Integer)
    savings = Column(Integer)
    credit_score = Column(Integer)
    loan_amount = Column(Integer)
    spending_score = Column(Integer)
    recommended_segment = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())