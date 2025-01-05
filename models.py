from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db= SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Service Professional, customer
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.Date)
    is_admin = db.Column(db.Boolean,default=False)

    # Relationship to Customer and ServiceProfessional models
    customer = db.relationship('Customer', backref='user', uselist=False)
    service_professional = db.relationship('ServiceProfessional', backref='user', uselist=False)
class Service(db.Model):
    __tablename__ = 'services'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50)) 
    description = db.Column(db.Text, nullable=True)
    
    # Relationship 
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)
    professionals = db.relationship('ServiceProfessional', back_populates='service')
    

# Service Professional Model
class ServiceProfessional(db.Model):
    __tablename__ = 'service_professionals'



    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'),nullable=True)
    experience = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    phone = db.Column(db.String())
    profile_verified = db.Column(db.Boolean, default=False) # to mark if the admin verifies the professional
    rejected = db.Column(db.Boolean,default=0) #to mark rejection
    documents = db.Column(db.String) #link to attached documents
    status = db.Column(db.String(10),default='Active')
    # Relationship to ServiceRequest
    service_requests = db.relationship('ServiceRequest', backref='service_professional', lazy=True)
    service = db.relationship('Service', back_populates='professionals')
class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15), nullable=False)

    # Relationship to ServiceRequest
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True)
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professionals.id'), nullable=True) 
    date_of_request = db.Column(db.Date)
    date_of_completion = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Requested')  # Requested, Assigned, Closed
    remarks = db.Column(db.Text, nullable=True)
    ratings = db.Column(db.Float,nullable=True)
        
    # Relationships
    
with app.app_context():
    db.create_all()

#if admin exists, else create admin
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
       hashed_password = generate_password_hash('admin')
       admin = User(username='admin',password=hashed_password,role='Admin',email='Admin123@gmail.com',is_admin=True)
       db.session.add(admin)
       db.session.commit()
