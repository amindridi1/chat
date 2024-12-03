from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models.chat import Message
from datetime import datetime

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

@socketio.on('typing')
def handle_typing(data):
    room = data['room']
    username = data['username']
    emit('typing', {'username': username}, room=room)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    room = data['room']
    emit('stop_typing', room=room)