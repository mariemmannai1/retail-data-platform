
import ollama

response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Explain retail sales revenue in 2 short sentences."
        }
    ]
)

print(response["message"]["content"])
