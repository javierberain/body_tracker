from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///body_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    benchmark_measurement_id = db.Column(db.Integer, nullable=True)
    measurements = db.relationship('Measurement', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='Measurement.user_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    body_fat_percentage = db.Column(db.Float, nullable=False)
    visceral_fat_index = db.Column(db.Float, nullable=False)
    lean_mass_percentage = db.Column(db.Float, nullable=False)
    waist_circumference = db.Column(db.Float, nullable=True)
    hip_circumference = db.Column(db.Float, nullable=True)
    bicep_circumference = db.Column(db.Float, nullable=True)
    thigh_circumference = db.Column(db.Float, nullable=True)
    chest_circumference = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'weight': self.weight,
            'bmi': self.bmi,
            'body_fat_percentage': self.body_fat_percentage,
            'visceral_fat_index': self.visceral_fat_index,
            'lean_mass_percentage': self.lean_mass_percentage,
            'waist_circumference': self.waist_circumference,
            'hip_circumference': self.hip_circumference,
            'bicep_circumference': self.bicep_circumference,
            'thigh_circumference': self.thigh_circumference,
            'chest_circumference': self.chest_circumference
        }

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    if not user:
        # User was deleted or doesn't exist
        session.clear()
        flash('Your account no longer exists. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    measurements = Measurement.query.filter_by(user_id=user.id).order_by(Measurement.timestamp.desc()).all()
    
    print(f"DEBUG Dashboard: user={user.username}, benchmark_id={user.benchmark_measurement_id}")
    print(f"DEBUG Dashboard: Total measurements={len(measurements)}")
    if user.benchmark_measurement_id:
        benchmark_found = any(m.id == user.benchmark_measurement_id for m in measurements)
        print(f"DEBUG Dashboard: Benchmark found in measurements? {benchmark_found}")
    
    return render_template('dashboard.html', user=user, measurements=measurements)

@app.route('/add-measurement', methods=['GET', 'POST'])
@login_required
def add_measurement():
    if request.method == 'POST':
        try:
            # Helper function to get optional float
            def get_optional_float(field_name):
                value = request.form.get(field_name)
                return float(value) if value and value.strip() else None
            
            measurement = Measurement(
                user_id=session['user_id'],
                timestamp=datetime.now(),  # Auto-set to current time
                weight=float(request.form.get('weight')),
                bmi=float(request.form.get('bmi')),
                body_fat_percentage=float(request.form.get('body_fat_percentage')),
                visceral_fat_index=float(request.form.get('visceral_fat_index')),
                lean_mass_percentage=float(request.form.get('lean_mass_percentage')),
                waist_circumference=get_optional_float('waist_circumference'),
                hip_circumference=get_optional_float('hip_circumference'),
                bicep_circumference=get_optional_float('bicep_circumference'),
                thigh_circumference=get_optional_float('thigh_circumference'),
                chest_circumference=get_optional_float('chest_circumference')
            )
            db.session.add(measurement)
            db.session.commit()
            flash('Measurement added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error adding measurement: {str(e)}', 'danger')
    
    return render_template('add_measurement.html')

@app.route('/trends')
@login_required
def trends():
    # Check if viewing another user's trends (admin only)
    user_id = request.args.get('user_id', type=int)
    
    if user_id and user_id != session['user_id']:
        # Verify user is admin
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        user = User.query.get_or_404(user_id)
    else:
        user = User.query.get(session['user_id'])
    
    return render_template('trends.html', user=user)

@app.route('/all-data')
@login_required
def all_data():
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('Your account no longer exists. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    measurements = Measurement.query.filter_by(user_id=user.id).order_by(Measurement.timestamp.desc()).all()
    return render_template('all_data.html', user=user, measurements=measurements)

@app.route('/api/measurements/<int:user_id>')
@login_required
def get_measurements(user_id):
    # Check permission: users can only see their own data, admins can see all
    if not session.get('is_admin') and session['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    measurements = Measurement.query.filter_by(user_id=user_id).order_by(Measurement.timestamp).all()
    return jsonify([m.to_dict() for m in measurements])

@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
        else:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('admin_panel'))
    
    return render_template('create_user.html')

@app.route('/admin/view-user/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    measurements = Measurement.query.filter_by(user_id=user_id).order_by(Measurement.timestamp.desc()).all()
    return render_template('view_user.html', user=user, measurements=measurements)

@app.route('/delete-measurement/<int:measurement_id>', methods=['POST'])
@login_required
def delete_measurement(measurement_id):
    measurement = Measurement.query.get_or_404(measurement_id)
    
    # Check permission
    if not session.get('is_admin') and measurement.user_id != session['user_id']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(measurement)
    db.session.commit()
    flash('Measurement deleted successfully.', 'success')
    
    if session.get('is_admin'):
        return redirect(url_for('view_user', user_id=measurement.user_id))
    return redirect(url_for('dashboard'))

@app.route('/set-benchmark/<int:measurement_id>', methods=['POST'])
@login_required
def set_benchmark(measurement_id):
    measurement = Measurement.query.get_or_404(measurement_id)
    
    # Check that measurement belongs to current user
    if measurement.user_id != session['user_id']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get(session['user_id'])
    user.benchmark_measurement_id = measurement_id
    db.session.commit()
    
    print(f"DEBUG: Set benchmark for user {user.username} (id={user.id}) to measurement {measurement_id}")
    print(f"DEBUG: Benchmark saved: user.benchmark_measurement_id = {user.benchmark_measurement_id}")
    
    flash(f'Benchmark set to {measurement.timestamp.strftime("%b %d, %Y")}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/clear-benchmark', methods=['POST'])
@login_required
def clear_benchmark():
    user = User.query.get(session['user_id'])
    user.benchmark_measurement_id = None
    db.session.commit()
    flash('Benchmark cleared.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.get(session['user_id'])
        
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        elif len(new_password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

@app.route('/admin/add-entry', methods=['GET', 'POST'])
@admin_required
def admin_add_entry():
    users = User.query.filter_by(is_admin=False).order_by(User.username).all()
    today = datetime.now().strftime('%Y-%m-%d')
    preselected_user_id = request.args.get('user_id', type=int)

    if request.method == 'POST':
        try:
            def get_optional_float(field_name):
                value = request.form.get(field_name)
                return float(value) if value and value.strip() else None

            timestamp = datetime.strptime(request.form.get('timestamp'), '%Y-%m-%d')
            user_id = int(request.form.get('user_id'))

            measurement = Measurement(
                user_id=user_id,
                timestamp=timestamp,
                weight=float(request.form.get('weight')),
                bmi=float(request.form.get('bmi')),
                body_fat_percentage=float(request.form.get('body_fat_percentage')),
                visceral_fat_index=float(request.form.get('visceral_fat_index')),
                lean_mass_percentage=float(request.form.get('lean_mass_percentage')),
                waist_circumference=get_optional_float('waist_circumference'),
                hip_circumference=get_optional_float('hip_circumference'),
                bicep_circumference=get_optional_float('bicep_circumference'),
                thigh_circumference=get_optional_float('thigh_circumference'),
                chest_circumference=get_optional_float('chest_circumference')
            )
            db.session.add(measurement)
            db.session.commit()
            user = User.query.get(user_id)
            flash(f'Entry added successfully for {user.username}!', 'success')
            return redirect(url_for('admin_panel'))
        except Exception as e:
            flash(f'Error adding entry: {str(e)}', 'danger')

    return render_template('admin_add_entry.html', users=users, today=today, preselected_user_id=preselected_user_id)

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_panel'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('admin_panel'))

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create default admin if none exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')  # CHANGE THIS PASSWORD IMMEDIATELY
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created. Username: admin, Password: admin123")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
