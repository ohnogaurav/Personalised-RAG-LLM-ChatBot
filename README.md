# Personalised RAG LLM ChatBot

[GitHub Repository](https://github.com/ohnogaurav/Personalised-RAG-LLM-ChatBot) | [Hugging Face Demo](https://huggingface.co/spaces/ohnogaurav/Personal-memory-llm)

---

## Overview

This project is a **Personalised Chatbot** that uses **RAG (Retrieval-Augmented Generation)** with **Google Gemini LLM** and **MongoDB** to store user-specific memory. The bot can remember past facts about each user and provide context-aware responses.  

It’s a showcase of a **blend of software engineering, LLM integration, and RAG principles** — demonstrating not just AI usage but also database-backed personalization.

---

## Features

- **Persistent Memory**: Each user has a unique memory stored in MongoDB.
- **Contextual Responses**: Uses stored memory to generate relevant answers.
- **Generative LLM**: Powered by Google Gemini 2.5 API.
- **Dynamic Updates**: Automatically updates memory when users provide new facts.
- **Interactive Web UI**: Gradio interface for quick testing and demo.

---

## Architecture

```text
User
 │
 ▼
Gradio Frontend
 │
 ▼
Backend (Python)
 │
 ▼
Google Gemini LLM API
 │
 ▼
MongoDB (Persistent User Memory)
```

- Users interact via the Gradio interface.  
- User memory is fetched from MongoDB for context.  
- Gemini API generates responses augmented by retrieved memory.  
- Memory is updated automatically based on specific keywords in user input.  

---

## Tech Stack

- **Frontend**: Gradio  
- **Backend**: Python  
- **LLM**: Google Gemini 2.5 (`genai` SDK)  
- **Database**: MongoDB Atlas  
- **Hosting**: Hugging Face Spaces  

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

3. Set environment variables (recommended via Hugging Face Secrets):

```bash
export MONGO_URI="your_mongodb_connection_string"
export GOOGLE_API_KEY="your_gemini_api_key"
```

4. Run the app locally:

```bash
python app.py
```

5. Access the Gradio interface in your browser at `http://localhost:7860`.

---

## Usage

1. Enter your **username** and **message**.  
2. The bot retrieves your previous memory (if any) and provides a response.  
3. If your message contains a new fact (like "I love cats" or "My favorite color is blue"), it is stored automatically for future conversations.  

---

## Key Functions in Code

- `get_user_memory(username)`: Retrieves memory from MongoDB for a given user.  
- `update_user_memory(username, new_fact)`: Adds new facts to user memory.  
- `generate_text_with_api(prompt)`: Calls Google Gemini API to generate LLM responses.  
- `chat(username, query)`: Orchestrates memory retrieval, response generation, and memory updates.  

---

## Deployment

- Hosted on **Hugging Face Spaces** for an interactive demo.  
- MongoDB Atlas used for persistent user data storage.  
- Fully modular backend allowing easy updates or migration to other LLMs or DBs.

---

## Future Improvements

- Semantic search or vector embeddings for memory retrieval (RAG in full).  
- Multi-user memory isolation with sessions.  
- Conversation summarization to reduce memory size over time.  
- Enhanced UI/UX with chat history and editable memory.  

---

## License

Open-source under **MIT License**.