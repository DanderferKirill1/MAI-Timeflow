from app import create_app
from app.models import Group, Institute, Level, Schedule

app = create_app()

with app.app_context():
    print('Institutes:')
    for i in Institute.query.all():
        print(f'  - {i}')
    
    print('\nLevels:')
    for l in Level.query.all():
        print(f'  - {l}')
    
    print('\nGroups:')
    for g in Group.query.all():
        print(f'  - {g}')
        
    print('\nSchedule:')
    for s in Schedule.query.all():
        print(f'  - {s.day} {s.time_slot}: {s.subject_code} (ауд. {s.room_number}, тип: {s.subject_type})') 