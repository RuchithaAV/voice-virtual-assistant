from time import perf_counter
from ollama import Client

client = Client(host="http://localhost:11434", timeout=120)

question = input("Ask a question: ")
print("Generating an answer...")
start = perf_counter()

response = client.chat(
    model="qwen3:1.7b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful voice assistant. "
                "Answer briefly in plain language, using at most three sentences."
            ),
        },
        {"role": "user", "content": question},
    ],
    think=False,
    options={"num_ctx": 2048, "num_predict": 150},
)

print(f"Assistant: {response.message.content}")
print(f"Elapsed time: {perf_counter() - start:.1f} seconds")