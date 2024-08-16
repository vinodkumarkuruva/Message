from flask import render_template, url_for, flash, redirect, request
from flask_socketio import emit, join_room, leave_room
from app import app, db, socketio
from app.forms import RegistrationForm, LoginForm, InterestForm
from app.models import User, Interest, Message
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/users")
@login_required
def users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('users.html', users=users)

@app.route("/send_interest/<int:user_id>", methods=['GET', 'POST'])
@login_required
def send_interest(user_id):
    form = InterestForm()
    if form.validate_on_submit():
        interest = Interest(sender_id=current_user.id, recipient_id=user_id, message=form.message.data)
        db.session.add(interest)
        db.session.commit()
        flash('Interest sent!', 'success')
        return redirect(url_for('users'))
    return render_template('send_interest.html', form=form)

@app.route("/interests")
@login_required
def interests():
    received_interests = Interest.query.filter_by(recipient_id=current_user.id).all()
    return render_template('interests.html', interests=received_interests)

@app.route("/accept_interest/<int:interest_id>")
@login_required
def accept_interest(interest_id):
    interest = Interest.query.get_or_404(interest_id)
    if interest.recipient_id == current_user.id:
        interest.status = 'accepted'
        db.session.commit()
        flash('Interest accepted!', 'success')
        return redirect(url_for('chat', recipient_id=interest.sender_id))
    return redirect(url_for('interests'))

@app.route("/reject_interest/<int:interest_id>")
@login_required
def reject_interest(interest_id):
    interest = Interest.query.get_or_404(interest_id)
    if interest.recipient_id == current_user.id:
        interest.status = 'rejected'
        db.session.commit()
        flash('Interest rejected!', 'danger')
    return redirect(url_for('interests'))

@app.route("/chat/<int:recipient_id>")
@login_required
def chat(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    return render_template('chat.html', recipient=recipient)

@socketio.on('send_message')
def handle_send_message(data):
    message = Message(sender_id=current_user.id, recipient_id=data['recipient_id'], content=data['message'])
    db.session.add(message)
    db.session.commit()
    socketio.emit('receive_message', {'message': data['message'], 'user': current_user.username}, room=f'user_{data["recipient_id"]}')
    socketio.emit('receive_message', {'message': data['message'], 'user': current_user.username}, room=f'user_{current_user.id}')

@socketio.on('load_messages')
def handle_load_messages(data):
    recipient_id = data['recipient_id']
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id) |
        (Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp).all()
    emit('load_messages', [{'content': msg.content} for msg in messages], room=f'user_{current_user.id}')

@socketio.on('connect')
def handle_connect():
    join_room(f'user_{current_user.id}')

@socketio.on('disconnect')
def handle_disconnect():
    leave_room(f'user_{current_user.id}')
