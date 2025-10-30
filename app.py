from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tekneat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['SECRET_KEY'] = 'your_secret_key'  # Ganti dengan kunci rahasia unik Anda
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model Database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Simpan password plain untuk sederhana
    role = db.Column(db.String(50), default='user')  # Role: admin or user

    def __repr__(self):
        return f'<User {self.username}>'

class Toko(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Toko {self.nama}>'

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    in_stock = db.Column(db.Boolean, default=True)
    max_order = db.Column(db.Integer, default=20)  # Batasan maksimal porsi per menu
    stock = db.Column(db.Integer, default=100)  # Stok yang tersedia
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=False)
    toko = db.relationship('Toko', backref=db.backref('menus', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Menu {self.name} in Toko {self.toko_id}>'

class Penjualan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Penjualan {self.menu_id} on {self.date}>'

class Pesanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toko_id = db.Column(db.Integer, db.ForeignKey('toko.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    
    def __repr__(self):
        return f'<Pesanan {self.menu_id} for Toko {self.toko_id}>'

with app.app_context():
    db.create_all()
    # Create default admin user if none exists
    if not User.query.first():
        admin = User(username='galuh', password='123', role='admin')
        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()  # Cek username dan password
        if user:
            login_user(user)
            flash('Login berhasil! Selamat datang, admin.')
            return redirect(url_for('admin'))
        flash('Login gagal. Cek username dan password.')
    return render_template('login.html')  # Buat template login.html baru

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toko_list')
def toko_list():
    toko_list = Toko.query.all()
    best_sellers = {}
    for toko in toko_list:
        menus = Menu.query.filter_by(toko_id=toko.id).all()
        if menus:
            max_sales = 0
            best_menu = None
            for menu in menus:
                sales_count = Penjualan.query.filter_by(menu_id=menu.id).count()
                if sales_count > max_sales:
                    max_sales = sales_count
                    best_menu = menu
            if best_menu:
                best_sellers[toko.id] = best_menu.image_url
        else:
            best_sellers[toko.id] = None
    return render_template('toko_list.html', toko_list=toko_list, best_sellers=best_sellers)

@app.route('/all_menus')
def all_menus():
    toko_list = Toko.query.all()
    best_menus = []
    for toko in toko_list:
        menus = Menu.query.filter_by(toko_id=toko.id).all()
        if menus:
            max_sales = 0
            best_menu = None
            for menu in menus:
                sales_count = Penjualan.query.filter_by(menu_id=menu.id).count()
                if sales_count > max_sales:
                    max_sales = sales_count
                    best_menu = menu
            if best_menu:
                best_menus.append((best_menu, toko))
    return render_template('all_menus.html', all_menus=best_menus)

@app.route('/toko/<int:toko_id>')
def toko_detail(toko_id):
    toko = Toko.query.get_or_404(toko_id)
    menus = Menu.query.filter_by(toko_id=toko_id).all()
    best_menu = None
    if menus:
        max_sales = 0
        for menu in menus:
            sales_count = Penjualan.query.filter_by(menu_id=menu.id).count()
            if sales_count > max_sales:
                max_sales = sales_count
                best_menu = menu
    return render_template('toko_detail.html', toko=toko, menus=menus, best_menu=best_menu)

@app.route('/add_menu', methods=['GET', 'POST'])
@login_required  # Hanya admin
def add_menu():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menambah menu.')
        return redirect(url_for('admin'))
    toko_list = Toko.query.all()
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        in_stock = 'in_stock' in request.form
        stock = int(request.form['stock'])
        toko_id = int(request.form['toko_id'])
        image = request.files.get('image')
        image_url = None
        if image:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            image_url = f"images/{image_filename}"
        new_menu = Menu(name=name, price=price, image_url=image_url, in_stock=in_stock, stock=stock, toko_id=toko_id)
        db.session.add(new_menu)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_menu.html', toko_list=toko_list)

@app.route('/add_toko', methods=['GET', 'POST'])
@login_required  # Hanya admin
def add_toko():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menambah toko.')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        nama = request.form['nama']
        new_toko = Toko(nama=nama)
        db.session.add(new_toko)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_toko.html')

@app.route('/edit_toko/<int:toko_id>', methods=['GET', 'POST'])
@login_required  # Hanya admin
def edit_toko(toko_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengedit toko.')
        return redirect(url_for('admin'))
    toko = Toko.query.get_or_404(toko_id)
    if request.method == 'POST':
        toko.nama = request.form['nama']
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_toko.html', toko=toko)

@app.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
@login_required  # Hanya admin
def edit_menu(menu_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengedit menu.')
        return redirect(url_for('admin'))
    menu = Menu.query.get_or_404(menu_id)
    if request.method == 'POST':
        menu.name = request.form['name']
        menu.price = float(request.form['price'])
        menu.in_stock = 'in_stock' in request.form
        menu.stock = int(request.form['stock'])
        image = request.files.get('image')
        if image:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            menu.image_url = f"images/{image_filename}"
        db.session.commit()
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    return render_template('edit_menu.html', menu=menu)

@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
@login_required  # Hanya admin
def delete_menu(menu_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat menghapus menu.')
        return redirect(url_for('admin'))
    menu = Menu.query.get_or_404(menu_id)
    # Hapus penjualan terkait
    Penjualan.query.filter_by(menu_id=menu_id).delete()
    db.session.commit()
    # Hapus menu
    db.session.delete(menu)
    db.session.commit()
    flash(f'Menu "{menu.name}" berhasil dihapus!')
    return redirect(url_for('admin'))

@app.route('/order/<int:menu_id>', methods=['GET', 'POST'])
def order(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        # Hitung total pesanan yang sudah ada untuk menu ini
        total_ordered = db.session.query(db.func.sum(Pesanan.quantity)).filter_by(menu_id=menu_id).scalar() or 0
        if total_ordered + quantity > menu.max_order:
            flash(f'Pesanan gagal! Total pesanan melebihi batas maksimal {menu.max_order} porsi.')
            return redirect(url_for('toko_detail', toko_id=menu.toko_id))
        if not menu.in_stock:
            flash('Menu ini sedang tidak tersedia.')
            return redirect(url_for('toko_detail', toko_id=menu.toko_id))
        if quantity > menu.stock:
            flash(f'Pesanan gagal! Stok tidak mencukupi. Stok tersedia: {menu.stock} porsi.')
            return redirect(url_for('toko_detail', toko_id=menu.toko_id))
        new_order = Pesanan(toko_id=menu.toko_id, menu_id=menu_id, quantity=quantity)
        db.session.add(new_order)
        # Kurangi stok
        menu.stock -= quantity
        db.session.commit()
        flash(f'Pesanan {quantity} porsi {menu.name} berhasil dibuat!')
        return redirect(url_for('toko_detail', toko_id=menu.toko_id))
    return render_template('order.html', menu=menu)

@app.route('/record_sale', methods=['GET', 'POST'])
@login_required
def record_sale():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mencatat penjualan.')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        menu_id = int(request.form['menu_id'])
        quantity = int(request.form['quantity'])
        new_sale = Penjualan(menu_id=menu_id, quantity=quantity)
        db.session.add(new_sale)
        db.session.commit()
        flash(f'Penjualan {quantity} porsi berhasil dicatat!')
        return redirect(url_for('admin'))
    menus = Menu.query.all()
    return render_template('record_sale.html', menus=menus)

@app.route('/admin')
@login_required
def admin():
    toko_list = Toko.query.all()
    total_toko = len(toko_list)
    total_menus = Menu.query.count()
    total_penjualan = Penjualan.query.count()
    menus = {}
    for toko in toko_list:
        menus[toko.id] = []
        for menu in toko.menus:
            menu.pesanan = Pesanan.query.filter_by(menu_id=menu.id).all()
            menus[toko.id].append(menu)
    return render_template('admin.html', toko_list=toko_list, total_toko=total_toko, total_menus=total_menus, total_penjualan=total_penjualan, menus=menus)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
