PROMPT_TERM_SHEET = """
**Objective:** Create a term sheet outlining the key terms and conditions for the proposed merger or acquisition between Company A and Company B. Use the provided company information and specified outline.

**Inputs:**

1. **Company A Details:**  
    {company_a_details}

2. **Company B Details:**  
    {company_b_details}

3. **Document Outline (Markdown format):**  
    {document_outline}

**Task:**

Using the above inputs, draft a term sheet following the provided outline. The document should succinctly summarize the key financial, legal, and operational terms of the transaction. Ensure clarity and precision in outlining the structure, valuation, conditions, and commitments of the deal, all formatted according to the specified Markdown outline.
"""

PROMPT_DEFINITIVE_AGREEMENT = """
**Objective:** Write a definitive agreement for the merger/acquisition between Company A and Company B using the provided company details and outline.

**Inputs:**

1. **Company A Details:**  
    {company_a_details}

2. **Company B Details:**  
    {company_b_details}  

3. **Document Outline (Markdown format):**  
    {document_outline}

**Task:**

Using the above inputs, draft a definitive agreement following the given outline. Ensure the agreement accurately reflects the business and legal considerations necessary for the merger/acquisition, and is formatted according to the specified Markdown outline.
"""

PROMPT_LETTER_OF_INTENT = """
**Objective:** Write a Letter of Intent to outline the preliminary terms and intentions for the merger or acquisition between Company A and Company B. Use the provided company details and the specified outline format.

**Inputs:**

1. **Company A Details:**  
    {company_a_details}

2. **Company B Details:**  
    {company_b_details}

3. **Document Outline (Markdown format):**  
    {document_outline}

**Task:**

Utilizing the inputs above, draft a Letter of Intent that aligns with the provided outline. This document should clearly express the intentions of both parties regarding the key aspects of the proposed transaction, including objectives, transaction structure, valuation, confidentiality, and any other preliminary terms. Ensure it is clearly formatted according to the specified Markdown outline.
"""

PROMPT_NDA = """
**Objective:** Write a Non-Disclosure Agreement to protect confidential information exchanged between Company A and Company B during the merger or acquisition discussions. Use the provided company details and the specified outline format.

**Inputs:**

1. **Company A Details:**  
    {company_a_details}

2. **Company B Details:**  
    {company_b_details}

3. **Document Outline (Markdown format):**  
    {document_outline}

**Task:**

Using the inputs above, draft a Non-Disclosure Agreement following the provided outline. This document should specify the obligations of both parties concerning the confidentiality of any proprietary information shared during the merger or acquisition process. Ensure to include key elements such as the definition of confidential information, duration of confidentiality, permitted disclosures, and any penalties for breaches. Format the NDA according to the specified Markdown outline.
"""

PROMPT_DUE_DILIGENCE = """
**Objective:** Prepare a Due Diligence Request List to gather necessary information and documents from Company A and Company B for the merger or acquisition process. Use the provided company details and specified outline format.

**Inputs:**

1. **Company A Details:**  
    {company_a_details}

2. **Company B Details:**  
    {company_b_details}

3. **Document Outline (Markdown format):**  
    {document_outline}

**Task:**

Using the inputs above, draft a Due Diligence Request List following the provided outline. This document should detail all essential documents and information needed to thoroughly assess the business, financial, legal, and operational aspects of both companies. Ensure to cover all relevant categories, such as financial records, legal documents, intellectual property, contracts, regulatory compliance, and human resources. Format the request list according to the specified Markdown outline.
"""
