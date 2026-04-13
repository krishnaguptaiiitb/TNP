from flask import Blueprint, request, jsonify, current_app, g
from flask_cors import CORS
from database.build import YearPlacement, create_year_placement_class, Base, Placements, unmap_dynamic_class, Companies, Students
from datetime import date, datetime, time, timezone
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, IntegrityError, OperationalError
from sqlalchemy import inspect, select
from database.utils import pattern_regex, evaluate_expression
import sqlalchemy as sa
from sqlalchemy import and_ , or_
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy import and_, update, func
placements_bp = Blueprint('placements', __name__, url_prefix='/placements')

@placements_bp.route('/', methods=['GET'])
def get_placements():
    placements = [
        {"session_id": 1, "session_date": "2023-01-15", "table_name": "placements_2023"},
        {"session_id": 2, "session_date": "2023-06-20", "table_name": "placements_2023_midyear"},
    ]
    return jsonify(placements)


@placements_bp.route('/create/<table_name>', methods=['POST'])
def create_placement_table(table_name: str):
    """
    Dynamically creates a new placement table, records the creation in Placements, 
    and NEVER drops the physical table if a subsequent error occurs.
    """
    
    # 1. Check for session/engine
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    
    table_class = None
    
    # === PRE-CHECK: DOES THE PHYSICAL TABLE ALREADY EXIST? ===
    # Using reflection (inspector) to check existence before mapping/creation.
    inspector = inspect(session_engine.bind)
    if table_name in inspector.get_table_names():
        return jsonify({
            "error": f"Table '{table_name}' already exists in the database. Creation aborted."
        }), 409 # 409 Conflict, since resource already exists
        
    # 2. Attempt to map the DYNAMIC CLASS and create the TABLE
    try:
        # Get the ORM class for the dynamic table
        table_class = create_year_placement_class(table_name)
        dynamic_table = table_class.__table__ 
        
        # Create the specific table using its __table__ object
        # create_all uses CHECK FIRST, so this won't fail if the table exists
        # unless it exists with a different schema (which is handled by SQLAlchemyError)
        Base.metadata.create_all(session_engine.bind, tables=[dynamic_table])
        print(f"DEBUG: Table '{table_name}' created.")

    except (SQLAlchemyError, InvalidRequestError, OperationalError) as e:
        # This catches errors like invalid SQL, connection issues, or schema mismatches
        # Cleanup the ORM mapping if table creation fails
        if table_class:
            try:
                unmap_dynamic_class(table_class, Base)
            except Exception:
                pass
        
        return jsonify({"error": f"Failed to create table '{table_name}' in DB: {str(e)}"}), 500
    
    # 3. Attempt to add CONTROL ENTRY (Placements)
    try:
        plaement_entry = Placements(
            session_date=datetime.now(timezone.utc).date(),
            table_name=table_name
        )
        session_engine.add(plaement_entry)

        # 4. Attempt to COMMIT the transaction
        session_engine.commit()
        print(f"DEBUG: Control entry added and transaction committed.")

        # FINAL CLEANUP (Success Path):
        unmap_dynamic_class(table_class, Base)
        return jsonify({"message": f"Placement table '{table_name}' created successfully."}), 201

    except SQLAlchemyError as e:
        # A commit failure means the CONTROL ENTRY failed.
        session_engine.rollback()
        
        # CRITICAL CHANGE: The physical table creation succeeded (Step 2), 
        # but the control entry failed (Step 3). We now have an **ORPHANED PHYSICAL TABLE**.
        # The physical table is LEFT ALONE, as requested.
        
        print(f"WARNING: Orphaned physical table '{table_name}' created but not logged due to commit failure.")
        
        # Clean up the in-memory ORM mapping (always required on failure/success)
        try:
            unmap_dynamic_class(table_class, Base)
        except Exception:
            pass
            
        # Determine error code
        http_code = 500
        if isinstance(e, IntegrityError):
            http_code = 409 # Conflict, e.g., table_name already logged by another process
            
        return jsonify({
            "error": f"Control entry failed. Physical table '{table_name}' was created but not logged. Error: {str(e)}"
        }), http_code

    finally:
        if 'table_class' in locals() and table_class is not None:
            del table_class




@placements_bp.route('/sessions', methods=['GET'])
def get_all_sessions():
    """
    Fetches all placement sessions from the Placements control table.
    """
    
    # 1. Check for session/engine
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    
    try:
        # 2. Query all placement sessions
        sessions = session_engine.scalars(select(Placements)).all()
        
        # 3. Serialize to list of dicts
        result = []
        for session in sessions:
            result.append({
                "session_id": session.session_id,
                "session_date": session.session_date.isoformat() if session.session_date else None,
                "table_name": session.table_name
            })
        
        return jsonify({"message": "ok", "data": result, "length": len(result)}), 200

    except SQLAlchemyError as e:
        return jsonify({"error": f"Failed to fetch placement sessions: {str(e)}"}), 500





@placements_bp.route('/sessions/entry/<table_name>', methods=['GET'])
def get_placement_data(table_name: str):
    """
    Fetches all placement records from the specified dynamic placement table.
    """

    s_entry_id = request.args.get('entry_id', None)
    s_scholar_no = request.args.get('scholar_no', None)
    s_status = request.args.get('status', None)
    s_company_id = request.args.get('company_id', None)

    
    # 1. Check for session/engine (Keep outside the try)
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    
    # === PRE-CHECK: DOES THE PHYSICAL TABLE EXIST? === (Keep outside the try)
    inspector = inspect(session_engine.bind)
    if table_name not in inspector.get_table_names():
        return jsonify({
            "error": f"Table '{table_name}' does not exist in the database."
        }), 404 # Not Found
    
    # Initialize outside the try block for access in finally
    table_class = None 
    page_no = request.args.get('page', default=1, type=int)
    page_size = request.args.get('size', default=50, type=int)
    offset = (page_no - 1) * page_size
    
    try:
        # 2. Map the dynamic class
        # This is where the class object (table_class) is created and mapped.
        where_conditions = and_(
                table_class.scholar_no.like(f"%{s_scholar_no}%") if s_scholar_no else True,
                table_class.company_id == s_company_id if s_company_id else True,
                table_class.status == s_status if s_status else True,
                table_class.entry_id == s_entry_id if s_entry_id else True
            )
        table_class = create_year_placement_class(table_name)
        count_query = select(func.count()).select_from(Companies).where(where_conditions)
        statement = select(table_class).where(where_conditions).offset(offset).limit(page_size)
        # 3. Query all records
        # Use session.scalars(select(table_class)).all() for SQLAlchemy 2.0 style
        total_counts = session_engine.execute(count_query).scalar_one()
        records = session_engine.scalars(statement).all()
        
        # 4. Serialize records to list of dicts
        result = []
        # Optimization: use table_class.__table__.columns once outside the loop
        columns = table_class.__table__.columns 
        for record in records:
            data = {
                'entry_id' : int(record.entry_id),
                'scholar_no' : record.scholar_no,
                'status' : record.status.value if record.status else None,
                'package' : float(record.package) if record.package is not None else None,
                'offer_date' : datetime.strftime(record.offer_date, '%Y-%m-%d'),
                'company_id' : int(record.company_id)
            }
            result.append(data)
        return jsonify({"message":"ok" , "data": result, "length": len(result), "page": page_no, "total": total_counts, "page_size" : page_size}), 200

    except (SQLAlchemyError, InvalidRequestError) as e:
        # Catch and handle errors during class mapping or querying
        return jsonify({"error": f"Failed to fetch data from '{table_name}': {str(e)}"}), 500

    finally:
        # 5. Guaranteed cleanup of the dynamic class map
        # This runs on success (after return) and on exception (after except)
        if table_class:
            try:
                # Use the robust unmapping function
                unmap_dynamic_class(table_class, Base)
                # It is good practice to explicitly delete the reference too
                del table_class 
            except Exception as cleanup_e:
                print(f"WARNING: Failed to clean up dynamic ORM mapping: {cleanup_e}")




@placements_bp.route("/sessions/entry/<string:table_name>/", methods=['POST'])
def post_data(table_name):
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    inspector = inspect(session_engine.bind)
    if table_name not in inspector.get_table_names():
        return jsonify(
            {
                "error" : f"Table {table_name} does not exists"
            }
        ), 404
    
    table_class = None
    try:
        table_class = create_year_placement_class(table_name)

        data = request.get_json()

        last_status, last_message = "Start", True
        last_status, last_message, scholar_no = evaluate_expression('scholar_no', last_status, last_message, data.get('scholar_no', None), pattern_regex['scholar_no'])
        last_status, last_message, company_id = evaluate_expression('company_id', last_status, last_message, data.get('company_id', None), pattern_regex['company_id'])
        last_status, last_message, package = evaluate_expression('package', last_status, last_message, data.get('package', None), pattern_regex['package'])
        last_status, last_message, status = evaluate_expression('status', last_status, last_message, data.get('status', None), pattern_regex['placement_status'])
        last_status, last_message, offer_date = evaluate_expression('offer_date', last_status, last_message, data.get('offer_date', None), pattern_regex['offer_date'])

        print(f"DEBUG: Validation results - status: {last_status}, message: {last_message}")
        print(scholar_no, company_id, package, status, offer_date)
        if last_status is False:
            return jsonify({"error" : last_message}), 400
        
        student = session_engine.get(Students, scholar_no)
        if not student:
            return jsonify({"error": f"Student with scholar_no '{scholar_no}' does not exist."}), 404
        
        company = session_engine.get(Companies, int(company_id))
        if not company:
            return jsonify({"error": f"Company with company_id '{company_id}' does not exist."}), 404
        
        print(company.job_type, student.placement_active)
        if (company.status != Companies.StatusEnum.PENDING):
            return jsonify({'error' : 'can\'t apply in company {company.company_name} with status {company.status}'})
        
        if (
            (
                company.job_type == Companies.JobTypeEnum.INTERNSHIP or 
                company.job_type == Companies.JobTypeEnum.BOTH
            ) and
            student.internship_active != Students.InternshipEnum.ACTIVE
        ) or (
            (
                company.job_type == Companies.JobTypeEnum.FULL_TIME or
                company.job_type == Companies.JobTypeEnum.BOTH
            ) and
            student.placement_active != Students.PlacementEnum.ACTIVE
        ) :
            return jsonify({"error": f"Student with scholar_no '{scholar_no}' is not active for the job type '{company.job_type.value}'."}), 400

       
        existing_entry = session_engine.scalars(
            select(table_class).where(
                and_(
                    table_class.scholar_no == scholar_no,
                    table_class.company_id == int(company_id)
                )
            )
        ).first()

        if existing_entry:
            return jsonify({"error": f"Student already applied for this {company.job_type.name.lower()} job."}), 409
        
        new_entry = table_class(
            scholar_no = scholar_no,
            company_id = int(company_id),
            package = float(package) if package is not None else None,
            status = status,
            offer_date = datetime.strptime(offer_date, '%Y-%m-%d').date()
        )


        session_engine.add(new_entry)
        session_engine.commit()

        return jsonify({"message":"ok"})
    
    except IntegrityError as ie:
        return jsonify({"error" : f"Error while commiting entries {str(ie)} in table {table_name}"})

    finally:
        if table_class:
            try:
                unmap_dynamic_class(table_class, Base)
                del table_class
            except Exception as cleanup_e:
                print(f"WARNING: Failed to clean up dynamic ORM mapping: {cleanup_e}")


@placements_bp.route("/sessions/entry/<string:table_name>/<entry_id>", methods=['PUT'])
def update_data(table_name, entry_id):
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    inspector = inspect(session_engine.bind)
    if table_name not in inspector.get_table_names():
        return jsonify(
            {
                "error" : f"Table {table_name} does not exists"
            }
        ), 404
    
    table_class = None
    try:
        table_class = create_year_placement_class(table_name)

        data = request.get_json()
        print(data)
        last_status, last_message = "Start", True
        last_status, last_message, package = evaluate_expression('package', last_status, last_message, data.get('package', None), pattern_regex['package'])
        last_status, last_message, status = evaluate_expression('status', last_status, last_message, data.get('status', None), pattern_regex['placement_status'])
        last_status, last_message, offer_date = evaluate_expression('offer_date', last_status, last_message, data.get('offer_date', None), pattern_regex['offer_date'])

        print(f"DEBUG: Validation results - status: {last_status}, message: {last_message}")
        print(package, status, offer_date)
        if last_status is False:
            return jsonify({"error" : last_message}), 400
        
       
        existing_entry = session_engine.get(table_class, entry_id)

        
        
        existing_entry.package = float(package) if package is not None else None
        existing_entry.status = status
        existing_entry.offer_date = datetime.strptime(offer_date, '%Y-%m-%d').date()

        session_engine.commit()
        data = data = {
                'entry_id' : int(existing_entry.entry_id),
                'scholar_no' : existing_entry.scholar_no,
                'status' : existing_entry.status.value if existing_entry.status else None,
                'package' : float(existing_entry.package) if existing_entry.package is not None else None,
                'offer_date' : datetime.strftime(existing_entry.offer_date, '%Y-%m-%d'),
                'company_id' : int(existing_entry.company_id)
            }
        student = session_engine.get(Students, existing_entry.scholar_no)
        company = session_engine.get(Companies, int(existing_entry.company_id))
        if (company.job_type == company.JobTypeEnum.INTERNSHIP):
            student.internship_active = Students.InternshipEnum.INACTIVE if existing_entry.status == YearPlacement.PlacementStatus.SELECTED else Students.InternshipEnum.ACTIVE
        if (company.job_type == company.JobTypeEnum.FULL_TIME):
            student.placement_active = Students.PlacementEnum.INACTIVE if existing_entry.status == YearPlacement.PlacementStatus.SELECTED else Students.PlacementEnum.ACTIVE
        session_engine.commit()

        return jsonify(
            {
                "message" : "ok",
                "data" : data
            }
        )
    
    except IntegrityError as ie:
        return jsonify({"error" : f"Error while commiting entries {str(ie)} in table {table_name}"})

    finally:
        if table_class:
            try:
                unmap_dynamic_class(table_class, Base)
                del table_class
            except Exception as cleanup_e:
                print(f"WARNING: Failed to clean up dynamic ORM mapping: {cleanup_e}")







@placements_bp.route('/companies/list', methods=['GET'])
def get_companies():
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    try:
        page_no = request.args.get('page', default=1, type=int)
        page_size = request.args.get('size', default=50, type=int)
        offset = (page_no - 1) * page_size

        s_company_id = request.args.get("company_id", None)
        s_company_name = request.args.get("company_name", None)
        s_posts = request.args.get("posts", None)
        s_job_type = request.args.get("job_type", None)
        s_ctc_min = request.args.get("ctc_min", None)
        s_ctc_max = request.args.get("ctc_max", None)
        s_location = request.args.get("location", None)
        s_status = request.args.get("status", None)
        s_visit_date = request.args.get("visit_date", None)
        query = request.args.get("query", None)



        where_conditions = (
            and_(
                or_(
                    Companies.company_id.like(f'%{query}%'),
                    Companies.company_name.like(f'%{query}%'),
                    Companies.posts.like(f'%{query}%'),
                    Companies.job_type.like(f'%{query}%'),
                    Companies.location.like(f'%{query}%'),
                    Companies.status.like(f'%{query}%'),
                ) if query else True,
                Companies.company_id == s_company_id if s_company_id else True,
                Companies.company_name.like(f"%{s_company_name}%") if s_company_name else True,
                Companies.posts.like(f"%{s_posts}%") if s_posts else True,
                Companies.job_type.value == s_job_type if s_job_type else True,
                Companies.ctc_min >= float(s_ctc_min) if s_ctc_min else True,
                Companies.ctc_max <= float(s_ctc_max) if s_ctc_max else True,
                Companies.location == s_location if s_location else True,
                Companies.status == s_status if s_status else True,
                Companies.visit_date == datetime.strptime(s_visit_date, '%Y-%m-%d').date() if s_visit_date else True
            )
        )
        count_query = select(func.count()).select_from(Companies).where(where_conditions)
        query = select(Companies).where(where_conditions).offset(offset).limit(page_size)
        total_counts = session_engine.execute(count_query).scalar_one()
        companies = session_engine.scalars(query).all()
        companies_list = []
        for company in companies:
            companies_list.append({
                "company_id": company.company_id,
                "company_name": company.company_name,
                "posts": company.posts,
                "job_type": company.job_type.value if company.job_type else None,
                "ctc_min": company.ctc_min,
                "ctc_max": company.ctc_max,
                "applied_students": company.applied_students,
                "selected_students": company.selected_students,
                "visit_date": company.visit_date.isoformat() if company.visit_date else None,
                "location": company.location.value if company.location else None,
                "status": company.status.value if company.status else None
            })

        return jsonify({"message": "ok", "data": companies_list, "length": len(companies_list), "page": page_no, "total" : total_counts, "page_size" : page_size}), 200
        
    except SQLAlchemyError as e:
        return jsonify({"error": f"Failed to fetch companies: {str(e)}"}), 500
    




@placements_bp.route('/companies/', methods=['POST'])
def add_company():
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    try:
        data = request.get_json()
        print(data.get('status'))
        last_status, last_message = "Start", True
        last_status, last_message, company_name = evaluate_expression('company_name', last_status, last_message, data.get('company_name', None), pattern_regex['company_name'])
        last_status, last_message, posts = evaluate_expression('posts', last_status, last_message, data.get('posts', None), pattern_regex['posts'])
        last_status, last_message, job_type = evaluate_expression('job_type', last_status, last_message, data.get('job_type', None), pattern_regex['job_type'])
        last_status, last_message, ctc_min = evaluate_expression('ctc_min', last_status, last_message, str(data.get('ctc_min', None)), pattern_regex['ctc_min'])
        last_status, last_message, ctc_max = evaluate_expression('ctc_max', last_status, last_message, str(data.get('ctc_max', None)), pattern_regex['ctc_max'])
        last_status, last_message, applied_students = evaluate_expression('applied_students', last_status, last_message, str(data.get('applied_students', None)), pattern_regex['applied_students'])
        last_status, last_message, selected_students = evaluate_expression('selected_students', last_status, last_message, str(data.get('selected_students', None)), pattern_regex['selected_students'])
        last_status, last_message, visit_date = evaluate_expression('visit_date', last_status, last_message, data.get('visit_date', None), pattern_regex['visit_date'])
        last_status, last_message, location = evaluate_expression('location', last_status, last_message, data.get('location', None), pattern_regex['location'])
        last_status, last_message, status = evaluate_expression('status', last_status, last_message, data.get('status', None), pattern_regex['status'])

        print(f"DEBUG: Validation results - status: {last_status}, message: {last_message}")
        print(company_name, posts, job_type, ctc_min, ctc_max, applied_students,
              selected_students, visit_date, location, status)
        if last_status is False:
            return jsonify({"error" : last_message}), 400
        
        new_company = Companies(
            company_name = company_name,
            posts = posts,
            job_type = job_type,
            ctc_min = float(ctc_min) if ctc_min is not None else None,
            ctc_max = float(ctc_max) if ctc_max is not None else None,
            applied_students = int(applied_students),
            selected_students = int(selected_students),
            visit_date = datetime.strptime(visit_date, '%Y-%m-%d').date(),
            location = location,
            status = status
        )

        query = select(Companies).where(
            and_(
                Companies.company_name == company_name,
                Companies.visit_date == datetime.strptime(visit_date, '%Y-%m-%d').date(),
                Companies.location == location,
                Companies.posts == posts)
        )

        existing_company = session_engine.scalars(query).first()
        if existing_company:
            return jsonify({"error": "Company with the same name, visit date, location, and posts already exists."}), 409

        session_engine.add(new_company)
        session_engine.commit()
        return jsonify({"message":"ok", "data": {"company_id": new_company.company_id}}), 201
    except IntegrityError as ie:
        session_engine.rollback()
        return jsonify({"error" : f"Error while commiting entries {str(ie)} in Companies table"}), 400
    except SQLAlchemyError as e:
        session_engine.rollback()
        return jsonify({"error": f"Failed to add company: {str(e)}"}), 500
    except Exception as ex:
        session_engine.rollback()
        return jsonify({"error": f"Unexpected error: {str(ex)}"}), 500
    finally:
        pass

@placements_bp.route('/companies/<company_id>', methods=['PUT'])
def update_company(company_id):
    session_engine = getattr(g, 'db', None)
    if session_engine is None or session_engine.bind is None:
        return jsonify({"error": "Database session or engine not found"}), 500
    try:
        data = request.get_json()
        last_status, last_message = "Start", True
        last_status, last_message, company_name = evaluate_expression('company_name', last_status, last_message, data.get('company_name', None), pattern_regex['company_name'])
        last_status, last_message, posts = evaluate_expression('posts', last_status, last_message, data.get('posts', None), pattern_regex['posts'])
        last_status, last_message, job_type = evaluate_expression('job_type', last_status, last_message, data.get('job_type', None), pattern_regex['job_type'])
        last_status, last_message, ctc_min = evaluate_expression('ctc_min', last_status, last_message, str(data.get('ctc_min', None)), pattern_regex['ctc_min'])
        last_status, last_message, ctc_max = evaluate_expression('ctc_max', last_status, last_message, str(data.get('ctc_max', None)), pattern_regex['ctc_max'])
        last_status, last_message, visit_date = evaluate_expression('visit_date', last_status, last_message, data.get('visit_date', None), pattern_regex['visit_date'])
        last_status, last_message, location = evaluate_expression('location', last_status, last_message, data.get('location', None), pattern_regex['location'])
        last_status, last_message, status = evaluate_expression('status', last_status, last_message, data.get('status', None), pattern_regex['status'])

        if last_status is False:
            return jsonify({"error" : last_message}), 400
        

        existing_company = session_engine.get(Companies, company_id)
        if not existing_company:
            return jsonify({"error": f"Company not found with id {company_id}."}), 409
        

        existing_company.status = status
        existing_company.ctc_min = float(ctc_min) if ctc_min else 0.0
        existing_company.ctc_max = float(ctc_max) if ctc_max else 0.0
        existing_company.location = location
        existing_company.company_name = company_name
        existing_company.posts = posts
        existing_company.job_type = job_type
        existing_company.visit_date = datetime.strptime(visit_date, "%Y-%m-%d")

        session_engine.commit()

        json_data = existing_company.to_json()

        return jsonify({"message":"ok", "data": json_data}), 201
    except IntegrityError as ie:
        session_engine.rollback()
        return jsonify({"error" : f"Error while commiting entries {str(ie)} in Companies table"}), 400
    except SQLAlchemyError as e:
        session_engine.rollback()
        return jsonify({"error": f"Failed to add company: {str(e)}"}), 500
    except Exception as ex:
        session_engine.rollback()
        return jsonify({"error": f"Unexpected error: {str(ex)}"}), 500
    finally:
        pass

def update_placement_count(session, instance):
    company_id = instance.company_id

# Count all applied students for this company
    applied_count = (
        session.query(instance.__class__)
        .filter(instance.__class__.company_id == company_id)
        .count()
    )

    # Count all selected students for this company
    selected_count = (
        session.query(instance.__class__)
        .filter(
            and_(
                instance.__class__.company_id == company_id,
                instance.__class__.status == instance.PlacementStatus.SELECTED
            )
        )
        .count()
    )

    # Update the Companies table with the new counts
    session.query(Companies).filter(Companies.company_id == company_id).update(
        {
            Companies.applied_students: applied_count,
            Companies.selected_students: selected_count,
        },
        synchronize_session=False,   # avoids stale data in session
    )


@event.listens_for(Session, "after_flush")
def after_flush(session, flush_context):
    for instance in session.new:
        if isinstance(instance, YearPlacement):
            update_placement_count(session, instance)
            print(f"DEBUG: New YearPlacement entry added: {instance}")
    for instance in session.dirty:
        if isinstance(instance, YearPlacement):
            update_placement_count(session, instance)
            print(f"DEBUG: YearPlacement entry updated: {instance}")

