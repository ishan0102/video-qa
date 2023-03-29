import sieve


@sieve.function(
    name="video-splitter-with-metadata",
    gpu=False,
    python_packages=["ffmpeg-python==0.2.0"],
    system_packages=[
        "libgl1-mesa-glx",
        "libglib2.0-0",
        "ffmpeg",
    ],
    python_version="3.8",
    iterator_input=True,
)
def video_splitter(video: sieve.Video, name: str) -> sieve.Image:
    for vid, na in zip(video, name):
        # use ffmpeg to extract all frames in video as bmp files and return the path to the folder
        import tempfile

        temp_dir = tempfile.mkdtemp()

        # run at 1 fps
        import subprocess

        subprocess.call(
            [
                "ffmpeg",
                "-i",
                vid.path,
                "-vf",
                f"fps=1",
                f"{temp_dir}/%09d.jpg",
            ]
        )
        import os
        import uuid

        filenames = os.listdir(temp_dir)
        print(f"Splitting {vid.path} into {len(filenames)} frames")
        filenames.sort()
        for i, filename in enumerate(filenames):
            frame_number = i * vid.fps
            yield sieve.Image(
                path=os.path.join(temp_dir, filename),
                frame_number=frame_number,
                frame_count=vid.frame_count,
                fps=vid.fps,
                video_name=na,
                type="frame",
                x0=0,
                y0=0,
                x1=vid.width,
                y1=vid.height,
                id=f"{na}_{i}_{uuid.uuid4()}",
                video_path=vid.url,
            )
