import sys
import yaml
import os

def add_to_gallery(image_path, title, caption, link):
    data_file = "data/gallery.yml"
    
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found.")
        return

    with open(data_file, 'r') as f:
        gallery = yaml.safe_load(f) or []

    # Normalize image path to be relative to static root
    # Example: static/img/articles/test.png -> img/articles/test.png
    clean_img = image_path.replace("static/", "")

    new_entry = {
        "image": clean_img,
        "title": title,
        "caption": caption,
        "link": link
    }

    gallery.append(new_entry)

    with open(data_file, 'w') as f:
        yaml.dump(gallery, f, sort_keys=False)
    
    print(f"Successfully added '{title}' to gallery.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python scripts/add_to_gallery.py <image_path> <title> <caption-text> <link>")
        sys.exit(1)
    
    add_to_gallery(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
