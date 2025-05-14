from werkzeug.security import check_password_hash, generate_password_hash

from . import db

class User(db.Model):
    """Таблица USERS: данные для авторизации пользователя."""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.profile_id'), nullable=False)
    profile = db.relationship('StudentProfile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

class StudentProfile(db.Model):
    """Таблица STUDENT_PROFILES: профиль студента."""
    __tablename__ = 'student_profiles'

    profile_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    language = db.Column(db.String(10))
    group_code = db.Column(db.String(20), db.ForeignKey('groups.group_code'), nullable=False)
    group = db.relationship('Group', backref='student_profiles')

    def __repr__(self):
        return f"<StudentProfile {self.first_name} {self.last_name}>"

class Group(db.Model):
    """Таблица GROUPS: группы студентов."""
    __tablename__ = 'groups'

    group_code = db.Column(db.String(20), primary_key=True)
    group_name = db.Column(db.String(50), nullable=False)
    course_number = db.Column(db.String(10), db.ForeignKey('courses.course_number'), nullable=False)
    course = db.relationship('Course', backref='groups')

    def __repr__(self):
        return f"<Group {self.group_code}>"

class Course(db.Model):
    """Таблица COURSES: курсы."""
    __tablename__ = 'courses'

    course_number = db.Column(db.String(10), primary_key=True)
    institute_code = db.Column(db.String(10), db.ForeignKey('institutes.institute_code'), nullable=False)
    institute = db.relationship('Institute', backref='courses')

    def __repr__(self):
        return f"<Course {self.course_number}>"

class Institute(db.Model):
    """Таблица INSTITUTES: институты."""
    __tablename__ = 'institutes'

    institute_code = db.Column(db.String(10), primary_key=True)
    institute_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Institute {self.institute_code}>"

class Teacher(db.Model):
    """Таблица TEACHERS: преподаватели."""
    __tablename__ = 'teachers'

    teacher_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Teacher {self.full_name}>"

class Subject(db.Model):
    """Таблица SUBJECTS: предметы."""
    __tablename__ = 'subjects'

    subject_code = db.Column(db.String(10), primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Subject {self.subject_code}>"

class Schedule(db.Model):
    """Таблица SCHEDULES: расписание."""
    __tablename__ = 'schedules'

    schedule_id = db.Column(db.Integer, primary_key=True)
    group_code = db.Column(db.String(20), db.ForeignKey('groups.group_code'), nullable=False)
    weekday = db.Column(db.String(10), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    subject_code = db.Column(db.String(10), db.ForeignKey('subjects.subject_code'), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    group = db.relationship('Group', backref='schedules')
    subject = db.relationship('Subject', backref='schedules')
    teacher = db.relationship('Teacher', backref='schedules')

    def __repr__(self):
        return f"<Schedule {self.schedule_id}>"