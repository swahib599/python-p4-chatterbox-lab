from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False  # Make JSON output pretty

CORS(app)  # Enable CORS for all routes
migrate = Migrate(app, db)

db.init_app(app)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Welcome to the Message API!"

# GET all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages]), 200

# POST a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    
    # Error handling for missing fields
    if not data or 'body' not in data or 'username' not in data:
        return jsonify({'error': 'Invalid input'}), 400  # Error response

    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()
    return jsonify(new_message.to_dict()), 201

# PATCH (update) a message by ID
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()
    
    # Error handling for missing fields
    if not data or 'body' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    # Use db.session.get() instead of the deprecated query.get()
    message = db.session.get(Message, id)
    if message is None:
        return jsonify({'error': 'Message not found'}), 404

    message.body = data['body']
    db.session.commit()
    return jsonify(message.to_dict()), 200

# DELETE a message by ID
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # Use db.session.get() instead of the deprecated query.get()
    message = db.session.get(Message, id)
    if message is None:
        return jsonify({'error': 'Message not found'}), 404

    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Message deleted successfully'}), 204

if __name__ == '__main__':
    app.run(port=5555)
