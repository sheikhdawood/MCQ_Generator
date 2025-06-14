import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

from mcqgenrator.utils import read_file, get_table_data, process_file
from mcqgenrator.logger import logging

# Load environment variables
load_dotenv()

# Load RESPONSE_JSON template
with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Title
st.title("MCQs Creator Application with LangChain 🦜⛓️")

# Input form
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=['pdf', 'txt'])
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

if button and uploaded_file and mcq_count and subject and tone:
        with st.spinner("⏳ Generating your quiz..."):
            try:
                results = process_file(
                    file=uploaded_file,
                    number=mcq_count,
                    subject=subject,
                    tone=tone,
                    response_json=json.dumps(RESPONSE_JSON)
                )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("❌ Error while generating MCQs.")
            else:
                if results:
                    st.markdown("### ✅ Combined MCQ Table")
                    all_mcq_data = []
                    for result in results:
                        quiz = result.get("quiz", "")
                        table_data = get_table_data(quiz)
                        if table_data:
                            all_mcq_data.extend(table_data)

                    df = pd.DataFrame(all_mcq_data)
                    df.index += 1
                    st.table(df)

                    st.markdown("### 🧠 Last Chunk Review")
                    st.text_area(label="Review", value=results[-1].get("review", ""), height=150)

                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download MCQs CSV", data=csv, file_name="mcqs_output.csv", mime="text/csv")
                else:
                    st.error("⚠️ No MCQs were generated.")
