import pandas as pd
import random
import hashlib
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

# Load data from CSV files
companies_df = pd.read_csv('companies.csv')
customers_df = pd.read_csv('customers.csv')
transactions_df = pd.read_csv('transactions.csv')
risk_assessment_df = pd.read_csv('risk_assessment.csv')

# 1. Define the Company Class
class Company:
    def __init__(self, company_id, name, address):
        self.company_id = company_id
        self.name = name
        self.address = address
        self.transactions = []

# 2. Define the Customer Class
class Customer:
    def __init__(self, customer_id, name, phone, address):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.address = address
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

# 3. Define the Transaction Class
class Transaction:
    def __init__(self, transaction_id, amount, method, customer_id, company_id, timestamp, hash):
        self.transaction_id = transaction_id
        self.amount = amount
        self.method = method
        self.customer_id = customer_id
        self.company_id = company_id
        self.timestamp = timestamp
        self.hash = hash
        self.risk_assessment = None  # Linked to a RiskAssessment later

    def add_risk_assessment(self, risk_assessment):
        self.risk_assessment = risk_assessment

# 4. Define the RiskAssessment Class with Prediction Logic
class RiskAssessment:
    def __init__(self, assessment_id, risk_score, customer_id, transaction_id, timestamp, model=None):
        self.assessment_id = assessment_id
        self.risk_score = risk_score
        self.timestamp = timestamp
        self.customer_id = customer_id
        self.transaction_id = transaction_id
        self.model = model  # The linear regression model for predictions

    def predict_risk(self, amount):
        # Use the model to predict the risk based on the transaction amount
        if self.model:
            # Ensure that the input is in the same format as the training data
            X_new = pd.DataFrame([[amount]], columns=['Amount'])  # Create DataFrame with the same column name
            predicted_risk = self.model.predict(X_new)[0]
            return predicted_risk
        return None

# 5. Initialize Entities from CSV Data
def initialize_entities():
    # Initialize companies
    companies = []
    for _, row in companies_df.iterrows():
        companies.append(Company(row['CompanyID'], row['Name'], row['Address']))

    # Initialize customers
    customers = []
    for _, row in customers_df.iterrows():
        customers.append(Customer(row['CustomerID'], row['Name'], row['Phone'], row['Address']))

    # Initialize transactions
    transactions = []
    for _, row in transactions_df.iterrows():
        transaction = Transaction(row['TransactionID'], row['Amount'], row['Method'], 
                                  row['CustomerID'], row['CompanyID'], row['Timestamp'], row['Hash'])
        transactions.append(transaction)

    # Initialize risk assessments
    risk_assessments = []
    for _, row in risk_assessment_df.iterrows():
        risk_assessment = RiskAssessment(row['AssessmentID'], row['RiskScore'], 
                                         row['CustomerID'], row['TransactionID'], row['Timestamp'])
        risk_assessments.append(risk_assessment)

    return companies, customers, transactions, risk_assessments

# 6. Link Risk Assessments to Transactions
def link_risk_assessments_to_transactions(transactions, risk_assessments):
    for transaction in transactions:
        for risk_assessment in risk_assessments:
            if transaction.transaction_id == risk_assessment.transaction_id:
                transaction.add_risk_assessment(risk_assessment)

# 7. Simulate New Transactions (Simplified)
def simulate_new_transactions(customers, companies):
    new_transactions = []
    for _ in range(10):  # Simulate 10 new transactions (reduced number)
        customer = random.choice(customers)
        company = random.choice(companies)
        amount = random.randint(100, 10000)  # Random transaction amount
        method = random.choice(['Credit', 'Debit'])  # Random payment method
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate a unique transaction ID and hash
        transaction_id = f"T{random.randint(10000, 99999)}"
        hash = hashlib.sha256(f"{transaction_id}{amount}{method}{timestamp}".encode()).hexdigest()

        # Create a new transaction
        new_transaction = Transaction(transaction_id, amount, method, customer.customer_id, company.company_id, timestamp, hash)
        customer.add_transaction(new_transaction)
        company.transactions.append(new_transaction)
        new_transactions.append(new_transaction)

    return new_transactions

# 8. Train Linear Regression Model on Historical Data
def train_risk_model(risk_assessment_df, transactions_df):
    # Preprocess data: Merge risk assessments and transactions to get features
    df = pd.merge(risk_assessment_df, transactions_df, on='TransactionID')
    
    # Select relevant features for prediction
    X = df[['Amount']]  # For simplicity, using only transaction amount as feature
    y = df['RiskScore']  # Target is the RiskScore
    
    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)
    return model

# 9. Simulate Risk Prediction for New Loan Request
def predict_risk(model, new_transaction):
    # Use the transaction amount as input to predict risk score
    predicted_risk = model.predict(np.array([[new_transaction.amount]]))[0]
    print(f"Predicted Risk Score for Transaction {new_transaction.transaction_id}: {predicted_risk:.2f}")
    
    # Simulate whether the loan is risky or not based on a threshold (e.g., >0.5 is risky)
    if predicted_risk > 0.5:
        print(f"Transaction {new_transaction.transaction_id} is risky!")
    else:
        print(f"Transaction {new_transaction.transaction_id} is not risky.")

# 10. Simulate the Complete Process (With Risk Prediction for New Loans)
def run_simulation():
    companies, customers, transactions, risk_assessments = initialize_entities()
    link_risk_assessments_to_transactions(transactions, risk_assessments)
    
    # Train the risk prediction model on historical data
    model = train_risk_model(risk_assessment_df, transactions_df)
    
    # Link the trained model to RiskAssessment class instances
    for risk_assessment in risk_assessments:
        risk_assessment.model = model
    
    # Simulate new transactions and their risk assessments (Reduced number of new transactions)
    new_transactions = simulate_new_transactions(customers, companies)
    
    # Predict risk for new transactions and add risk assessment
    for new_transaction in new_transactions:
        # Create a new risk assessment with a placeholder risk score
        risk_assessment = RiskAssessment(
            assessment_id=f"RA{random.randint(1000, 9999)}",
            risk_score=0,  # Placeholder for risk score
            customer_id=new_transaction.customer_id,
            transaction_id=new_transaction.transaction_id,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            model=model  # Provide model for risk prediction
        )
        
        # Use the model to predict risk score
        predicted_risk = risk_assessment.predict_risk(new_transaction.amount)
        
        # Add the predicted risk score to the risk assessment
        risk_assessment.risk_score = predicted_risk
        
        # Link the risk assessment to the transaction
        new_transaction.add_risk_assessment(risk_assessment)

        # Display the predicted risk score for the transaction
        print(f"Risk prediction added for Transaction {new_transaction.transaction_id}: {predicted_risk:.2f}")
        
        # Simulate whether the loan is risky or not based on predicted risk score
        if predicted_risk > 0.73:
            print(f"Transaction {new_transaction.transaction_id} is risky!")
        else:
            print(f"Transaction {new_transaction.transaction_id} is not risky.")

# Run the simulation
run_simulation()