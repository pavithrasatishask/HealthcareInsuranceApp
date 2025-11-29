"""
Main Flask application for Healthcare Insurance API.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.users import users_bp
from routes.policies import policies_bp
from routes.claims import claims_bp

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(policies_bp)
app.register_blueprint(claims_bp)


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'message': 'Healthcare Insurance API is running',
        'version': '1.0.0',
        'status': 'healthy'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        exit(1)
    
    # Run the application
    app.run(debug=Config.FLASK_ENV == 'development', host='0.0.0.0', port=5000)

