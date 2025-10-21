import gradio as gr
from memory import get_user_memory, update_user_memory
from genapicall import generate_text

def chat(username, query):
    memory_list = get_user_memory(username)
    memory_text = "\n".join(memory_list) if memory_list else "No memory yet."

    prompt = f"""
You are a helpful assistant.
The user's name is {username}.

Here is what you remember about the user:
{memory_text}

The user just said:
{query}

Based on this information, provide a helpful and relevant response. If the user stated a new fact, acknowledge it.
"""
    answer = generate_text(prompt)

    # Save new facts
    new_fact_keywords = ["i love", "my", "i am", "i like", "i have", "my name is"]
    if any(query.lower().strip().startswith(k) for k in new_fact_keywords):
        update_user_memory(username, query)

    return answer

def launch_interface():
    iface = gr.Interface(
        fn=chat,
        inputs=[gr.Textbox(label="Username"), gr.Textbox(label="Your Message")],
        outputs="text",
        title="🧠 Personal Memory Chatbot",
        description="A chatbot that remembers what you tell it using MongoDB and answers via Google Gemini 2.5 API."
    )
    iface.launch()
