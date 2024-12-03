import os
import uuid
import pathway as pw
from fastapi import FastAPI, File, UploadFile
from pathlib import Path
import time
import asyncio
from typing import List

app = FastAPI()

with open("definitive_agreement_outline.txt", "r") as f:
    definitive_agreement_outline = f.read()
with open("term_sheet_outline.txt", "r") as f:
    term_sheet_outline = f.read()
with open("letter_of_intent_outline.txt", "r") as f:
    letter_of_intent_outline = f.read()
with open("nda_outline.txt", "r") as f:
    nda_outline = f.read()
with open("due_diligence_outline.txt", "r") as f:
    due_diligence_outline = f.read()

os.makedirs("MA", exist_ok=True)

data_sources = [
    pw.io.fs.read(
        "./MA",
        format="binary",
        mode="streaming",
        with_metadata=True,
    )
]


async def generate_agreement():
    pass


@app.post("/submit")
async def ingest(files: List[UploadFile] = File(...)):
    for file in files:
        file_location = f"MA/{uuid.uuid4()}_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

    asyncio.create_task(generate_agreement())

    return {"message": "Files uploaded successfully, agreement generation in progress."}


async def generate_documents():
    # This function will eventually generate the documents using LLM
    pass


# Function to generate insights based on document headings
async def generate_insights():
    # This will generate insights based on document headings and other logic
    pass


# Function to send the final documents to the user
async def send_documents():
    # This will send the generated documents to the user
    pass


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
