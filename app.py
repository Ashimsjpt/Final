from flask import Flask, render_template, request, send_from_directory
import os
import cv2

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
PROCESSED_FOLDER = './static/processed'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            # Save the uploaded file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Convert the image to grayscale
            img = cv2.imread(filepath)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Save the grayscale image
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], f"gray_{file.filename}")
            cv2.imwrite(processed_path, gray_img)

            return f"""
            File uploaded and processed successfully! <br>
            <a href="/static/uploads/{file.filename}" target="_blank">Original Image</a><br>
            <a href="/static/processed/gray_{file.filename}" target="_blank">Grayscale Image</a>
            """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

