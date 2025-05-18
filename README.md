# EcoFinds

Empowering Sustainable Consumption through a Second-Hand Marketplace

EcoFinds is a Flask-based web application that helps users discover, buy, and sell eco-friendly second-hand products. The platform promotes sustainable living by making it easy to list unused items, shop for pre-loved goods, and support a circular economy.

---

## Features

- User authentication and registration
- Product listings with images and detailed descriptions
- Add, edit, and manage your own product listings
- Shopping cart and checkout functionality
- Order history and previous purchases
- User dashboard for managing listings and purchases
- Responsive, modern UI with Bootstrap 5

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/shivam-kumar25/Eco-finds-92.git
   cd Eco-finds-92
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

## Database Setup

To reset and initialize the database, run:
```sh
python reset_db.py
```

---

## Running the Application

Start the Flask app with:
```sh
python run.py
```
The application will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Project Structure

```
eco-finds-92/
│
├── src/
│   ├── templates/         # HTML templates (Jinja2)
│   ├── static/            # CSS, JS, images
│   ├── init_db.py         # Database initialization logic
│   └── ...                # Other modules
├── reset_db.py            # Script to reset and reinitialize the database
├── run.py                 # Application entry point
├── requirements.txt
└── README.md
```

---

## Video
Link: https://drive.google.com/drive/folders/1cWphwFjqHeZ7OhSqZjKXbTLqhr8IiW-e?usp=sharing


## Default Users

After database initialization, the following default users are available for testing:

| Username      | Email               | Password        | Role    |
|---------------|---------------------|-----------------|---------|
| admin         | admin@example.com   | adminpassword   | Admin   |
| ecoSeller     | seller@example.com  | password        | Seller  |
| greenBuyer    | buyer@example.com   | password        | Buyer   |


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

---
