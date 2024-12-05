import os
from langchain_openai import ChatOpenAI
import PyPDF2
import tiktoken
from pydantic import BaseModel
from typing import Optional
import json
from contracts import contract_checklist
import uvicorn
import pymongo
from fastapi import FastAPI, File, UploadFile
import asyncio
import uuid
import io


uri = "mongodb://localhost:27017/"
client = pymongo.MongoClient(uri)
db = client["flags"]
db = db["results"]
app = FastAPI()

os.environ["OPENAI_API_KEY"]="sk-"

class Eval(BaseModel):
        item: str
        is_met: int
        explaination: str
        reference : Optional[str]

class Evals(BaseModel):
    evals: list[Eval]
    checklist_relevance: float


async def convert_to_mongo_format(data):
    """
    Converts the input data into a MongoDB-friendly format.
    """
    # Iterate over each category in the data
    converted_data = {}
    for category, category_data in data.items():
        category_entry = category_data.dict()
        converted_data[category] = category_entry

    return converted_data
async def extract_pdf_text(content: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# def count_tokens(text):
#     encoding = tiktoken.encoding_for_model("gpt-4o-mini")
#     return len(encoding.encode(text))

async def evaluate(text:str,id:str) -> Evals:
    llm = ChatOpenAI(model="gpt-4o-mini")
    lines = text.splitlines()
    numbered_contract = "\n".join([f"{i+1}. {line}" for i, line in enumerate(lines)])
    evaluations = {}
    for title, checklist in contract_checklist.items():
        prompt = f"""
        Check the legal contract to ensure that the following checklist is met:
        {checklist}

        The legal contract:
        {numbered_contract}

        Also find out the relevance of checklist which checks for correctness in {title}.

        Evaluation of a checklist item must follow this pydantic model:
        class Eval(BaseModel):
            item: str
            is_met: int | [0, 5] with 0 being not met and 5 being met
            explaination: str
            reference : Optional[str] | Lines (start)-(end) provide the reference of line numbers is is_met is less than 4.

        The output should be json dump of:
        class Evals(BaseModel):
            evals: list[Eval]
            checklist_relevance: float | between 0 to 1 with 1 being relevant

        Do not output any additional text.
        """
        output = llm.invoke(prompt).content

        try:
            evals = Evals(**json.loads(output[7:-3]))
            evaluations[title] = evals
        except Exception as e:
            print(e)
    print(evaluations)
    data = await convert_to_mongo_format(evaluations)
    db.update_one({"id": id}, {"$set": data}, upsert=True)
    print("DONE")
    

@app.post("/submit")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()   
    id = str(uuid.uuid4())
    text = await extract_pdf_text(content)
    asyncio.create_task(evaluate(text,id))

    return {
        "message": "Files uploaded successfully, agreement generation in progress.",
        "conversation_id": id,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8230)





