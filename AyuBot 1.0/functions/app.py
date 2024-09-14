import os
from flask import jsonify
from app import app

@app.route('/api/hello')
def hello(event, context):
    return jsonify({'message': 'Hello from Flask!'})