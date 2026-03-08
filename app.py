import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask import jsonify
from flask import request, redirect, url_for, flash
from sqlalchemy.orm import Session

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

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='enrollments', lazy=True)
    course = db.relationship('Course', backref='enrollments', lazy=True)

class SupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Text, nullable=False)

class CategoryProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(150), nullable=False)
    total_courses = db.Column(db.Integer, nullable=False)
    student_completed = db.Column(db.JSON, nullable=False)

with app.app_context():
    db.create_all()

def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/')
@app.route('/home')
def index():
    user_id = session.get('user_id')
    user = None

    user = db.session.get(User, user_id)
    if user and user.is_admin:
        return redirect(url_for('dashboard'))

    if user_id:
        user = db.session.get(User, user_id)
    
    instructors = Instructor.query.all()
    return render_template('index.html', instructors=instructors, user=user)

@app.route('/instructor')
@login_required
def instructor():
    user_id = session.get('user_id')
    user = None

    if user_id:
        user = db.session.get(User, user_id)
    instructors = Instructor.query.all()
    return render_template('instructor.html', instructors=instructors, user=user)

@app.route('/courses', defaults={'instructor_id': None})
@app.route('/courses/<int:instructor_id>')
@login_required
def courses(instructor_id):
    user_id = session.get('user_id')
    user = None

    if user_id:
        user = db.session.get(User, user_id)

    if instructor_id:
        courses_db = Course.query.filter_by(instructor_id=instructor_id).all()
    else:
        courses_db = Course.query.all()

    enrolled_courses = {enrollment.course_id for enrollment in Enrollment.query.filter_by(student_id=user_id).all()}

    return render_template('courses.html', courses=courses_db, enrolled_courses=enrolled_courses, user=user)

@app.route('/enroll', defaults={'course_id': None})
@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    user_id = session.get('user_id')
    user = None

    if user_id:
        user = db.session.get(User, user_id)
    
    if course_id:
        course = db.session.get(Course, course_id)
        
        if course:
            pdfs = CoursePDF.query.filter_by(course_id=course.id).all()
            playlists = Playlist.query.filter_by(course_id=course.id).all()
            weeks = Week.query.filter_by(course_id=course.id).all()

            return render_template('enroll.html', course=course, pdfs=pdfs, playlists=playlists, weeks=weeks, user=user)
        else:
            flash('Course not found.', 'danger')
            return redirect(url_for('courses'))
    else:
        flash('Invalid course ID.', 'danger')
        return redirect(url_for('courses'))

@app.route('/enroll_course/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    user_id = session.get('user_id')
    course = Course.query.get(course_id)

    if not course:
        return {"status": "error", "message": "Course not found"}, 404

    existing_enrollment = Enrollment.query.filter_by(student_id=user_id, course_id=course_id).first()
    if existing_enrollment:
        return {"status": "info", "message": "You are already enrolled in this course"}

    new_enrollment = Enrollment(student_id=user_id, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()

    return {"status": "success", "message": f"Enrolled in {course.title}"}, 200

@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    user_id = session.get('user_id')
    user = None

    if user_id:
        user = db.session.get(User, user_id)

    if request.method == 'POST':
        name = user.name
        email = user.email
        about_me = request.form['aboutMe']
        new_application = Application(name=name, email=email, about_me=about_me)
        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('apply'))
    return render_template('apply.html', user=user)

@app.route('/add_course', methods=['POST'])
@login_required
def add_course():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    if not user.is_instructor:
        flash('Only instructors can create courses.', 'danger')
        return redirect(url_for('profile'))

    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    price = request.form.get('price')
    week = int(request.form.get('week'))
    rating = 0.0
    last_course = db.session.query(Course).order_by(Course.course_id.desc()).first()
    if last_course:
        course_id = str(int(last_course.course_id) + 1)
    else:
        course_id = "1"

    image = request.files['image']
    image_filename = f"{course_id}_{image.filename}"
    image_path = os.path.join("static", "assets", "img", "course_images", image_filename)
    image.save(image_path)
    new_course = Course(
        category=category,
        title=title,
        instructor_id=str(user_id),
        course_id=course_id,
        description=description,
        image=f"assets/img/course_images/{image_filename}",
        price=price,
        week=week,
        rating=rating,
    )
    db.session.add(new_course)
    db.session.commit()
    flash('Course added successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    profile_picture = user.profile_picture if user.profile_picture else url_for('static', filename='default-profile.png')

    if user.is_instructor:
        courses = Course.query.filter_by(instructor_id=user.id).all()
        students = {}
        for course in courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            students[course.id] = [enrollment.student for enrollment in enrollments]

        return render_template(
            'profile.html',
            user=user,
            profile_picture=profile_picture,
            courses=courses,
            students=students
        )
    else:
        enrollments = Enrollment.query.filter_by(student_id=user_id).all()
        enrolled_courses = [enrollment.course for enrollment in enrollments]
        category_progress = CategoryProgress.query.all()
        student_progress = {}

        for category in category_progress:
            total_courses = category.total_courses
            completed_courses = 0
            for record in category.student_completed:
                if str(user_id) in record:
                    completed_courses = record[str(user_id)]
                    break
            progress_percentage = (completed_courses / total_courses) * 100 if total_courses > 0 else 0
            student_progress[category.category_name] = {
                "completed_courses": completed_courses,
                "progress_percentage": progress_percentage
            }

        return render_template(
            'profile.html',
            user=user,
            profile_picture=profile_picture,
            enrolled_courses=enrolled_courses,
            student_progress=student_progress
        )

@app.route('/submit_support', methods=['POST'])
@login_required
def submit_support():
    user_id = session.get('user_id')

    if not user_id:
        flash('You need to log in to submit a support request.', 'danger')
        return redirect(url_for('login'))

    details = request.form.get('supportMe')

    if not details.strip():
        flash('Support details cannot be empty.', 'danger')
        return redirect(url_for('profile'))

    new_support = SupportRequest(user_id=user_id, details=details)
    db.session.add(new_support)
    db.session.commit()
    flash('Support request submitted successfully!', 'success')
    return redirect(url_for('profile'))

@app.template_filter('getattr')
def getattr_filter(obj, attr):
    return getattr(obj, attr, None)

@app.route('/api/get_record', methods=['GET'])
@login_required
def get_record():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    if not user or not user.is_admin:
        return redirect(url_for('index'))

    table_name = request.args.get('table')
    record_id = request.args.get('id')

    if not table_name or not record_id:
        return {"error": "Table and ID are required"}, 400

    model_class = globals().get(table_name)
    if not model_class or not issubclass(model_class, db.Model):
        return {"error": f"Invalid table name: {table_name}"}, 400

    record = db.session.get(model_class, record_id)
    if not record:
        return {"error": f"Record with ID {record_id} not found in {table_name}"}, 404

    record_data = {column.name: getattr(record, column.name) for column in record.__table__.columns}
    return jsonify(record_data)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    if not user or not user.is_admin:
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        table = request.form.get('table')
        record_id = request.form.get('id')
        email = request.form.get('email')

        model_class = globals().get(table)
        if not model_class or not issubclass(model_class, db.Model):
            flash(f"Invalid table name: {table}", "danger")
            return redirect(url_for('dashboard'))

        record = model_class.query.get(record_id)
        if not record and action != "accept":
            flash(f"Record {record_id} not found.", "danger")
            return redirect(url_for('dashboard'))

        if action == "accept":
            user_to_update = User.query.filter_by(email=email).first()
            if user_to_update:
                user_to_update.is_instructor = True
                db.session.commit()
                flash(f"User {user_to_update.name} has been accepted as an instructor.", "success")
            else:
                flash("User not found in the User table.", "danger")

        elif action == "delete":
            db.session.delete(record)
            db.session.commit()
            flash(f"Record {record_id} deleted from {table}.", "success")

        elif action == "edit":
            for field, value in request.form.items():
                if field in ['action', 'id', 'table']:
                    continue
                if isinstance(getattr(record, field), bool):
                    value = value.lower() == 'true'
                setattr(record, field, value)
            db.session.commit()
            flash(f"Record {record_id} updated in {table}.", "success")

    tables = {}
    for model_name, model_class in globals().items():
        if isinstance(model_class, type) and issubclass(model_class, db.Model):
            tables[model_name] = model_class.query.all()

    applications = Application.query.all()
    
    applicants_not_instructors = []
    for app in applications:
        user_in_db = User.query.filter_by(email=app.email).first()
        if user_in_db and not user_in_db.is_instructor:
            applicants_not_instructors.append({"name": app.name, "email": app.email})

    return render_template('dashboard.html', applications=applicants_not_instructors, tables=tables)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:

        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
        if user and user.is_admin:
            return redirect(url_for('dashboard'))

        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered!', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
