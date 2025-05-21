from flask import Flask, render_template, Response, jsonify
import cv2
from pose_detection import YogaPoseDetector

app = Flask(__name__)
pose_detector = YogaPoseDetector()
camera = None
last_feedback = "Align yourself to match the pose"

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def generate_frames():
    global camera
    print('generate_frames: START')
    
    # First get the camera
    camera = get_camera()
    if camera is None:
        print('Failed to initialize camera')
        return
    
    # Now start the frame generation loop
    while True:
        if camera is None:
            print('generate_frames: camera is None, stopping stream')
            break
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)  # Mirror the frame
            processed_frame, feedback = pose_detector.check_pose(frame)
            global last_feedback
            last_feedback = feedback
            
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/yoga')
def yoga():
    return render_template('yoga_pose.html', current_pose=pose_detector.get_current_pose_name())

@app.route('/video_feed')
def video_feed():
    print('video_feed route hit')
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pose_feedback')
def pose_feedback():
    return jsonify({
        'feedback': last_feedback,
        'current_pose': pose_detector.get_current_pose_name()
    })

@app.route('/meditation')
def meditation():
    return render_template('meditation.html')

@app.route('/diet')
def diet():
    return render_template('diet.html')

@app.route('/generate_diet_plan', methods=['POST'])
def generate_diet_plan():
    data = request.form
    name = data.get('name', '')
    practice_level = data.get('practice-level', 'beginner')
    goal = data.get('goal', 'flexibility')
    
    # Generate personalized diet plan based on inputs
    diet_plan = {
        'name': name,
        'practice_level': practice_level,
        'goal': goal,
        'meals': {
            'breakfast': {
                'title': 'Prana Vardhak Prata',
                'description': 'Start your day with traditional Indian recipes that boost energy and support yoga practice',
                'nutrition': {
                    'protein': '20g',
                    'fiber': '10g'
                },
                'recipes': [
                    'Besan Chilla with Curd',
                    'Moong Dal Chilla with Coriander Chutney',
                    'Oats Poha with Seasonal Vegetables'
                ]
            },
            'lunch': {
                'title': 'Bala Vardhak Bhojan',
                'description': 'Nutrient-rich Indian meals to build strength and support active yoga practice',
                'nutrition': {
                    'carbs': '45g',
                    'protein': '30g'
                },
                'recipes': [
                    'Chana Masala with Brown Rice',
                    'Dal Tadka with Whole Wheat Roti',
                    'Mixed Vegetable Pulao with Curd'
                ]
            },
            'dinner': {
                'title': 'Shanti Pradayak Bhojan',
                'description': 'Light, easily digestible Indian meals to support post-yoga recovery',
                'nutrition': {
                    'healthy_fats': '15g',
                    'fiber': '12g'
                },
                'recipes': [
                    'Sattu Litti with Ghee',
                    'Moong Dal Khichdi with Jeera Rice',
                    'Vegetable Upma with Seasonal Greens'
                ]
            }
        }
    }
    
    return jsonify(diet_plan)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/zen_therapy')
def zen_therapy():
    return render_template('zen_therapy.html')

from flask import request

@app.route('/close_camera', methods=['POST'])
def close_camera():
    print('close_camera route hit')
    global camera
    if camera is not None:
        print('Camera object exists, releasing...')
        camera.release()
        camera = None
        print('Camera released.')
        return jsonify({'success': True})
    print('No camera to release.')
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)
