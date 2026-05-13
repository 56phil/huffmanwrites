from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import yaml
import os

app = Flask(__name__)
DATA_FILE = "/Users/prh/Developer/huffmanwrites/data/gallery.yml"
STATIC_ROOT = "/Users/prh/Developer/huffmanwrites/static"

def load_gallery():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return yaml.safe_load(f) or []

def save_gallery(data):
    with open(DATA_FILE, 'w') as f:
        yaml.dump(data, f, sort_keys=False)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gallery Manager</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
               background: #1a1a1a; color: #efefef; padding: 40px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { color: #fff; border-bottom: 1px solid #333; padding-bottom: 20px; }
        .toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .btn { padding: 8px 16px; border-radius: 6px; text-decoration: none; cursor: pointer; 
               border: none; font-size: 14px; transition: opacity 0.2s; display: inline-block; }
        .btn-primary { background: #007AFF; color: white; }
        .btn-danger { background: #FF3B30; color: white; }
        .btn-secondary { background: #3a3a3c; color: white; }
        table { width: 100%; border-collapse: collapse; background: #2c2c2e; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #3a3a3c; }
        th { background: #3a3a3c; color: #aaa; font-size: 12px; text-transform: uppercase; }
        .img-preview { width: 60px; height: 34px; object-fit: cover; border-radius: 4px; background: #000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gallery Manager</h1>
        <div class="toolbar">
            <a href="/add" class="btn btn-primary">+ Add Image</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Preview</th>
                    <th>Title</th>
                    <th>Caption</th>
                    <th>Link</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in gallery %}
                <tr>
                    <td><img src="/img-srv{{ item.image }}" class="img-preview"></td>
                    <td>{{ item.title }}</td>
                    <td>{{ item.caption }}</td>
                    <td><code style="color:#aaa">{{ item.link }}</code></td>
                    <td>
                        <a href="/edit/{{ loop.index0 }}" class="btn btn-secondary">Edit</a>
                        <a href="/delete/{{ loop.index0 }}" class="btn btn-danger" onclick="return confirm('Delete this item?')">Del</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
'''

EDIT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Edit Item</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
               background: #1a1a1a; color: #efefef; padding: 40px; }
        .container { max-width: 500px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #aaa; font-size: 14px; }
        input, textarea { width: 100%; padding: 8px; background: #1c1c1e; border: 1px solid #3a3a3c; 
                           color: white; border-radius: 4px; box-sizing: border-box; }
        .btn { padding: 8px 16px; border-radius: 6px; cursor: pointer; border: none; font-size: 14px; text-decoration: none; display: inline-block; }
        .btn-primary { background: #007AFF; color: white; }
        .btn-secondary { background: #3a3a3c; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ page_title }}</h1>
        <form method="POST" action="{{ action_url }}">
            <div class="form-group">
                <label>Image Path</label>
                <input type="text" name="image" value="{{ item.image if item else '' }}" {% if edit %}readonly{% endif %}>
            </div>
            <div class="form-group">
                <label>Title</label>
                <input type="text" name="title" value="{{ item.title if item else '' }}">
            </div>
            <div class="form-group">
                <label>Caption</label>
                <textarea name="caption" rows="3">{{ item.caption if item else '' }}</textarea>
            </div>
            <div class="form-group">
                <label>Link</label>
                <input type="text" name="link" value="{{ item.link if item else '' }}">
            </div>
            <button type="submit" class="btn btn-primary">Save Changes</button>
            <a href="/" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, gallery=load_gallery())

@app.route('/add')
def add_page():
    return render_template_string(EDIT_TEMPLATE, page_title='Add New Item', item=None, item_idx=None, edit=False, action_url='/save-new')

@app.route('/save-new', methods=['POST'])
def save_new():
    item = {
        'image': request.form.get('image'),
        'title': request.form.get('title'),
        'caption': request.form.get('caption'),
        'link': request.form.get('link')
    }
    gallery = load_gallery()
    gallery.append(item)
    save_gallery(gallery)
    return redirect(url_for('index'))

@app.route('/edit/<int:index>')
def edit_page(index):
    gallery = load_gallery()
    if index >= len(gallery): return "Not found", 404
    return render_template_string(EDIT_TEMPLATE, page_title='Edit Gallery Item', item=gallery[index], item_idx=index, edit=True, action_url=f'/save/{index}')

@app.route('/save/<int:index>', methods=['POST'])
def save_edit(index):
    gallery = load_gallery()
    if index >= len(gallery): return "Not found", 404
    item = gallery[index]
    item['title'] = request.form.get('title')
    item['caption'] = request.form.get('caption')
    item['link'] = request.form.get('link')
    save_gallery(gallery)
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_item(index):
    gallery = load_gallery()
    gallery.pop(index)
    save_gallery(gallery)
    return redirect(url_for('index'))

@app.route('/img-srv/<path:filename>')
def serve_image(filename):
    clean_path = filename.lstrip('/')
    return send_from_directory(STATIC_ROOT, clean_path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
