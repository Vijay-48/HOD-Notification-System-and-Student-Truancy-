import pymongo
import mysql
import mysql.connector
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
import uuid

class DatabaseManager:
    def __init__(self, config):
        self.mongo_client = pymongo.MongoClient(config['mongodb_uri'])
        self.mysql_engine = create_engine(config['mysql_uri'])
        self.Base = declarative_base()
        self.Session = sessionmaker(bind=self.mysql_engine)
    
    class Student(declarative_base()):
        __tablename__ = 'students'
        id = Column(Integer, primary_key=True)
        student_uuid = Column(String, unique=True)
        name = Column(String)
        department = Column(String)
        email = Column(String)
        phone = Column(String)
    
    class Attendance(declarative_base()):
        __tablename__ = 'attendance'
        id = Column(Integer, primary_key=True)
        student_id = Column(Integer)
        date = Column(DateTime)
        status = Column(Boolean)
        location = Column(String)
    
    def create_tables(self):
        self.Base.metadata.create_all(self.mysql_engine)
    
    def register_student(self, student_data):
        session = self.Session()
        student = self.Student(
            student_uuid=str(uuid.uuid4()),
            name=student_data['name'],
            department=student_data['department'],
            email=student_data['email'],
            phone=student_data['phone']
        )
        session.add(student)
        session.commit()
        return student.student_uuid
    
    def log_truancy_incident(self, incident_data):
        mongo_db = self.mongo_client['truancy_system']
        incidents_collection = mongo_db['incidents']
        
        incident = {
            'student_id': incident_data['student_id'],
            'timestamp': incident_data['timestamp'],
            'location': incident_data['location'],
            'video_snapshot': incident_data.get('video_snapshot'),
            'verified': False
        }
        
        return incidents_collection.insert_one(incident)
    
    def get_student_schedule(self, student_id, timestamp):
        mongo_db = self.mongo_client['truancy_system']
        schedules_collection = mongo_db['schedules']
        
        schedule = schedules_collection.find_one({
            'student_id': student_id,
            'start_time': {'$lte': timestamp},
            'end_time': {'$gte': timestamp}
        })
        
        return schedule is not None
    
    def get_department_head(self, department):
        session = self.Session()
        hod = session.query(self.Student).filter_by(department=department).first()
        return {
            'email': hod.email,
            'phone': hod.phone
        }
    
    def anonymize_student_data(self, student_id):
        mongo_db = self.mongo_client['truancy_system']
        incidents_collection = mongo_db['incidents']
        
        incidents_collection.update_many(
            {'student_id': student_id},
            {'$set': {'student_id': self.hash_identifier(student_id)}}
        )
    
    def hash_identifier(self, identifier):
        return bcrypt.hashpw(str(identifier).encode(), bcrypt.gensalt()).decode()

# Configuration example
config = {
    'mongodb_uri': 'mongodb://localhost:27017',
    'mysql_uri': 'mysql://root:root@localhost:3306/truancy_db'
}

# Initialize database manager
db_manager = DatabaseManager(config)
db_manager.create_tables()