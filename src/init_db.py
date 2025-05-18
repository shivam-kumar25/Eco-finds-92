from src import create_app, db
from src.models.category import Category
from src.models.user import User
from src.models.product import Product
from datetime import datetime, timedelta
import sys

def reset_db():
    """Drop all tables and recreate them"""
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print('All tables dropped!')
        
        # Create tables
        db.create_all()
        print('Tables recreated successfully!')

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
          # Create demo users if no users exist
        if User.query.count() == 0:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('adminpassword')
            
            seller1 = User(username='ecoSeller', email='seller@example.com', is_admin=False)
            seller1.set_password('password')
            
            buyer1 = User(username='greenBuyer', email='buyer@example.com', is_admin=False)
            buyer1.set_password('password')
            
            db.session.add_all([admin, seller1, buyer1])
            db.session.commit()
            print('Demo users created!')
            
            # Add sample products if none exist
            if Product.query.count() == 0:
                # Get categories
                electronics = Category.query.filter_by(name='Electronics').first()
                clothing = Category.query.filter_by(name='Clothing').first()
                home_garden = Category.query.filter_by(name='Home & Garden').first()
                books_media = Category.query.filter_by(name='Books & Media').first()
                sports = Category.query.filter_by(name='Sports & Outdoors').first()
                  # Sample products
                products = [
                    Product(
                        name='Refurbished Smartphone',
                        description='Fully functional smartphone in excellent condition. Battery health at 90%. Comes with charger and box.',
                        price=249.99,
                        condition='Refurbished - Excellent',
                        image_filename='smartphone.jpg',
                        seller_id=seller1.id,
                        category_id=electronics.id,
                        created_at=datetime.utcnow() - timedelta(days=5),
                        eco_impact_score=4,
                        estimated_co2_saved=35.2,
                        original_packaging=True
                    ),
                    Product(
                        name='Vintage Denim Jacket',
                        description='Genuine vintage denim jacket from the 90s. Size M. Great condition with minimal wear.',
                        price=45.00,
                        condition='Used - Very Good',
                        image_filename='denim_jacket.jpg',
                        seller_id=seller1.id,
                        category_id=clothing.id,
                        created_at=datetime.utcnow() - timedelta(days=10),
                        eco_impact_score=5,
                        estimated_co2_saved=12.7,
                        original_packaging=False
                    ),
                    Product(
                        name='Bamboo Cutlery Set',
                        description='Eco-friendly bamboo cutlery set with knife, fork, spoon and chopsticks. Perfect for camping or daily use.',
                        price=12.50,
                        condition='Used - Like New',
                        image_filename='bamboo_cutlery.jpg',
                        seller_id=admin.id,
                        category_id=home_garden.id,
                        created_at=datetime.utcnow() - timedelta(days=3),
                        eco_impact_score=5,
                        estimated_co2_saved=0.8,
                        original_packaging=True
                    ),
                    Product(
                        name='Classic Novel Collection',
                        description='Set of 5 classic novels in paperback. All in good condition with minimal highlighting.',
                        price=18.99,
                        condition='Used - Good',
                        image_filename='novels.jpg',
                        seller_id=admin.id,
                        category_id=books_media.id,
                        created_at=datetime.utcnow() - timedelta(days=7),
                        eco_impact_score=3,
                        estimated_co2_saved=5.3,
                        original_packaging=False
                    ),
                   
                    Product(
                        name='Wooden Chess Set',
                        description='Hand-carved wooden chess set with inlaid board. Minor wear but all pieces present and in great condition.',
                        price=35.99,                        condition='Used - Good',
                        image_filename='chess_set.jpg',
                        seller_id=buyer1.id,
                        category_id=books_media.id,
                        created_at=datetime.utcnow() - timedelta(days=9),
                        eco_impact_score=3,
                        estimated_co2_saved=3.7,
                        original_packaging=False
                    )
                ]
                
                db.session.add_all(products)
                db.session.commit()
                print('Sample products created!')
        
        print('Database initialized successfully!')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_db()
    init_db()
