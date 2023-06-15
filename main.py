from flask import Flask, render_template, request
import os
import face_recognition

app = Flask(__name__)

KNOWN_FACES_DIR = 'known_faces'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

known_face_encodings = []
known_face_names = []

def load_known_faces():
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            image_path = os.path.join(KNOWN_FACES_DIR, filename)
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(name)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'image' not in request.files:
        return 'No image file selected'

    image_file = request.files['image']
    if image_file.filename == '':
        return 'No image file selected'

    if image_file and allowed_file(image_file.filename):
        name = request.form['name']
        if name == '':
            return 'Please provide a name for the uploaded image'

        image_path = os.path.join(KNOWN_FACES_DIR, f'{name}.jpg')
        image_file.save(image_path)

        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]

        known_face_encodings.append(encoding)
        known_face_names.append(name)

        return 'Image uploaded and associated with the provided name'

    return 'Invalid file format'

@app.route('/recognition_result', methods=['POST'])
def recognition_result():
    if 'image' not in request.files:
        return 'No image file selected'

    image_file = request.files['image']
    if image_file.filename == '':
        return 'No image file selected'

    if image_file and allowed_file(image_file.filename):
        uploaded_image = face_recognition.load_image_file(image_file)
        uploaded_face_encodings = face_recognition.face_encodings(uploaded_image)

        if len(uploaded_face_encodings) == 0:
            return 'No face found in the uploaded image'

        recognition_results = []
        for uploaded_face_encoding in uploaded_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, uploaded_face_encoding)
            name = 'Not Matched'

            if True in matches:
                match_indices = [i for i, match in enumerate(matches) if match]
                names = [known_face_names[i] for i in match_indices]
                name = ', '.join(names)

            recognition_results.append(f"Match: {name}")

        return render_template('recognition_result.html', results=recognition_results)

    return 'Invalid file format'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    load_known_faces()
    app.run()
