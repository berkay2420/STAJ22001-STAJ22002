import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from LLM_integration import prompts


_= load_dotenv(find_dotenv())

client=OpenAI (
  api_key=os.environ.get('GROQ_API_KEY'),
)

client = Groq()

def generate_Out_Of_Scope_Response(message):

    response = ""

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": f""" {prompts.out_of_scope_propmt} . This is the out of scope message that you need to generate response: {message}""" 
            }
        ],
        temperature=0.8,
        max_tokens=1024,
        top_p=0.8,
        stream=True,
        stop=None,
    )   

    for chunk in completion:
        response += chunk.choices[0].delta.content or ""

    return response


def generate_suggestion_response(message):
    response = ""

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role":"system",
                "content": f"{prompts.make_suggestion_prompt}"
            },
            {
                "role": "user",
                "content": f""" This is the request message that you need to make a suggestion about: {message}""" 
            }
        ],
        temperature=0.8,
        max_tokens=1024,
        top_p=0.8,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        response += chunk.choices[0].delta.content or ""

    return response
