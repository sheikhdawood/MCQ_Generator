import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

from mcqgenrator.utils import read_file, get_table_data
from mcqgenrator.MCQGenrator import generate_evaluate_chain
from mcqgenrator.logger import logging

# Load environment variables
load_dotenv()

# Load RESPONSE_JSON template
with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Title
st.title("MCQs Creator Application with LangChain 🦜⛓️")

# Create user input form
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=['pdf', 'txt'])
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("⏳ Generating your quiz..."):
            try:
                # Extract text from file
                text = read_file(uploaded_file)

                # Generate MCQs using Groq LLM chain
                response = generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("❌ Error while generating MCQs. Check logs.")
            else:
                # Display results
                if isinstance(response, dict):
                    quiz = response.get("quiz", "")

                    st.markdown("### 🔍 Raw Quiz Output")
                    st.code(quiz)

                    if quiz:
                        table_data = get_table_data(quiz)
                        if table_data:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.markdown("### ✅ Generated MCQs")
                            st.table(df)

                            st.markdown("### 🧠 Expert Review")
                            st.text_area(label="Review", value=response.get("review", ""), height=150)
                        else:
                            st.error("⚠️ Quiz was generated but could not parse MCQs into table format.")
                    else:
                        st.error("⚠️ Empty quiz data received from LLM.")
                else:
                    st.error("⚠️ Unexpected response format.")
                    st.write(response)
