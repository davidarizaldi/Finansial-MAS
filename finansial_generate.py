import pandas as pd
import random
import hashlib
from datetime import datetime

# Set the seed for reproducibility
random.seed(42)

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
    def __init__(self, transaction_id, amount, method, customer_id, company_id):
        self.transaction_id = transaction_id
        self.amount = amount
        self.method = method
        self.customer_id = customer_id
        self.company_id = company_id
        self.timestamp = datetime.now()
        self.hash = self.generate_hash()
        self.risk_assessment = None  # Linked to a RiskAssessment later

    def generate_hash(self):
        # Generate a simple hash for the transaction
        return hashlib.sha256(f"{self.transaction_id}{self.amount}{self.timestamp}".encode()).hexdigest()

    def add_risk_assessment(self, risk_assessment):
        self.risk_assessment = risk_assessment

# 4. Define the RiskAssessment Class
class RiskAssessment:
    def __init__(self, assessment_id, risk_score, customer_id, transaction_id):
        self.assessment_id = assessment_id
        self.risk_score = risk_score
        self.timestamp = datetime.now()
        self.customer_id = customer_id
        self.transaction_id = transaction_id

# 5. Generate Data
def generate_data():
    # 1. Generate companies (10 companies)
    companies = [Company(i, f"Company {i}", f"Address {i}") for i in range(1, 11)]

    # 2. Generate customers (100 customers)
    customers = [Customer(i, f"Customer {i}", f"Phone {i}", f"Address {i}") for i in range(1, 101)]

    # 3. Generate transactions (1000 transactions)
    transactions = []
    for i in range(1, 1001):
        customer = random.choice(customers)
        company = random.choice(companies)
        amount = random.randint(1000, 5000)
        method = random.choice(['Credit', 'Debit', 'Transfer'])
        transaction = Transaction(i, amount, method, customer.customer_id, company.company_id)
        transactions.append(transaction)
        customer.add_transaction(transaction)  # Link transaction to customer
        company.transactions.append(transaction)  # Link transaction to company

    # 4. Generate risk assessments (100 risk assessments)
    risk_assessments = []
    for i in range(1, 101):
        customer = random.choice(customers)
        transaction = random.choice(customer.transactions)
        risk_score = random.uniform(0.5, 0.9)
        risk_assessment = RiskAssessment(i, risk_score, customer.customer_id, transaction.transaction_id)
        risk_assessments.append(risk_assessment)
        transaction.add_risk_assessment(risk_assessment)  # Link risk assessment to transaction

    return companies, customers, transactions, risk_assessments

# 6. Convert Data to DataFrames for CSV output
def save_data_to_csv(companies, customers, transactions, risk_assessments):
    # Convert to DataFrame and save as CSV
    companies_data = [(company.company_id, company.name, company.address) for company in companies]
    companies_df = pd.DataFrame(companies_data, columns=["CompanyID", "Name", "Address"])
    companies_df.to_csv('companies.csv', index=False)

    customers_data = [(customer.customer_id, customer.name, customer.phone, customer.address) for customer in customers]
    customers_df = pd.DataFrame(customers_data, columns=["CustomerID", "Name", "Phone", "Address"])
    customers_df.to_csv('customers.csv', index=False)

    transactions_data = [(transaction.transaction_id, transaction.amount, transaction.method, 
                          transaction.customer_id, transaction.company_id, transaction.timestamp, transaction.hash) 
                         for transaction in transactions]
    transactions_df = pd.DataFrame(transactions_data, columns=["TransactionID", "Amount", "Method", "CustomerID", 
                                                               "CompanyID", "Timestamp", "Hash"])
    transactions_df.to_csv('transactions.csv', index=False)

    risk_assessments_data = [(risk_assessment.assessment_id, risk_assessment.risk_score, risk_assessment.timestamp, 
                              risk_assessment.customer_id, risk_assessment.transaction_id) 
                             for risk_assessment in risk_assessments]
    risk_assessment_df = pd.DataFrame(risk_assessments_data, columns=["AssessmentID", "RiskScore", "Timestamp", 
                                                                      "CustomerID", "TransactionID"])
    risk_assessment_df.to_csv('risk_assessment.csv', index=False)

# Generate data
companies, customers, transactions, risk_assessments = generate_data()

# Save the generated data to CSV
save_data_to_csv(companies, customers, transactions, risk_assessments)

# Paths to saved CSV files
('companies.csv', 'customers.csv', 'transactions.csv', 'risk_assessment.csv')