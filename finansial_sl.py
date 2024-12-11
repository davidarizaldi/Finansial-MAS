import streamlit as st
import pandas as pd
import random
import hashlib
from datetime import datetime
from finansial_ekosistem import initialize_entities, simulate_new_transactions, train_risk_model, RiskAssessment, Transaction, run_simulation
from sklearn.linear_model import LinearRegression
import numpy as np

# Load the necessary dataframes
risk_assessment_df = pd.read_csv('risk_assessment.csv')
transactions_df = pd.read_csv('transactions.csv')

# Initialize entities from the finansial_ekosistem.py module
companies, customers, transactions, risk_assessments = initialize_entities()

# Train the model on historical data (load dataframes from CSVs)
model = train_risk_model(risk_assessment_df, transactions_df)

st.set_page_config(layout="wide")

# Streamlit UI
st.title('Risk Assessment Simulation for Transactions')

# Create three columns: Left for transactions, middle for customers, right for companies, and simulating transactions
col1, col2, col3, col4 = st.columns(4)

# First Column: Displaying Transactions in Scrollable Area
with col1:
    st.header("Transactions")
    
    # Create a dataframe to display transaction details
    transaction_data = {
        "CustomerID": [transaction.customer_id for transaction in transactions],
        "Amount": [transaction.amount for transaction in transactions]
    }
    
    # Convert to DataFrame
    transactions_df_display = pd.DataFrame(transaction_data)
    
    # Display the DataFrame in Streamlit
    st.dataframe(transactions_df_display)

# Second Column: Displaying Customers in Table
with col2:
    st.header("Customers")
    
    # Create a dataframe for customers
    customer_data = {
        "Customer Name": [customer.name for customer in customers]
    }
    
    # Convert to DataFrame
    customers_df_display = pd.DataFrame(customer_data)
    
    # Display the DataFrame in Streamlit
    st.dataframe(customers_df_display)

# Third Column: Displaying Companies in Table
with col3:
    st.header("Companies")
    
    # Create a dataframe for companies
    company_data = {
        "Company Name": [company.name for company in companies]
    }
    
    # Convert to DataFrame
    companies_df_display = pd.DataFrame(company_data)
    
    # Display the DataFrame in Streamlit
    st.dataframe(companies_df_display)

with col4:
    st.header("Create New Transaction")
    
    # Scrollable selectbox for choosing a Customer
    customer_names = [customer.name for customer in customers]
    selected_customer = st.selectbox('Select a Customer', customer_names)

    # Scrollable selectbox for choosing a Company
    company_names = [company.name for company in companies]
    selected_company = st.selectbox('Select a Company', company_names)

    # Manually input transaction amount
    amount = st.number_input('Enter Transaction Amount', min_value=0, step=1)

    # Button to simulate transaction
    if st.button("Simulate Transaction"):
        # Generate a random transaction ID and method (Credit or Debit)
        transaction_id = f"T{random.randint(10000, 99999)}"
        method = random.choice(['Credit', 'Debit'])
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create a unique hash for the transaction
        hash = hashlib.sha256(f"{transaction_id}{amount}{method}{timestamp}".encode()).hexdigest()

        # Find the selected customer and company objects based on their names
        selected_customer_obj = next(customer for customer in customers if customer.name == selected_customer)
        selected_company_obj = next(company for company in companies if company.name == selected_company)

        # Create a new transaction
        new_transaction = Transaction(
            transaction_id=transaction_id, 
            amount=amount, 
            method=method, 
            customer_id=selected_customer_obj.customer_id,  # Using customer_id here
            company_id=selected_company_obj.company_id,  # Using company_id here
            timestamp=timestamp, 
            hash=hash
        )

        # Add the new transaction to the selected customer and company
        selected_customer_obj.add_transaction(new_transaction)
        selected_company_obj.transactions.append(new_transaction)
        
        # Create or find the corresponding risk assessment
        risk_assessment = RiskAssessment(
            assessment_id=f"RA{random.randint(1000, 9999)}",
            risk_score=0,  # Placeholder for risk score
            customer_id=new_transaction.customer_id,
            transaction_id=new_transaction.transaction_id,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            model=model  # Provide model for risk prediction
        )
        
        # Predict risk and display results
        predicted_risk = risk_assessment.predict_risk(new_transaction.amount)
        risk_assessment.risk_score = predicted_risk
        
        # Display the predicted risk score for the transaction
        st.write(f"Transaction ID: {new_transaction.transaction_id}, Amount: {new_transaction.amount}")
        st.write(f"Predicted Risk Score: {predicted_risk:.2f}")
        
        # Display if the transaction is risky or not based on the predicted score
        if predicted_risk > 0.73:
            st.write(f"Transaction {new_transaction.transaction_id} is risky!")
        else:
            st.write(f"Transaction {new_transaction.transaction_id} is not risky.")

    # Button to simulate 10 new transactions
    if st.button("Simulate 10 Transactions"):
        # Simulate new transactions
        new_transactions = simulate_new_transactions(customers, companies)
        
        # Iterate over the new transactions and predict risk for each
        for new_transaction in new_transactions:
            # Create or find the corresponding risk assessment for the transaction
            risk_assessment = None
            for assessment in risk_assessments:
                if assessment.transaction_id == new_transaction.transaction_id:
                    risk_assessment = assessment
                    break
            
            if risk_assessment is None:
                # If no existing risk assessment, create a new one
                risk_assessment = RiskAssessment(
                    assessment_id=f"RA{random.randint(1000, 9999)}",
                    risk_score=0,  # Placeholder for risk score
                    customer_id=new_transaction.customer_id,
                    transaction_id=new_transaction.transaction_id,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    model=model  # Provide model for risk prediction
                )
                risk_assessments.append(risk_assessment)  # Add to the list of assessments

            # Now, predict the risk if risk_assessment exists
            if risk_assessment and risk_assessment.model:
                predicted_risk = risk_assessment.predict_risk(new_transaction.amount)
                risk_assessment.risk_score = predicted_risk  # Update the risk score

                # Display the predicted risk score for the transaction
                st.write(f"Transaction ID: {new_transaction.transaction_id}, Amount: {new_transaction.amount}")
                st.write(f"Predicted Risk Score: {predicted_risk:.2f}")

                # Simulate whether the loan is risky or not based on predicted risk score
                if predicted_risk > 0.73:
                    st.write(f"Transaction {new_transaction.transaction_id} is risky!")
                else:
                    st.write(f"Transaction {new_transaction.transaction_id} is not risky.")
