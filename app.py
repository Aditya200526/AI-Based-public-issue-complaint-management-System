from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "hackathon_secret_key_2025_civic_ai"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ==================== MODELS ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    complaints = db.relationship('Complaint', backref='user', lazy=True)


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(20), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    landmark = db.Column(db.String(200))
    image = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Resolved
    ai_suggested_category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== AI CATEGORIZATION ====================
def ai_categorize(description):
    """AI-assisted complaint categorization using keyword matching"""
    text = description.lower()

    rules = {
        'Streetlight / Electricity': [
            'streetlight', 'street light', 'light', 'electricity', 'power',
            'pole', 'bulb', 'lamp', 'dark', 'not working light', 'no light'
        ],
        'Road / Pothole': [
            'pothole', 'road', 'street', 'path', 'asphalt', 'crack',
            'broken road', 'digging', 'uneven', 'damaged road', 'hole in road'
        ],
        'Water Supply': [
            'water', 'leakage', 'pipe', 'tap', 'supply', 'drinking water',
            'pipeline', 'no water', 'water shortage', 'burst pipe'
        ],
        'Drainage / Sewage': [
            'drain', 'drainage', 'sewage', 'sewer', 'gutter', 'overflow',
            'blockage', 'clogged', 'stagnant', 'dirty water'
        ],
        'Garbage / Sanitation': [
            'garbage', 'trash', 'waste', 'dustbin', 'cleaning', 'sanitation',
            'rubbish', 'litter', 'dump', 'uncollected'
        ],
        'Other': []
    }

    scores = {}
    for category, keywords in rules.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[category] = score

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'Other'


# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not name or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['is_admin'] = user.is_admin
            flash(f'Welcome, {user.name}!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))


@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    complaints = Complaint.query.filter_by(user_id=session['user_id']).order_by(Complaint.created_at.desc()).all()
    return render_template('user_dashboard.html', complaints=complaints)


@app.route('/submit', methods=['GET', 'POST'])
def submit_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        description = request.form['description'].strip()
        landmark = request.form.get('landmark', '').strip()
        category = request.form.get('category', '').strip()

        if not description:
            flash('Description is required!', 'danger')
            return redirect(url_for('submit_complaint'))

        # AI Assistance
        ai_category = ai_categorize(description)
        if not category or category == 'Auto':
            category = ai_category

        # Generate unique complaint ID
        count = Complaint.query.count() + 1
        complaint_id = f"CMP{datetime.now().strftime('%Y%m%d')}{count:04d}"

        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                image_filename = f"{complaint_id}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        complaint = Complaint(
            complaint_id=complaint_id,
            user_id=session['user_id'],
            category=category,
            description=description,
            landmark=landmark,
            image=image_filename,
            ai_suggested_category=ai_category,
            status='Pending'
        )
        db.session.add(complaint)
        db.session.commit()

        flash(f'Complaint submitted successfully! Your ID: {complaint_id}', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('submit_complaint.html')


@app.route('/track/<complaint_id>')
def track(complaint_id):
    complaint = Complaint.query.filter_by(complaint_id=complaint_id).first_or_404()
    return render_template('track.html', complaint=complaint)


@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))

    status_filter = request.args.get('status', 'All')
    query = Complaint.query
    if status_filter != 'All':
        query = query.filter_by(status=status_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    stats = {
        'total': Complaint.query.count(),
        'pending': Complaint.query.filter_by(status='Pending').count(),
        'in_progress': Complaint.query.filter_by(status='In Progress').count(),
        'resolved': Complaint.query.filter_by(status='Resolved').count()
    }
    return render_template('admin_dashboard.html', complaints=complaints, stats=stats, current_filter=status_filter)


@app.route('/admin/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    complaint = Complaint.query.get_or_404(id)
    new_status = request.form['status']
    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Status updated to {new_status}', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== INIT ====================
def create_admin():
    admin = User.query.filter_by(email='admin@civic.ai').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@civic.ai',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created → email: admin@civic.ai | password: admin123")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    print("\n🚀 AI Public Complaint System is running!")
    print("👉 Open: http://127.0.0.1:5000")
    print("👤 Admin Login: admin@civic.ai / admin123\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
