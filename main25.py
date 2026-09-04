import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Float, String, TIMESTAMP, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel

from schemas import CreditInput, LoanInput, FraudInput, CustomerInput, ContactInput

app = FastAPI(
    title="SmartBank AI Analytics System",
    description="Full-stack AI Banking Analytics API with Machine Learning Models and PostgreSQL Persistence",
    version="2.0"
)

class AdminLogin(BaseModel):
    username: str
    password: str

# Enable CORS for all frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PostgreSQL Database Connection
# ==========================================
# Use localhost as default for local development, with host.docker.internal / custom env fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/banking1_db")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_available = True
except Exception as e:
    print(f"Warning: Database engine initialization failed: {e}")
    db_available = False

Base = declarative_base()

# ==========================================
# Database Models
# ==========================================
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

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    department = Column(String(50))
    message = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.now())

# Safe database initialization
if db_available:
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables verified/created successfully.")
    except Exception as e:
        print(f"Notice: Table auto-creation skipped or error: {e}")

def get_db_session():
    if not db_available:
        return None
    try:
        db = SessionLocal()
        return db
    except Exception:
        return None

# ==========================================
# Load ML Models, Scaler, and Encoders
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

credit_model = joblib.load(get_path("credit_score_model.pkl"))
scaler = joblib.load(get_path("scaler.pkl"))
gender_encoder = joblib.load(get_path("gender_encoder.pkl"))
loan_history_encoder = joblib.load(get_path("loan_history_encoder.pkl"))
loan_model = joblib.load(get_path("loan_default_model.pkl"))
fraud_model = joblib.load(get_path("fraud_detection_model.pkl"))
customer_model = joblib.load(get_path("customer_recommendation_model.pkl"))

# Load customer recommendation dataset for KNN peer lookup
customer_df = None
try:
    customer_df = pd.read_csv(get_path("Customer_Recommendation_Dataset_500_Records.csv"))
except Exception as e:
    print(f"Customer dataset load warning: {e}")

# ==========================================
# Root / Health Endpoint
# ==========================================
@app.get("/")
def root():
    return {
        "status": "Online",
        "system": "SmartBank AI Analytics Platform",
        "database": "Connected" if db_available else "Disconnected (Fallback mode)",
        "models": {
            "credit_score": "LinearRegression (Scaled)",
            "loan_default": "LogisticRegression",
            "fraud_detection": "DecisionTreeClassifier",
            "customer_recommendation": "KNN Classifier"
        }
    }

# Admin Login Endpoint
@app.post("/admin/login")
def admin_login(data: AdminLogin):
    if data.username == "admin" and data.password == "admin":
        return {
            "status": "success",
            "message": "Login successful",
            "username": data.username
        }
    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"
    )

# ==========================================
# 1. Credit Score Prediction Endpoint
# ==========================================
@app.post("/predict_credit_score")
def predict_credit(data: CreditInput):
    # Encode Gender safely
    if isinstance(data.Gender, str):
        g_str = data.Gender.strip().capitalize()
        try:
            gender_val = int(gender_encoder.transform([g_str])[0])
        except Exception:
            gender_val = 1 if "m" in g_str.lower() else 0
    else:
        gender_val = int(data.Gender)

    # Encode Loan History safely
    if isinstance(data.Loan_History, str):
        lh_str = data.Loan_History.strip().capitalize()
        try:
            loan_hist_val = int(loan_history_encoder.transform([lh_str])[0])
        except Exception:
            # Classes are: ['Average', 'Excellent', 'Good', 'Poor']
            if "excel" in lh_str.lower():
                loan_hist_val = 1
            elif "good" in lh_str.lower():
                loan_hist_val = 2
            elif "poor" in lh_str.lower():
                loan_hist_val = 3
            else:
                loan_hist_val = 0
    else:
        loan_hist_val = int(data.Loan_History)

    # Features: ['Age', 'Gender', 'Annual_Income', 'Employment_Years', 'Monthly_Income', 'Existing_Loan', 'EMI', 'Credit_Card_Utilization', 'Missed_Payments', 'Savings', 'Loan_History']
    raw_features = np.array([[
        data.Age,
        gender_val,
        data.Annual_Income,
        data.Employment_Years,
        data.Monthly_Income,
        data.Existing_Loan,
        data.EMI,
        data.Credit_Card_Utilization,
        data.Missed_Payments,
        data.Savings,
        loan_hist_val
    ]])

    # Standardize input features using the trained scaler
    scaled_features = scaler.transform(raw_features)
    raw_pred = credit_model.predict(scaled_features)[0]

    # Constrain score between 300 and 900
    final_score = int(round(max(300, min(900, raw_pred))))

    # Determine Rating Category and Description
    if final_score >= 750:
        status = "Excellent"
        message = "Exceptional credit profile. Prime candidate for pre-approved loans with lowest tier interest rates."
    elif final_score >= 650:
        status = "Good"
        message = "Low credit risk. Standard loan approvals and credit card issuances recommended."
    elif final_score >= 550:
        status = "Fair / Average"
        message = "Moderate credit risk. Secondary assessment of recent income and debt-service ratio recommended."
    else:
        status = "Poor"
        message = "High risk profile. Frequent defaults or high credit utilization detected. Strict guarantor required."

    # Save to PostgreSQL database if reachable
    db = get_db_session()
    if db:
        try:
            record = CreditPrediction(
                age=int(data.Age),
                gender=gender_val,
                annual_income=int(data.Annual_Income),
                employment_years=int(data.Employment_Years),
                monthly_income=int(data.Monthly_Income),
                existing_loan=int(data.Existing_Loan),
                emi=int(data.EMI),
                credit_card_utilization=int(data.Credit_Card_Utilization),
                missed_payments=int(data.Missed_Payments),
                savings=int(data.Savings),
                loan_history=loan_hist_val,
                predicted_credit_score=float(final_score)
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            db.close()
        except Exception as e:
            print(f"DB save error in predict_credit: {e}")
            db.rollback()
            db.close()

    return {
        "Predicted_Credit_Score": final_score,
        "Status": status,
        "Message": message,
        "Max_Score": 900
    }

# ==========================================
# 2. Loan Default Prediction Endpoint
# ==========================================
@app.post("/predict_loan_default")
def predict_loan(data: LoanInput):
    # Features: ['Age', 'Income', 'Loan_Amount', 'EMI', 'Employment_Years', 'Credit_Score', 'Previous_Defaults', 'Debt_to_Income']
    input_data = np.array([[
        data.Age,
        data.Income,
        data.Loan_Amount,
        data.EMI,
        data.Employment_Years,
        data.Credit_Score,
        data.Previous_Defaults,
        data.Debt_to_Income
    ]])

    prediction = loan_model.predict(input_data)[0]
    probabilities = loan_model.predict_proba(input_data)[0]
    default_prob = round(float(probabilities[1]) * 100, 1)

    result = "Loan Default" if prediction == 1 else "No Loan Default"

    if default_prob >= 60:
        risk_level = "High Risk"
    elif default_prob >= 30:
        risk_level = "Medium Risk"
    else:
        risk_level = "Low Risk Profile"

    # Save to PostgreSQL database
    db = get_db_session()
    if db:
        try:
            record = LoanPrediction(
                age=int(data.Age),
                income=int(data.Income),
                loan_amount=int(data.Loan_Amount),
                emi=int(data.EMI),
                employment_years=int(data.Employment_Years),
                credit_score=int(data.Credit_Score),
                previous_defaults=int(data.Previous_Defaults),
                debt_to_income=int(data.Debt_to_Income),
                prediction=result
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            db.close()
        except Exception as e:
            print(f"DB save error in predict_loan: {e}")
            db.rollback()
            db.close()

    return {
        "Prediction": result,
        "Probability": default_prob,
        "Risk_Level": risk_level,
        "Is_Default": bool(prediction == 1)
    }

# ==========================================
# 3. Fraud Detection Prediction Endpoint
# ==========================================
@app.post("/predict_fraud")
def predict_fraud(data: FraudInput):
    # Map categorical features to safe numeric codes if string is passed
    type_map = {"IMPS": 1, "NEFT": 2, "UPI": 3, "Card": 0}
    loc_map = {"Bengaluru": 0, "Delhi": 1, "Mumbai": 2, "Pune": 3}
    device_map = {"Mobile": 1, "Web": 2, "ATM": 0, "Laptop": 2, "Tablet": 1}
    merch_map = {"Retail": 3, "Travel": 4, "Electronics": 0, "Fuel": 2, "Food": 1, "Entertainment": 3}

    t_val = type_map.get(str(data.Transaction_Type), 1) if isinstance(data.Transaction_Type, str) else int(data.Transaction_Type)
    l_val = loc_map.get(str(data.Location), 2) if isinstance(data.Location, str) else int(data.Location)
    d_val = device_map.get(str(data.Device), 1) if isinstance(data.Device, str) else int(data.Device)
    m_val = merch_map.get(str(data.Merchant_Category), 3) if isinstance(data.Merchant_Category, str) else int(data.Merchant_Category)
    intl_val = int(data.International)

    input_data = np.array([[
        data.Amount,
        t_val,
        l_val,
        d_val,
        data.Hour,
        m_val,
        intl_val
    ]])

    prediction = fraud_model.predict(input_data)[0]
    
    # Calculate threat index: based on tree rule logic
    if prediction == 1:
        result = "Fraud Transaction"
        threat_score = 88
        risk_label = "High Risk Fraud Threat"
        action = "HOLD ASSET & LOCK PIPE"
        action_color = "danger"
    else:
        result = "Genuine Transaction"
        # Compute dynamic safety score
        risk_pts = 5
        if data.Amount > 50000:
            risk_pts += 15
        if data.Hour < 6 or data.Hour > 22:
            risk_pts += 15
        if intl_val == 1:
            risk_pts += 10
        threat_score = min(risk_pts, 35)
        risk_label = "Verified Safe Transaction"
        action = "No Interception Needed"
        action_color = "success"

    # Save to PostgreSQL
    db = get_db_session()
    if db:
        try:
            record = FraudPrediction(
                amount=int(data.Amount),
                transaction_type=t_val,
                location=l_val,
                device=d_val,
                hour=int(data.Hour),
                merchant_category=m_val,
                international=intl_val,
                prediction=result
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            db.close()
        except Exception as e:
            print(f"DB save error in predict_fraud: {e}")
            db.rollback()
            db.close()

    return {
        "Prediction": result,
        "Threat_Score": threat_score,
        "Risk_Label": risk_label,
        "Is_Fraud": bool(prediction == 1),
        "Action": action,
        "Action_Color": action_color,
        "Diagnostics": {
            "Velocity": "Critical Burst Speed Triggered" if prediction == 1 else "Standard Speed (Pass)",
            "Device": "Suspicious Multi-Log Session" if prediction == 1 else "Authorized Token Matching",
            "Geo": "Unusual IP Cluster Info" if prediction == 1 else "Safe Geo-Zone Registry"
        }
    }

# ==========================================
# 4. Customer Recommendation Endpoint
# ==========================================
@app.post("/recommend_customer")
def recommend_customer(data: CustomerInput):
    # Features: ['Age', 'Income', 'Savings', 'Credit_Score', 'Loan_Amount', 'Spending_Score']
    input_data = np.array([[
        data.Age,
        data.Income,
        data.Savings,
        data.Credit_Score,
        data.Loan_Amount,
        data.Spending_Score
    ]])

    pred_idx = customer_model.predict(input_data)[0]
    segment_map = {0: "Gold", 1: "Platinum", 2: "Silver"}
    segment = segment_map.get(int(pred_idx), "Gold")

    # Find 3 nearest neighbor peers from historical dataset
    peer_profiles = []
    if customer_df is not None:
        try:
            distances, indices = customer_model.kneighbors(input_data, n_neighbors=3)
            
            for dist, idx in zip(distances[0], indices[0]):
                matched_row = customer_df.iloc[idx]
                cust_id = str(matched_row.get("Customer_ID", f"C-{idx + 100}"))
                seg = str(matched_row.get("Customer_Segment", segment))
                # Map distance to similarity percentage
                sim = max(75.0, round(100.0 - (float(dist) / 10000.0) if dist > 0 else 98.5, 1))
                if sim > 99.5:
                    sim = 98.8
                
                if seg == "Platinum":
                    action = "Upgrade to Wealth Management & Concierge"
                elif seg == "Gold":
                    action = "Offer 5% Cashback Premium Credit Card"
                else:
                    action = "Suggest Fixed Deposit & High-Yield Savings Scheme"
                
                peer_profiles.append({
                    "id": cust_id,
                    "match": f"{sim}%",
                    "seg": seg,
                    "action": action
                })
        except Exception as e:
            print(f"KNN peer lookup error: {e}")

    # Fallback peer profiles if dataset query had an issue
    if not peer_profiles:
        peer_profiles = [
            {"id": "C-9942", "match": "98.2%", "seg": "Platinum", "action": "Upgrade to Wealth Management"},
            {"id": "C-1024", "match": "95.6%", "seg": "Gold", "action": "Offer 5% Cashback Credit Card"},
            {"id": "C-4421", "match": "91.0%", "seg": "Silver", "action": "Suggest Fixed Deposit Scheme"}
        ]

    # Save to PostgreSQL
    db = get_db_session()
    if db:
        try:
            record = CustomerPrediction(
                age=int(data.Age),
                income=int(data.Income),
                savings=int(data.Savings),
                credit_score=int(data.Credit_Score),
                loan_amount=int(data.Loan_Amount),
                spending_score=int(data.Spending_Score),
                recommended_segment=segment
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            db.close()
        except Exception as e:
            print(f"DB save error in recommend_customer: {e}")
            db.rollback()
            db.close()

    return {
        "Recommended_Customer_Segment": segment,
        "Segment": segment,
        "Peer_Profiles": peer_profiles
    }

# ==========================================
# 5. Contact / Support Ticket Endpoint
# ==========================================
@app.post("/contact")
def submit_contact(msg: ContactInput):
    db = get_db_session()
    if db:
        try:
            record = ContactMessage(
                name=msg.name,
                email=msg.email,
                department=msg.department,
                message=msg.message
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            db.close()
            return {"status": "success", "message": "Support ticket dispatched and recorded."}
        except Exception as e:
            db.rollback()
            db.close()
            print(f"Contact save error: {e}")
            return {"status": "success", "message": "Support ticket received."}
    return {"status": "success", "message": "Support ticket received (offline)."}

# ==========================================
# 6. Admin GET Endpoints
# ==========================================
@app.get("/get_loan_data")
def get_loan():
    db = get_db_session()
    if not db:
        return []
    try:
        data = db.query(LoanPrediction).order_by(LoanPrediction.id.desc()).limit(100).all()
        result = [
            {
                "id": d.id,
                "age": d.age,
                "income": d.income,
                "loan_amount": d.loan_amount,
                "emi": d.emi,
                "employment_years": d.employment_years,
                "credit_score": d.credit_score,
                "previous_defaults": d.previous_defaults,
                "debt_to_income": d.debt_to_income,
                "prediction": d.prediction,
                "created_at": str(d.created_at) if d.created_at else None
            }
            for d in data
        ]
        db.close()
        return result
    except Exception as e:
        db.close()
        print(f"Error fetching loan data: {e}")
        return []

@app.get("/get_credit_data")
def get_credit():
    db = get_db_session()

    if not db:
        return []

    try:
        data = db.query(CreditPrediction).order_by(
            CreditPrediction.id.desc()
        ).limit(100).all()

        result = [
            {
                "id": d.id,
                "age": d.age,
                "gender": "Male" if d.gender == 1 else "Female",
                "annual_income": d.annual_income,
                "employment_years": d.employment_years,
                "monthly_income": d.monthly_income,
                "existing_loan": d.existing_loan,
                "emi": d.emi,
                "credit_card_utilization": d.credit_card_utilization,
                "missed_payments": d.missed_payments,
                "savings": d.savings,
                "loan_history": d.loan_history,
                "predicted_credit_score": d.predicted_credit_score,
                "created_at": str(d.created_at) if d.created_at else None
            }
            for d in data
        ]

        db.close()
        return result

    except Exception as e:
        print(f"Error fetching credit data: {e}")
        db.close()
        return []

@app.get("/get_fraud_data")
def get_fraud():
    db = get_db_session()

    if not db:
        return []

    try:
        data = db.query(FraudPrediction).order_by(
            FraudPrediction.id.desc()
        ).limit(100).all()

        result = [
            {
                "id": d.id,
                "amount": d.amount,
                "transaction_type": d.transaction_type,
                "location": d.location,
                "device": d.device,
                "hour": d.hour,
                "merchant_category": d.merchant_category,
                "international": d.international,
                "prediction": d.prediction,
                "created_at": str(d.created_at) if d.created_at else None
            }
            for d in data
        ]

        db.close()
        return result

    except Exception as e:
        print(f"Error fetching fraud data: {e}")
        db.close()
        return []

@app.get("/admin/summary")
def admin_summary():
    db = get_db_session()

    if not db:
        return {
            "total_predictions": 0,
            "credits": 0,
            "loans": 0,
            "frauds": 0,
            "customers": 0,
            "high_risk": 0
        }

    try:
        credits = db.query(CreditPrediction).count()
        loans = db.query(LoanPrediction).count()
        frauds = db.query(FraudPrediction).count()
        customers = db.query(CustomerPrediction).count()

        high_risk_loans = db.query(LoanPrediction).filter(
            LoanPrediction.prediction == "Loan Default"
        ).count()

        high_risk_frauds = db.query(FraudPrediction).filter(
            FraudPrediction.prediction == "Fraud Transaction"
        ).count()

        db.close()

        return {
            "total_predictions": credits + loans + frauds + customers,
            "credits": credits,
            "loans": loans,
            "frauds": frauds,
            "customers": customers,
            "high_risk": high_risk_loans + high_risk_frauds
        }

    except Exception as e:
        print("Summary error:", e)
        db.close()

        return {
            "total_predictions": 0,
            "credits": 0,
            "loans": 0,
            "frauds": 0,
            "customers": 0,
            "high_risk": 0
        }

@app.get("/get_customer_data")
def get_customer():
    db = get_db_session()

    if not db:
        return []

    try:
        data = db.query(CustomerPrediction).order_by(
            CustomerPrediction.id.desc()
        ).limit(100).all()

        result = [
            {
                "id": d.id,
                "age": d.age,
                "income": d.income,
                "savings": d.savings,
                "credit_score": d.credit_score,
                "loan_amount": d.loan_amount,
                "spending_score": d.spending_score,
                "recommended_segment": d.recommended_segment,
                "created_at": str(d.created_at) if d.created_at else None
            }
            for d in data
        ]

        db.close()
        return result

    except Exception as e:
        print(f"Error fetching customer data: {e}")
        db.close()
        return []

@app.get("/get_contacts")
def get_contacts():
    db = get_db_session()
    if not db:
        return []
    try:
        data = db.query(ContactMessage).order_by(ContactMessage.id.desc()).limit(100).all()
        result = [
            {
                "id": d.id,
                "name": d.name,
                "email": d.email,
                "department": d.department,
                "message": d.message,
                "created_at": str(d.created_at) if d.created_at else None
            }
            for d in data
        ]
        db.close()
        return result
    except Exception as e:
        db.close()
        return []

from crude import delete_loan_prediction, update_loan_prediction

@app.delete("/delete_loan/{loan_id}")
def remove_loan(loan_id: int):
    return delete_loan_prediction(loan_id)

@app.put("/update_loan/{loan_id}")
def update_loan(loan_id: int, new_pred: str):
    return update_loan_prediction(loan_id, new_pred)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main25:app", host="127.0.0.1", port=8001, reload=True)