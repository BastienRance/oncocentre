from flask import Flask
from models import db
from routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'carpem-oncocentre-dev-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oncocentre.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)