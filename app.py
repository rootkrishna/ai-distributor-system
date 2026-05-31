"""
AI Distributor Management System
Backend: Flask with SQLite
Author: AI Development Team
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os
import json
import pandas as pd
from xml.etree.ElementTree import Element, SubElement, ElementTree
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from functools import wraps
import io

# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///distributor_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize Database
db = SQLAlchemy(app)

# ===========================
# DATABASE MODELS
# ===========================

class User(db.Model):
    """User model for system users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Admin, Manager, DSR
    zone = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<User {self.name}>'


class Invoice(db.Model):
    """Invoice model for invoices"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    products = db.Column(db.JSON)  # Store as JSON: [{"name": "", "qty": 0, "price": 0}]
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Pending')  # Pending, Completed
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


# ===========================
# AUTHENTICATION DECORATOR
# ===========================

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ===========================
# ROUTES - AUTHENTICATION
# ===========================

@app.route('/', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('login'))


# ===========================
# ROUTES - DASHBOARD
# ===========================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with stats and charts"""
    # Calculate statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(status='Active').count()
    inactive_users = User.query.filter_by(status='Inactive').count()
    
    # Zone-wise summary
    zones = db.session.query(User.zone, db.func.count(User.id)).group_by(User.zone).all()
    zone_summary = {zone: count for zone, count in zones}
    
    # Role-wise summary
    roles = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
    role_summary = {role: count for role, count in roles}
    
    # Total invoices
    total_invoices = Invoice.query.count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'zone_summary': zone_summary,
        'role_summary': role_summary,
        'total_invoices': total_invoices,
    }
    
    return render_template('dashboard.html', **context)


# ===========================
# ROUTES - USER MANAGEMENT
# ===========================

@app.route('/users')
@login_required
def users():
    """Display all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    return render_template('users.html', users=users)


@app.route('/api/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add new user via API"""
    try:
        data = request.json
        
        # Validate required fields
        if not all(k in data for k in ['user_id', 'name', 'email', 'password', 'phone', 'role', 'zone']):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(user_id=data['user_id']).first():
            return jsonify({'status': 'error', 'message': 'User ID already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
        
        # Create new user
        new_user = User(
            user_id=data['user_id'],
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            phone=data['phone'],
            role=data['role'],
            zone=data['zone'],
            status=data.get('status', 'Active')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'User added successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_user(user_id):
    """Manage user: Get, Edit, Delete"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # GET user details
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'zone': user.zone,
            'status': user.status
        })
    
    # Check authorization
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    # UPDATE user
    if request.method == 'PUT':
        try:
            data = request.json
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.role = data.get('role', user.role)
            user.zone = data.get('zone', user.zone)
            user.status = data.get('status', user.status)
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User updated successfully'})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    # DELETE user
    if request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User deleted successfully'})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/users')
@login_required
def get_users_json():
    """Get all users as JSON"""
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'user_id': u.user_id,
        'name': u.name,
        'email': u.email,
        'phone': u.phone,
        'role': u.role,
        'zone': u.zone,
        'status': u.status,
        'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for u in users])


# ===========================
# ROUTES - INVOICE MANAGEMENT
# ===========================

@app.route('/invoice')
@login_required
def invoice():
    """Invoice creation page"""
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoice.html', invoices=invoices)


@app.route('/api/invoice/create', methods=['POST'])
@login_required
def create_invoice():
    """Create new invoice"""
    try:
        data = request.json
        
        if not data.get('customer_name') or not data.get('products'):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Calculate total amount
        total = sum(p['quantity'] * p['price'] for p in data['products'])
        
        # Generate invoice number
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        invoice_num = f"INV-{(last_invoice.id if last_invoice else 0) + 1:05d}"
        
        # Create invoice
        new_invoice = Invoice(
            invoice_number=invoice_num,
            customer_name=data['customer_name'],
            products=data['products'],
            total_amount=total,
            created_by=session.get('name')
        )
        
        db.session.add(new_invoice)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Invoice created successfully',
            'invoice_id': new_invoice.id,
            'invoice_number': invoice_num
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/invoice/<int:invoice_id>')
@login_required
def get_invoice(invoice_id):
    """Get invoice details"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        return jsonify({'status': 'error', 'message': 'Invoice not found'}), 404
    
    return jsonify({
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'customer_name': invoice.customer_name,
        'products': invoice.products,
        'total_amount': invoice.total_amount,
        'status': invoice.status,
        'created_at': invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'created_by': invoice.created_by
    })


@app.route('/invoice/<int:invoice_id>/pdf')
@login_required
def download_invoice_pdf(invoice_id):
    """Generate and download invoice as PDF"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        return jsonify({'status': 'error', 'message': 'Invoice not found'}), 404
    
    try:
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30
        )
        story.append(Paragraph('INVOICE', title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice details
        details = [
            ['Invoice Number:', invoice.invoice_number],
            ['Customer Name:', invoice.customer_name],
            ['Date:', invoice.created_at.strftime('%Y-%m-%d')],
            ['Created By:', invoice.created_by]
        ]
        
        details_table = Table(details, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4788')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Products table
        products_data = [['Product', 'Quantity', 'Price', 'Total']]
        for product in invoice.products:
            products_data.append([
                product['name'],
                str(product['quantity']),
                f"${product['price']:.2f}",
                f"${product['quantity'] * product['price']:.2f}"
            ])
        
        products_table = Table(products_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        products_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(products_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Total
        total_style = ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            alignment=2
        )
        story.append(Paragraph(f'<b>Total Amount: ${invoice.total_amount:.2f}</b>', total_style))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{invoice.invoice_number}.pdf'
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===========================
# ROUTES - EXPORT DATA
# ===========================

@app.route('/export/users/excel')
@login_required
@admin_required
def export_users_excel():
    """Export users to Excel"""
    try:
        users = User.query.all()
        
        # Create DataFrame
        data = [{
            'User ID': u.user_id,
            'Name': u.name,
            'Email': u.email,
            'Phone': u.phone,
            'Role': u.role,
            'Zone': u.zone,
            'Status': u.status,
            'Created At': u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for u in users]
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, sheet_name='Users', index=False)
        excel_buffer.seek(0)
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/export/users/xml')
@login_required
@admin_required
def export_users_xml():
    """Export users to XML"""
    try:
        users = User.query.all()
        
        # Create XML structure
        root = Element('users')
        for user in users:
            user_elem = SubElement(root, 'user')
            
            SubElement(user_elem, 'id').text = str(user.id)
            SubElement(user_elem, 'user_id').text = user.user_id
            SubElement(user_elem, 'name').text = user.name
            SubElement(user_elem, 'email').text = user.email
            SubElement(user_elem, 'phone').text = user.phone
            SubElement(user_elem, 'role').text = user.role
            SubElement(user_elem, 'zone').text = user.zone
            SubElement(user_elem, 'status').text = user.status
            SubElement(user_elem, 'created_at').text = user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create file
        xml_buffer = io.BytesIO()
        tree = ElementTree(root)
        tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
        xml_buffer.seek(0)
        
        return send_file(
            xml_buffer,
            mimetype='application/xml',
            as_attachment=True,
            download_name=f'users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/export/invoices/excel')
@login_required
def export_invoices_excel():
    """Export invoices to Excel"""
    try:
        invoices = Invoice.query.all()
        
        # Create DataFrame
        data = [{
            'Invoice Number': inv.invoice_number,
            'Customer Name': inv.customer_name,
            'Total Amount': inv.total_amount,
            'Status': inv.status,
            'Created By': inv.created_by,
            'Created At': inv.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for inv in invoices]
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, sheet_name='Invoices', index=False)
        excel_buffer.seek(0)
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'invoices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===========================
# ROUTES - AI FEATURES
# ===========================

@app.route('/api/ai/clean-duplicates', methods=['POST'])
@login_required
@admin_required
def clean_duplicates():
    """Remove duplicate users by email"""
    try:
        # Find duplicates
        duplicates = db.session.query(User.email, db.func.count(User.id)).group_by(User.email).having(db.func.count(User.id) > 1).all()
        
        deleted_count = 0
        for email, count in duplicates:
            # Keep first, delete others
            users = User.query.filter_by(email=email).order_by(User.id).all()
            for user in users[1:]:
                db.session.delete(user)
                deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Cleaned {deleted_count} duplicate records',
            'duplicates_found': len(duplicates)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ai/generate-summary', methods=['POST'])
@login_required
@admin_required
def generate_summary():
    """Generate basic data summary report"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(status='Active').count()
        inactive_users = User.query.filter_by(status='Inactive').count()
        
        roles = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
        zones = db.session.query(User.zone, db.func.count(User.id)).group_by(User.zone).all()
        
        total_invoices = Invoice.query.count()
        total_revenue = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
        
        summary = f"""
=== AI DISTRIBUTOR MANAGEMENT SYSTEM - SUMMARY REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

USER STATISTICS:
- Total Users: {total_users}
- Active Users: {active_users} ({(active_users/total_users*100 if total_users > 0 else 0):.1f}%)
- Inactive Users: {inactive_users} ({(inactive_users/total_users*100 if total_users > 0 else 0):.1f}%)

ROLE DISTRIBUTION:
"""
        for role, count in roles:
            summary += f"- {role}: {count}\n"
        
        summary += "\nZONE DISTRIBUTION:\n"
        for zone, count in zones:
            summary += f"- {zone}: {count}\n"
        
        summary += f"""
INVOICE STATISTICS:
- Total Invoices: {total_invoices}
- Total Revenue: ${total_revenue:.2f}
- Average Invoice Value: ${(total_revenue/total_invoices if total_invoices > 0 else 0):.2f}

=== END OF REPORT ===
"""
        
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===========================
# DATABASE INITIALIZATION
# ===========================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        if not User.query.filter_by(email='admin@distributor.com').first():
            admin = User(
                user_id='ADMIN001',
                name='Admin User',
                email='admin@distributor.com',
                password=generate_password_hash('admin123'),
                phone='9999999999',
                role='Admin',
                zone='Headquarters',
                status='Active'
            )
            db.session.add(admin)
            
            # Add sample users
            sample_users = [
                User(
                    user_id='MGR001',
                    name='John Manager',
                    email='manager1@distributor.com',
                    password=generate_password_hash('pass123'),
                    phone='8888888888',
                    role='Distributor Manager',
                    zone='North Zone',
                    status='Active'
                ),
                User(
                    user_id='DSR001',
                    name='Sarah DSR',
                    email='dsr1@distributor.com',
                    password=generate_password_hash('pass123'),
                    phone='7777777777',
                    role='DSR',
                    zone='North Zone',
                    status='Active'
                ),
                User(
                    user_id='DSR002',
                    name='Mike DSR',
                    email='dsr2@distributor.com',
                    password=generate_password_hash('pass123'),
                    phone='6666666666',
                    role='DSR',
                    zone='South Zone',
                    status='Active'
                ),
            ]
            
            for user in sample_users:
                db.session.add(user)
            
            db.session.commit()
            print("Database initialized successfully!")


# ===========================
# ERROR HANDLERS
# ===========================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


# ===========================
# MAIN EXECUTION
# ===========================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
