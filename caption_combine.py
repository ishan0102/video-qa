import sieve


@sieve.function(
    name="image-captioner-combiner",
    gpu=False,
    python_packages=[
        "moviepy==1.0.3",
        "opencv-python==4.6.0.66",
        "uuid==1.30",
    ],
    python_version="3.8",
    iterator_input=True,
    persist_output=True,
)
def caption_and_combine(answers) -> sieve.Video:
    from moviepy.editor import ImageClip, concatenate_videoclips
    import cv2
    import textwrap
    import uuid

    # Add captions
    images = []
    for img, caption in answers:
        print("Creating video with caption: ", caption)
        img = img.array

        # Add caption with textwrap
        font = cv2.FONT_HERSHEY_SIMPLEX
        wrapped_text = textwrap.wrap(caption, width=30)
        font_size = 2
        font_thickness = 2

        for i, line in enumerate(wrapped_text):
            textsize = cv2.getTextSize(line, font, font_size, font_thickness)[0]

            gap = textsize[1] + 10

            y = int((img.shape[0] + textsize[1]) / 2) + i * gap + 40
            x = int((img.shape[1] - textsize[0]) / 2)

            cv2.putText(img, line, (x, y), font, font_size, (255, 255, 255), font_thickness, lineType=cv2.LINE_AA)

        # Convert the color format from BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Add the frame to the list of images
        images.append(img_rgb)

    # Combine the images into a video
    print("Combining all frames into video...")
    clips = [ImageClip(m).set_duration(1) for m in images]
    video = concatenate_videoclips(clips)
    video_path = f"{uuid.uuid4()}.mp4"
    video.write_videofile(video_path, fps=30)
    return sieve.Video(path=video_path)
