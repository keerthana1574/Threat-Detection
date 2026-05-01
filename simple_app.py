from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'message': 'Server is running!'})

@app.route('/api/realtime/social-media/start', methods=['POST'])
def start_monitoring():
    data = request.get_json() or {}
    return jsonify({'success': True, 'message': 'Monitoring started'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)