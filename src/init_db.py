from src import create_app, db
from src.models.category import Category
from src.models.user import User

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have categories
        if Category.query.count() == 0:
            # Create default categories
            categories = [
                Category(name='Electronics', description='Electronic devices and gadgets'),
                Category(name='Clothing', description='Sustainable and second-hand clothing'),
                Category(name='Home & Garden', description='Eco-friendly home products and garden items'),
                Category(name='Books & Media', description='Used books, movies, and music'),
                Category(name='Sports & Outdoors', description='Sporting goods and outdoor equipment')
            ]
            
            db.session.add_all(categories)
            db.session.commit()
            print('Default categories created!')
        
        # Create a demo admin user if no users exist
        if User.query.count() == 0:
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('adminpassword')
            db.session.add(admin)
            db.session.commit()
            print('Demo admin user created!')
        
        print('Database initialized successfully!')

if __name__ == '__main__':
    init_db()
