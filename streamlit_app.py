import streamlit as st
import requests
import pandas as pd

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/query/"

st.title("Chat Assistant for SQLite Database")

# Input box for user query
user_query = st.text_input("Enter your SQL query:", "")

if st.button("Run Query"):
    if user_query:
        response = requests.post(API_URL, json={"query": user_query})
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                df = pd.DataFrame(results)  # Convert JSON to DataFrame
                st.dataframe(df)  # Display as table
            else:
                st.warning("No results found.")
        else:
            st.error(f"Error: {response.json()['detail']}")
    else:
        st.warning("Please enter a query.")
