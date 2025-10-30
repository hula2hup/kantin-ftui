from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tekneat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Menu model with the new column
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    in_stock = db.Column(db.Boolean, default=True)
    max_order = db.Column(db.Integer, default=20)  # New column
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=False)

with app.app_context():
    # Add the new column to existing database
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE menu ADD COLUMN max_order INTEGER DEFAULT 20"))
        conn.commit()
    print("Column 'max_order' added to 'menu' table successfully.")
