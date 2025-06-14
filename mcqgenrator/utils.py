import PyPDF2
import json
import re
import traceback
import pandas as pd
from tqdm import tqdm
from mcqgenrator.MCQGenrator import generate_evaluate_chain

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            return "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        except Exception as e:
            raise Exception("Error reading the PDF file") from e
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        raise Exception("Unsupported file format: only PDF and text files are supported.")

def chunk_text(text, max_words=500):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield ' '.join(words[i:i + max_words])

def get_table_data(quiz_str):
    try:
        if not quiz_str or not quiz_str.strip():
            return None
        json_objects = re.findall(r'({\s*".+?"\s*:\s*{.*?}})', quiz_str, re.DOTALL)
        quiz_dict = {}
        for obj_str in json_objects:
            try:
                obj = json.loads(obj_str)
                quiz_dict.update(obj)
            except json.JSONDecodeError:
                continue
        quiz_table_data = []
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            options = " || ".join([f"{opt} -> {text}" for opt, text in value.get("options", {}).items()])
            correct = value.get("correct", "")
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return None

def process_file(file, number, subject, tone, response_json):
    try:
        full_text = read_file(file)
        results = []
        for chunk in tqdm(chunk_text(full_text)):
            output = generate_evaluate_chain.invoke({
                "text": chunk,
                "number": number,
                "subject": subject,
                "tone": tone,
                "response_json": response_json
            })

            results.append(output)
        return results
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return None

def save_all_mcqs(results, output_file="final_mcqs.csv"):
    all_mcq_data = []
    for result in results:
        if isinstance(result, dict):
            quiz = result.get("quiz", "")
        else:
            quiz = result
        table_data = get_table_data(quiz)
        if table_data:
            all_mcq_data.extend(table_data)
    df = pd.DataFrame(all_mcq_data)
    df.to_csv(output_file, index=False)
    print(f"✅ MCQs saved to {output_file}")
