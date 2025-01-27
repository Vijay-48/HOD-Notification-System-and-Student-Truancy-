import logging
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from firebase_admin import messaging
import firebase_admin

class NotificationService:
    def __init__(self, config):
        # Initialize notification services
        self.twilio_client = TwilioClient(config['twilio_sid'], config['twilio_token'])
        self.sendgrid_client = SendGridAPIClient(config['sendgrid_api_key'])
        
        # Initialize Firebase for cloud messaging
        firebase_admin.initialize_app()
        
        # Setup logging
        logging.basicConfig(
            filename='truancy_logs.json', 
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
    
    def send_sms(self, student, incident):
        message = self.twilio_client.messages.create(
            body=f"Truancy Alert: {student['name']} detected at {incident['location']}",
            from_='+1234567890',
            to=student['phone_number']
        )
        return message.sid
    
    def send_email(self, hod_email, incident):
        message = {
            'personalizations': [{
                'to': [{'email': hod_email}],
                'subject': 'Student Truancy Detected'
            }],
            'from': {'email': 'alerts@school.com'},
            'content': [{
                'type': 'text/plain', 
                'value': f"Truancy Detected:\nStudent: {incident['student_name']}\n"
                         f"Location: {incident['location']}\n"
                         f"Time: {incident['timestamp']}"
            }]
        }
        self.sendgrid_client.client.mail.send.post(request_body=message)
    
    def send_mobile_notification(self, hod_token, incident):
        message = messaging.Message(
            notification={
                'title': 'Truancy Alert',
                'body': f"{incident['student_name']} detected outside class"
            },
            token=hod_token
        )
        messaging.send(message)
    
    def log_incident(self, incident):
        logging.info(json.dumps(incident))

# Configuration and usage example
config = {
    'twilio_sid': 'your_twilio_sid',
    'twilio_token': 'your_twilio_token',
    'sendgrid_api_key': 'your_sendgrid_key'
}
notification_service = NotificationService(config)