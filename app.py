from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("POST request received")
        file = request.files.get('image')
        if file:
            print(f"File received: {file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return f"File uploaded successfully: {file.filename}"
        else:
            print("No file found in the request")
    return render_template('index.html')
