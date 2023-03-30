from typing import Dict

import sieve


@sieve.function(
    name="ask-gpt-4",
    python_packages=[
        "openai==0.27.2",
        "python-dotenv==0.21.1",
    ],
    persist_output=True,
    iterator_input=True,
)
def ask_gpt_4(features: Dict, question: str) -> Dict:
    import json
    import os

    import openai
    from dotenv import load_dotenv

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    features = [f for f in features]
    question = [q for q in question]

    print(f"Features: {features}")
    print(f"Question: {question}")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a video analysis agent. I will give you captions for each frame. You must use this data to answer a question about the video and you must cite ALL of your sources."},
            {"role": "user", "content": "You must return your responses in JSON format. In your response, return an object that says `answer` and has a string that answers the question. Also have a `sources` field that is a list of objects that have a `type` field that is `caption` and a `frame_number` field that is the frame number of the source. Cite all of your sources!"},
            {"role": "user", "content": f"Here is the data: {features}. Use the most commonly occurring keywords to inform your answer to the following question. {question}"},
        ],
    )

    print(response)
    try:
        print(response.choices[0].message.content)
        answer = json.loads(response.choices[0].message.content)
        print(f"The answer is: {answer['answer']}")
    except json.JSONDecodeError:
        answer = {"answer": "I don't know", "sources": []}

    return answer
