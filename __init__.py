from flask import Flask, request
from flask_login import LoginManager
from models.user_model import User, db
from flask_cors import CORS
import os

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Get environment
    env = os.environ.get('FLASK_ENV', 'development')
    is_development = env == 'development'
    
    # Get allowed origins from environment or use a default for development
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',') if not is_development else '*'
    
    # Fix CORS configuration
    CORS(
        app, 
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type", "Authorization"],
        vary_header=True
    )
    
    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        # Get the origin from the request
        origin = request.headers.get('Origin', '')
        
        # In development mode, allow all origins
        if is_development:
            response.headers.add('Access-Control-Allow-Origin', origin or '*')
        else:
            # In production, check if origin is allowed
            if origin and (allowed_origins == '*' or origin in (allowed_origins if isinstance(allowed_origins, list) else [allowed_origins])):
                response.headers.add('Access-Control-Allow-Origin', origin)
        
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
    
    # Set up LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints with URL prefixes
    from routes.lead_routes import lead_bp
    from routes.auth_routes import auth_bp
    
    app.register_blueprint(lead_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='')
    
    # Handle OPTIONS request for root to support CORS preflight
    @app.route('/', methods=['GET', 'OPTIONS'])
    def index():
        if request.method == 'OPTIONS':
            return '', 200
        return 'LeadGen API is running!'
    
    return app

# Create application instance
app = create_app()
