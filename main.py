from typing import List
from fastapi import FastAPI, Form, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Float,DATE,or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import date, datetime
import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.middleware.cors import CORSMiddleware

# Database setup
DATABASE_URL = "mysql+pymysql://root:9518@127.0.0.1:3307/gi"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI setup
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origin(s) you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model for the Counselor table
class Counselor(Base):
    __tablename__ = "counselor"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255))
    email = Column(String(length=255), unique=True, index=True)
    password = Column(String(length=255))

    # Relationship with CourseCounselor and BatchCounselor
    courses = relationship("CourseCounselor", back_populates="counselor")
    batches = relationship("BatchCounselor", back_populates="counselor")
    remarks = relationship("StudentRemarks", back_populates="counselor")

# Model for the Course table
class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255))
    fees = Column(Float)
    duration = Column(String(length=255))
    pdf = Column(String(length=255))
    prerequisites_sub = Column(String(length=255))
    sample_project = Column(String(length=255))
    description = Column(String(length=1000))
    other_link = Column(String(length=255))
    objective = Column(String(length=1000))
    note = Column(String(length=1000))
    status = Column(Integer, default=1)

    # Relationship with CourseCounselor
    counselors = relationship("CourseCounselor", back_populates="course")
    batches = relationship("Batch", back_populates="course")
    students = relationship("StudentCourse", back_populates="course")

# Model for the CourseCounselor table
class CourseCounselor(Base):
    __tablename__ = "course_counselor"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"))
    counselor_id = Column(Integer, ForeignKey("counselor.id"))
    type_of_operation = Column(String(length=50))
    time_stamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with Course and Counselor
    course = relationship("Course", back_populates="counselors")
    counselor = relationship("Counselor", back_populates="courses")

# Model for the Batch table
class Batch(Base):
    __tablename__ = "batch"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255))
    course_id = Column(Integer, ForeignKey("course.id"))
    time = Column(String(length=50))
    trainer_name = Column(String(length=255))
    daily_hours = Column(Float)
    weekly_days = Column(String(length=255)) #
    start_date = Column(DATE)
    expected_end_date = Column(DATE)
    status = Column(Integer, default=1)
    time_stamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with BatchCounselor
    counselors = relationship("BatchCounselor", back_populates="batch")
    course = relationship("Course", back_populates="batches")

# Model for the BatchCounselor table
class BatchCounselor(Base):
    __tablename__ = "batch_counselor"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batch.id"))
    counselor_id = Column(Integer, ForeignKey("counselor.id"))
    type_of_operation = Column(String(length=50))
    time_stamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with Batch and Counselor
    batch = relationship("Batch", back_populates="counselors")
    counselor = relationship("Counselor", back_populates="batches")

# Model for the Student table
class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255))
    email = Column(String(length=255), unique=True, index=True)
    contact_1 = Column(String(length=10))
    contact_2 = Column(String(length=10))
    area = Column(String(length=255))
    college_name = Column(String(length=255))
    mode = Column(String(length=50))
    date_of_join = Column(DATE)
    reference = Column(String(length=255))

    # Relationship with StudentRemarks and StudentCourse
    remarks = relationship("StudentRemarks", back_populates="student")
    courses = relationship("StudentCourse", back_populates="student")

# Model for the StudentRemarks table
class StudentRemarks(Base):
    __tablename__ = "student_remarks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    counselor_id = Column(Integer, ForeignKey("counselor.id"))
    remark = Column(String(length=1000))
    status = Column(Integer, default=1)
    time_stamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with Student and Counselor
    student = relationship("Student", back_populates="remarks")
    counselor = relationship("Counselor", back_populates="remarks")

# Model for the StudentCourse table
class StudentCourse(Base):
    __tablename__ = "student_course"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    course_id = Column(Integer, ForeignKey("course.id"))
    fees = Column(Float)
    time_stamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with Student and Course
    student = relationship("Student", back_populates="courses")
    course = relationship("Course", back_populates="students")
    
class StudentRequest(BaseModel):
    name: str
    email: str
    contact_1: str
    contact_2: str
    area: str
    college_name: str
    mode: str
    date_of_join: date
    reference: str
    counselor_id: int
    course_ids: List[int]
    fees_list: List[float]
    pdf_list: List[str]
    remark: str

# Create the tables
Base.metadata.create_all(bind=engine)

# Email configuration
class Envs:
    MAIL_USERNAME = 'infotechg87@gmail.com'
    MAIL_PASSWORD = 'ouct ffmr lyoj kmaf'
    MAIL_FROM = 'infotechg87@gmail.com'
    MAIL_PORT = '587'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_FROM_NAME = 'Course Pdf'

template_folder_path = os.path.abspath('./templates')

conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=template_folder_path
)

# Send email function
async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')

# Background task to send email
def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
    message_body = f"{body['title']}\n\nname: {body['name']}\nPdf Link: {body['pdf_link']}"

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=message_body,
        subtype='plain',  # Change subtype to 'plain' for a simple text email
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=None)


# Email format validation
def is_valid_email(email: str):
    return "@" in email
    
@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Counselor).filter(Counselor.email == email, Counselor.password == password).first()
    if user:
        counselor_id = user.id
        # return {"message": "Login successful"}
        raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": status.HTTP_200_OK,"message": "Login Successfully", "counselor_id": counselor_id}
    )
    else:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"status": status.HTTP_401_UNAUTHORIZED,"message": "Invalid credentials"}
        )
    
@app.post("/add_course")
def add_course(
    counselor_id: int = Form(...),
    # type_of_operation: str = Form(...),
    name: str = Form(...),
    fees: float = Form(...),
    duration: str = Form(...),
    pdf: str = Form(...),
    prerequisites_sub: str = Form(...),
    sample_project: str = Form(...),
    description: str = Form(...),
    other_link: str = Form(...),
    objective: str = Form(...),
    note: str = Form(...),
    db: Session = Depends(get_db)
):
    # Get counselor name based on counselor_id
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")

    counselor_name = counselor.name  # Assuming counselor has a 'name' attribute

    # Create a new course
    new_course = Course(
        name=name,
        fees=fees,
        duration=duration,
        pdf=pdf,
        prerequisites_sub=prerequisites_sub,
        sample_project=sample_project,
        description=description,
        other_link=other_link,
        objective=objective,
        note=note
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # Add the course_counselor entry
    new_course_counselor = CourseCounselor(
        course_id=new_course.id,
        counselor_id=counselor_id,
        # type_of_operation=type_of_operation,
        type_of_operation=counselor_name + " " + "Add Course",
        time_stamp=datetime.utcnow()
    )

    db.add(new_course_counselor)
    db.commit()

    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": status.HTTP_200_OK,"message": "Course added successfully"}
    )
        
@app.get("/get_all_courses")
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return {"courses": courses}

@app.get("/get_course/{course_id}")
def get_course(course_id: int , db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Course not found"}
        )

    # Fetch associated data or relationships if needed
    # counselors = [counselor.name for counselor in course.counselors]
    # batches = [batch.name for batch in course.batches]
    # students = [student.name for student in course.students]

    course_data = {
        "course_id": course.id,
        "course_name": course.name,
        "fees": course.fees,
        "duration": course.duration,
        "pdf": course.pdf,
        "prerequisites_sub": course.prerequisites_sub,
        "sample_project": course.sample_project,
        "description": course.description,
        "other_link": course.other_link,
        "objective": course.objective,
        "note": course.note,
        "status": course.status,
        # "counselors": counselors,
        # "batches": batches,
        # "students": students
        # Include other fields or relationships as needed
    }

    return course_data

@app.put("/update_course/{course_id}")
def update_course(
    course_id: int,
    counselor_id: int = Form(...),
    # type_of_operation: str = Form(...),
    name: str = Form(...),
    fees: float = Form(...),
    duration: str = Form(...),
    pdf: str = Form(...),
    prerequisites_sub: str = Form(...),
    sample_project: str = Form(...),
    description: str = Form(...),
    other_link: str = Form(...),
    objective: str = Form(...),
    note: str = Form(...),
    status: int = Form(...),
    db: Session = Depends(get_db)
):
    # Get the existing course
    existing_course = db.query(Course).filter(Course.id == course_id).first()
    if not existing_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get counselor name based on counselor_id
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")

    counselor_name = counselor.name  # Assuming counselor has a 'name' attribute

    # Update course data
    existing_course.name = name
    existing_course.fees = fees
    existing_course.duration = duration
    existing_course.pdf = pdf
    existing_course.prerequisites_sub = prerequisites_sub
    existing_course.sample_project = sample_project
    existing_course.description = description
    existing_course.other_link = other_link
    existing_course.objective = objective
    existing_course.note = note
    existing_course.status = status

    # Add the course_counselor entry for the update operation
    new_course_counselor = CourseCounselor(
        course_id=course_id,
        counselor_id=counselor_id,
        # type_of_operation=type_of_operation,
        type_of_operation=counselor_name + " " + "Update Course",
        time_stamp=datetime.utcnow()
    )

    db.add(new_course_counselor)
    db.commit()
    
    return {"message": "Course updated successfully"}
    
    # raise HTTPException(
    #     status_code=status.HTTP_200_OK,
    #     detail={"status": status.HTTP_200_OK,"message": "Course updated successfully"}
    # )

@app.get("/get_all_course_and_fees")
def get_all_course_and_fees(db: Session = Depends(get_db)):
    courses = db.query(Course).all()

    course_data = []
    for course in courses:
        course_data.append({
            "course_id": course.id,
            "course_name": course.name,
            "fees": course.fees,
            "pdf": course.pdf,
        })

    return JSONResponse(content={"courses_and_fees": course_data})

@app.get("/get_all_course_counselor")
def get_all_course_counselor(db: Session = Depends(get_db)):
    course_counselors = db.query(CourseCounselor).all()

    course_counselor_data = []
    for course_counselor in course_counselors:
        course_name = db.query(Course.name).filter(Course.id == course_counselor.course_id).first()
        counselor_name = db.query(Counselor.name).filter(Counselor.id == course_counselor.counselor_id).first()

        course_counselor_data.append({
            "course_id": course_counselor.course_id,
            "course_name": course_name[0] if course_name else None,
            "counselor_id": course_counselor.counselor_id,
            "counselor_name": counselor_name[0] if counselor_name else None,
            "type_of_operation": course_counselor.type_of_operation,
            "time_stamp": course_counselor.time_stamp.strftime("%Y-%m-%d %H:%M:%S") if course_counselor.time_stamp else None,
        })

    return JSONResponse(content={"course_counselors": course_counselor_data})

@app.post("/add_batch")
def add_batch(
    counselor_id: int = Form(...),
    name: str = Form(...),
    course_id: int = Form(...),
    time: str = Form(...),
    trainer_name: str = Form(...),
    daily_hours: float = Form(...),
    weekly_days: str = Form(...),
    start_date: date = Form(...),
    expected_end_date: date = Form(...),
    db: Session = Depends(get_db)
):
    # Get counselor name based on counselor_id
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")

    counselor_name = counselor.name  # Assuming counselor has a 'name' attribute

    # Create a new batch
    new_batch = Batch(
        # id=1,
        name=name,
        course_id=course_id,
        time=time,
        trainer_name=trainer_name,
        daily_hours=daily_hours,
        weekly_days=weekly_days,
        start_date=start_date,
        expected_end_date=expected_end_date,
        time_stamp=datetime.utcnow()
    )

    db.add(new_batch)
    # Session.flush()
    db.commit()
    db.refresh(new_batch)

    # Add the batch_counselor entry
    new_batch_counselor = BatchCounselor(
        batch_id=new_batch.id,
        counselor_id=counselor_id,
        type_of_operation=counselor_name + " " + "Add Batch"
    )

    db.add(new_batch_counselor)
    db.commit()

    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": status.HTTP_200_OK,"message": "Batch added successfully"}
    )

@app.get("/get_all_batches")
def get_all_batches(db: Session = Depends(get_db)):
    batches = db.query(Batch).all()

    # Fetch associated course names
    batch_data = []
    for batch in batches:
        course_name = db.query(Course.name).filter(Course.id == batch.course_id).first()
        batch_data.append({
            "batch_id": batch.id,
            "batch_name": batch.name,
            "course_name": course_name[0] if course_name else None,
            "time": batch.time,
            "trainer_name": batch.trainer_name,
            "daily_hours": batch.daily_hours,
            "weekly_days": batch.weekly_days,
            "start_date": batch.start_date,
            "expected_end_date": batch.expected_end_date,
            "status": batch.status,
            "time_stamp": batch.time_stamp
        })

    return {"batches": batch_data}

@app.get("/get_batch/{batch_id}")
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    # Get the batch by batch_id
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail={"message": "Batch not found"}
        )

    # Fetch associated course name
    course_name = db.query(Course.name).filter(Course.id == batch.course_id).first()

    # Convert the result to a dictionary for JSON response
    batch_data = {
        "batch_id": batch.id,
        "batch_name": batch.name,
        "course_name": course_name[0] if course_name else None,
        "time": batch.time,
        "trainer_name": batch.trainer_name,
        "daily_hours": batch.daily_hours,
        "weekly_days": batch.weekly_days,
        "start_date": batch.start_date,
        "expected_end_date": batch.expected_end_date,
        "status": batch.status,
        "time_stamp": batch.time_stamp
    }

    return batch_data

@app.put("/update_batch/{batch_id}")
def update_batch(
    batch_id: int,
    counselor_id: int = Form(...),
    # type_of_operation: str = Form(...),
    name: str = Form(...),
    time: str = Form(...),
    trainer_name: str = Form(...),
    daily_hours: float = Form(...),
    weekly_days: str = Form(...),
    start_date: date = Form(...),
    expected_end_date: date = Form(...),
    status: int = Form(...),
    db: Session = Depends(get_db)
):
    # Get the existing batch
    existing_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not existing_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Get counselor name based on counselor_id
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")

    counselor_name = counselor.name  # Assuming counselor has a 'name' attribute

    # Update batch data
    existing_batch.name = name
    existing_batch.time = time
    existing_batch.trainer_name = trainer_name
    existing_batch.daily_hours = daily_hours
    existing_batch.weekly_days = weekly_days
    existing_batch.start_date = start_date
    existing_batch.expected_end_date = expected_end_date
    existing_batch.status = status

    # Add the batch_counselor entry for the update operation
    new_batch_counselor = BatchCounselor(
        batch_id=batch_id,
        counselor_id=counselor_id,
        type_of_operation=counselor_name + " " + "Update Batch",
        time_stamp=datetime.utcnow()
    )

    db.add(new_batch_counselor)
    db.commit()
    
    return {"message": "Batch updated successfully"}

    # raise HTTPException(
    #     status_code=status.HTTP_200_OK,
    #     detail={"status": status.HTTP_200_OK,"message": "Batch updated successfully"}
    # )

@app.get("/get_all_batch_counselor")
def get_all_batch_counselor(db: Session = Depends(get_db)):
    batch_counselors = db.query(BatchCounselor).all()

    batch_counselor_data = []
    for batch_counselor in batch_counselors:
        batch_name = db.query(Batch.name).filter(Batch.id == batch_counselor.batch_id).first()
        counselor_name = db.query(Counselor.name).filter(Counselor.id == batch_counselor.counselor_id).first()

        batch_counselor_data.append({
            "batch_id": batch_counselor.batch_id,
            "batch_name": batch_name[0] if batch_name else None,
            "counselor_id": batch_counselor.counselor_id,
            "counselor_name": counselor_name[0] if counselor_name else None,
            "type_of_operation": batch_counselor.type_of_operation,
            "time_stamp": batch_counselor.time_stamp.strftime("%Y-%m-%d %H:%M:%S") if batch_counselor.time_stamp else None,
        })

    return JSONResponse(content={"batch_counselors": batch_counselor_data})

@app.post("/add_student")
def add_student(request: StudentRequest, db: Session = Depends(get_db)):
    
    # Check email format
    if not is_valid_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"status": status.HTTP_422_UNPROCESSABLE_ENTITY, "message": "Invalid email format"},
        )
        
    existing_student = db.query(Student).filter(Student.email == request.email).first()
    if existing_student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    # Create a new student
    new_student = Student(
        name=request.name,
        email=request.email,
        contact_1=request.contact_1,
        contact_2=request.contact_2,
        area=request.area,
        college_name=request.college_name,
        mode=request.mode,
        date_of_join=request.date_of_join,
        reference=request.reference
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Add the single remark for the student
    new_remark = StudentRemarks(
        student_id=new_student.id,
        counselor_id=request.counselor_id,
        remark=request.remark
    )

    db.add(new_remark)
    db.commit()

    # Add courses for the student
    for i in range(len(request.course_ids)):
        # Add the student_course entry
        new_course = StudentCourse(
            student_id=new_student.id,
            course_id=request.course_ids[i],
            fees=request.fees_list[i]
        )

        db.add(new_course)
        db.commit()
        
    for i in range(len(request.pdf_list)):
        pdf_data = request.pdf_list[i]

        name = request.name
        email = request.email
        pdf_link = pdf_data

        send_email_background(BackgroundTasks(),"Subject PDF", email, {
            "title": "Subject PDF",
            "name": name,
            "pdf_link": pdf_link
        })
        
    #  # Add PDF data for the student
    # for i in range(len(request.pdf_list)):
    #     pdf_data = request.pdf_list[i]
        
    #     name=request.name
    #     email=request.email
    #     pdf_link = pdf_data
        
    #     print("PDF",pdf_data)
    #     print("Name",name)
    #     print("Email",email)
    #     print("PDF_link",pdf_link)
    
    #     get_pdf_link(name,email,pdf_data)

    # background_tasks.add_task(send_email_background, background_tasks, "Subject PDF", email, {
    #     "title": "Subject PDF",
    #     "name": name,
    #     "pdf_link": pdf_link
    # })

    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": status.HTTP_200_OK,"message": "Student added successfully"}
    )
    
def get_pdf_link(name: str, email: str, pdf_link: List):
    send_email_background("Subject PDF", email, {
        "title": "Subject PDF",
        "name": name,
        "pdf_link": pdf_link
    })
    

@app.get("/get_all_students")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()

    student_data = []
    for student in students:
        remarks = [{"remark": remark.remark,"status": remark.status, "time_stamp": remark.time_stamp} for remark in student.remarks]
        courses = []

        for course in student.courses:
            # Fetch course name from the Course table using course_id
            course_name = db.query(Course).filter(Course.id == course.course_id).first().name

            courses.append({
                "course_id": course.course_id,
                "course_name": course_name,
                "fees": course.fees,
                "time_stamp": course.time_stamp
            })

        student_data.append({
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "contact_1": student.contact_1,
            "contact_2": student.contact_2,
            "area": student.area,
            "college_name": student.college_name,
            "mode": student.mode,
            "date_of_join": student.date_of_join,
            "reference": student.reference,
            "remarks": remarks,
            "courses": courses,
        })

    return {"students": student_data}

# Endpoint to get a student by ID
@app.get("/get_student/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    remarks = [{"remark": remark.remark, "time_stamp": remark.time_stamp} for remark in student.remarks]
    courses_data = []

    for course in student.courses:
        course_data = {
            "course_id": course.course_id,
            "fees": course.fees,
            "time_stamp": course.time_stamp,
            "course_name": course.course.name  # Assuming there's a 'name' attribute in the Course model
        }
        courses_data.append(course_data)

    student_data = {
        "student_id": student.id,
        "name": student.name,
        "email": student.email,
        "contact_1": student.contact_1,
        "contact_2": student.contact_2,
        "area": student.area,
        "college_name": student.college_name,
        "mode": student.mode,
        "date_of_join": student.date_of_join,
        "reference": student.reference,
        "remarks": remarks,
        "courses": courses_data,
    }

    return student_data

@app.put("/update_student/{student_id}")
def update_student(
    student_id: int,
    request: StudentRequest,
    db: Session = Depends(get_db)
):
    # Get the existing student
    existing_student = db.query(Student).filter(Student.id == student_id).first()
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Update student data
    existing_student.name = request.name
    existing_student.email = request.email
    existing_student.contact_1 = request.contact_1
    existing_student.contact_2 = request.contact_2
    existing_student.area = request.area
    existing_student.college_name = request.college_name
    existing_student.mode = request.mode
    existing_student.date_of_join = request.date_of_join
    existing_student.reference = request.reference

    # Delete existing student courses
    db.query(StudentCourse).filter(StudentCourse.student_id == student_id).delete()

    # Add the student_remarks entry for the update operation
    new_remark = StudentRemarks(
        student_id=student_id,
        counselor_id=request.counselor_id,
        remark=request.remark
    )

    db.add(new_remark)
    db.commit()

    # Add the new student courses
    for i in range(len(request.course_ids)):
        new_course = StudentCourse(
            student_id=student_id,
            course_id=request.course_ids[i],
            fees=request.fees_list[i]
        )
        db.add(new_course)

    db.commit()
    
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": status.HTTP_200_OK,"message": "Student updated successfully"}
    )

@app.get("/search_course", response_model=List[dict])
def search_course(
    search_course: str = None,
    db: Session = Depends(get_db)
):
    # Build the query dynamically based on the provided search term
    query = db.query(Course)
    if search_course:
        query = query.filter(
            Course.name.ilike(f"%{search_course}%")
        )

    # Execute the query and retrieve the results
    courses = query.all()

    # Convert the result to a list of dictionaries for JSON response
    course_list = [
        {
            "course_id": course.id,
            "course_name": course.name,
            "fees": course.fees,
            "duration": course.duration,
            "pdf": course.pdf,
            "prerequisites_sub": course.prerequisites_sub,
            "sample_project": course.sample_project,
            "description": course.description,
            "other_link": course.other_link,
            "objective": course.objective,
            "note": course.note,
            "status": course.status
        }
        for course in courses
    ]

    if not search_course or not course_list:
        raise HTTPException(
            status_code=404,
            detail={"message": "No courses found"}
        )

    return course_list

@app.get("/search_batch", response_model=List[dict])
def search_batch(
    search_batch: str = None,
    db: Session = Depends(get_db)
):
    # Build the query dynamically based on the provided search term
    query = db.query(Batch).join(Course).filter(
        or_(
            Batch.name.ilike(f"%{search_batch}%"),
            Batch.trainer_name.ilike(f"%{search_batch}%"),
            Course.name.ilike(f"%{search_batch}%")
        )
    )

    # Execute the query and retrieve the results
    batches = query.all()

    # Convert the result to a list of dictionaries for JSON response
    batch_list = [
        {
            "batch_id": batch.id,
            "batch_name": batch.name,
            "course_name": batch.course.name if batch.course else None,
            "time": batch.time,
            "trainer_name": batch.trainer_name,
            "daily_hours": batch.daily_hours,
            "weekly_days": batch.weekly_days,
            "start_date": batch.start_date,
            "expected_end_date": batch.expected_end_date,
            "status": batch.status,
            "time_stamp": batch.time_stamp
        }
        for batch in batches
    ]

    if not search_batch or not batch_list:
        raise HTTPException(
            status_code=404,
            detail={"message": "No batches found"}
        )

    return batch_list

@app.get("/search_student", response_model=List[dict])
def search_student(
    search_term: str = None,
    db: Session = Depends(get_db)
):
    # Build the query dynamically based on the provided search term
    query = db.query(Student).join(StudentCourse, Course, StudentRemarks).filter(
        or_(
            or_(
                Student.name.ilike(f"%{search_term}%"),
                Student.area.ilike(f"%{search_term}%"),
                Student.college_name.ilike(f"%{search_term}%"),
                Student.mode.ilike(f"%{search_term}%"),
            ),
            Course.name.ilike(f"%{search_term}%")
        )
    )

    # Execute the query and retrieve the results
    students = query.all()

    # Convert the result to a list of dictionaries for JSON response
    student_list = [
        {
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "contact_1": student.contact_1,
            "contact_2": student.contact_2,
            "area": student.area,
            "college_name": student.college_name,
            "mode": student.mode,
            "date_of_join": student.date_of_join,
            "reference": student.reference,
            "courses": [
                {
                    "course_id": course.course_id,
                    "course_name": course.course.name,
                    "fees": course.fees,
                    "time_stamp": course.time_stamp
                }
                for course in student.courses
            ],
            "remarks": [
                {
                    "remark": remark.remark,
                    "time_stamp": remark.time_stamp
                }
                for remark in student.remarks
            ],
            # Include other fields as needed
        }
        for student in students
    ]

    if not search_term or not student_list:
        raise HTTPException(
            status_code=404,
            detail={"message": "No students found"}
        )

    return student_list
