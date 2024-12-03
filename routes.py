from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import app, db, socketio, login_manager
from models import User, Message, ChatRoom
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat_rooms'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('chat_rooms'))
            
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/chat_rooms')
@login_required
def chat_rooms():
    rooms = ChatRoom.query.all()
    return render_template('chat_rooms.html', rooms=rooms)

@app.route('/room/<int:room_id>')
@login_required
def room(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp).all()
    return render_template('room.html', room=room, messages=messages)

@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        room = ChatRoom(name=name, description=description)
        room.members.append(current_user)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('chat_rooms'))
    return render_template('create_room.html')

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{current_user.username} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{current_user.username} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    content = data['message']
    room_id = data['room']
    
    message = Message(content=content, user_id=current_user.id, room_id=room_id)
    db.session.add(message)
    db.session.commit()
    
    emit('message', {
        'msg': content,
        'user': current_user.username,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }, room=room_id)