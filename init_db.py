from app import app, db, User

with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(username='galuh', password='123', role='admin')
        db.session.add(admin)
        db.session.commit()
    print('Database initialized successfully.')
