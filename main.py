import scenedetect
from pytube import YouTube
import csv

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

YT_URLS = [
    ("https://www.youtube.com/watch?v=oOpKDASqLT8", "mourao"),
    ("https://www.youtube.com/watchv=jL-Csf1pNCI", "carmem"),
    ("https://www.youtube.com/watch?v=fRrsD4RH9SY", "nachtmusik"),
]


def get_video_and_cut_times():
    for i, (url, filename) in enumerate(YT_URLS):

        print(f'Processing "{filename}"')
        print('Downloading...')
        filename_prefix=str(i + 1).zfill(3) + '-'
        YouTube(
            url,
            on_progress_callback=lambda stream, chunk, remaining: print(sizeof_fmt(remaining)),
        ).streams.first().download(filename=filename + '.mp4', filename_prefix=filename_prefix)
        print('Download successful!')

        print('Splitting scenes...')
        scene_list = scenedetect.detect(f"{filename_prefix}{filename}.mp4", scenedetect.AdaptiveDetector())
        times = [
            (s[0].frame_num / s[0].framerate, s[1].frame_num / s[1].framerate)
            for s in scene_list
        ]
        print('Split successful!')

        print('Exporting to csv...')
        with open(f"{filename_prefix}{filename}.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["start", "end", "level"])
            for start, end in times:
                writer.writerow([start, end, 1])
        print(f'Done processing "{filename}".')
        print()

if __name__ == "__main__":
    get_video_and_cut_times()

