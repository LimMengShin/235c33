from app import db, Funds, Subjects, Users, NAMES, GROUPS, bcrypt

db.drop_all()
db.create_all()
for name in NAMES:
    student = Funds(name=name,funds=0)
    db.session.add(student)

subjects = GROUPS[2:6]
for subject in subjects:
    sub = Subjects(subject_name=subject)
    db.session.add(sub)

user = Users(username="USERNAME", password=bcrypt.generate_password_hash("PASSWORD"))
db.session.add(user)

db.session.commit()