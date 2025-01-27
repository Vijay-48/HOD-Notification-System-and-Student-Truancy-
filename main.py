import cv2
from student_detection import StudentTruancyDetector
from notification_service import NotificationService
from database import StudentDatabase, ScheduleDatabase

class TruancyDetectionSystem:
    def __init__(self, config):
        # Initialize components
        self.student_db = StudentDatabase(config['database'])
        self.schedule_db = ScheduleDatabase(config['database'])
        
        self.detector = StudentTruancyDetector(
            yolo_model_path=config['models']['yolo'],
            lstm_model_path=config['models']['lstm'],
            schedule_db=self.schedule_db
        )
        
        self.notification_service = NotificationService(config['notifications'])
    
    def process_video_stream(self, video_stream):
        while True:
            ret, frame = video_stream.read()
            if not ret:
                break
            
            # Detect students in the frame
            students = self.detector.detect_students(frame)
            
            for student in students:
                # Validate potential truancy
                if self.detector.validate_truancy(student, timestamp=datetime.now()):
                    # Prepare incident details
                    incident = {
                        'student_id': student['id'],
                        'student_name': student['name'],
                        'location': student['location'],
                        'timestamp': datetime.now(),
                        'frame_snapshot': frame
                    }
                    
                    # Get HOD contact
                    hod = self.student_db.get_department_head(student['department'])
                    
                    # Send notifications
                    self.notification_service.send_sms(student, incident)
                    self.notification_service.send_email(hod['email'], incident)
                    self.notification_service.send_mobile_notification(hod['fcm_token'], incident)
                    
                    # Log the incident
                    self.notification_service.log_incident(incident)
    
    def run(self, video_source):
        video_stream = cv2.VideoCapture(video_source)
        self.process_video_stream(video_stream)

# Configuration
config = {
    'database': {
        'host': 'localhost',
        'user': 'admin',
        'password': 'secure_password'
    },
    'models': {
        'yolo': 'models/student_detection.pt',
        'lstm': 'models/temporal_analysis.h5'
    },
    'notifications': {
        'twilio_sid': 'your_twilio_sid',
        'twilio_token': 'your_twilio_token',
        'sendgrid_api_key': 'your_sendgrid_key'
    }
}

# Initialize and run the system
truancy_system = TruancyDetectionSystem(config)
truancy_system.run(video_source='campus_cctv.mp4')