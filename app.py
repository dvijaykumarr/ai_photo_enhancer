import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
import base64

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp'}

def enhance_image(image_path):
    """Enhance image using similar techniques to the GitHub repo"""
    try:
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to PIL Image for enhancement
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Enhance color
        enhancer = ImageEnhance.Color(img_pil)
        img_pil = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img_pil)
        img_pil = enhancer.enhance(2.0)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img_pil)
        img_pil = enhancer.enhance(1.2)
        
        # Convert back to OpenCV format
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        # Save enhanced image
        enhanced_path = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_' + os.path.basename(image_path))
        cv2.imwrite(enhanced_path, img)
        
        return enhanced_path
    except Exception as e:
        print(f"Enhancement error: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Enhance the image
        enhanced_path = enhance_image(filepath)
        
        if enhanced_path:
            return jsonify({
                'status': 'success',
                'original': f'/static/uploads/{filename}',
                'enhanced': f'/static/uploads/enhanced_{filename}'
            })
    
    return jsonify({'status': 'error', 'message': 'File processing failed'}), 500

@app.route('/static/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)