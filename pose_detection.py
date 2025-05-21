import cv2
import numpy as np
import mediapipe as mp
from cvzone.PoseModule import PoseDetector
import pyttsx3
import threading
import time

class YogaPoseDetector:
    def __init__(self):
        self.detector = PoseDetector()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.last_voice_time = 0
        self.voice_cooldown = 3  # seconds between voice prompts
        self.pose_hold_time = 0
        self.pose_start_time = None
        self.required_hold_time = 5  # seconds to hold each pose
        
        self.pose_angles = {
            "pranamasana": {  # Prayer Pose
                "shoulders": (80, 100),
                "elbows": (165, 180),
                "spine": (165, 180)
            },
            "hasta_uttanasana": {  # Raised Arms Pose
                "shoulders": (165, 180),
                "elbows": (165, 180),
                "spine": (165, 180)
            },
            "hasta_padasana": {  # Forward Bend
                "hips": (0, 45),
                "knees": (165, 180),
                "spine": (0, 45)
            },
            "ashwa_sanchalanasana": {  # Equestrian Pose
                "front_knee": (85, 95),
                "back_knee": (165, 180),
                "front_hip": (80, 100)
            },
            "parvatasana": {  # Mountain Pose
                "shoulders": (165, 180),
                "hips": (165, 180),
                "spine": (165, 180)
            },
            "ashtanga_namaskara": {  # Eight Limbed Salutation
                "elbows": (80, 100),
                "knees": (165, 180),
                "hips": (165, 180)
            },
            "bhujangasana": {  # Cobra Pose
                "elbows": (165, 180),
                "spine": (45, 60),
                "hips": (165, 180)
            },
            "adho_mukha_svanasana": {  # Downward Dog
                "shoulders": (165, 180),
                "hips": (45, 90),
                "knees": (165, 180)
            }
        }
        
        self.pose_instructions = {
            "pranamasana": "Stand straight with feet together and hands in prayer position",
            "hasta_uttanasana": "Raise your arms up, bend slightly backward",
            "hasta_padasana": "Bend forward and touch your toes",
            "ashwa_sanchalanasana": "Step right foot back, bend left knee, look up",
            "parvatasana": "Form an inverted V with your body",
            "ashtanga_namaskara": "Lower your body, keep elbows bent",
            "bhujangasana": "Lift your chest up into cobra pose",
            "adho_mukha_svanasana": "Push back into downward dog position"
        }
        self.current_pose = "pranamasana"
        self.pose_sequence = [
            "pranamasana",
            "hasta_uttanasana",
            "hasta_padasana",
            "ashwa_sanchalanasana",
            "parvatasana",
            "ashtanga_namaskara",
            "bhujangasana",
            "adho_mukha_svanasana",
            # Reverse sequence
            "parvatasana",
            "ashwa_sanchalanasana",
            "hasta_padasana",
            "hasta_uttanasana",
            "pranamasana"
        ]
        self.pose_index = 0

    def calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points"""
        angle = np.arctan2(p3[1] - p2[1], p3[0] - p2[0]) - \
                np.arctan2(p1[1] - p2[1], p1[0] - p2[0])
        angle = np.abs(angle * 180.0 / np.pi)
        if angle > 180:
            angle = 360 - angle
        return angle

    def __init__(self):
        self.detector = PoseDetector()
        self.tts_engine = pyttsx3.init()
        self.last_voice_time = 0
        self.voice_cooldown = 2  # Reduced cooldown between prompts
        self.pose_hold_time = 0
        self.pose_start_time = None
        self.required_hold_time = 5  # seconds to hold each pose
        self.last_feedback = ""
        self.feedback_repeat_count = 0
        self.max_repeats = 5  # Increased max repeats
        self.last_incorrect_parts = set()  # Track which parts were incorrect
        
        # Initialize pose sequence
        self.current_pose = "pranamasana"
        self.pose_sequence = [
            "pranamasana",
            "hasta_uttanasana",
            "hasta_padasana",
            "ashwa_sanchalanasana",
            "parvatasana",
            "ashtanga_namaskara",
            "bhujangasana",
            "adho_mukha_svanasana",
            # Reverse sequence
            "parvatasana",
            "ashwa_sanchalanasana",
            "hasta_padasana",
            "hasta_uttanasana",
            "pranamasana"
        ]
        self.pose_index = 0
        
        # Initialize pose angles
        self.pose_angles = {
            "pranamasana": {  # Prayer Pose
                "shoulders": (80, 100),
                "elbows": (165, 180),
                "spine": (165, 180)
            },
            "hasta_uttanasana": {  # Raised Arms Pose
                "shoulders": (165, 180),
                "elbows": (165, 180),
                "spine": (165, 180)
            },
            "hasta_padasana": {  # Forward Bend
                "hips": (0, 45),
                "knees": (165, 180),
                "spine": (0, 45)
            },
            "ashwa_sanchalanasana": {  # Equestrian Pose
                "front_knee": (85, 95),
                "back_knee": (165, 180),
                "front_hip": (80, 100)
            },
            "parvatasana": {  # Mountain Pose
                "shoulders": (165, 180),
                "hips": (165, 180),
                "spine": (165, 180)
            },
            "ashtanga_namaskara": {  # Eight Limbed Salutation
                "elbows": (80, 100),
                "knees": (165, 180),
                "hips": (165, 180)
            },
            "bhujangasana": {  # Cobra Pose
                "elbows": (165, 180),
                "spine": (45, 60),
                "hips": (165, 180)
            },
            "adho_mukha_svanasana": {  # Downward Dog
                "shoulders": (165, 180),
                "hips": (45, 90),
                "knees": (165, 180)
            }
        }
        
        # Initialize text-to-speech
        try:
            voices = self.tts_engine.getProperty('voices')
            self.tts_engine.setProperty('voice', voices[1].id)  # Use female voice
            self.tts_engine.setProperty('rate', 150)  # Adjust speed
            self.tts_engine.setProperty('volume', 1.0)  # Max volume
        except Exception as e:
            print(f"Speech initialization error: {e}")

    def speak(self, text):
        """Speak the given text immediately"""
        try:
            def speak_text():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak_text)
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"Speech error: {e}")

    def check_pose(self, img):
        """Check if current pose is correct"""
        img = self.detector.findPose(img)
        lmList, bboxInfo = self.detector.findPosition(img, draw=False)
        
        if not lmList:
            self.speak("Please stand in front of the camera")
            return img, "No pose detected"

        feedback = []
        pose_correct = True

        # Get key points
        shoulders = (self.calculate_angle(lmList[11][:2], lmList[12][:2], lmList[14][:2]),
                    self.calculate_angle(lmList[13][:2], lmList[11][:2], lmList[12][:2]))
        elbows = (self.calculate_angle(lmList[13][:2], lmList[15][:2], lmList[11][:2]),
                  self.calculate_angle(lmList[14][:2], lmList[16][:2], lmList[12][:2]))
        spine = self.calculate_angle(lmList[7][:2], lmList[11][:2], lmList[23][:2])
        hips = (self.calculate_angle(lmList[11][:2], lmList[23][:2], lmList[25][:2]),
                self.calculate_angle(lmList[12][:2], lmList[24][:2], lmList[26][:2]))
        knees = (self.calculate_angle(lmList[23][:2], lmList[25][:2], lmList[27][:2]),
                 self.calculate_angle(lmList[24][:2], lmList[26][:2], lmList[28][:2]))

        # Check current pose
        if self.current_pose == "pranamasana":
            if not all(80 <= angle <= 100 for angle in shoulders):
                feedback.append("Bring your hands to prayer position")
                pose_correct = False
            if not all(165 <= angle <= 180 for angle in elbows):
                feedback.append("Keep your arms straight")
                pose_correct = False

        elif self.current_pose == "hasta_uttanasana":
            if not all(165 <= angle <= 180 for angle in shoulders):
                feedback.append("Raise your arms up")
                pose_correct = False
            if not (165 <= spine <= 180):
                feedback.append("Bend slightly backward")
                pose_correct = False

        elif self.current_pose == "hasta_padasana":
            if not all(0 <= angle <= 45 for angle in hips):
                feedback.append("Bend forward more")
                pose_correct = False
            if not all(165 <= angle <= 180 for angle in knees):
                feedback.append("Keep your legs straight")
                pose_correct = False

        # Add checks for other poses...

        # Initialize colors for each body part and feedback list
        colors = {
            'shoulders': (0, 255, 0),  # Default to green
            'arms': (0, 255, 0),
            'spine': (0, 255, 0),
            'hips': (0, 255, 0),
            'legs': (0, 255, 0)
        }
        feedback_text = []
        
        # Get angle ranges for current pose
        pose_range = self.pose_angles.get(self.current_pose, {})
        feedback_text = []
        
        # Initialize feedback message
        if not pose_range:
            feedback = "Unknown pose"
            self.speak(feedback, force=True)
            return img, feedback, False
        
        # Check shoulders
        if "shoulders" in pose_range:
            min_angle, max_angle = pose_range["shoulders"]
            if not all(min_angle <= angle <= max_angle for angle in shoulders):
                colors['shoulders'] = (0, 0, 255)
                colors['arms'] = (0, 0, 255)
                feedback_text.append("Adjust your shoulder position")
        
        # Check elbows
        if "elbows" in pose_range:
            min_angle, max_angle = pose_range["elbows"]
            if not all(min_angle <= angle <= max_angle for angle in elbows):
                colors['arms'] = (0, 0, 255)
                feedback_text.append("Straighten your arms")
        
        # Check spine
        if "spine" in pose_range:
            min_angle, max_angle = pose_range["spine"]
            if not (min_angle <= spine <= max_angle):
                colors['spine'] = (0, 0, 255)
                feedback_text.append("Adjust your back position")
        
        # Check hips
        if "hips" in pose_range:
            min_angle, max_angle = pose_range["hips"]
            if not all(min_angle <= angle <= max_angle for angle in hips):
                colors['hips'] = (0, 0, 255)
                colors['spine'] = (0, 0, 255)
                feedback_text.append("Adjust your hip position")
        
        # Check knees
        if "knees" in pose_range:
            min_angle, max_angle = pose_range["knees"]
            if not all(min_angle <= angle <= max_angle for angle in knees):
                colors['legs'] = (0, 0, 255)
                feedback_text.append("Straighten your knees")
        
        # Special cases for specific poses
        if self.current_pose == "ashwa_sanchalanasana":
            if "front_knee" in pose_range:
                min_angle, max_angle = pose_range["front_knee"]
                if not (min_angle <= front_knee <= max_angle):
                    colors['legs'] = (0, 0, 255)
                    feedback_text.append("Bend your front knee more")
        
        # Prepare and speak feedback
        if feedback_text:
            feedback = "\n".join(feedback_text)
        else:
            feedback = "Correct pose!"
        
        # Always speak the current feedback
        self.speak(feedback)
        
        # Set pose correctness
        pose_correct = len(feedback_text) == 0
        
        # Draw points
        for i, point in enumerate(lmList):
            cv2.circle(img, point[:2], 5, (0, 255, 0), cv2.FILLED)
        
        # Draw connections with specific colors
        # Torso
        cv2.line(img, lmList[11][:2], lmList[12][:2], colors['shoulders'], 2)  # Shoulders
        cv2.line(img, lmList[11][:2], lmList[23][:2], colors['spine'], 2)  # Left body side
        cv2.line(img, lmList[12][:2], lmList[24][:2], colors['spine'], 2)  # Right body side
        cv2.line(img, lmList[23][:2], lmList[24][:2], colors['hips'], 2)  # Hips
        
        # Arms
        cv2.line(img, lmList[11][:2], lmList[13][:2], colors['arms'], 2)  # Left upper arm
        cv2.line(img, lmList[13][:2], lmList[15][:2], colors['arms'], 2)  # Left lower arm
        cv2.line(img, lmList[12][:2], lmList[14][:2], colors['arms'], 2)  # Right upper arm
        cv2.line(img, lmList[14][:2], lmList[16][:2], colors['arms'], 2)  # Right lower arm
        
        # Legs
        cv2.line(img, lmList[23][:2], lmList[25][:2], colors['legs'], 2)  # Left upper leg
        cv2.line(img, lmList[25][:2], lmList[27][:2], colors['legs'], 2)  # Left lower leg
        cv2.line(img, lmList[24][:2], lmList[26][:2], colors['legs'], 2)  # Right upper leg
        cv2.line(img, lmList[26][:2], lmList[28][:2], colors['legs'], 2)  # Right lower leg

        # Handle pose transitions
        if pose_correct:
            if self.pose_start_time is None:
                self.pose_start_time = time.time()
                self.pose_hold_time = 0
            else:
                self.pose_hold_time = time.time() - self.pose_start_time
                
                # Check if pose has been held long enough
                if self.pose_hold_time >= self.required_hold_time:
                    next_pose = self.pose_sequence[(self.pose_index + 1) % len(self.pose_sequence)]
                    self.speak(f"Excellent! Moving to {next_pose.replace('_', ' ')}")
                    self.pose_index = (self.pose_index + 1) % len(self.pose_sequence)
                    self.current_pose = self.pose_sequence[self.pose_index]
                    self.pose_start_time = None
                else:
                    # Show remaining time
                    remaining = self.required_hold_time - self.pose_hold_time
                    cv2.putText(img, f"Hold pose for {int(remaining)}s", 
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            self.pose_start_time = None
            self.pose_hold_time = 0
            cv2.putText(img, f"Adjust your {self.current_pose.replace('_', ' ')} pose", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            if feedback:
                self.speak(feedback[0])  # Speak the first correction needed
                for i, text in enumerate(feedback):
                    cv2.putText(img, text, (50, 100 + 30*i), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return img, "\n".join(feedback) if feedback else "Pose is correct"

    def get_current_pose_name(self):
        return self.current_pose.replace('_', ' ').title()
