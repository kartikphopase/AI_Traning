# JalSanchay – Interview Preparation

## 1. 60-Second Project Pitch

JalSanchay is an AI-powered rainwater harvesting and groundwater recharge assistant that helps users understand technical water conservation guidelines and perform practical calculations.

The main problem I wanted to solve was that important information is scattered across lengthy Central Ground Water Board (CGWB) technical PDFs. Users may need to search different chapters for runoff coefficients, roof characteristics, design guidelines, and calculation formulas.

I built a Retrieval-Augmented Generation system using ChromaDB and Groq, with a FastAPI backend and Streamlit frontend. The system retrieves relevant technical information and provides answers with source citations. I also integrated a rooftop rainwater harvesting calculator and a LangGraph-based agent workflow so calculations are handled by deterministic tools rather than relying on the LLM to do arithmetic.

I added input validation, response caching, prompt-injection safeguards, logging, Docker, GitHub Actions, and deployed the application on Render.

The goal is to make technical rainwater harvesting information easier to access while keeping calculations more reliable and traceable.

## 2. Ten Likely Interview Questions and Answers

### Q1. What problem does JalSanchay solve?

JalSanchay addresses the difficulty of finding and applying technical rainwater harvesting and groundwater recharge information from lengthy technical documents. Instead of manually searching PDFs, users can ask questions and receive relevant answers with source references. The calculator also helps users estimate rooftop rainwater harvesting requirements.

### Q2. Why did you choose RAG instead of a normal chatbot?

A normal chatbot may generate answers from its general training knowledge, which can be unreliable for technical guidelines. RAG retrieves relevant information from the CGWB documents and supplies it as context to the LLM. This helps ground answers in the source material and makes citations possible.

### Q3. Explain the architecture of JalSanchay.

The frontend is built using Streamlit, while FastAPI exposes backend endpoints. PDF content is extracted, split into chunks, and indexed in ChromaDB. During a question, the retrieval component finds relevant chunks and passes them to the Groq-powered LLM. The agent workflow can also invoke calculation tools. LangGraph manages the workflow, including approval handling.

### Q4. What was the hardest technical challenge?

The hardest challenge was extracting and connecting technical information distributed across different sections of the CGWB PDF.

For example, runoff coefficients for different areas are available in Table 4.4, roof-specific coefficients are in Table 7.2, and ready reckoners are in Table 7.4. These tables and formulas are not always easy to extract cleanly from PDFs.

A retrieval system must identify the correct table for the user's context rather than returning a similar-looking but inappropriate value.

Another important challenge was ensuring that the agent performs calculations using a deterministic tool instead of asking the LLM to calculate volumes itself. The LLM interprets the request and identifies the required information, while the calculation tool performs the arithmetic. This improves consistency and makes the calculation process easier to validate.

### Q5. Why should an LLM not perform the actual rainwater calculations?

LLMs generate text probabilistically and can make arithmetic mistakes. Rainwater harvesting calculations require numerical reliability.

I use the LLM for understanding the question and coordinating the workflow, while a dedicated calculation tool performs the mathematical operations. This separates language understanding from numerical computation.

### Q6. How did you implement document retrieval?

I extracted text from the CGWB PDF, divided it into manageable chunks, generated embeddings, and stored the chunks with metadata in ChromaDB.

When a user asks a question, the system generates a query representation, retrieves relevant chunks, and supplies the retrieved context to the LLM to generate an answer.

The system also preserves source metadata to support citations.

### Q7. Why did you introduce local embeddings?

The original implementation used Gemini embeddings. During deployment, Gemini API quota limits caused embedding requests to fail.

To improve availability, I implemented a local HashingVectorizer-based fallback while preserving the original Gemini collection. The active embedding provider is tracked in ChromaDB configuration.

The local fallback is keyword-oriented rather than semantically equivalent to Gemini embeddings, so retrieval quality needs to be evaluated separately.

### Q8. How did you improve production reliability?

I implemented several improvements:

- Response caching with a maximum of 128 entries and a 300-second TTL.
- Input validation for question length and retrieval parameters.
- Prompt-injection safeguards for user input and retrieved documents.
- Logging for request latency, cache hits, and token usage.
- Local embedding fallback for Gemini quota failures.
- Automated Ruff, pytest, and Docker build checks through GitHub Actions.

The project has 15 passing tests from the local test run.

### Q9. How did you evaluate the RAG system?

I used a 15-question evaluation set and compared two retrieval configurations.

Configuration A achieved 80.95% keyword coverage, while Configuration B achieved 83.33%. Configuration B was selected as the winner.

Both configurations passed the Q6 abstention test, where the system was expected to say "I don't know" when asked for current groundwater levels at an exact plot in Kopargaon.

Keyword coverage measures retrieval coverage, not overall answer accuracy. This distinction is important when interpreting the results.

### Q10. What would you improve next?

I would improve PDF table extraction and table-aware retrieval so that numerical values remain connected to their headings, units, locations, and conditions.

I would also expand the evaluation dataset, test calculation accuracy against manually verified examples, monitor production latency and retrieval quality, and improve the local embedding fallback with a stronger embedding approach.

## 3. My Hardest Problem – Interview Story

**Problem:** Important numerical information was distributed across tables and formulas in different chapters of the CGWB PDF.

**Examples:**
- Table 4.4: runoff coefficients for different areas.
- Table 7.2: runoff coefficients for roofs.
- Table 7.4: ready reckoners.

**Why it was difficult:**

PDF extraction can lose table structure, headings, row-column relationships, and units. Simply retrieving text near a relevant keyword may return an incorrect value or miss the relationship between a table and its intended application.

**My engineering approach:**

1. Extract document content and preserve page and chunk metadata.
2. Retrieve relevant technical context for the user's question.
3. Keep the LLM responsible for interpreting the request and coordinating the workflow.
4. Use a deterministic calculation tool for numerical calculations.
5. Validate the calculation logic independently instead of trusting generated arithmetic.

**What I learned:**

A reliable domain-specific AI system needs more than an LLM. It needs good document processing, accurate retrieval, structured numerical data, deterministic tools, validation, and source traceability.

## 4. Demo Talking Points

During the demo, explain the following in order:

1. Open the live JalSanchay application.
2. Show the Knowledge Assistant.
3. Ask a question about rooftop rainwater harvesting.
4. Explain how the retrieved source information supports the answer.
5. Show the calculator and enter sample inputs.
6. Explain that a deterministic tool performs the calculation.
7. Show the generated design output, if available.
8. Explain the backend architecture and deployment briefly.

## 5. Important Technical Details

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Primary LLM | Groq – openai/gpt-oss-120b |
| Original embeddings | Gemini – gemini-embedding-001 |
| Local fallback | Scikit-learn HashingVectorizer |
| Vector database | ChromaDB |
| Agent workflow | LangGraph |
| Testing | Pytest and Ruff |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Deployment | Render |

## 6. Final Interview Reminder

Be prepared to explain not only what technologies you used, but why you used them.

Emphasize the separation between:
- Retrieval and answer generation.
- LLM reasoning and deterministic calculations.
- Technical source information and generated responses.
- Local development and production deployment.

Do not describe keyword coverage as answer accuracy, and do not claim the local HashingVectorizer is equivalent to semantic embeddings.
