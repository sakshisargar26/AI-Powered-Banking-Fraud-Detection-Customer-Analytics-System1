# SmartBank AI Analytics Platform

An end-to-end full-stack Banking Decision Support system connecting a responsive HTML5/CSS3/JavaScript Frontend to a FastAPI Machine Learning backend backed by PostgreSQL.

## Features & Modules
1. **Credit Score Prediction**: Estimates customer credit scores (300–900) using Linear Regression with standard feature scaling (`scaler.pkl`).
2. **Loan Default Detection**: Evaluates credit default risks and probability using Logistic Regression (`loan_default_model.pkl`).
3. **Fraud Detection**: Flags high-risk telemetric vectors using a Decision Tree Classifier (`fraud_detection_model.pkl`).
4. **Customer Recommendation**: Profiles customers into Gold, Platinum, and Silver tiers using K-Nearest Neighbors (KNN) with peer-profile matching.
5. **PostgreSQL Database Storage**: Automatically logs all predictions into database tables (`credit_predictions`, `loan_predictions`, `fraud_predictions`, `customer_predictions`, `contact_messages`).
6. **Admin Command Center**: Real-time administrative dashboard for querying, monitoring, and managing database records.

---

## Tech Stack
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (Fetch API), FontAwesome 6
- **Backend**: FastAPI, Uvicorn, Pydantic, SQLAlchemy
- **Database**: PostgreSQL (`banking1_db`)
- **Machine Learning**: Scikit-Learn, Joblib, NumPy, Pandas

---

## How to Run

### 1. Start the FastAPI Backend
Open a terminal in the `backend/` folder and run:
```bash
python -m uvicorn main25:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Open the Frontend
You can either:
- Open `frontend/index.html` directly in your web browser (Chrome, Edge, Firefox), OR
- Serve it via a local static web server from the `frontend/` folder:
```bash
python -m http.server 5500
```
Then visit: [http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html)

---

## API Endpoints
- `GET  /` - System & Database Health Check
- `POST /predict_credit_score` - Scaled Credit Score Estimation
- `POST /predict_loan_default` - Default Risk Probability & Assessment
- `POST /predict_fraud` - Anomaly Threat Index
- `POST /recommend_customer` - KNN Customer Segmentation & Offers
- `POST /contact` - Dispatch & Store Operations Ticket
- `GET  /get_loan_data` - Retrieve logged loan predictions
- `GET  /get_credit_data` - Retrieve logged credit predictions
- `GET  /get_fraud_data` - Retrieve logged fraud predictions
- `GET  /get_contacts` - Retrieve logged support messages
- `DELETE /delete_loan/{loan_id}` - Delete specific loan record