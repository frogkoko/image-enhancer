from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Enhancement Studio</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3a56d4;
            --secondary: #7209b7;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --gray-light: #e9ecef;
            --success: #4cc9f0;
            --border-radius: 12px;
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
            color: var(--dark);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 10px;
        }

        .logo i {
            font-size: 2.5rem;
            color: var(--primary);
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 1.1rem;
            color: var(--gray);
            max-width: 600px;
            margin: 0 auto;
        }

        .app-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        @media (max-width: 1024px) {
            .app-container {
                grid-template-columns: 1fr;
            }
        }

        .upload-section {
            background: white;
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            height: fit-content;
        }

        .upload-area {
            border: 2px dashed var(--gray-light);
            border-radius: var(--border-radius);
            padding: 40px 20px;
            text-align: center;
            transition: var(--transition);
            cursor: pointer;
            margin-bottom: 20px;
        }

        .upload-area:hover {
            border-color: var(--primary);
            background-color: rgba(67, 97, 238, 0.03);
        }

        .upload-area i {
            font-size: 3rem;
            color: var(--primary);
            margin-bottom: 15px;
        }

        .upload-area h3 {
            margin-bottom: 10px;
            font-weight: 600;
        }

        .upload-area p {
            color: var(--gray);
            margin-bottom: 20px;
        }

        .upload-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-block;
        }

        .upload-btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }

        input[type="file"] {
            display: none;
        }

        .image-preview {
            margin-top: 20px;
            text-align: center;
        }

        .image-preview img {
            max-width: 100%;
            max-height: 300px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .controls-section {
            background: white;
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--shadow);
        }

        .section-title {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 25px;
            font-size: 1.3rem;
            font-weight: 600;
        }

        .section-title i {
            color: var(--primary);
        }

        .controls-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .controls-grid {
                grid-template-columns: 1fr;
            }
        }

        .control-item {
            margin-bottom: 15px;
        }

        .control-header {
            display: flex;
            justify-content: between;
            margin-bottom: 8px;
        }

        .control-label {
            font-weight: 600;
            color: var(--dark);
        }

        .control-value {
            color: var(--primary);
            font-weight: 600;
        }

        .slider-container {
            position: relative;
            height: 6px;
            background: var(--gray-light);
            border-radius: 3px;
        }

        .slider-fill {
            position: absolute;
            height: 100%;
            background: var(--primary);
            border-radius: 3px;
            width: 50%;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            -webkit-appearance: none;
            background: transparent;
            position: relative;
            z-index: 2;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: white;
            border: 2px solid var(--primary);
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }

        .filters-section {
            margin-bottom: 30px;
        }

        .filters-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }

        @media (max-width: 480px) {
            .filters-grid {
                grid-template-columns: 1fr;
            }
        }

        .filter-option {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 15px;
            background: var(--gray-light);
            border-radius: 8px;
            cursor: pointer;
            transition: var(--transition);
        }

        .filter-option:hover {
            background: #dbeafe;
        }

        .filter-option.active {
            background: #dbeafe;
            border: 1px solid var(--primary);
        }

        .filter-option input {
            display: none;
        }

        .filter-checkbox {
            width: 20px;
            height: 20px;
            border: 2px solid var(--gray);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
        }

        .filter-option.active .filter-checkbox {
            background: var(--primary);
            border-color: var(--primary);
        }

        .filter-option.active .filter-checkbox:after {
            content: "✓";
            color: white;
            font-size: 14px;
            font-weight: bold;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        @media (max-width: 480px) {
            .action-buttons {
                flex-direction: column;
            }
        }

        .btn {
            padding: 14px 25px;
            border: none;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            flex: 1;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
        }

        .btn-secondary {
            background: white;
            color: var(--primary);
            border: 1px solid var(--primary);
        }

        .btn-secondary:hover {
            background: #f0f4ff;
            transform: translateY(-2px);
        }

        .btn-success {
            background: var(--success);
            color: white;
        }

        .btn-success:hover {
            background: #3ab0d9;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 201, 240, 0.3);
        }

        .results-section {
            background: white;
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--shadow);
            grid-column: 1 / -1;
        }

        .images-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        @media (max-width: 768px) {
            .images-comparison {
                grid-template-columns: 1fr;
            }
        }

        .image-container {
            text-align: center;
        }

        .image-container h3 {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .image-placeholder {
            background: var(--gray-light);
            border-radius: var(--border-radius);
            height: 300px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--gray);
        }

        .image-placeholder i {
            font-size: 3rem;
            margin-bottom: 15px;
        }

        .image-result {
            max-width: 100%;
            max-height: 400px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .status-message {
            padding: 15px;
            border-radius: var(--border-radius);
            margin: 20px 0;
            text-align: center;
            display: none;
        }

        .status-success {
            background: #e8f5e9;
            color: #2e7d32;
            display: block;
        }

        .status-error {
            background: #ffebee;
            color: #c62828;
            display: block;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 30px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(67, 97, 238, 0.2);
            border-left: 4px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        footer {
            text-align: center;
            margin-top: 40px;
            color: var(--gray);
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <i class="fas fa-magic"></i>
            </div>
            <h1>Image Enhancement Studio</h1>
            <p class="subtitle">Transform your images with professional-grade adjustments and filters in seconds</p>
        </header>

        <div class="app-container">
            <div class="upload-section">
                <div class="section-title">
                    <i class="fas fa-upload"></i>
                    <h2>Upload Image</h2>
                </div>
                
                <div class="upload-area" id="uploadArea">
                    <i class="fas fa-cloud-upload-alt"></i>
                    <h3>Drag & Drop or Click to Upload</h3>
                    <p>Supports JPG, PNG, and WebP up to 16MB</p>
                    <label for="imageInput" class="upload-btn">Choose File</label>
                    <input type="file" id="imageInput" accept="image/*">
                </div>
                
                <div class="image-preview">
                    <img id="originalImage" src="" alt="Uploaded image" style="display:none;">
                    <div id="originalPlaceholder" class="image-placeholder">
                        <i class="far fa-image"></i>
                        <p>Your image will appear here</p>
                    </div>
                </div>
            </div>

            <div class="controls-section">
                <div class="section-title">
                    <i class="fas fa-sliders-h"></i>
                    <h2>Adjustments</h2>
                </div>
                
                <div class="controls-grid">
                    <div class="control-item">
                        <div class="control-header">
                            <span class="control-label">Brightness</span>
                            <span class="control-value" id="brightnessValue">1.0</span>
                        </div>
                        <div class="slider-container">
                            <div class="slider-fill" id="brightnessFill"></div>
                            <input type="range" id="brightness" min="0" max="2" step="0.1" value="1">
                        </div>
                    </div>
                    
                    <div class="control-item">
                        <div class="control-header">
                            <span class="control-label">Contrast</span>
                            <span class="control-value" id="contrastValue">1.0</span>
                        </div>
                        <div class="slider-container">
                            <div class="slider-fill" id="contrastFill"></div>
                            <input type="range" id="contrast" min="0" max="2" step="0.1" value="1">
                        </div>
                    </div>
                    
                    <div class="control-item">
                        <div class="control-header">
                            <span class="control-label">Sharpness</span>
                            <span class="control-value" id="sharpnessValue">1.0</span>
                        </div>
                        <div class="slider-container">
                            <div class="slider-fill" id="sharpnessFill"></div>
                            <input type="range" id="sharpness" min="0" max="2" step="0.1" value="1">
                        </div>
                    </div>
                    
                    <div class="control-item">
                        <div class="control-header">
                            <span class="control-label">Saturation</span>
                            <span class="control-value" id="colorValue">1.0</span>
                        </div>
                        <div class="slider-container">
                            <div class="slider-fill" id="colorFill"></div>
                            <input type="range" id="color" min="0" max="2" step="0.1" value="1">
                        </div>
                    </div>
                </div>
                
                <div class="filters-section">
                    <div class="section-title">
                        <i class="fas fa-filter"></i>
                        <h2>Filters</h2>
                    </div>
                    
                    <div class="filters-grid">
                        <div class="filter-option" id="blurOption">
                            <div class="filter-checkbox"></div>
                            <span>Blur</span>
                            <input type="checkbox" id="blur">
                        </div>
                        
                        <div class="filter-option" id="detailOption">
                            <div class="filter-checkbox"></div>
                            <span>Enhance Detail</span>
                            <input type="checkbox" id="detail">
                        </div>
                        
                        <div class="filter-option" id="edgeOption">
                            <div class="filter-checkbox"></div>
                            <span>Edge Enhance</span>
                            <input type="checkbox" id="edge">
                        </div>
                        
                        <div class="filter-option" id="smoothOption">
                            <div class="filter-checkbox"></div>
                            <span>Smooth</span>
                            <input type="checkbox" id="smooth">
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="applyEnhancement()">
                        <i class="fas fa-bolt"></i>
                        Apply Enhancement
                    </button>
                    <button class="btn btn-secondary" onclick="resetControls()">
                        <i class="fas fa-redo"></i>
                        Reset
                    </button>
                </div>
            </div>

            <div class="results-section">
                <div class="section-title">
                    <i class="fas fa-images"></i>
                    <h2>Results</h2>
                </div>
                
                <div class="images-comparison">
                    <div class="image-container">
                        <h3><i class="fas fa-image"></i> Original</h3>
                        <img id="originalResult" class="image-result" src="" alt="Original image" style="display:none;">
                        <div id="originalResultPlaceholder" class="image-placeholder">
                            <i class="far fa-file-image"></i>
                            <p>Original image will appear here</p>
                        </div>
                    </div>
                    
                    <div class="image-container">
                        <h3><i class="fas fa-star"></i> Enhanced</h3>
                        <img id="enhancedImage" class="image-result" src="" alt="Enhanced image" style="display:none;">
                        <div id="enhancedPlaceholder" class="image-placeholder">
                            <i class="fas fa-magic"></i>
                            <p>Enhanced image will appear here</p>
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-success" onclick="downloadImage()">
                        <i class="fas fa-download"></i>
                        Download Enhanced Image
                    </button>
                </div>
            </div>
        </div>

        <div class="loading" id="loadingIndicator">
            <div class="spinner"></div>
            <p>Processing your image...</p>
        </div>

        <div class="status-message" id="status"></div>

        <footer>
            <p>Image Enhancement Studio | Powered by Flask & Pillow</p>
        </footer>
    </div>

    <script>
        let originalImageData = null;

        // Upload area interaction
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('imageInput');

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--primary)';
            uploadArea.style.backgroundColor = 'rgba(67, 97, 238, 0.05)';
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = 'var(--gray-light)';
            uploadArea.style.backgroundColor = '';
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--gray-light)';
            uploadArea.style.backgroundColor = '';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleImageSelection();
            }
        });

        fileInput.addEventListener('change', handleImageSelection);

        function handleImageSelection() {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    originalImageData = event.target.result;
                    
                    // Update preview image
                    document.getElementById('originalImage').src = originalImageData;
                    document.getElementById('originalImage').style.display = 'block';
                    document.getElementById('originalPlaceholder').style.display = 'none';
                    
                    // Update original result image
                    document.getElementById('originalResult').src = originalImageData;
                    document.getElementById('originalResult').style.display = 'block';
                    document.getElementById('originalResultPlaceholder').style.display = 'none';
                    
                    showStatus('Image uploaded successfully!', 'success');
                };
                reader.readAsDataURL(file);
            }
        }

        // Update slider value displays and fill
        function updateSlider(id) {
            const slider = document.getElementById(id);
            const valueDisplay = document.getElementById(id + 'Value');
            const fill = document.getElementById(id + 'Fill');
            
            valueDisplay.textContent = slider.value;
            fill.style.width = `${(slider.value / slider.max) * 100}%`;
            
            // Update slider color based on value
            if (slider.value > 1) {
                fill.style.background = 'var(--success)';
            } else if (slider.value < 1) {
                fill.style.background = '#ff6b6b';
            } else {
                fill.style.background = 'var(--primary)';
            }
        }

        // Initialize sliders
        ['brightness', 'contrast', 'sharpness', 'color'].forEach(id => {
            const slider = document.getElementById(id);
            slider.addEventListener('input', () => updateSlider(id));
            updateSlider(id); // Initialize on page load
        });

        // Filter options interaction
        document.querySelectorAll('.filter-option').forEach(option => {
            option.addEventListener('click', function() {
                this.classList.toggle('active');
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
            });
        });

        async function applyEnhancement() {
            if (!originalImageData) {
                showStatus('Please upload an image first!', 'error');
                return;
            }

            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('status').style.display = 'none';

            const formData = new FormData();
            const blob = await fetch(originalImageData).then(r => r.blob());
            formData.append('image', blob);
            formData.append('brightness', document.getElementById('brightness').value);
            formData.append('contrast', document.getElementById('contrast').value);
            formData.append('sharpness', document.getElementById('sharpness').value);
            formData.append('color', document.getElementById('color').value);
            formData.append('blur', document.getElementById('blur').checked);
            formData.append('detail', document.getElementById('detail').checked);
            formData.append('edge', document.getElementById('edge').checked);
            formData.append('smooth', document.getElementById('smooth').checked);

            try {
                const response = await fetch('/enhance', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    document.getElementById('enhancedImage').src = url;
                    document.getElementById('enhancedImage').style.display = 'block';
                    document.getElementById('enhancedPlaceholder').style.display = 'none';
                    showStatus('Enhancement applied successfully!', 'success');
                } else {
                    showStatus('Error applying enhancement', 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            }

            document.getElementById('loadingIndicator').style.display = 'none';
        }

        async function downloadImage() {
            const enhancedImg = document.getElementById('enhancedImage');
            if (!enhancedImg.src || enhancedImg.style.display === 'none') {
                showStatus('Please apply enhancement first!', 'error');
                return;
            }

            const link = document.createElement('a');
            link.href = enhancedImg.src;
            link.download = 'enhanced_image.png';
            link.click();
            showStatus('Image downloaded successfully!', 'success');
        }

        function resetControls() {
            // Reset sliders
            document.getElementById('brightness').value = 1;
            document.getElementById('contrast').value = 1;
            document.getElementById('sharpness').value = 1;
            document.getElementById('color').value = 1;
            
            // Update slider displays
            ['brightness', 'contrast', 'sharpness', 'color'].forEach(id => updateSlider(id));
            
            // Reset filters
            document.querySelectorAll('.filter-option').forEach(option => {
                option.classList.remove('active');
                option.querySelector('input[type="checkbox"]').checked = false;
            });
            
            showStatus('Controls reset to default values', 'success');
        }

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status-message status-' + type;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/enhance', methods=['POST'])
def enhance_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img = Image.open(file.stream)
        
        # Get enhancement parameters
        brightness = float(request.form.get('brightness', 1.0))
        contrast = float(request.form.get('contrast', 1.0))
        sharpness = float(request.form.get('sharpness', 1.0))
        color = float(request.form.get('color', 1.0))
        
        # Apply enhancements
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(color)
        
        # Apply filters
        if request.form.get('blur') == 'true':
            img = img.filter(ImageFilter.BLUR)
        
        if request.form.get('detail') == 'true':
            img = img.filter(ImageFilter.DETAIL)
        
        if request.form.get('edge') == 'true':
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        
        if request.form.get('smooth') == 'true':
            img = img.filter(ImageFilter.SMOOTH)
        
        # Save to bytes
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)