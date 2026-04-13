from flask import Blueprint, request, jsonify, g, send_file
from flask_cors import CORS
from sqlalchemy import text, select, update, extract, and_, or_, func
from sqlalchemy.exc import IntegrityError
import re
from database.build import Students
from datetime import datetime
from database.utils import pattern_regex, evaluate_expression
import pandas as pd
import io

def convert_to_user(row):
    return Students(
        scholar_no=row['scholar_no'],
        name=row['name'],
        graduation_year=to_year(row['graduation_year']),
        mail_id=row['mail_id'],
        phone_no=row['phone_no'],
        branch_id=row['branch_id'],
        program=row['program'],
        placement_active=row['placement_active'].upper(),
        internship_active=row['internship_active'].upper()
    )




to_year = lambda x: datetime(year=int(x), month=6, day=1).date()
students_bp = Blueprint('students', __name__, url_prefix='/students')


@students_bp.route('/register', methods=['POST'])
def register_student():


    session_engine = getattr(g, 'db', None)
    
    if(session_engine is None):
        return jsonify({"error": "Database session not found"}), 500
    
    
    req_type = request.args.get('type', 'entry').lower()
    
    if (req_type == 'upload'):
        file = request.files.get('file', None)
        if file is None:
            return jsonify({"error": "File not found"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Invalid file format, only CSV allowed"}), 400
        
        try:
            df = pd.read_csv(file)
            users = df.apply(convert_to_user, axis=1).to_list()
            session_engine.add_all(users)
            session_engine.commit()

            return jsonify({"message": "ok", "data": {"length": len(users)}}), 201
    
        except Exception as e:
            return jsonify({"error": f"Error reading CSV file: {str(e)}"}), 400

    body = request.get_json()
    if body is None:
        return jsonify({"error": "Invalid JSON body"}), 400
    

    last_status, last_message = True, "Valid Input"
    last_status, last_message, scholar_no = evaluate_expression('scholar_no', last_status, last_message, body.get('scholar_no', None), pattern_regex['scholar_no'])
    last_status, last_message, name = evaluate_expression('name', last_status, last_message, body.get('name', None), pattern_regex['name'])
    last_status, last_message, graduation_year = evaluate_expression('graduation_year', last_status, last_message, body.get('graduation_year', None), pattern_regex['graduation_year'])
    last_status, last_message, mail_id = evaluate_expression('mail_id', last_status, last_message, body.get('mail_id', None), pattern_regex['mail_id'])
    last_status, last_message, phone_no = evaluate_expression('phone_no', last_status, last_message, body.get('phone_no', None), pattern_regex['phone_no'])
    last_status, last_message, branch_id = evaluate_expression('branch_id', last_status, last_message, body.get('branch_id', None), pattern_regex['branch_id'])
    last_status, last_message, program = evaluate_expression('program', last_status, last_message, body.get('program', None), pattern_regex['program'])
    last_status, last_message, placement_active = evaluate_expression('active_status', last_status, last_message, body.get('placement_active', None), pattern_regex['placement_active'])
    last_status, last_message, internship_active = evaluate_expression('internship_status', last_status, last_message, body.get('internship_active', None), pattern_regex['internship_active'])

    if last_status is False:
        return jsonify({"error": last_message}), 400
    
    # Insert into database
    try:
        student = Students(
            scholar_no=scholar_no,
            name=name,
            graduation_year=to_year(graduation_year),
            mail_id=mail_id,
            phone_no=phone_no,
            branch_id=branch_id,
            program=program,
            placement_active=placement_active.upper(),
            internship_active=internship_active.upper()
        )
        session_engine.add(student)
        session_engine.commit()
    except Exception as e:
        session_engine.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "ok", "data": {
        "scholar_no": scholar_no,}}), 201

@students_bp.route('/list', methods=['GET'])
def get_student():

    session_engine = getattr(g, 'db', None)
    if(session_engine is None):
        return jsonify({"error": "Database session not found"}), 500

    scholar_no = request.args.get('scholar_no', None)
    name = request.args.get('name', None)
    graduation_year = request.args.get('graduation_year', None)
    program = request.args.get('program', None)
    branch_id = request.args.get('branch_id', None)
    placement_active = request.args.get('placement_active', '').upper()
    internship_active = request.args.get('internship_active', '').upper()
    page_size = request.args.get('length', 10)
    page_no = request.args.get('page', 1)

    offset_ = (int(page_no) - 1) * int(page_size)

    conditions = and_(
            Students.scholar_no.like(f"%{scholar_no}%") if scholar_no else True,
            Students.name.like(f"%{name}%") if name else True,
            extract('year', Students.graduation_year)==graduation_year if graduation_year and graduation_year.isdigit() else True,
            Students.program==program if program else True,
            Students.branch_id==branch_id if branch_id else True,
            Students.placement_active==placement_active.upper() if placement_active.upper() in ['ACTIVE', 'INACTIVE'] else True,
            Students.internship_active==internship_active.upper() if internship_active.upper() in ['ACTIVE', 'INACTIVE'] else True
        )

    count_query = select(func.count()).select_from(Students).where(conditions)
    statement = select(Students).where(conditions).offset(offset_).limit(int(page_size))
    entries = session_engine.scalars(statement).all()
    total_count = session_engine.execute(count_query).scalar_one()

    students_list = []
    for student in entries:
        students_list.append({
            "scholar_no": student.scholar_no,
            "name": student.name,
            "graduation_year": student.graduation_year.isoformat(),
            "mail_id": student.mail_id,
            "phone_no": student.phone_no,
            "branch_id": student.branch_id,
            "program": student.program,
            "placement_active": student.placement_active.value,
            "internship_active": student.internship_active.value
        })
    if(request.args.get('download', 'false').lower() == 'true'):
        csv_buffer = io.BytesIO()
        pd.DataFrame(students_list).to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)

        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name='students_list.csv'
        )
    return jsonify({"message": "ok", 'length' : len(students_list) ,'page' : int(page_no) , "data": students_list, "page_size": int(page_size), "total": int(total_count)}), 200

@students_bp.route('/update/<scholar_no>', methods=['PUT'])
def update_student(scholar_no):
    session_engine = getattr(g, 'db', None)
    if(session_engine is None):
        return jsonify({"error": "Database session not found"}), 500

    body = request.get_json()
    if body is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    last_status, last_message = True, "Valid Input"
    last_status, last_message, name = evaluate_expression('name', last_status, last_message, body.get('name', None), pattern_regex['name'])
    last_status, last_message, graduation_year = evaluate_expression('graduation_year', last_status, last_message, body.get('graduation_year', None), pattern_regex['graduation_year'])
    last_status, last_message, mail_id = evaluate_expression('mail_id', last_status, last_message, body.get('mail_id', None), pattern_regex['mail_id'])
    last_status, last_message, phone_no = evaluate_expression('phone_no', last_status, last_message, body.get('phone_no', None), pattern_regex['phone_no'])
    last_status, last_message, branch_id = evaluate_expression('branch_id', last_status, last_message, body.get('branch_id', None), pattern_regex['branch_id'])
    last_status, last_message, program = evaluate_expression('program', last_status, last_message, body.get('program', None), pattern_regex['program'])
    last_status, last_message, placement_active = evaluate_expression('active_status', last_status, last_message, body.get('placement_active', None), pattern_regex['placement_active'])
    last_status, last_message, internship_active = evaluate_expression('internship_status', last_status, last_message, body.get('internship_active', None), pattern_regex['internship_active'])

    if last_status is False:
        return jsonify({"error": last_message}), 400

    try:
        statement = update(Students).where(Students.scholar_no == scholar_no).values(
            name=name,
            graduation_year=to_year(graduation_year),
            mail_id=mail_id,
            phone_no=phone_no,
            branch_id=branch_id,
            program=program,
            placement_active=placement_active.upper(),
            internship_active=internship_active.upper()
        )
        result = session_engine.execute(statement)
        if result.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        session_engine.commit()
    except Exception as e:
        session_engine.rollback()
        return jsonify({"error": str(e)}), 500
    
    record_statment = select(Students).where(Students.scholar_no == scholar_no)
    student = session_engine.scalars(record_statment).first()
    if student is None:
        return jsonify({"error": "Student not found after update"}), 404
    updated_student = {
        "scholar_no": student.scholar_no,
        "name": student.name,
        "graduation_year": student.graduation_year.year,
        "mail_id": student.mail_id,
        "phone_no": student.phone_no,
        "branch_id": student.branch_id,
        "program": student.program,
        "placement_active": student.placement_active.value,
        "internship_active": student.internship_active.value
    }
    return jsonify({"message": "ok", "data": updated_student}), 200

@students_bp.route("/", methods=['GET'])
def get_students():
    session_engine = getattr(g, 'db', None)
    if(session_engine is None):
        return jsonify({"error": "Database session not found"}), 500
    
    result = session_engine.execute(text("SHOW TABLES"))
    x_status = [row for row in result.fetchall()]
    print(x_status)

    return jsonify({"message": 'ok'}), 200