from flask import Flask, render_template, request
import os
import face_recognition

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(ROOT_DIR, '..', 'known_faces')
KNOWN_FACES_DIR2 = os.path.join(ROOT_DIR, '..', 'known_faces2')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

known_face_encodings = []
known_face_names = []
known_face_encodings2 = []  # New list for face encodings in known_faces2


def load_known_faces():
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            image_path = os.path.join(KNOWN_FACES_DIR, filename)
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(name)

    for filename in os.listdir(KNOWN_FACES_DIR2):
        if filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            image_path = os.path.join(KNOWN_FACES_DIR2, filename)
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings2.append(encoding)


@app.route('/')
def home():
    return render_template('index.html')


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
            matches1 = face_recognition.compare_faces(known_face_encodings, uploaded_face_encoding)
            matches2 = face_recognition.compare_faces(known_face_encodings2, uploaded_face_encoding)

            if True in matches1:
                match_indices = [i for i, match in enumerate(matches1) if match]
                names = [known_face_names[i] for i in match_indices]
                recognition_results.append(f"Match in known_faces: {', '.join(names)}")
            elif True in matches2:
                match_indices = [i for i, match in enumerate(matches2) if match]
                names = [os.path.basename(os.path.splitext(filename)[0]) for filename in os.listdir(KNOWN_FACES_DIR2)]
                recognition_results.append(f"Match in known_faces2: {', '.join(names)}")
            else:
                recognition_results.append("Not Matched")

        return render_template('recognition_result.html', results=recognition_results)

    return 'Invalid file format'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    load_known_faces()
    app.run()
