import openai

openai.api_key = "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"

def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="gpt-4o-mini",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        response = chat_with_gpt(user_input)
        print(f"Bot: {response}")