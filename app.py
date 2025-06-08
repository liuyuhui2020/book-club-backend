from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import qrcode
import os
import io
from base64 import b64encode
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

EVENTS = []

@app.route("/api/events")
def get_events():
    city = request.args.get("city")
    filtered = [e for e in EVENTS if e["city"] == city]
    sorted_events = sorted(filtered, key=lambda e: e["start_time"])
    return jsonify(sorted_events)

@app.route("/api/events/<int:event_id>")
def get_event_detail(event_id):
    event = next((e for e in EVENTS if e["id"] == event_id), None)
    return jsonify(event)

@app.route("/api/events/<int:event_id>/register", methods=["POST"])
def register(event_id):
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    qr_text = f"event:{event_id}, name:{name}, phone:{phone}"
    img = qrcode.make(qr_text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_base64 = b64encode(buf.getvalue()).decode("utf-8")
    return jsonify({"qr_url": f"data:image/png;base64,{qr_base64}"})

@app.route("/api/admin/events", methods=["POST"])
def create_event():
    name = request.form.get("name")
    city = request.form.get("city")
    start_time = request.form.get("start_time")
    creator = request.form.get("creator")
    max_participants = int(request.form.get("max_participants"))
    description = request.form.get("description")
    recommendation = request.form.get("recommendation")
    type_ = request.form.get("type")

    image_file = request.files.get("image")
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)

    new_event = {
        "id": len(EVENTS) + 1,
        "name": name,
        "city": city,
        "start_time": start_time,
        "creator": creator,
        "max_participants": max_participants,
        "current_participants": 0,
        "description": description,
        "recommendation": recommendation,
        "type": type_,
        "image": f"/uploads/{filename}"
    }
    EVENTS.append(new_event)
    return jsonify({"success": True, "event": new_event})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
