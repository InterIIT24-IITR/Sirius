# Sasuke

Multi-Agent tool for answering your queries specialising in knowledge queries in legal and financial topics exploiting Pathway's solutions for fast RAG application.

## Directory Structure

```
.
├── README.md
├── __init__.py
├── agent.py
├── common
│   ├── __init__.py
│   ├── classifier_agent.py
│   ├── general_agent.py
│   ├── hyde.py
│   └── reranker.py
├── finance_agent
│   ├── __init__.py
│   ├── agent.py
│   └── single_retrieval.py
├── legal_agent
│   ├── __init__.py
│   ├── agent.py
│   └── single_retrieval.py
├── rag
│   ├── Dockerfile
│   ├── client.py
│   ├── documents
│   ├── requirements.txt
│   └── server.py
└── requirements.txt
```

## Setup
Following setup is for Linux Machines, see the Windows Setup subheading for the relevant changes

Environment
```sh
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### VectorStore
Add documents to `rag/documents`
```sh
cd rag
pip install -r requirements.txt
python server.py
```

### Multi-Agent Tool

Run the tool
```sh
python -m agent
{enter_your_query}
```

### Windows Setup
For setting up the venv use 
```sh
.\venv\Scripts\activate
```

For VectorStoreServer
```sh
cd rag
docker build -t <image> .
docker run --name <container> <image>
```

## Approach
- The query is processed by AdaRAG and either sent to general, financial or legal query agent.
- In financial or legal query agent, query is answered on basis of context, unless RAG fails, where it currently answers using its general knowledge.
- For RAG, we pass through HyDe agent for a supposed answer for broader context search from VectorStore.
- We rerank the documents and return the retrieve documents.
- Retrieved documents are passed to LLM for answer generation.