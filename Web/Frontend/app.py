from flask import Flask, jsonify, send_from_directory, render_template
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

FILES_DIR = os.path.join(app.root_path, 'static', 'files')

@app.route('/')
def index():
    return render_template('Dashboard.html')

@app.route('/api/files')
def list_files():
    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)

    files = []
    for filename in os.listdir(FILES_DIR):
        file_path = os.path.join(FILES_DIR, filename)
        if os.path.isfile(file_path):
            files.append({
                "name": filename,
                "path": f"/files/{filename}"
            })

    return jsonify(files)

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(FILES_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)