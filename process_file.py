import os
import subprocess
import sys
from pathlib import Path

import scenedetect
from pytube import YouTube
import csv
from insert_labels_into_hierarchies import merge


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


YT_URLS = [
    ("https://www.youtube.com/watch?v=tsm1rizxAj8", "beethoven-2nd-symphony"),
]


def convert_timecode_to_seconds(timestamp):
    hours, minutes, seconds = map(float, timestamp.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def download(url, filename):
    """Currently broken due to YouTube update. Next pytube release will probably fix it."""
    YouTube(
        url,
        on_progress_callback=lambda stream, chunk, remaining: print(sizeof_fmt(remaining)),
    ).streams.first().download(filename=filename + '.mp4')


def split_scenes(path: str):
    args = ['scenedetect', '-i', path, 'list-scenes', 'save-images', '-n', '1']
    # args += ['time', '--start', '0s', '--end', '10s']  # use these args for testing on parts of the video
    p = subprocess.run(args, shell=True)
    return p.returncode

def move_split_output_to_separate_folder(filename):
    files_to_move = Path().glob(f"{filename}*")

    dir = Path(filename)
    dir.mkdir(exist_ok=True)
    for path in files_to_move:
        if path.name.endswith('.mp4'):
            continue
        new_path = dir / path.name
        try:
            os.replace(path, new_path)
        except OSError:
            pass

    files_to_rename = dir.glob(filename + '-*')

    for path in files_to_rename:
        new_path = dir / path.name.replace(filename + '-', '')
        try:
            os.replace(path, new_path)
        except OSError:
            pass


def generate_tilia_csvs(filename):
    hierarchy_data = []
    dir = Path(filename)
    with open(dir / 'Scenes.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        next(reader)
        for row in reader:
            scene_number = row[0]
            start_time = convert_timecode_to_seconds(row[2])
            end_time = convert_timecode_to_seconds(row[5])
            hierarchy_data.append([start_time, end_time, 1, scene_number])

    with open(dir / 'hierarchies.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['start', 'end', 'level', 'label'])
        for row in hierarchy_data:
            writer.writerow(row)

    with open(dir / 'labels.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['scene_number', 'label'])
        for i in range(len(hierarchy_data) + 1):
            writer.writerow([i + 1, ''])


def get_video_and_cut_times():
    for i, (url, filename) in enumerate(YT_URLS):
        download(url, filename)
        split_scenes(filename)
        move_split_output_to_separate_folder(filename)
        generate_tilia_csvs(filename)


def process_yt_url(url, filename):
    download(url, filename)
    split_scenes(filename)
    move_split_output_to_separate_folder(filename)
    generate_tilia_csvs(filename)


def process_local_file(filename) -> Path:
    print('Processing ' + filename + '.')
    returncode = split_scenes(filename + '.mp4')
    if returncode != 0:
        print('Failed to split video.')
        return
    move_split_output_to_separate_folder(filename)
    generate_tilia_csvs(filename)
    print('Finished processing ' + filename + '.\n\n')
    return Path(filename)


if __name__ == "__main__":
    filename = input("filename: ")
    filename = filename.split(".mp4")[0]
    dir = process_local_file(filename)
    while input("Proceed with merge? (Y/n)") not in {"", "Y", "y"}:
        pass

    merge(dir)
