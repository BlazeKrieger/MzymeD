from flask import Flask, request, render_template_string, jsonify
import os
import sys
sys.path.insert(0, 'src')
from mzymed.app import MzymeDApp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
mzymed = MzymeDApp()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MzymeD</title>
</head>
<body>
    <h1>MzymeD - Enzyme-Substrate Molecular Dynamics</h1>
    <div>
        <h2>Upload Enzyme</h2>
        <form action="/upload_enzyme" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
    </div>
    <div>
        <h2>Upload Substrate</h2>
        <form action="/upload_substrate" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
