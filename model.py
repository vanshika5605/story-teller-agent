import os
import openai

def call_model(system_prompt: str, user_prompt: str, max_tokens=3000, temperature=0.1) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",   # do not change this model
        messages=messages,
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."