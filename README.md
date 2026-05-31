# AI Distributor Management System

A comprehensive web-based management system for distributor operations with AI features, built with Flask, SQLite, and vanilla JavaScript.

## 🚀 Features

### 1. **Authentication & Authorization**
- Login & Logout system
- Role-based access control (Admin, Manager, DSR)
- Session management
- Password hashing with Werkzeug

### 2. **Dashboard**
- Real-time statistics (Total Users, Active/Inactive counts)
- Zone-wise and role-wise distribution charts
- Interactive visualizations using Chart.js
- Quick overview of invoices

### 3. **User Management**
- Create, Read, Update, Delete users
- User fields: ID, Name, Phone, Email, Role, Zone, Status
- Pagination support
- Role-based access control

### 4. **Invoice System**
- Create invoices with multiple products
- Dynamic product line items
- Real-time total calculation
- Download invoices as PDF
- View invoice history
- Invoice storage in database

### 5. **Data Export**
- Export users to Excel (.xlsx)
- Export users to XML
- Export invoices to Excel
- Admin-only feature

### 6. **AI Features**
- **Clean Data**: Remove duplicate user records
- **Generate Summary**: Generate system summary reports in text format

### 7. **Database**
- SQLite database with SQLAlchemy ORM
- Persistent data storage
- Automatic schema creation
- Sample data initialization

## 📋 Requirements

- Python 3.7+
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Pandas 2.0.3
- ReportLab 4.0.4
- Openpyxl 3.1.2

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-distributor-system.git
cd ai-distributor-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
Open your browser and go to: `http://localhost:5000`

## 🔐 Default Credentials

```
Email: admin@distributor.com
Password: admin123
```

## 📁 Project Structure

```
ai-distributor-system/
├── app.py                          # Main Flask application
├── requirements.txt                # Project dependencies
├── distributor_system.db          # SQLite database (auto-created)
├── templates/
│   ├── base.html                  # Base template with sidebar
│   ├── login.html                 # Login page
│   ├── dashboard.html             # Dashboard with stats
│   ├── users.html                 # User management
│   ├── invoice.html               # Invoice system
│   ├── 404.html                   # Error page
│   └── 500.html                   # Error page
├── static/
│   ├── css/
│   │   └── style.css              # All styles
│   └── js/
│       └── script.js              # Frontend logic
└── README.md                       # Documentation
```

## 🎯 Usage Guide

### Admin Login
- Email: `admin@distributor.com`
- Password: `admin123`

### Add New User
1. Go to **Users** section
2. Click **Add New User** button
3. Fill in user details
4. Click **Save User**

### Create Invoice
1. Go to **Invoice** section
2. Click **Create New Invoice**
3. Enter customer name
4. Add products with quantity and price
5. Click **Create Invoice**
6. Download as PDF

### Export Data
1. Go to **Export** menu (Admin only)
2. Select format (Excel or XML)
3. Download file

### AI Tools
1. Go to **AI Tools** menu (Admin only)
2. **Clean Data**: Remove duplicates
3. **Generate Summary**: Create report

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    role VARCHAR(50) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Invoices Table
```sql
CREATE TABLE invoice (
    id INTEGER PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    products JSON,
    total_amount FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);
```

## 🔧 API Endpoints

### Authentication
- `GET/POST /` - Login
- `GET /logout` - Logout

### Dashboard
- `GET /dashboard` - Dashboard view

### Users
- `GET /users` - List all users
- `GET /api/users` - Get users as JSON
- `GET /api/users/<id>` - Get user details
- `POST /api/users/add` - Add new user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

### Invoices
- `GET /invoice` - Invoice page
- `GET /api/invoice/<id>` - Get invoice details
- `POST /api/invoice/create` - Create invoice
- `GET /invoice/<id>/pdf` - Download PDF

### Export
- `GET /export/users/excel` - Export users to Excel
- `GET /export/users/xml` - Export users to XML
- `GET /export/invoices/excel` - Export invoices to Excel

### AI Features
- `POST /api/ai/clean-duplicates` - Remove duplicates
- `POST /api/ai/generate-summary` - Generate summary

## 🎨 Features Breakdown

### Dashboard Widgets
- **Total Users Card** - Shows total user count
- **Active Users Card** - Shows active user percentage
- **Inactive Users Card** - Shows inactive user count
- **Total Invoices Card** - Shows invoice statistics
- **Zone Distribution Chart** - Doughnut chart
- **Role Distribution Chart** - Pie chart
- **Zone Summary Table** - Detailed breakdown

### User Management
- **Pagination**: 10 users per page
- **Search/Filter**: By role, zone, status
- **Actions**: Edit, Delete
- **Validation**: Email uniqueness, phone format
- **Password Hashing**: Werkzeug security

### Invoice System
- **Dynamic Products**: Add/remove product rows
- **Real-time Calculation**: Automatic total calculation
- **PDF Generation**: Professional invoice layout
- **Invoice History**: View all invoices
- **Status Tracking**: Pending/Completed

### Data Export
- **Excel Format**: Uses Pandas and Openpyxl
- **XML Format**: Standard XML structure
- **Timestamps**: Includes export date

### AI Features
- **Duplicate Detection**: Find duplicate emails
- **Data Cleaning**: Preserve first entry, remove others
- **Summary Generation**: Comprehensive system report

## 🔒 Security Considerations

1. **Password Hashing**: All passwords are hashed using Werkzeug
2. **Session Management**: Uses Flask sessions
3. **CSRF Protection**: Add CSRF tokens in production
4. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
5. **Authorization Checks**: Role-based decorators

## 📝 Customization

### Change Secret Key
In `app.py`, update:
```python
app.config['SECRET_KEY'] = 'your-new-secret-key'
```

### Add New Roles
Update user creation form and add role in role selection dropdown

### Modify Database
Update models in `app.py` and run:
```python
db.drop_all()
db.create_all()
```

### Customize Styling
Edit `static/css/style.css` for colors, fonts, and layouts

## 🐛 Troubleshooting

### Database not found
```bash
# Delete database and reinitialize
rm distributor_system.db
python app.py
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Port already in use
```bash
# Change port in app.py
app.run(port=5001)
```

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created as a full-stack web application example for distributor management.

## 📞 Support

For issues or questions, please create an issue in the repository.

## 🚀 Deployment

### Production Setup
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Add CSRF protection
4. Use environment variables for secrets
5. Configure proper database backups

### Example with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Future Enhancements

- [ ] Advanced search and filters
- [ ] Email notifications
- [ ] Mobile app version
- [ ] Advanced analytics
- [ ] Real-time sync
- [ ] Multi-user collaboration
- [ ] Inventory management
- [ ] Payment integration

---

**Version**: 1.0.0  
**Last Updated**: 2024
