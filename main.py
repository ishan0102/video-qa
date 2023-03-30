from typing import Dict, Tuple

import sieve

from gpt import ask_gpt_4

from caption_combine import caption_and_combine


@sieve.function(
    name="sort-captions",
    iterator_input=True,
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
)
def concatenate_features(sorted_captions) -> Dict:
    return {
        "captions": [c for c in sorted_captions],
        # "sort_outputs": [o for o in sort_outputs],
        # "blip2_outputs": [o for o in blip2_outputs],
    }


@sieve.function(
    name="display-frames",
    iterator_input=True,
)
def display_frames(images: sieve.Image, gpt_output: Dict) -> Tuple[sieve.Image, str]:
    images = [i for i in images]
    gpt_output = [g for g in gpt_output]
    print(f"GPT Output: {gpt_output}")
    for source in gpt_output[0]["sources"]:
        for image in images:
            if image.frame_number == source["frame_number"]:
                print(f"Displaying frame {image.frame_number} and caption {source['caption']}")
                yield (image, source["caption"])


@sieve.function(
    name="combine-outputs",
    iterator_input=True,
    persist_output=True,
)
def combine_outputs(video: sieve.Video, gpt_output: Dict) -> Dict:
    import json

    videos = [v for v in video]
    gpt_output = [g for g in gpt_output]

    print(videos[0])
    print(gpt_output[0])

    output = {
        "video": videos[0].url,
        "gpt_output": gpt_output[0]["answer"],
    }
    return json.dumps(output)


@sieve.workflow(name="video_qa")
def video_qa(video: sieve.Video, question: str) -> Dict:
    images = sieve.reference("ishan0102-utexas-edu/video-splitter-with-fps")(video, question)

    # Image captioning
    captions = sieve.reference("ishan0102-utexas-edu/vit-gpt2")(images)
    sorted_captions = sort_captions(captions)

    # YOLO/SORT
    # yolo_outputs = sieve.reference("ishan0102-utexas-edu/yolo")(images)
    # sort_outputs = sieve.reference("ishan0102-utexas-edu/sort")(yolo_outputs)

    # Blip2
    # blip2_outputs = sieve.reference("ishan0102-utexas-edu/blip2")(images)

    # Call GPT-4
    concatenated_features = concatenate_features(sorted_captions)
    gpt_output = ask_gpt_4(concatenated_features, question)
    answers = display_frames(images, gpt_output)
    output_video = caption_and_combine(answers)
    final_output = combine_outputs(output_video, gpt_output)
    return final_output
