import csv


scene_number_to_label = {}
with open('labels.csv', 'r', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for scene_number, label in reader:
        scene_number_to_label[scene_number] = label

    print(scene_number_to_label)

hierarchies_with_labels = []
with open('hierarchies.csv', 'r', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for start, end, level, scene_number in reader:
        try:
            hierarchies_with_labels.append([start, end, level, scene_number_to_label[scene_number]])
        except KeyError:
            print('No instrument found for scene number', scene_number)
            hierarchies_with_labels.append([start, end, level, ''])

with open('hierarchies_with_instruments.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['start', 'end', 'level', 'label'])
    writer.writerows(hierarchies_with_labels)