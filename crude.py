from sqlalchemy.orm import Session
from main25 import SessionLocal, LoanPrediction, CreditPrediction, FraudPrediction, CustomerPrediction

def get_all_loan_predictions():
    db = SessionLocal()
    data = db.query(LoanPrediction).all()
    db.close()
    return data

def delete_loan_prediction(loan_id: int):
    db = SessionLocal()
    record = db.query(LoanPrediction).filter(LoanPrediction.id == loan_id).first()
    if record:
        db.delete(record)
        db.commit()
    db.close()
    return {"message": "Record Deleted"}


def update_loan_prediction(loan_id: int, new_prediction: str):
    db = SessionLocal()
    record = db.query(LoanPrediction).filter(LoanPrediction.id == loan_id).first()
    if record:
        record.prediction = new_prediction
        db.commit()
        db.refresh(record)
    db.close()
    return record

def get_loan_by_id(loan_id: int):
    db = SessionLocal()
    record = db.query(LoanPrediction).filter(LoanPrediction.id == loan_id).first()
    db.close()
    return record