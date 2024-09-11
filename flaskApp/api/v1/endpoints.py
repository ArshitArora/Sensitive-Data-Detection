from flask import Blueprint, jsonify, request, send_file
from api.v1.services import detect_sensitive_info
import os
v1_blueprint = Blueprint('v1', __name__)

@v1_blueprint.route("/detectSensitiveInfo", methods = ['POST'])
def detectSensitiveInfo():
    if "file" not in request.files:
        return jsonify({'error' : 'No file attached', 'status' : 400})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error' : 'No file attached', 'status' : 400})
    name = "uploads/image." + file.filename.split(".")[-1]
    file.save(name)
    try: 
        result = detect_sensitive_info(name)
        os.remove(name)
    except Exception as e:
        os.remove(name)
        return jsonify({'error' : str(e), 'status' : 500})
    if isinstance(result, str):
        if result == "Image is non-sensitive":
            return jsonify({'response' : result, 'status' : 200})
        elif result == "Could not find any mathing patterns.":
            return jsonify({'response' : "Image is sensitive but could not blur info.", 'status' : 200})
    else :
        return send_file("outputs/blurred_image.jpg", mimetype = 'image/jpeg', as_attachment = True, download_name = "blurred_image.jpg")

@v1_blueprint.route("/healthCheck", methods=['GET'])
def healthCheck():
    return "API is Up..."
