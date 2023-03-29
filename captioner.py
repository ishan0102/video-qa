from typing import Dict

import sieve


@sieve.Model(
    name="vit-gpt2-image-captioner",
    gpu=True,
    python_version="3.8",
    python_packages=[
        "torch==1.8.1",
        "transformers==4.23.1",
    ],
    iterator_input=True,
)
class ImageCaptioner:
    def __setup__(self):
        from transformers import AutoTokenizer, VisionEncoderDecoderModel, ViTFeatureExtractor

        device = "cuda"
        encoder_checkpoint = "nlpconnect/vit-gpt2-image-captioning"
        decoder_checkpoint = "nlpconnect/vit-gpt2-image-captioning"
        model_checkpoint = "nlpconnect/vit-gpt2-image-captioning"
        self.feature_extractor = ViTFeatureExtractor.from_pretrained(encoder_checkpoint)
        self.tokenizer = AutoTokenizer.from_pretrained(decoder_checkpoint)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_checkpoint).to(device)
        self.clean_text = lambda x: x.replace("<|endoftext|>", "").split("\n")[0]

    def __predict__(self, images: sieve.Image) -> Dict:
        for image in images:
            image_features = self.feature_extractor(image.array, return_tensors="pt").pixel_values.to("cuda")
            caption_ids = self.model.generate(image_features, max_length=64)[0]
            caption_text = self.clean_text(self.tokenizer.decode(caption_ids))
            print(f"Frame {image.frame_numer}: {caption_text}")
            yield {
                "caption": caption_text,
                "frame_number": image.frame_number,
            }
