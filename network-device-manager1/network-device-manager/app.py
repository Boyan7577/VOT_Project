from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for flash messages
db = SQLAlchemy(app)

# Network Device Model
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False, unique=True)  # Assuming IPv4 format
    device_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)

# Function to validate IP addresses
def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if pattern.match(ip):
        parts = ip.split(".")
        return all(0 <= int(part) < 256 for part in parts)
    return False

# Home route to display devices
@app.route('/')
def index():
    devices = Device.query.all()
    return render_template('index.html', devices=devices)

# Route to add a new device
@app.route('/add', methods=['POST'])
def add_device():
    ip_address = request.form.get('ip_address')
    device_type = request.form.get('device_type')
    location = request.form.get('location')

    # Validate IP address and device type
    valid_device_types = ['Router', 'Switch', 'PC', 'Server']
    if not is_valid_ip(ip_address):
        flash("Invalid IP address format. Please enter a valid IPv4 address.", "error")
        return redirect(url_for('index'))
    elif device_type not in valid_device_types:
        flash(f"Invalid device type. Choose one of {', '.join(valid_device_types)}.", "error")
        return redirect(url_for('index'))

    # Check if device with the same IP address already exists
    existing_device = Device.query.filter_by(ip_address=ip_address).first()
    if existing_device:
        flash("A device with this IP address already exists. Please use a unique IP address.", "error")
    else:
        # Add device if all checks pass
        new_device = Device(ip_address=ip_address, device_type=device_type, location=location)
        db.session.add(new_device)
        db.session.commit()
        flash("Device added successfully!", "success")

    return redirect(url_for('index'))

# Route to delete a device
@app.route('/delete/<int:id>')
def delete_device(id):
    device = Device.query.get_or_404(id)
    db.session.delete(device)
    db.session.commit()
    flash("Device deleted successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the app is in an application context for db.create_all()
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True, host='0.0.0.0', port=5000)
