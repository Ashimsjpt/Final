from flask import Flask, render_template, request, send_from_directory
import os
import cv2
import numpy as np
from stl import mesh  # Ensure numpy-stl is installed: pip install numpy-stl

app = Flask(__name__)

# Define folders for uploads and STL files
UPLOAD_FOLDER = './static/uploads'
STL_FOLDER = './static/stl'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STL_FOLDER'] = STL_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STL_FOLDER, exist_ok=True)

def image_to_stl(image_path, output_path, height=10, base_thickness=2, is_foreground=True):
    """
    Convert an image into an STL file.
    :param image_path: Path to input image.
    :param output_path: Path to save the STL file.
    :param height: Height of the 3D model.
    :param base_thickness: Thickness of the base layer.
    :param is_foreground: If True, generates foreground STL; otherwise, background STL.
    """
    try:
        # Read the image in grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Invalid image file.")

        # Resize the image to reduce STL file size and processing time
        img = cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA)

        # Convert to binary using adaptive thresholding
        binary = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Invert the image for background STL
        if not is_foreground:
            binary = cv2.bitwise_not(binary)

        vertices = []
        faces = []

        h, w = binary.shape
        for y in range(h):
            for x in range(w):
                if binary[y, x] == 255:  # Foreground or background pixel
                    z_start = base_thickness
                    z_end = z_start + height
                    base_idx = len(vertices)
                    
                    # Define cube vertices
                    vertices.extend([
                        [x, y, z_start], [x + 1, y, z_start], [x + 1, y + 1, z_start], [x, y + 1, z_start],
                        [x, y, z_end],   [x + 1, y, z_end],   [x + 1, y + 1, z_end],   [x, y + 1, z_end]
                    ])
                    
                    # Define cube faces
                    faces.extend([
                        [base_idx, base_idx + 1, base_idx + 2], [base_idx, base_idx + 2, base_idx + 3],  # Bottom
                        [base_idx + 4, base_idx + 5, base_idx + 6], [base_idx + 4, base_idx + 6, base_idx + 7],  # Top
                        [base_idx, base_idx + 1, base_idx + 5], [base_idx, base_idx + 5, base_idx + 4],  # Side 1
                        [base_idx + 1, base_idx + 2, base_idx + 6], [base_idx + 1, base_idx + 6, base_idx + 5],  # Side 2
                        [base_idx + 2, base_idx + 3, base_idx + 7], [base_idx + 2, base_idx + 7, base_idx + 6],  # Side 3
                        [base_idx + 3, base_idx, base_idx + 4], [base_idx + 3, base_idx + 4, base_idx + 7]  # Side 4
                    ])

        # Create the 3D STL mesh
        stl_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):
                stl_mesh.vectors[i][j] = vertices[face[j]]

        # Save the STL file
        stl_mesh.save(output_path)
        return True
    except Exception as e:
        print(f"Error in image_to_stl: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No file selected", 400

    # Save uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Define STL output paths
    foreground_stl = os.path.join(app.config['STL_FOLDER'], 'foreground.stl')
    background_stl = os.path.join(app.config['STL_FOLDER'], 'background.stl')

    # Convert to STL
    if not image_to_stl(filepath, foreground_stl, height=10, is_foreground=True):
        return "Error generating foreground STL", 500
    if not image_to_stl(filepath, background_stl, height=5, is_foreground=False):
        return "Error generating background STL", 500

    # Return links for download
    return f"""
    <h1>STL Files Generated</h1>
    <a href="/download/foreground.stl" download>Download Foreground STL</a><br>
    <a href="/download/background.stl" download>Download Background STL</a><br>
    """

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['STL_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
