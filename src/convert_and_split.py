import os
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from sklearn.model_selection import train_test_split

RAW_BASE = "/content/raw"
YOLO_BASE = "/content/potholemap_yolo"
COUNTRIES = ["Czech", "Japan"]
CLASS_MAP = {
    "D40": 0,  # pothole
    "D44": 1,  # pothole_repair
}


def convert_xml_to_yolo():
    for folder in ["images", "labels"]:
        os.makedirs(os.path.join(YOLO_BASE, folder), exist_ok=True)

    stats = Counter()

    for country in COUNTRIES:
        base = os.path.join(RAW_BASE, country, country, "train")
        images_dir = os.path.join(base, "images")
        xml_dir = os.path.join(base, "annotations", "xmls")

        for filename in sorted(os.listdir(images_dir)):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            image_name = os.path.splitext(filename)[0]
            xml_path = os.path.join(xml_dir, image_name + ".xml")

            out_image_name = f"{country}_{filename}"
            shutil.copy2(
                os.path.join(images_dir, filename),
                os.path.join(YOLO_BASE, "images", out_image_name),
            )

            labels = []
            if os.path.exists(xml_path):
                root = ET.parse(xml_path).getroot()
                size = root.find("size")
                width = float(size.findtext("width"))
                height = float(size.findtext("height"))

                for obj in root.findall("object"):
                    class_name = obj.findtext("name")
                    if class_name not in CLASS_MAP:
                        continue

                    box = obj.find("bndbox")
                    xmin = float(box.findtext("xmin"))
                    ymin = float(box.findtext("ymin"))
                    xmax = float(box.findtext("xmax"))
                    ymax = float(box.findtext("ymax"))

                    x_center = ((xmin + xmax) / 2.0) / width
                    y_center = ((ymin + ymax) / 2.0) / height
                    box_width = (xmax - xmin) / width
                    box_height = (ymax - ymin) / height

                    class_id = CLASS_MAP[class_name]
                    labels.append(
                        f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"
                    )
                    stats[class_name] += 1

            out_label_name = f"{country}_{image_name}.txt"
            with open(
                os.path.join(YOLO_BASE, "labels", out_label_name),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("\n".join(labels))

            stats["images"] += 1
            if len(labels) == 0:
                stats["negative_images"] += 1

    print("Conversion terminée !")
    print("Images:", stats["images"])
    print("Annotations D40:", stats["D40"])
    print("Annotations D44:", stats["D44"])
    print("Images négatives:", stats["negative_images"])


def split_dataset():
    images_dir = os.path.join(YOLO_BASE, "images")
    labels_dir = os.path.join(YOLO_BASE, "labels")

    positive = []
    negative = []

    for filename in sorted(os.listdir(images_dir)):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        stem = os.path.splitext(filename)[0]
        label_path = os.path.join(labels_dir, stem + ".txt")
        content = (
            open(label_path, "r", encoding="utf-8").read().strip()
            if os.path.exists(label_path)
            else ""
        )
        if content:
            positive.append(filename)
        else:
            negative.append(filename)

    train_pos, temp_pos = train_test_split(positive, test_size=0.30, random_state=42)
    val_pos, test_pos = train_test_split(temp_pos, test_size=1 / 3, random_state=42)

    train_neg, temp_neg = train_test_split(negative, test_size=0.30, random_state=42)
    val_neg, test_neg = train_test_split(temp_neg, test_size=1 / 3, random_state=42)

    splits = {
        "train": train_pos + train_neg,
        "val": val_pos + val_neg,
        "test": test_pos + test_neg,
    }

    for split_name, files in splits.items():
        for folder in ["images", "labels"]:
            os.makedirs(os.path.join(YOLO_BASE, split_name, folder), exist_ok=True)
        for filename in files:
            stem = os.path.splitext(filename)[0]
            shutil.copy2(
                os.path.join(images_dir, filename),
                os.path.join(YOLO_BASE, split_name, "images", filename),
            )
            shutil.copy2(
                os.path.join(labels_dir, stem + ".txt"),
                os.path.join(YOLO_BASE, split_name, "labels", stem + ".txt"),
            )
        print(f"{split_name} : {len(files)} images")


if __name__ == "__main__":
    convert_xml_to_yolo()
    split_dataset()