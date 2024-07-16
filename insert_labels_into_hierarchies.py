import csv
from pathlib import Path

def merge(dir: Path):
    scene_number_to_label = {}
    with open(dir / 'labels.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for scene_number, label in reader:
            scene_number_to_label[scene_number] = label

    hierarchies_with_labels = []
    with open(dir / 'hierarchies.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for start, end, level, scene_number in reader:
            try:
                hierarchies_with_labels.append([start, end, level, scene_number_to_label[scene_number]])
            except KeyError:
                print('No instrument found for scene number', scene_number)
                hierarchies_with_labels.append([start, end, level, ''])

    with open(dir / 'hierarchies_with_instruments.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['start', 'end', 'level', 'label'])
        writer.writerows(hierarchies_with_labels)