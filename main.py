from typing import Dict

import sieve


@sieve.function(
    name="sort-captions",
    iterator_input=True,
    persist_output=True,
)
def sort_captions(captions: Dict) -> str:
    sorted_captions = sorted(captions, key=lambda x: x["frame_number"])
    for caption in sorted_captions:
        yield caption["caption"]


@sieve.function(
    name="concatenate-features",
    iterator_input=True,
    persist_output=True,
)
def concatenate_features(sorted_captions, sort_outputs) -> Dict:
    return {
        "captions": [c for c in sorted_captions],
        "sort_outputs": [o for o in sort_outputs],
    }


@sieve.workflow(name="video_qa")
def video_qa(video: sieve.Video, question: str) -> Dict:
    images = sieve.reference("ishan0102-utexas-edu/video-splitter-with-metadata")(video, question)

    # Image captioning
    captions = sieve.reference("ishan0102-utexas-edu/image-captioner")(images)
    sorted_captions = sort_captions(captions)

    # YOLO/SORT
    yolo_outputs = sieve.reference("ishan0102-utexas-edu/yolo")(images)
    sort_outputs = sieve.reference("ishan0102-utexas-edu/sort")(yolo_outputs)

    concatenated_features = concatenate_features(sorted_captions, sort_outputs)
    return concatenated_features
