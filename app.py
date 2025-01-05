from flask import Flask,render_template
 

app = Flask(__name__)

from dotenv import load_dotenv
import os
from app import app 



load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
 
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads/documents')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import models

import controllers


if __name__ == '__main__':
    app.run(debug=True)