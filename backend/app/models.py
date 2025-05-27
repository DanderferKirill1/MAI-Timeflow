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
        return f"<Пользователь {self.email}>"


class StudentProfile(db.Model):
    """Таблица STUDENT_PROFILES: профиль студента."""
    __tablename__ = 'student_profiles'

    profile_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    language = db.Column(db.String(10))
    group_code = db.Column(db.String(20), db.ForeignKey('groups.group_code'), nullable=False)
    group = db.relationship('Group', backref='student_profiles')

    def __repr__(self):
        return f"<Профиль {self.first_name} {self.last_name}, группа {self.group_code}>"


class Group(db.Model):
    """Таблица GROUPS: группы студентов."""
    __tablename__ = 'groups'

    group_code = db.Column(db.String(20), primary_key=True)
    course_number = db.Column(db.String(10), db.ForeignKey('courses.course_number'), nullable=False)
    institute_name = db.Column(db.String(100), db.ForeignKey('institutes.institute_name'), nullable=False)
    level_name = db.Column(db.String(100), db.ForeignKey('levels.level_name'), nullable=False)
    course = db.relationship('Course', backref='groups')
    institute = db.relationship('Institute', backref='groups')
    level = db.relationship('Level', backref='groups')

    def __repr__(self):
        return f"<Группа {self.group_code}, курс {self.course_number}, {self.institute_name}, {self.level_name}>"


class Level(db.Model):
    """Таблица LEVELS: ступени обучения."""
    __tablename__ = 'levels'

    level_code = db.Column(db.String(10), primary_key=True)
    level_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Ступень {self.level_code}. {self.level_name}"


class Course(db.Model):
    """Таблица COURSES: курсы."""
    __tablename__ = 'courses'

    course_number = db.Column(db.String(10), primary_key=True)

    def __repr__(self):
        return f"<Курс {self.course_number}>"


class Institute(db.Model):
    """Таблица INSTITUTES: институты."""
    __tablename__ = 'institutes'

    institute_code = db.Column(db.String(10), primary_key=True)
    institute_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<{self.institute_code} {self.institute_name}>"


class Teacher(db.Model):
    """Таблица TEACHERS: преподаватели."""
    __tablename__ = 'teachers'

    teacher_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))

    def __repr__(self):
        return f"<Преподаватель {self.teacher_id}: {self.full_name}>"


class Subject(db.Model):
    """Таблица SUBJECTS: предметы."""
    __tablename__ = 'subjects'

    subject_code = db.Column(db.String(150), primary_key=True)  # просто название предмета
    subject_name = db.Column(db.String(150))  # пока не нужно

    def __repr__(self):
        return f"<Предмет {self.subject_code}>"


class Week(db.Model):
    """Таблица WEEKS: недели."""
    __tablename__ = 'weeks'

    week_num = db.Column(db.Integer, primary_key=True)
    week_start = db.Column(db.String(20), nullable=False)
    week_end = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Неделя {self.week_num}: {self.week_start} - {self.week_end}"


class Schedule(db.Model):
    """Таблица SCHEDULES: расписание."""
    __tablename__ = 'schedules'

    lesson_id = db.Column(db.Integer, primary_key=True)
    week_num = db.Column(db.Integer, db.ForeignKey('weeks.week_num'), nullable=False)
    group_code = db.Column(db.String(20), db.ForeignKey('groups.group_code'), nullable=False)
    day = db.Column(db.String(50), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    subject_code = db.Column(db.String(150), db.ForeignKey('subjects.subject_code'), nullable=False)
    subject_type = db.Column(db.String(10))
    room_number = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    week = db.relationship('Week', backref='schedules')
    group = db.relationship('Group', backref='schedules')
    subject = db.relationship('Subject', backref='schedules')
    teacher = db.relationship('Teacher', backref='schedules')

    def __repr__(self):
        return f"Неделя №{self.week_num}: {self.group_code}, {self.day}, {self.time_slot}, {self.subject_code}, {self.subject_type}, {self.room_number},"
