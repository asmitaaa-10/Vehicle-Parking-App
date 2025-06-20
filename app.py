from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from sqlalchemy import func

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'app123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CHART_FOLDER'] = os.path.join(os.getcwd(), 'charts')
    os.makedirs(app.config['CHART_FOLDER'], exist_ok=True)
    app.config['PASSWORD_HASH'] = 'app123'
    db.init_app(app)
    return app

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(20), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan')

class Parking(db.Model):
    __tablename__ = 'parking'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(20), nullable=False)
    pin_code = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', back_populates='parking', cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='A')
    parking = db.relationship('Parking', back_populates='spots')
    bookings = db.relationship('Booking', back_populates='spot', cascade='all, delete-orphan')

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='O')
    parking_cost = db.Column(db.Float, nullable=False)
    user = db.relationship('User', back_populates='bookings')
    spot = db.relationship('ParkingSpot', back_populates='bookings')

def create_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', fullname='Admin', address='Admin123', pincode='123456',
                     password=generate_password_hash('app123'))
        db.session.add(admin)
        db.session.commit()

app = create_app()
app.app_context().push()
with app.app_context():
    db.create_all()
    create_admin()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if not check_password_hash(user.password, password):
                flash("Invalid password.", "danger")
                return redirect(url_for('login'))
            session['username'] = username
            if user.username == 'admin':
                return redirect(url_for('admin'))
            else:
                session['user_id'] = user.id
                return redirect(url_for('user'))
        else:
            flash("User not found.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        address = request.form['address']
        pincode = request.form['pincode']
        user = User(username=username, password=generate_password_hash(password), fullname=fullname, address=address,
                    pincode=pincode)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('login'))

    query = request.args.get('query')

    if query:
        parkings = Parking.query.filter(Parking.prime_location_name.ilike(f'%{query}%')).all()
    else:
        parkings = Parking.query.all()

    available_counts = {}
    for parking in parkings:
        available_counts[parking.id] = ParkingSpot.query.filter_by(parking_id=parking.id, status='A').count()

    return render_template('user.html', parkings=parkings, available_counts=available_counts, query=query)

@app.route('/parking', methods=['GET', 'POST'])
def parking():
    if 'username' not in session:
        return redirect(url_for('login'))
    parkings = Parking.query.all()
    available_counts = {}
    for parking in parkings:
        available_counts[parking.id] = ParkingSpot.query.filter_by(parking_id=parking.id, status='A').count()
    return render_template('parking.html', parkings=parkings, available_counts=available_counts)

@app.route('/add_parking', methods=['GET', 'POST'])
def add_parking():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        prime_location_name = request.form['prime_location_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price = float(request.form['price'])
        number_of_spots = int(request.form['number_of_spots'])
        parking = Parking(prime_location_name=prime_location_name,
                          address=address,
                          pin_code=pin_code,
                          price=price, number_of_spots=number_of_spots)
        db.session.add(parking)
        db.session.flush()  # flush to get parking.id before adding spots
        for i in range(1, number_of_spots + 1):
            spot = ParkingSpot(parking_id=parking.id, spot_number=i, status='A')
            db.session.add(spot)
        db.session.commit()
        flash("Parking added successfully.", "success")
        return redirect(url_for('parking'))
    return render_template('add_parking.html')

@app.route('/edit_parking/<int:parking_id>', methods=['GET', 'POST'])
def edit_parking(parking_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    parking = Parking.query.get_or_404(parking_id)
    if request.method == 'POST':
        parking.prime_location_name = request.form['prime_location_name']
        parking.address = request.form['address']
        parking.pin_code = request.form['pin_code']
        parking.price = float(request.form['price'])
        new_spot_count = int(request.form['number_of_spots'])

        current_spots = {spot.spot_number: spot for spot in parking.spots}

        for i in range(1, new_spot_count + 1):
            if i not in current_spots:
                spot = ParkingSpot(parking_id=parking.id, spot_number=i, status='A')
                db.session.add(spot)

        for i in range(new_spot_count + 1, len(current_spots) + 1):
            spot = current_spots.get(i)
            if spot:
                has_history = Booking.query.filter_by(spot_id=spot.id).first()
                if spot.status == 'A' and not has_history:
                    db.session.delete(spot)
        parking.number_of_spots = new_spot_count
        db.session.commit()
        flash("Parking updated successfully.", "success")
        return redirect(url_for('parking'))
    return render_template('edit_parking.html', parking=parking)

@app.route('/booking/<int:parking_id>', methods=['GET', 'POST'])
def booking(parking_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    parking = Parking.query.get_or_404(parking_id)
    user_id = session['user_id']

    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']

        # Find available spot with status 'A' (Available), case insensitive check
        available_spot = ParkingSpot.query.filter(
            ParkingSpot.parking_id == parking.id,
            func.lower(ParkingSpot.status) == 'a'
        ).first()

        print(f"Available spot found for booking: {available_spot}")  # Debug print

        if not available_spot:
            flash('No available spots for booking.', 'danger')
            return redirect(url_for('user'))

        # Mark spot as occupied
        available_spot.status = 'O'

        # Create booking with end_time=None (no sentinel)
        booking = Booking(
            user_id=user_id,
            vehicle_number=vehicle_number,
            spot_id=available_spot.id,
            start_time=datetime.now(),
            end_time=None,
            status='O',
            parking_cost=parking.price
        )
        db.session.add(booking)
        db.session.commit()
        flash('Spot booked successfully!', 'success')
        return redirect(url_for('user'))

    return render_template('booking.html', spot_id=parking_id, user_id=user_id, parking=parking)

@app.route('/delete_parking/<int:parking_id>', methods=['POST'])
def delete_parking(parking_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    parking = Parking.query.get_or_404(parking_id)
    if parking.spots:
        for spot in parking.spots:
            if spot.status == 'O':
                flash('Cannot delete a parking lot with active bookings.', 'error')
                return redirect(url_for('parking'))
            db.session.delete(spot)
    db.session.delete(parking)
    db.session.commit()
    flash("Parking deleted successfully.", "success")
    return redirect(url_for('parking'))

@app.route('/history', methods=['GET', 'POST'])
def history():
    if 'username' not in session:
        return redirect(url_for('login'))

    all_bookings = Booking.query.filter_by(user_id=session['user_id']).all()

    # Fix: lowercase status comparison
    recent_bookings = [b for b in all_bookings if b.status.lower().strip() == 'o']
    past_bookings = [b for b in all_bookings if b.status.lower().strip() != 'o']

    return render_template('booking_history.html',
                           recent_bookings=recent_bookings,
                           past_bookings=past_bookings)


@app.route('/delete_spot/<int:spot_id>', methods=['GET', 'POST'])
def delete_spot(spot_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status == 'O':
        flash('Cannot delete a spot with active bookings.', 'error')
        return redirect(url_for('parking'))
    db.session.delete(spot)
    db.session.commit()
    flash("Spot deleted successfully.", "success")
    return redirect(url_for('parking'))

@app.route('/release/<int:booking_id>', methods=['GET', 'POST'])
def release(booking_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    booking = Booking.query.get_or_404(booking_id)

    # Check if already released
    if booking.status != 'O' or booking.end_time is not None:
        flash('This spot has already been released.', 'warning')
        return redirect(url_for('history'))

    booking.end_time = datetime.now()
    duration = booking.end_time - booking.start_time
    hours = max(1, int(duration.total_seconds() // 3600))  # minimum 1 hour charge
    booking.parking_cost = hours * booking.spot.parking.price
    booking.status = 'Released'
    booking.spot.status = 'A'  # mark spot as available again

    db.session.commit()
    flash('Parking spot released successfully!', 'success')
    return redirect(url_for('history'))

if __name__ == '__main__':
    app.run(debug=True)
