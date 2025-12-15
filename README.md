# TopStyle Business Management System

12A comprehensive business management system for tailoring and rental services, built with Django and modern web technologies.

## 🚀 Features

### Core Functionality
- **Order Management**: Create, track, and manage orders for rental, repair, and customization services
- **Customer Management**: Complete CRUD operations for customer data with order history
- **Inventory Management**: Track products, materials, and rental items with real-time status
- **Sales Tracking**: Monitor sales performance with detailed analytics and reports
- **Rental Management**: Handle rental items with due dates and overdue notifications
- **Activity Logging**: Comprehensive audit trail of all system activities

### Advanced Features
- **Real-time Dashboard**: Live statistics and performance metrics
- **QR Code Generation**: Generate QR codes for order tracking
- **PDF/Excel Reports**: Export data in multiple formats
- **Responsive Design**: Mobile-friendly interface with Bootstrap 5
- **Form Validation**: Client-side and server-side validation
- **Notification System**: Real-time alerts and notifications
- **Search & Filtering**: Advanced search capabilities across all modules

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Additional Libraries**:
  - Pillow (image processing)
  - qrcode (QR code generation)
  - reportlab (PDF generation)
  - openpyxl (Excel export)
  - django-crispy-forms (form styling)

## 📋 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CAPSTONE2.0_CURSUR
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate sample data (optional)**
   ```bash
   python manage.py populate_data
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open browser and go to `http://127.0.0.1:8000`
   - Login with your superuser credentials

## 📊 System Modules

### 1. Dashboard
- Real-time statistics and KPIs
- Quick action buttons
- Recent orders and low stock alerts
- Sales trends and charts
- Rental status overview

### 2. Order Management
- Create orders for rental, repair, and customization
- Order tracking with QR codes
- Payment processing
- Order status management
- Comprehensive order history

### 3. Customer Management
- Customer database with contact information
- Order history per customer
- Customer statistics and analytics
- Search and filter capabilities

### 4. Inventory Management
- Product catalog with categories
- Stock level monitoring
- Low stock alerts
- Product images and descriptions
- Inventory transactions tracking

### 5. Sales Analytics
- Sales performance metrics
- Revenue tracking
- Payment method analysis
- Top-selling products
- Monthly/daily sales trends

### 6. Rental Management
- Rental item tracking
- Due date monitoring
- Overdue notifications
- Return processing
- Rental status management

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=TopStyle
```

### Database Configuration
The system uses SQLite by default. To use PostgreSQL or MySQL, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📱 API Endpoints

### Customer API
- `GET /api/customers/` - List all customers
- `GET /api/customers/{id}/` - Get customer details

### Inventory API
- `GET /api/inventory-status/` - Get real-time inventory status
- `POST /api/sales-calculation/` - Calculate sales data

### Order API
- `POST /api/order-tracking/` - Track order status
- `POST /api/orders/create/` - Create new order

## 🎨 Customization

### Styling
- Modify `templates/business/base.html` for global styling
- Update CSS variables in the `<style>` section
- Customize Bootstrap theme colors

### Business Logic
- Update pricing in `templates/business/create_order.html`
- Modify order types in `business/models.py`
- Customize reports in `business/views.py`

## 📈 Performance Optimization

### Database Optimization
- Use `select_related()` and `prefetch_related()` for queries
- Add database indexes for frequently queried fields
- Implement caching for expensive operations

### Frontend Optimization
- Minify CSS and JavaScript files
- Optimize images
- Use CDN for static assets

## 🔒 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Input validation and sanitization
- Secure file upload handling
- SQL injection prevention

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 Deployment

### Production Settings
1. Set `DEBUG = False` in settings
2. Configure proper database
3. Set up static file serving
4. Configure email settings
5. Set up SSL certificate

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with core functionality
- Customer management system
- Order processing and tracking
- Inventory management
- Sales analytics
- Rental management
- Responsive design
- Notification system

## 🎯 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced reporting dashboard
- [ ] SMS integration for notifications
- [ ] Barcode scanning functionality
- [ ] Multi-location support
- [ ] Advanced user roles and permissions
- [ ] Integration with payment gateways
- [ ] Automated inventory reordering
- [ ] Customer loyalty program
- [ ] Advanced analytics and AI insights

---

**TopStyle Business Management System** - Streamlining your tailoring and rental business operations.

## 🔁 Quick start (Windows)

If you see an error like "\START_SYSTEM.bat : The term '\START_SYSTEM.bat' is not recognized...", that means PowerShell interpreted a leading backslash as an absolute path.

To start the system from the project root use one of these safe commands:

PowerShell (recommended):
```powershell
.\run-start.ps1
```

Cmd or double-clickable wrapper:
```powershell
.\run-start.bat
```

You can also run the built-in PowerShell starter directly with an execution policy bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\START_SYSTEM.ps1
```

These wrappers ensure the project scripts are executed from the repository folder so relative paths like `venv\` and `manage.py` resolve correctly.