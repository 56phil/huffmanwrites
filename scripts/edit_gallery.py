import sys
import yaml
import os

def update_gallery_item(index, title=None, caption=None, link=None):
    data_file = "data/gallery.yml"
    
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found.")
        return

    with open(data_file, 'r') as f:
        gallery = yaml.safe_load(f) or []

    if index < 0 or index >= len(gallery):
        print(f"Error: Index {index} out of range. Gallery has {len(gallery)} items (0 to {len(gallery)-1}).")
        return

    item = gallery[index]
    if title is not None: item['title'] = title
    if caption is not None: item['caption'] = caption
    if link is not None: item['link'] = link

    with open(data_file, 'w') as f:
        yaml.dump(gallery, f, sort_keys=False)
    
    print(f"Updated item {index} ('{item['title']}').")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/edit_gallery.py <index> [title] [caption] [link]")
        print("Example: python scripts/edit_gallery.py 0 \"New Title\" \"New Caption\" \"/posts/new-url/\"")
        sys.exit(1)
    
    try:
        idx = int(sys.argv[1])
    except ValueError:
        print("Error: Index must be an integer.")
        sys.exit(1)
        
    title = sys.argv[2] if len(sys.argv) > 2 else None
    caption = sys.argv[3] if len(sys.argv) > 3 else None
    link = sys.argv[4] if len(sys.argv) > 4 else None
    
    update_gallery_item(idx, title, caption, link)
