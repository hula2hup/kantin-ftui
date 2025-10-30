from app import app, db, User

with app.app_context():
    db.session.query(User).delete()
    db.session.commit()
    print("All users deleted.")
