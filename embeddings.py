from typing import Dict, List

import sieve


@sieve.Model(
    name="pinecone-upload-qa",
    python_packages=[
        "pinecone-client==2.2.1",
        "python-dotenv==0.21.1",
        "torch==1.8.1",
        "git+https://github.com/openai/CLIP.git",
    ],
    run_commands=[
        "mkdir -p /root/.cache/clip",
        "wget -O /root/.cache/clip/ViT-B-32.pt https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    ],
    iterator_input=True,
)
class PineconeUploadImages:
    def __setup__(self):
        import clip

        self.model, self.preprocess = clip.load("ViT-B/32", device="cpu")

    def __predict__(self, images: sieve.Image, user_id: str) -> str:
        import os

        import pinecone
        from dotenv import load_dotenv

        load_dotenv()

        from PIL import Image

        clip_embeddings = []
        for image in images:
            metadata = {
                "type": image.type,
                "video_name": image.video_name,
                "frame_number": image.frame_number,
                "frame_count": image.frame_count,
                "fps": image.fps,
                "x0": image.x0,
                "y0": image.y0,
                "x1": image.x1,
                "y1": image.y1,
                "video_path": image.video_path,
            }

            preprocessed_image = self.preprocess(Image.open(image.path)).unsqueeze(0).to("cpu")
            image_features = self.model.encode_image(preprocessed_image)
            features = list(image_features.cpu().detach().numpy()[0])
            features = [float(x) for x in features]
            clip_embeddings.append({"id": image.id, "features": features, "metadata": metadata})

        api_key = os.getenv("PINECONE_API_KEY")
        pinecone.init(api_key=api_key, environment="us-west1-gcp")
        index_name = "video-copilot"
        index = pinecone.Index(index_name=index_name)

        vectors = []
        for clip_embedding in clip_embeddings:
            vectors.append((clip_embedding["id"], clip_embedding["features"], clip_embedding["metadata"]))

        # HACK: convert iterator input to string
        for user in user_id:
            user_id = user
            break

        response = index.upsert(vectors=vectors, namespace=user_id)
        if "upserted_count" in response:
            print(f"Successfully upserted {response['upserted_count']} vectors")
        else:
            print("Failed to upsert vectors")

        return user_id


@sieve.Model(
    name="pinecone-query-qa",
    python_packages=[
        "pinecone-client==2.2.1",
        "python-dotenv==0.21.1",
        "openai==0.27.2",
        "torch==1.8.1",
        "git+https://github.com/openai/CLIP.git",
    ],
    run_commands=[
        "mkdir -p /root/.cache/clip",
        "wget -O /root/.cache/clip/ViT-B-32.pt https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    ],
    iterator_input=True,
)
class PineconeQueryText:
    def __setup__(self):
        import clip

        self.model, self.preprocess = clip.load("ViT-B/32", device="cpu")

    def __predict__(self, images: sieve.Image, question: str, user_id: str) -> sieve.Image:
        import os

        import clip
        import openai
        import pinecone
        from dotenv import load_dotenv

        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

        api_key = os.getenv("PINECONE_API_KEY")
        pinecone.init(api_key=api_key, environment="us-west1-gcp")
        index_name = "video-copilot"
        index = pinecone.Index(index_name=index_name)

        # HACK: convert iterator input to string
        for q in question:
            question = q
            break

        for user in user_id:
            user_id = user
            break

        # Convert question to CLIP format
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a CLIP converter. You take a question and convert it to a prompt that a CLIP model would understand. Only reply with the prompt, do not include any other text."},
                {"role": "user", "content": f"Here is a question: {question}. What is a good CLIP prompt?"},
            ],
        )
        prompt = response.choices[0].message.content
        print(f"Prompt: {prompt}")

        # Encode the query text with CLIP
        print(f"Querying for {prompt}")
        tokenized = clip.tokenize(prompt).to("cpu")
        text_features = self.model.encode_text(tokenized)
        features = list(text_features.cpu().detach().numpy()[0])
        features = [float(x) for x in features]
        print(f"Query features: {features}")

        # Get the top-k nearest neighbors
        matches = index.query(
            vector=features,
            top_k=7,
            namespace=user_id,
            include_metadata=True,
            include_values=True,
        )["matches"]

        # Keep matches over a certain threshold
        print([match["score"] for match in matches])
        matches = [match for match in matches if match["score"] > 0.2]

        found_frames = []
        for image in images:
            print(f"Checking frame {image.frame_number}")
            for match in matches:
                print(f"Checking match {match['metadata']['frame_number']}")
                if image.frame_number == match["metadata"]["frame_number"] and image.frame_number not in found_frames:
                    print(f"Matched {image.frame_number}")
                    found_frames.append(image.frame_number)
                    yield image
