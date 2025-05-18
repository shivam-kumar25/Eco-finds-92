from src import create_app, db
from src.models.category import Category
from src.models.user import User
from src.models.product import Product
from datetime import datetime, timedelta

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
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('adminpassword')
            
            seller1 = User(username='ecoSeller', email='seller@example.com')
            seller1.set_password('password')
            
            buyer1 = User(username='greenBuyer', email='buyer@example.com')
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
                        image_url='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500',
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
                        image_url='https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=500',
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
                        image_url='https://images.unsplash.com/photo-1584269600519-112d071b35e6?w=500',
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
                        image_url='https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500',
                        seller_id=admin.id,
                        category_id=books_media.id,
                        created_at=datetime.utcnow() - timedelta(days=7),
                        eco_impact_score=3,
                        estimated_co2_saved=5.3,
                        original_packaging=False
                    ),
                    Product(
                        name='Yoga Mat (Barely Used)',
                        description='High-quality yoga mat, 6mm thickness. Used only a few times and thoroughly cleaned.',
                        price=15.00,
                        condition='Used - Like New',
                        image_url='https://images.unsplash.com/photo-1592432678016-e910b452f9a2?w=500',
                        seller_id=seller1.id,
                        category_id=sports.id,
                        created_at=datetime.utcnow() - timedelta(days=2),
                        eco_impact_score=4,
                        estimated_co2_saved=3.5,
                        original_packaging=False
                    ),
                    Product(
                        name='Reusable Water Bottle',
                        description='Stainless steel water bottle, keeps drinks cold for 24 hours or hot for 12 hours. Minor scratches but perfect functionality.',
                        price=10.99,
                        condition='Used - Good',
                        image_url='https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500',
                        seller_id=admin.id,
                        category_id=home_garden.id,
                        created_at=datetime.utcnow() - timedelta(days=15),
                        eco_impact_score=4,
                        estimated_co2_saved=2.1,
                        original_packaging=False
                    )
                ]
                
                db.session.add_all(products)
                db.session.commit()
                print('Sample products created!')
        
        print('Database initialized successfully!')

if __name__ == '__main__':
    init_db()
