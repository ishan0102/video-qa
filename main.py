from typing import Dict

import sieve

from captioner import ImageCaptioner
from splitter import video_splitter


@sieve.function(
    name="sort-captions",
    iterator_input=True,
    persist_output=True,
)
def sort_captions(captions: Dict) -> str:
    sorted_captions = sorted(captions, key=lambda x: x["frame_number"])
    return "\n".join([x["caption"] for x in sorted_captions])


@sieve.workflow(name="video_qa")
def video_qa(video: sieve.Video, question: str):
    images = video_splitter(video, question)
    captions = ImageCaptioner()(images)
    sorted_captions = sort_captions(captions)
    return sorted_captions
