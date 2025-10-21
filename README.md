# Personalised RAG LLM ChatBot

[GitHub Repository](https://github.com/ohnogaurav/Personalised-RAG-LLM-ChatBot) | [Hugging Face Demo](https://huggingface.co/spaces/ohnogaurav/Personal-memory-llm)

---

## Overview

This project is a **Personalised Chatbot** that uses **RAG (Retrieval-Augmented Generation)** with **Google Gemini LLM** and **MongoDB** to store user-specific memory. The bot can remember past facts about each user and provide context-aware responses.

It demonstrates a **clean modular architecture**, combining **LLM integration, persistent storage, and a user-friendly Gradio interface**, showcasing real-world software engineering practices alongside AI.

---

## Features

* **Persistent Memory**: Each user has a unique memory stored in MongoDB.
* **Contextual Responses**: Responses are augmented by stored memory.
* **Generative LLM**: Powered by Google Gemini 2.5 via `genai` SDK.
* **Dynamic Memory Updates**: Automatically stores new facts shared by users.
* **Interactive Web UI**: Lightweight and responsive Gradio interface.
* **Modular Codebase**: Functions split into logical modules for maintainability.

---

## Architecture

```text
User
 │
 ▼
Gradio Frontend
 │
 ▼
Backend (Python Modules)
 ├─ memory.py        --> Handles MongoDB interactions
 ├─ genapicall.py    --> Handles Gemini API calls
 ├─ gradio_interface.py --> Orchestrates chat logic and UI
 └─ config.py        --> Stores constants & environment variables
 │
 ▼
Google Gemini LLM API
 │
 ▼
MongoDB (Persistent User Memory)
```

* Users interact via the Gradio interface.
* Memory is fetched from MongoDB to provide context-aware responses.
* Google Gemini API generates the output using stored memory.
* Memory is automatically updated based on predefined keywords.

---

## Tech Stack

* **Frontend**: Gradio
* **Backend**: Python (modular structure)
* **LLM**: Google Gemini 2.5 (`genai` SDK)
* **Database**: MongoDB Atlas
* **Hosting**: Hugging Face Spaces

---

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/ohnogaurav/Personalised-RAG-LLM-ChatBot.git
cd Personalised-RAG-LLM-ChatBot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (recommended via Hugging Face Secrets or `.env` file):

```bash
export MONGO_URI="your_mongodb_connection_string"
export GOOGLE_API_KEY="your_gemini_api_key"
```

4. Run the app locally:

```bash
python app.py
```

5. Open the Gradio interface in your browser at `http://localhost:7860`.

---

## Usage

1. Enter your **username** and **message**.
2. The bot retrieves your previous memory (if any) and provides a response.
3. If your message contains a new fact (like "I love cats" or "My favorite color is blue"), it is stored automatically for future conversations.

---

## Key Modules & Functions

| Module                | Function                                 | Description                                                             |
| --------------------- | ---------------------------------------- | ----------------------------------------------------------------------- |
| `memory.py`           | `get_user_memory(username)`              | Retrieves memory from MongoDB for a user.                               |
| `memory.py`           | `update_user_memory(username, new_fact)` | Adds new facts to user memory.                                          |
| `genapicall.py`       | `generate_text(prompt)`                  | Calls Google Gemini API to generate LLM responses.                      |
| `gradio_interface.py` | `chat(username, query)`                  | Orchestrates memory retrieval, response generation, and memory updates. |
| `gradio_interface.py` | `launch_interface()`                     | Launches the Gradio web interface.                                      |

---

## Deployment

* Hosted on **Hugging Face Spaces** for a live demo.
* MongoDB Atlas used for persistent, multi-user memory.
* Modular backend allows **easy updates**, swapping LLMs, or switching databases.

---

## Future Improvements

* Implement semantic search or vector embeddings for **advanced RAG memory retrieval**.
* Multi-session support with isolated user memory.
* Conversation summarization to reduce memory size over time.
* Enhanced UI/UX with **chat history, editable memory, and rich formatting**.

---

## License

Open-source under **MIT License**.
