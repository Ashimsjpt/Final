from flask import Flask, render_template, request
import os
import cv2
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
PROCESSED_FOLDER = './static/processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['image']
        process_type = request.form['process_type']

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Read the uploaded image in grayscale
            img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

            # Apply GaussianBlur to reduce noise
            blurred_img = cv2.GaussianBlur(img, (5, 5), 0)

            if process_type == "sobel":
                # Sobel Edge Detection
                sobelx = cv2.Sobel(blurred_img, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(blurred_img, cv2.CV_64F, 0, 1, ksize=3)
                sobel = cv2.magnitude(sobelx, sobely)
                sobel = cv2.convertScaleAbs(sobel)

                # Apply morphological operations to clean up the edges
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                sobel_cleaned = cv2.morphologyEx(sobel, cv2.MORPH_CLOSE, kernel)

                # Enhance line darkness by thresholding
                _, darkened_lines = cv2.threshold(sobel_cleaned, 50, 255, cv2.THRESH_BINARY)

                # Invert colors so lines are black, background is white
                inverted_sobel = cv2.bitwise_not(darkened_lines)

                processed_img = inverted_sobel

            else:
                # Default to grayscale if no valid process_type is selected
                processed_img = blurred_img

            # Save the processed image
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{process_type}_{file.filename}")
            cv2.imwrite(processed_path, processed_img)

            # Generate HTML response to display images
            return f"""
            <h1>Image Uploaded and Processed</h1>
            <h2>Original Image:</h2>
            <img src="/static/uploads/{file.filename}" alt="Original Image" style="max-width: 400px;">
            <h2>{process_type.capitalize()} Image:</h2>
            <img src="/static/processed/{process_type}_{file.filename}" alt="{process_type.capitalize()} Image" style="max-width: 400px;">
            <br><br>
            <a href="/">Upload Another Image</a>
            """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
