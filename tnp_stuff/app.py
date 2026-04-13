from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlalchemy as sa
import os
from sqlalchemy.orm import sessionmaker, scoped_session
from students.routes import students_bp
from placements.routes import placements_bp

UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = sa.create_engine("mysql+mysqldb://krishnagupta:godkrishna@localhost:3306/sonal_db", echo=True)
SessionLocal = sessionmaker(bind=engine)
CORS(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.before_request
def before_request():
    g.db = SessionLocal()

@app.teardown_request
def teardown_request(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()



app.register_blueprint(placements_bp, url_prefix='/api/placements')
app.register_blueprint(students_bp, url_prefix='/api/students')

if __name__ == '__main__':
    app.run(debug=True)
