from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.chat import chat_bp
from app.models.chat import ChatRoom, Message

@chat_bp.route('/rooms')
@login_required
def rooms():
    rooms = ChatRoom.query.all()
    return render_template('chat/rooms.html', rooms=rooms)

@chat_bp.route('/room/<int:room_id>')
@login_required
def room(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp).all()
    return render_template('chat/room.html', room=room, messages=messages)

@chat_bp.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        room = ChatRoom(name=name, description=description)
        room.members.append(current_user)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('chat.rooms'))
    return render_template('chat/create_room.html')