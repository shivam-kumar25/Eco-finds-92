from __init__ import create_app, db
from models.models import Category, User

app = create_app()

# Create database tables and populate them
with app.app_context():
    db.create_all()
    
    # Add categories if they don't exist
    categories = [
        {"name": "Furniture", "description": "Tables, chairs, sofas, and more"},
        {"name": "Electronics", "description": "Phones, laptops, cameras, and more"},
        {"name": "Clothing", "description": "Shirts, pants, dresses, and more"},
        {"name": "Books", "description": "Fiction, non-fiction, textbooks, and more"},
        {"name": "Kitchen", "description": "Utensils, appliances, cookware, and more"},
        {"name": "Home Decor", "description": "Art, lighting, decorative items, and more"},
        {"name": "Sports", "description": "Equipment, apparel, accessories, and more"},
        {"name": "Toys", "description": "Games, action figures, dolls, and more"}
    ]
    
    for category_data in categories:
        if not Category.query.filter_by(name=category_data["name"]).first():
            category = Category(name=category_data["name"], description=category_data["description"])
            db.session.add(category)
    
    # Create admin user if it doesn't exist
    admin_email = 'admin@ecofinds.com'
    if not User.query.filter_by(email=admin_email).first():
        admin_user = User(
            username='admin',
            email=admin_email,
            full_name='Admin User',
            bio='EcoFinds Administrator',
            is_admin=True,
            is_active=True,
            profile_picture='',
            phone_number='',
            address='',
            communication_preferences={},
            preferred_language='en',
            category_preferences=[]
        )
        admin_user.password = 'Admin@123' # This will be hashed
        db.session.add(admin_user)
    
    db.session.commit()

print("Database initialized with categories and admin user!")
            
#             db.session.add_all([admin, seller1, buyer1])
#             db.session.commit()
#             print('Demo users created!')
            
#             # Add sample products if none exist
#             if Product.query.count() == 0:
#                 # Get categories
#                 electronics = Category.query.filter_by(name='Electronics').first()
#                 clothing = Category.query.filter_by(name='Clothing').first()
#                 home_garden = Category.query.filter_by(name='Home & Garden').first()
#                 books_media = Category.query.filter_by(name='Books & Media').first()
#                 sports = Category.query.filter_by(name='Sports & Outdoors').first()
#                   # Sample products
#                 products = [
#                     Product(
#                         name='Refurbished Smartphone',
#                         description='Fully functional smartphone in excellent condition. Battery health at 90%. Comes with charger and box.',
#                         price=249.99,
#                         condition='Refurbished - Excellent',
#                         image_filename='smartphone.jpg',
#                         seller_id=seller1.id,
#                         category_id=electronics.id,
#                         created_at=datetime.utcnow() - timedelta(days=5),
#                         eco_impact_score=4,
#                         estimated_co2_saved=35.2,
#                         original_packaging=True
#                     ),
#                     Product(
#                         name='Vintage Denim Jacket',
#                         description='Genuine vintage denim jacket from the 90s. Size M. Great condition with minimal wear.',
#                         price=45.00,
#                         condition='Used - Very Good',
#                         image_filename='denim_jacket.jpg',
#                         seller_id=seller1.id,
#                         category_id=clothing.id,
#                         created_at=datetime.utcnow() - timedelta(days=10),
#                         eco_impact_score=5,
#                         estimated_co2_saved=12.7,
#                         original_packaging=False
#                     ),
#                     Product(
#                         name='Bamboo Cutlery Set',
#                         description='Eco-friendly bamboo cutlery set with knife, fork, spoon and chopsticks. Perfect for camping or daily use.',
#                         price=12.50,
#                         condition='Used - Like New',
#                         image_filename='bamboo_cutlery.jpg',
#                         seller_id=admin.id,
#                         category_id=home_garden.id,
#                         created_at=datetime.utcnow() - timedelta(days=3),
#                         eco_impact_score=5,
#                         estimated_co2_saved=0.8,
#                         original_packaging=True
#                     ),
#                     Product(
#                         name='Classic Novel Collection',
#                         description='Set of 5 classic novels in paperback. All in good condition with minimal highlighting.',
#                         price=18.99,
#                         condition='Used - Good',
#                         image_filename='novels.jpg',
#                         seller_id=admin.id,
#                         category_id=books_media.id,
#                         created_at=datetime.utcnow() - timedelta(days=7),
#                         eco_impact_score=3,
#                         estimated_co2_saved=5.3,
#                         original_packaging=False
#                     ),
                   
#                     Product(
#                         name='Wooden Chess Set',
#                         description='Hand-carved wooden chess set with inlaid board. Minor wear but all pieces present and in great condition.',
#                         price=35.99,                        condition='Used - Good',
#                         image_filename='chess_set.jpg',
#                         seller_id=buyer1.id,
#                         category_id=books_media.id,
#                         created_at=datetime.utcnow() - timedelta(days=9),
#                         eco_impact_score=3,
#                         estimated_co2_saved=3.7,
#                         original_packaging=False
#                     )
#                 ]
                
#                 db.session.add_all(products)
#                 db.session.commit()
#                 print('Sample products created!')
        
#         print('Database initialized successfully!')

# if __name__ == '__main__':
#     if len(sys.argv) > 1 and sys.argv[1] == '--reset':
#         reset_db()
#     init_db()
