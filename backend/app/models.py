from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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
        """Установка пароля пользователя."""
        self.password_hash = generate_password_hash(password)
        print(f"Generated password hash: {self.password_hash}")  # Отладочная информация

    def check_password(self, password):
        """Проверка пароля пользователя."""
        result = check_password_hash(self.password_hash, password)
        print(f"Checking password: {password}")  # Отладочная информация
        print(f"Current hash: {self.password_hash}")  # Отладочная информация
        print(f"Check result: {result}")  # Отладочная информация
        return result

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
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=True)
    week = db.relationship('Week', backref='schedules')
    group = db.relationship('Group', backref='schedules')
    subject = db.relationship('Subject', backref='schedules')
    teacher = db.relationship('Teacher', backref='schedules')

    def __repr__(self):
        return f"Неделя №{self.week_num}: {self.group_code}, {self.day}, {self.time_slot}, {self.subject_code}, {self.subject_type}, {self.room_number},"


class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    os_info = db.Column(db.String(100), nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'os_info': self.os_info,
            'last_activity': self.last_activity.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Notification(db.Model):
    """Таблица NOTIFICATIONS: уведомления пользователей."""
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'cancelled' или 'changed'
    subject_name = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', backref='notifications')

    def to_dict(self):
        """Преобразование объекта в словарь."""
        return {
            'notification_id': self.notification_id,
            'type': self.type,
            'subject_name': self.subject_name,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read
        }

    def __repr__(self):
        return f"Уведомление #{self.notification_id}: {self.type}, {self.subject_name}, {self.message}"


class NotificationSettings(db.Model):
    """Таблица NOTIFICATION_SETTINGS: настройки уведомлений пользователя."""
    __tablename__ = 'notification_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    schedule_changes = db.Column(db.Boolean, nullable=False, default=True)
    lesson_reminders = db.Column(db.Boolean, nullable=False, default=True)
    reminder_time = db.Column(db.Integer, nullable=False, default=15)  # время в минутах
    push_notifications = db.Column(db.Boolean, nullable=False, default=True)
    email_notifications = db.Column(db.Boolean, nullable=False, default=True)
    telegram_notifications = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', backref='notification_settings')

    def to_dict(self):
        """Преобразование объекта в словарь."""
        return {
            'schedule_changes': self.schedule_changes,
            'lesson_reminders': self.lesson_reminders,
            'reminder_time': self.reminder_time,
            'push_notifications': self.push_notifications,
            'email_notifications': self.email_notifications,
            'telegram_notifications': self.telegram_notifications
        }

    def __repr__(self):
        return f"Настройки уведомлений для пользователя {self.user_id}"
