import sqlalchemy as sa
import enum
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import instrumentation


Base = declarative_base()
metadata = Base.metadata
t_metadata = sa.MetaData()
print(t_metadata)


class Branches(Base):
    __tablename__ = 'branches'
    branch_id = sa.Column(sa.String(10), primary_key=True)
    branch_name = sa.Column(sa.String(50), nullable=False)
    hod = sa.Column(sa.String(50), nullable=False)


class Students(Base):
    class PlacementEnum(enum.Enum):
        ACTIVE = "Active"
        INACTIVE = "Inactive"
    
    class InternshipEnum(enum.Enum):
        ACTIVE = "Active"
        INACTIVE = "Inactive"

    __tablename__ = 'students'
    scholar_no = sa.Column(sa.String(15), primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    graduation_year = sa.Column(sa.Date, nullable=False)
    mail_id = sa.Column(sa.String(50), nullable=False)
    phone_no = sa.Column(sa.String(15), nullable=False)
    branch_id = sa.Column(sa.String(10), sa.ForeignKey('branches.branch_id'), nullable=False)
    program = sa.Column(sa.String(20), nullable=False)
    placement_active = sa.Column(sa.Enum(PlacementEnum), nullable=False)
    internship_active = sa.Column(sa.Enum(InternshipEnum), nullable=False)

class Companies(Base):
    class JobTypeEnum(enum.Enum):
        FULL_TIME = "Full_Time"
        INTERNSHIP = "Internship"
        BOTH = "Both"
    
    class LocationEnum(enum.Enum):
        ONSITE = "Onsite"
        REMOTE = "Remote"
        HYBRID = "Hybrid"
    
    class StatusEnum(enum.Enum):
        VISITED = "Visited"
        UPCOMING = "Upcoming"
        REJECTED = "Rejected"
        PENDING = "Pending"

    __tablename__ = 'companies'
    company_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    company_name = sa.Column(sa.String(50), nullable=False)
    posts = sa.Column(sa.String(100), nullable=False)
    job_type = sa.Column(sa.Enum(JobTypeEnum), nullable=False)
    ctc_min = sa.Column(sa.Float, nullable=True)
    ctc_max = sa.Column(sa.Float, nullable=True)
    applied_students = sa.Column(sa.Integer, nullable=False)
    selected_students = sa.Column(sa.Integer, nullable=False)
    visit_date = sa.Column(sa.Date, nullable=False)
    location = sa.Column(sa.Enum(LocationEnum), nullable=False)
    status = sa.Column(sa.Enum(StatusEnum), nullable=False)

    def to_json(self):
        self.json_object = {
            "company_id" : int(self.company_id),
            "company_name" : str(self.company_name),
            "posts" : str(self.posts),
            "job_type": str(self.job_type.value),
            "ctc_min": float(self.ctc_min) if self.ctc_min is not None else None,
            "ctc_max": float(self.ctc_max) if self.ctc_max is not None else None,
            "applied_students": int(self.applied_students),
            "selected_students": int(self.selected_students),
            "visit_date": str(self.visit_date),
            "location": str(self.location.value),
            "status": str(self.status.value)
        }

        return self.json_object

class YearPlacement(Base):
    class PlacementStatus(enum.Enum):
        APPLIED = "Applied"
        SELECTED = "Selected"
        REJECTED = "Rejected"

    __abstract__ = True
    entry_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    company_id = sa.Column(sa.Integer, sa.ForeignKey('companies.company_id'))
    scholar_no = sa.Column(sa.String(15), sa.ForeignKey('students.scholar_no'))
    package = sa.Column(sa.Float, nullable=True)
    status = sa.Column(sa.Enum(PlacementStatus), nullable=False)
    offer_date = sa.Column(sa.Date, nullable=False)

def create_year_placement_class(table_name) -> YearPlacement:
    return type(table_name, (YearPlacement,), {'__tablename__': table_name})


def unmap_dynamic_class(orm_class, Base):
    """
    Removes the ORM mapping for a given dynamic class completely.
    This is essential for long-running processes like a Flask server.
    """
    
    table_obj = orm_class.__table__
    
    # 1. Remove the Table object from the MetaData collection
    if table_obj is not None:
        try:
            # Safe removal from MetaData
            Base.metadata.remove(table_obj)
        except Exception:
            pass # Already removed, ignore

# Call this fixed function in the success and failure paths.

class Placed(Base):
    __tablename__ = 'placed'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    scholar_no = sa.Column(sa.String(15), sa.ForeignKey('students.scholar_no'))
    company_name = sa.Column(sa.String(50), nullable=False)
    date_of_placement = sa.Column(sa.Date, nullable=False)
    position = sa.Column(sa.String(100), nullable=False)


class Placements(Base):
    __tablename__ = 'placements'
    session_id = sa.Column(sa.Integer, primary_key=True)
    session_date = sa.Column(sa.Date, nullable=False)
    table_name = sa.Column(sa.String(50), nullable=False, unique=True)






if __name__ == '__main__':
    engine = sa.create_engine(
        "mysql+mysqldb://krishnagupta:godkrishna@localhost:3306/sonal_db",
        echo=True,
    )
    Base.metadata.create_all(engine)
    print("All tables created successfully.")



