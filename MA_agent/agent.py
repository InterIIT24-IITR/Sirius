# Mergers and Acquisition agent
import os
import uuid
import pathway as pw

# Use fastapi for the API
from flask import request
from flask import Flask
from sasuke.rag.client import retrieve_documents

app = Flask(__name__)

os.makedirs("MA", exist_ok=True)
data_sources = [
    pw.io.fs.read(
        "./MA",
        format="binary",
        mode="streaming",
        with_metadata=True,
    )
]


def agent():
    pass


@app.route("/submit", methods=["POST"])
def ingest():
    print(request.files)
    company_a_legal = request.files["company_a_legal"]
    # company_b_legal = request.form.get("company_b_legal")
    # company_a_finance = request.form.get("company_a_financial")
    # company_b_finance = request.form.get("company_b_financial")
    # user_instructions = request.form.get("user_instructions")
    unqiue_id = uuid.uuid4()
    MA_folder = f"MA/{unqiue_id}"
    os.makedirs(MA_folder, exist_ok=True)
    # store the file in folder
    company_a_legal.save(f"{MA_folder}/{company_a_legal.filename}")
    return {"message": "Files uploaded successfully"}
    # # store the files in folder all are text blobs
    # for file in company_a_legal:
    #     with open(f"{MA_folder}/{file.filename}", "w") as f:
    #         f.write(file.read())
    # for file in company_b_legal:
    #     with open(f"{MA_folder}/{file.filename}", "w") as f:
    #         f.write(file.read())
    # for file in company_a_finance:
    #     with open(f"{MA_folder}/{file.filename}", "w") as f:
    #         f.write(file.read())
    # for file in company_b_finance:
    #     with open(f"{MA_folder}/{file.filename}", "w") as f:
    #         f.write(file.read())


def retrieve(query: str):
    results = retrieve_documents(query)
    return results


def parse_outline():
    # Import outline documents in MA folder
    # open term sheet
    with open("MA/term_sheet.txt", "r") as f:
        term_sheet = f.read()
        # Convert it into format string for LLM prompt
    # open defeinitive agreement
    with open("MA/definitive_agreement.txt", "r") as f:
        definitive_agreement = f.read()
        # Convert it into format string for LLM prompt
    # open merger agreement
    with open("MA/letter_of_intent.txt", "r") as f:
        letter_of_intent = f.read()
        # Convert it into format string for LLM prompt


def generate_documents():
    # Generate documents using LLM
    prompt_term_sheet = ""
    prompt_definitive_agreement = ""
    prompt_letter_of_intent = ""
    # Generate term sheet, definitive agreement and letter of intent


def generate_insights():
    # Jayesh ke dibbe me headings hain, usko according insights generate karna hai
    # Generate insights using LLM
    # This will be streamed through websockets at the end of processing
    # risk associated, key points, key overlaps , key conflicts
    pass


# This will be final documents delivered to user
def send_documents():
    # Send generated documents to user
    pass


# Request (includes uploads) --> Thinking --> Generating Documents --> Sending Documents --> Streaming Insights

# start the flask app
if __name__ == "__main__":
    app.run(port=8000)
