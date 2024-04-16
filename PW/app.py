from flask import Flask, render_template, Response
import cv2
import datetime

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/save_face', methods=['POST'])
def save_face():
    # Зберегти обличчя користувача
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "static/faces/user_face_{}.jpg".format(timestamp)
    cv2.imwrite(filename, frame)
    cap.release()
    cv2.destroyAllWindows()
    return 'Обличчя успішно збережено!'


@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    # Розпізнати обличчя
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    faces = detect_face(frame)
    cap.release()
    cv2.destroyAllWindows()

    if len(faces) > 0:
        return 'Successfully: Обличчя розпізнано!'
    else:
        return 'Користувача не зареєстровано'


def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces


if __name__ == '__main__':
    app.run(debug=True)
