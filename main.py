from typing import Dict

import sieve

from gpt import ask_gpt_4


@sieve.function(
    name="sort-captions",
    iterator_input=True,
    persist_output=True,
)
def sort_captions(captions: Dict) -> Dict:
    sorted_captions = sorted(captions, key=lambda x: x["frame_number"])
    for caption in sorted_captions:
        yield {
            "caption": caption["caption"],
            "frame_number": caption["frame_number"],
        }


@sieve.function(
    name="concatenate-features",
    iterator_input=True,
    persist_output=True,
)
def concatenate_features(sorted_captions, sort_outputs, blip2_outputs) -> Dict:
    return {
        "captions": [c for c in sorted_captions],
        "sort_outputs": [o for o in sort_outputs],
        "blip2_outputs": [o for o in blip2_outputs],
    }


@sieve.workflow(name="video_qa")
def video_qa(video: sieve.Video, question: str) -> str:
    images = sieve.reference("ishan0102-utexas-edu/video-splitter-with-metadata")(video, question)

    # Image captioning
    captions = sieve.reference("ishan0102-utexas-edu/vit-gpt2")(images)
    sorted_captions = sort_captions(captions)

    # YOLO/SORT
    yolo_outputs = sieve.reference("ishan0102-utexas-edu/yolo")(images)
    sort_outputs = sieve.reference("ishan0102-utexas-edu/sort")(yolo_outputs)

    # Blip2
    # blip2_outputs = sieve.reference("ishan0102-utexas-edu/blip2")(images)

    # Call GPT-4
    concatenated_features = concatenate_features(sorted_captions, sort_outputs, blip2_outputs)
    gpt_output = ask_gpt_4(concatenated_features, question)

    return gpt_output
