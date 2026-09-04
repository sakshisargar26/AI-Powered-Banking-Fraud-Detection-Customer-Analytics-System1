// ==============================
// Credit Score Prediction
// ==============================

const creditForm = document.getElementById("creditForm");

creditForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const data = {
        Age: Number(document.getElementById("age").value),
        Gender: Number(document.getElementById("gender").value),
        Annual_Income: Number(document.getElementById("annual_income").value),
        Employment_Years: Number(document.getElementById("employment").value),
        Monthly_Income: Number(document.getElementById("monthly_income").value),
        Existing_Loan: Number(document.getElementById("loan").value),
        EMI: Number(document.getElementById("emi").value),
        Credit_Card_Utilization: Number(document.getElementById("utilization").value),
        Missed_Payments: Number(document.getElementById("missed").value),
        Savings: Number(document.getElementById("saving").value),
        Loan_History: Number(document.getElementById("history").value)
    };

    try {

        const response = await fetch("http://127.0.0.1:8000/predict_credit_score", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        document.getElementById("result").innerHTML =
            "Predicted Credit Score : " + result.Predicted_Credit_Score;

    } catch (error) {

        document.getElementById("result").innerHTML =
            "Unable to connect FastAPI Server";

        console.log(error);

    }

});


// ==============================
// Loan Default Prediction
// ==============================

const loanForm = document.getElementById("loanForm");

loanForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const data = {
        Age: Number(document.getElementById("loan_age").value),
        Income: Number(document.getElementById("loan_income").value),
        Loan_Amount: Number(document.getElementById("loan_amount").value),
        EMI: Number(document.getElementById("loan_emi").value),
        Employment_Years: Number(document.getElementById("loan_employment").value),
        Credit_Score: Number(document.getElementById("loan_credit_score").value),
        Previous_Defaults: Number(document.getElementById("loan_previous_default").value),
        Debt_to_Income: Number(document.getElementById("loan_debt").value)
    };

    try {

        const response = await fetch("http://127.0.0.1:8000/predict_loan_default", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        document.getElementById("loanResult").innerHTML =
            result.Prediction;

    } catch (error) {

        document.getElementById("loanResult").innerHTML =
            "Unable to connect FastAPI Server";

        console.log(error);

    }

});


// ==============================
// Fraud Detection
// ==============================

const fraudForm = document.getElementById("fraudForm");

fraudForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const data = {
        Amount: Number(document.getElementById("amount").value),
        Transaction_Type: Number(document.getElementById("transaction").value),
        Location: Number(document.getElementById("location").value),
        Device: Number(document.getElementById("device").value),
        Hour: Number(document.getElementById("hour").value),
        Merchant_Category: Number(document.getElementById("merchant").value),
        International: Number(document.getElementById("international").value)
    };

    try {

        const response = await fetch("http://127.0.0.1:8000/predict_fraud", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        document.getElementById("fraudResult").innerHTML =
            result.Prediction;

    } catch (error) {

        document.getElementById("fraudResult").innerHTML =
            "Unable to connect FastAPI Server";

        console.log(error);

    }

});


// ==============================
// Customer Recommendation
// ==============================

const customerForm = document.getElementById("customerForm");

customerForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const data = {
        Age: Number(document.getElementById("customer_age").value),
        Income: Number(document.getElementById("customer_income").value),
        Savings: Number(document.getElementById("customer_savings").value),
        Credit_Score: Number(document.getElementById("customer_credit").value),
        Loan_Amount: Number(document.getElementById("customer_loan").value),
        Spending_Score: Number(document.getElementById("customer_spending").value)
    };

    try {

        const response = await fetch("http://127.0.0.1:8000/recommend_customer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        document.getElementById("customerResult").innerHTML =
            result.Recommended_Customer_Segment;

    } catch (error) {

        document.getElementById("customerResult").innerHTML =
            "Unable to connect FastAPI Server";

        console.log(error);

    }

});