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
            {"role": "system", "content": "You are a video analysis agent. I will give you pieces of data such as captions for frames and objects tracked across frames. You must use this data to answer a question about the video."},
            {"role": "user", "content": f"Here is the data: {features}. {question}"},
        ],
    )

    print(response)
    return response.choices[0].message.content
        