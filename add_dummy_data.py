import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask import Flask
from datetime import datetime

os.system("rm instance/database.db")

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=True)
    is_instructor = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    instructor_id = db.Column(db.String(10), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(150), nullable=True)
    rating = db.Column(db.Float, default=4.5)
    courses_count = db.Column(db.Integer, default=0)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    instructor_id = db.Column(db.String(10), nullable=False)
    course_id = db.Column(db.String(10), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(150), nullable=True)
    rating = db.Column(db.Float, default=4.5)
    price = db.Column(db.String(50), nullable=True)
    week = db.Column(db.Integer, nullable=True)
    pdfs = db.relationship('CoursePDF', back_populates='course', cascade="all, delete-orphan")
    playlists = db.relationship('Playlist', back_populates='course', cascade="all, delete-orphan")
    weeks = db.relationship('Week', back_populates='course', cascade="all, delete-orphan")

class CoursePDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    pdf_filename = db.Column(db.String(150), nullable=False)
    course = db.relationship('Course', back_populates='pdfs')

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    youtube_playlist_link = db.Column(db.String(150), nullable=False)
    course = db.relationship('Course', back_populates='playlists')

class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    week = db.Column(db.String(150), nullable=False)
    course = db.relationship('Course', back_populates='weeks')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    about_me = db.Column(db.Text, nullable=True)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='messages', lazy=True)

class SupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='support_requests', lazy=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='enrollments', lazy=True)
    course = db.relationship('Course', backref='enrollments', lazy=True)

class CategoryProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(150), nullable=False)
    total_courses = db.Column(db.Integer, nullable=False)
    student_completed = db.Column(db.JSON, nullable=False)

with app.app_context():
    db.create_all()

def add_dummy_data():
    if User.query.first():
        print("Users already exist. Skipping dummy data insertion.")
    else:
        users = [
            User(
                name="Mr Jack",
                email="s1@gmail.com",
                password=generate_password_hash('1', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Alice Johnson",
                email="s2@gmail.com",
                password=generate_password_hash('2', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Bob Smith",
                email="s3@gmail.com",
                password=generate_password_hash('3', method='pbkdf2:sha256'),
                profile_picture=None,
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Charlie Davis",
                email="s4@gmail.com",
                password=generate_password_hash('4', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Mr Richard",
                email="s5@gmail.com",
                password=generate_password_hash('5', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="John Doe",
                email="i1@gmail.com",
                password=generate_password_hash('1', method='pbkdf2:sha256'),
                profile_picture="assets/img/img/i1.jpg",
                is_instructor=True,
                is_admin=False
            ),
            User(
                name="Jane Smith",
                email="i2@gmail.com",
                password=generate_password_hash('2', method='pbkdf2:sha256'),
                profile_picture="assets/img/img/i2.jpg",
                is_instructor=True,
                is_admin=False
            ),
            User(
                name="Alice Johnson",
                email="i3@gmail.com",
                password=generate_password_hash('3', method='pbkdf2:sha256'),
                profile_picture="assets/img/img/i3.jpg",
                is_instructor=True,
                is_admin=False
            ),
            User(
                name="Bob Brown",
                email="i4@gmail.com",
                password=generate_password_hash('4', method='pbkdf2:sha256'),
                profile_picture="assets/img/img/i4.jpg",
                is_instructor=True,
                is_admin=False
            ),
            User(
                name="Charlie Lee",
                email="i5@gmail.com",
                password=generate_password_hash('5', method='pbkdf2:sha256'),
                profile_picture="assets/img/img/i5.jpg",
                is_instructor=True,
                is_admin=False
            ),
            User(
                name="Ms Shannon",
                email="s6@gmail.com",
                password=generate_password_hash('6', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Mr Michael",
                email="s7@gmail.com",
                password=generate_password_hash('7', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False

            ),
            User(
                name="Ms Kimberly",
                email="s8@gmail.com",
                password=generate_password_hash('8', method='pbkdf2:sha256'),
                profile_picture=None,
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Mr Marie",
                email="s9@gmail.com",
                password=generate_password_hash('9', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Mr Benjamin",
                email="s10@gmail.com",
                password=generate_password_hash('10', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="admin",
                email="admin@elite.com",
                password=generate_password_hash('admin', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=True
            ),
            User(
                name="Mr Bob",
                email="i6@gmail.com",
                password=generate_password_hash('6', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),
            User(
                name="Mr Smith",
                email="i7@gmail.com",
                password=generate_password_hash('7', method='pbkdf2:sha256'),
                profile_picture="default-profile.png",
                is_instructor=False,
                is_admin=False
            ),

        ]
        db.session.add_all(users)
        db.session.commit()
        print("Users dummy data has been added successfully!")

    if Instructor.query.first():
        print("Instructors already exist. Skipping dummy data insertion.")
    else:
        instructors = [
            Instructor(name="John Doe", instructor_id="6", bio="Experienced web development instructor with 10+ years of experience.", profile_picture="assets/img/img/i1.jpg", rating=4.7, courses_count=5),
            Instructor(name="Jane Smith", instructor_id="7", bio="Full-stack developer and instructor, passionate about teaching.", profile_picture="assets/img/img/i2.jpg", rating=4.8, courses_count=7),
            Instructor(name="Alice Johnson", instructor_id="8", bio="Software engineer with a love for teaching programming.", profile_picture="assets/img/img/i3.jpg", rating=4.6, courses_count=6),
            Instructor(name="Bob Brown", instructor_id="9", bio="Expert in data science, specializing in machine learning and AI.", profile_picture="assets/img/img/i4.jpg", rating=4.9, courses_count=10),
            Instructor(name="Charlie Lee", instructor_id="10", bio="Passionate about front-end technologies and modern JavaScript frameworks.", profile_picture="assets/img/img/i5.jpg", rating=4.4, courses_count=4),
        ]
        db.session.add_all(instructors)
        db.session.commit()
        print("Instructors dummy data has been added successfully!")

    if Course.query.first():
        print("Courses already exist. Skipping dummy data insertion.")
    else:
        courses = [
            Course(category="Programming", title="Programming Fundamentals 1", instructor_id="6", course_id="1", description="Learn the basics of programming.", image="assets/img/course_images/c1.jpg", rating=4.5, price="Free", week=4),
            Course(category="Web Development", title="React JS for Beginners", instructor_id="7", course_id="2", description="Learn React from scratch.", image="assets/img/course_images/c4.jpg", rating=4.6, price="Free", week=6),
            Course(category="Web Development", title="JavaScript Basics", instructor_id="8", course_id="3", description="Introduction to JavaScript and its basics.", image="assets/img/course_images/c5.jpg", rating=4.7, price="Free", week=5),
            Course(category="Web Development", title="Building Websites", instructor_id="9", course_id="4", description="Create your first website.", image="assets/img/course_images/c3.jpg", rating=4.8, price="Free", week=8),
            Course(category="Programming", title="Advanced Python", instructor_id="10", course_id="5", description="Dive deep into Python programming.", image="assets/img/course_images/c2.jpg", rating=4.7, price="Free", week=10),
            Course(category="Programming", title="Programming Fundamentals 2", instructor_id="6", course_id="6", description="Learn the basics of programming.", image="assets/img/course_images/c1.jpg", rating=3.5, price="Free", week=4),
            Course(category="Programming", title="Programming Fundamentals 3", instructor_id="6", course_id="7", description="Learn the basics of programming.", image="assets/img/course_images/c1.jpg", rating=3.0, price="Free", week=4),
        ]
        db.session.add_all(courses)
        db.session.commit()
        print("Courses dummy data has been added successfully!")

    if CoursePDF.query.first():
        print("Course PDFs already exist. Skipping dummy data insertion.")
    else:
        course_pdfs = [
            CoursePDF(course_id=1, pdf_filename="programming_fundamentals_1_1.pdf"),
            CoursePDF(course_id=1, pdf_filename="programming_fundamentals_1_2.pdf"),
            CoursePDF(course_id=1, pdf_filename="programming_fundamentals_1_3.pdf"),
            CoursePDF(course_id=2, pdf_filename="react_for_beginners.pdf"),
            CoursePDF(course_id=2, pdf_filename="react_for_beginners.pdf"),
            CoursePDF(course_id=2, pdf_filename="react_for_beginners.pdf"),
            CoursePDF(course_id=3, pdf_filename="javascript_basic.pdf"),
            CoursePDF(course_id=3, pdf_filename="javascript_basic.pdf"),
            CoursePDF(course_id=3, pdf_filename="javascript_basic.pdf"),
            CoursePDF(course_id=4, pdf_filename="building_websites.pdf"),
            CoursePDF(course_id=4, pdf_filename="building_websites.pdf"),
            CoursePDF(course_id=4, pdf_filename="building_websites.pdf"),
            CoursePDF(course_id=5, pdf_filename="python.pdf"),
            CoursePDF(course_id=5, pdf_filename="python.pdf"),
            CoursePDF(course_id=5, pdf_filename="python.pdf"),
            CoursePDF(course_id=6, pdf_filename="programming_fundamentals_2_1.pdf"),
            CoursePDF(course_id=6, pdf_filename="programming_fundamentals_2_2.pdf"),
            CoursePDF(course_id=6, pdf_filename="programming_fundamentals_2_3.pdf"),
            CoursePDF(course_id=7, pdf_filename="programming_fundamentals_3_1.pdf"),
            CoursePDF(course_id=7, pdf_filename="programming_fundamentals_3_2.pdf"),
            CoursePDF(course_id=7, pdf_filename="programming_fundamentals_3_3.pdf"),
        ]
        db.session.add_all(course_pdfs)
        db.session.commit()
        print("Course PDFs dummy data has been added successfully!")

    if Playlist.query.first():
        print("Playlists already exist. Skipping dummy data insertion.")
    else:
        playlists = [
            Playlist(course_id=1, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=1, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=1, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=2, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=2, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=2, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=3, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=3, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=3, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=4, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=4, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=4, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=5, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=5, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=5, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=6, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=6, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=6, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=7, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=7, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
            Playlist(course_id=7, youtube_playlist_link="https://www.youtube.com/watch?v=rQoqCP7LX60&list=PLxgZQoSe9cg1drBnejUaDD9GEJBGQ5hMt"),
        ]
        db.session.add_all(playlists)
        db.session.commit()
        print("Playlists dummy data has been added successfully!")

    if Week.query.first():
        print("Weeks already exist. Skipping dummy data insertion.")
    else:
        weeks = [
            Week(course_id=1, week="Week 1: Introduction to Programming"),
            Week(course_id=1, week="Week 1: Introduction to Programming"),
            Week(course_id=2, week="Week 1: Introduction to React"),
        ]
        db.session.add_all(weeks)
        db.session.commit()
        print("Weeks dummy data has been added successfully!")

    if Application.query.first():
        print("Applications already exist. Skipping dummy data insertion.")
    else:
        applications = [
            Application(name="Mr Bob", email="i6@gmail.com", about_me="Aspiring web developer interested in learning full-stack development."),
            Application(name="Mr Smith", email="i7@gmail.com", about_me="Data science enthusiast eager to expand my knowledge."),
        ]
        db.session.add_all(applications)
        db.session.commit()
        print("Applications dummy data has been added successfully!")

    if Chat.query.first():
        print("Chat messages already exist. Skipping dummy data insertion.")
    else:
        chat_messages = [
            Chat(user_id=1, message="Hello! I would like to know more about Python."),
            Chat(user_id=2, message="Can you share more details about your web development courses?"),
        ]
        db.session.add_all(chat_messages)
        db.session.commit()
        print("Chat messages dummy data has been added successfully!")

    if SupportRequest.query.first():
        print("Support requests already exist. Skipping dummy data insertion.")
    else:
        support_requests = [
            SupportRequest(user_id=1, details="I need help with accessing the course materials."),
            SupportRequest(user_id=2, details="I encountered a payment issue while enrolling."),
        ]
        db.session.add_all(support_requests)
        db.session.commit()
        print("Support requests dummy data has been added successfully!")

    if Enrollment.query.first():
        print("Enrollment data already exists. Skipping dummy data insertion.")
    else:
        dummy_enrollments = [
            Enrollment(student_id=1, course_id=1),
            Enrollment(student_id=1, course_id=2),
            Enrollment(student_id=1, course_id=3),
            Enrollment(student_id=1, course_id=6),
            Enrollment(student_id=2, course_id=1),
            Enrollment(student_id=2, course_id=2),
            Enrollment(student_id=2, course_id=3),
            Enrollment(student_id=2, course_id=7),
            Enrollment(student_id=3, course_id=1),
            Enrollment(student_id=3, course_id=2),
            Enrollment(student_id=3, course_id=3),
            Enrollment(student_id=3, course_id=6),
            Enrollment(student_id=4, course_id=1),
            Enrollment(student_id=4, course_id=2),
            Enrollment(student_id=4, course_id=3),
            Enrollment(student_id=4, course_id=7),
            Enrollment(student_id=5, course_id=1),
            Enrollment(student_id=5, course_id=2),
            Enrollment(student_id=5, course_id=3),
            Enrollment(student_id=5, course_id=6),
            Enrollment(student_id=11, course_id=5),
            Enrollment(student_id=11, course_id=4),
            Enrollment(student_id=11, course_id=1),
            Enrollment(student_id=11, course_id=7),
            Enrollment(student_id=12, course_id=5),
            Enrollment(student_id=12, course_id=4),
            Enrollment(student_id=12, course_id=2),
            Enrollment(student_id=12, course_id=6),
            Enrollment(student_id=13, course_id=5),
            Enrollment(student_id=13, course_id=4),
            Enrollment(student_id=13, course_id=3),
            Enrollment(student_id=13, course_id=7),
            Enrollment(student_id=14, course_id=5),
            Enrollment(student_id=14, course_id=4),
            Enrollment(student_id=14, course_id=4),
            Enrollment(student_id=14, course_id=6),
            Enrollment(student_id=15, course_id=5),
            Enrollment(student_id=15, course_id=4),
            Enrollment(student_id=15, course_id=5),
            Enrollment(student_id=15, course_id=7),
        ]
        db.session.add_all(dummy_enrollments)
        db.session.commit()
        print("Enrollment dummy data added successfully!")

    if CategoryProgress.query.first():
        print("CategoryProgress data already exists. Skipping dummy data insertion.")
    else:
        category_progress_data = [
            CategoryProgress(
                category_name="Programming",
                total_courses=4,
                student_completed=[
                    {1: 2},
                    {2: 4},
                    {3: 0},
                    {4: 1},
                    {5: 1},
                    {6: 2},
                    {7: 3},
                    {8: 1},
                    {9: 1},
                    {10: 3}
                ]
            ),
            CategoryProgress(
                category_name="Web Development",
                total_courses=3,
                student_completed=[
                    {1: 3},
                    {2: 0},
                    {3: 1},
                    {4: 2},
                    {5: 3},
                    {6: 1},
                    {7: 0},
                    {8: 2},
                    {9: 3},
                    {10: 0}
                ]
            ),
        ]
        db.session.add_all(category_progress_data)
        db.session.commit()
        print("CategoryProgress dummy data has been added successfully!")

with app.app_context():
    add_dummy_data()
