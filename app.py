from flask import Flask, session, request, render_template, jsonify
from firebase_manager import FirebaseManager
from book_recommender import BookRecommender
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

class BookHarmonyServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.manager = FirebaseManager()

        # New User
        self.user = None

        self.seller = None

        self.buyer = None 

        self.PASSWORD = os.getenv("ADMIN_PASSWORD")

    def setup_routes(self):
        # Index Page
        self.app.add_url_rule('/', 'index', self.index_page)

        # Login Page
        self.app.add_url_rule('/login', 'login_page', self.login_page)
        self.app.add_url_rule('/login', 'login', self.login, methods=['POST'])

        # Register Page
        self.app.add_url_rule('/register', 'register_page', self.register_page)
        self.app.add_url_rule('/register', 'register', self.register, methods=['POST'])

        # User Dashboard Page
        self.app.add_url_rule('/dashboard', 'dashboard_page', self.dashboard_page)

        # Sell Book
        self.app.add_url_rule('/sell_book', 'sell_book', self.sell_book, methods=['POST'])

        # Remove Book
        self.app.add_url_rule('/remove_book', 'remove_book', self.remove_book, methods=['POST'])

        # Update Book Price
        self.app.add_url_rule('/update_price', 'update_price', self.update_price, methods=['POST'])

        # My Books Page
        self.app.add_url_rule('/mybooks', 'mybooks_page', self.mybooks_page)

        # My Sold Books Page
        self.app.add_url_rule('/sold_books', 'sold_books', self.sold_books_page)

        # Delivery Netword Page
        self.app.add_url_rule('/delivery', 'delivery_page', self.delivery_page)
        self.app.add_url_rule('/verify_password', 'verify_password', self.verify_password, methods=['POST'])
        self.app.add_url_rule('/mark_deliver', 'mark_deliver', self.mark_deliver, methods=['POST'])

        # Cart Page
        self.app.add_url_rule('/cart', 'cart_page', self.cart_page)
        self.app.add_url_rule('/add_to_cart', '/add_to_cart', self.add_to_cart, methods=['POST'])
        self.app.add_url_rule('/remove_from_cart', 'remove_from_cart', self.remove_from_cart, methods=['POST'])

        # Orders Page
        self.app.add_url_rule('/orders', 'orders_page', self.orders_page)
        self.app.add_url_rule('/give_rate', 'give_rate', self.give_rate, methods=['POST'])

        # Payment Page
        self.app.add_url_rule('/payment', 'payment_page', self.payment_page)

        # Process Order
        self.app.add_url_rule('/process_order', 'process_order', self.process_order, methods=['POST'])

        # Chat with Seller
        self.app.add_url_rule('/chat_with_seller', 'chat_with_seller', self.chat_with_seller_page)
        self.app.add_url_rule('/chat_seller', 'chat_seller', self.chat_seller, methods=['POST'])

        # Chat with Buyer
        self.app.add_url_rule('/chat_with_buyer', 'chat_with_buyer', self.chat_with_buyer_page)
        self.app.add_url_rule('/chat_buyer', 'chat_buyer', self.chat_buyer, methods=['POST'])

        self.app.add_url_rule('/send_message', 'send_message', self.send_message, methods=['POST'])
        self.app.add_url_rule('/get_messages', 'get_messages', self.get_messages)
        self.app.add_url_rule('/get_data', 'get_data', self.get_data)

        

        # Logout
        self.app.add_url_rule('/logout', 'logout', self.logout)

    def index_page(self):
        books = self.manager.fetch_books()

        recommender = BookRecommender(books)
        categories = []
        ratings = [0]
        recommend = None

        if self.user is not None:
            if self.manager.fetch_order_books(self.user):
                order_books = self.manager.fetch_order_books(self.user)
                categories.extend(order_books)

            if self.manager.fetch_cart_books(self.user):
                cart_books = self.manager.fetch_cart_books(self.user)
                for book_id, book_data in cart_books.items():
                    category = self.manager.fetch_category(self.user, book_id)
                    categories.append(category)
                
        if categories:
            categories = list(set(categories))
            recommended_books = recommender.recommend_books(categories, ratings)
            recommend = self.manager.filter_books_by_ids(books, recommended_books)

        for book_id, book_data in books.items():
            self.manager.get_image(book_data['filename'])

        return render_template('index.html', books=books, user=self.user, recommend=recommend)

    def login_page(self):
        return render_template('login.html')

    def register_page(self):
        return render_template('register.html')

    def dashboard_page(self):
        if self.user is not None:
            buyers = self.manager.fetch_buyers(self.user)
            return render_template('dashboard.html', buyers=buyers)
        else:
            return render_template('login.html')

    def login(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')

        self.user = self.manager.login_user(email, password)

        if self.user is not None:
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'})
        
    def register(self):
        data = request.json
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        pincode = data.get('pincode')
        password = data.get('password')

        state = data.get('state')
        city = data.get('city')

        temp_user = self.manager.register_user(email, password, name, address, phone, pincode, state, city)

        if temp_user is not None:
            return jsonify({'success': True, 'message': 'User registered successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Error registering/User alredy exists!'}) 
        
    def sell_book(self):
        # Get form data
        title = request.form.get('title')
        author = request.form.get('author')
        price = request.form.get('price')
        location = request.form.get('location')
        category = request.form.get('book_category')
        description = request.form.get('book_description')

        cover_img = request.files['coverImg']  # Uploaded cover image file
        if self.manager.add_book(self.user, title, author, price, location, description, category, cover_img):
            return jsonify({'message': 'Book successfully listed for sale!'})
        else:
            return jsonify({'message': 'Failed to add Book!'})

    def remove_book(self):
        if self.user is not None:
            data = request.json
            book_id = data.get('book_id')
            self.manager.delete_node(f'Users/{self.user.uid}/Books/{book_id}')
            self.manager.delete_node(f'Books/{book_id}')

            return jsonify({'message': 'Book removed from sale!'})
        else:
            return jsonify({'message': 'Book not exists!'})

    def update_price(self):
        if self.user is not None:
            data = request.json
            book_id = data.get('book_id')
            book_price = data.get('new_price')
            self.manager.update_book_price(self.user, book_id, book_price)
            return jsonify({'message': 'Price of book updated!'})
        else:
            return jsonify({'message': 'Book not exists!'})
        
    def mybooks_page(self):
        if self.user is not None:
            books = self.manager.fetch_mybooks(self.user)
            return render_template('mybooks.html', books=books)
        else:
            return render_template('login.html')
        
    def sold_books_page(self):
        if self.user is not None:
            orders = self.manager.fetch_purchase_orders(self.user)
            return render_template('purchase.html', orders=orders)
        else:
            return render_template('login.html')
        
    def delivery_page(self):
        transactions = self.manager.fetch_transaction()
        return render_template('delivery.html', transactions=transactions)
    
    def mark_deliver(self):
        data = request.json
        tid = data.get('tid')
        self.manager.mark_deliver(tid)
        return jsonify({'message': 'Marked as Delivered!'})
        
    def cart_page(self):
        if self.user is not None:
            books = self.manager.fetch_cart_books(self.user)
            new_data = {}
            if books:
                for key, value in books.items():
                    data = self.manager.fetch_specific_books(key)
                    new_data[key] = data
            return render_template('cart.html', books=new_data)
        else:
            return render_template('login.html')
        
    def add_to_cart(self):
        if self.user is not None:
            data = request.json
            book_id = data.get('book_id')

            if self.manager.is_node_present(f'Users/{self.user.uid}/Books/{book_id}'):
                return jsonify({'message': 'Error: You cant add your own book to cart!'})

            self.manager.add_to_users_cart(self.user, book_id)
            return jsonify({'message': 'Book added to cart successfully'})
        else:
            return jsonify({'message': 'Error to add Book'})
        
    def remove_from_cart(self):
        if self.user is not None:
            data = request.json
            book_id = data.get('book_id')
            self.manager.delete_node(f'Users/{ self.user.uid }/Cart/{ book_id }')
            return jsonify({'message': 'Book removed from cart!'})
        else:
            return jsonify({'message': 'Failed to remove book!'})
        
    def orders_page(self):
        if self.user is not None:
            orders = self.manager.fetch_orders(self.user)
            return render_template('orders.html', orders=orders)
        else:
            return render_template('login.html')
        
    def payment_page(self):
        if self.user is not None:
            books = self.manager.fetch_cart_books(self.user)
            user = self.manager.get_user_data(self.user)
            new_data = {}
            if books:
                for key, value in books.items():
                    data = self.manager.fetch_specific_books(key)
                    new_data[key] = data
            return render_template('payment.html', books=new_data, user=user)
        else:
            return render_template('login.html')

    def give_rate(self):
        data = request.json
        bookId = data.get('bookId')
        bookRating = data.get('bookRating')
        self.manager.give_rate(self.user, bookId, bookRating)
        return jsonify({'message': 'Rating given!'})

    def process_order(self):
        data = request.json
        book_ids = data.get('bookIds')
        total_price = data.get('totalPrice')

        timestamp = datetime.datetime.now().strftime("%Y/%m/%d_%H-%M-%S")

        node = self.manager.generate_sha(str(book_ids) + timestamp)

        self.manager.purchase_transaction(self.user, node, book_ids, total_price, timestamp)
        self.manager.delete_node(f'Users/{self.user.uid}/Cart')

        # Process the book data here
        return 'Book data received successfully!', 200
    
    def logout(self):
        if self.user is not None:
            self.user = None

        return render_template('login.html')

    def verify_password(self):
        data = request.json
        input_password = data.get('password')

        if input_password == self.PASSWORD:
            return jsonify({'success': True, 'message': 'Password correct'})
        else:
            return jsonify({'success': False, 'message': 'Incorrect password'}), 401

    def chat_with_seller_page(self):
        if self.seller is not None:
            self.buyer = None
            return render_template('chat_with_seller.html', receiver=self.seller, sender=self.user.uid)
        else:
            return render_template('cart.html')

    def chat_with_buyer_page(self):
        if self.buyer is not None:
            self.seller = None
            return render_template('chat_with_buyer.html', receiver=self.buyer, sender=self.user.uid)
        else:
            return render_template('cart.html')
        
    def chat_seller(self):
        if self.user is not None:
            data = request.json
            self.seller = data.get('seller_id')
            print(f'[*] Connecting to seller ID: {self.seller}')
            return jsonify({'message': 'Connected to seller!'})
        else:
            return jsonify({'message': 'Failed to connect with seller!'})

    def chat_buyer(self):
        if self.user is not None:
            data = request.json
            self.buyer = data.get('buyer_id')
            print(f'[*] Connecting to buyer ID: {self.buyer}')
            return jsonify({'message': 'Connected to buyer!'})
        else:
            return jsonify({'message': 'Failed to connect with buyer!'})
        
    def send_message(self):
        data = request.json
        message = data.get('message')
        name = self.manager.fetch_name(self.user)
        if self.seller is not None:
            message = f'<div class="message sent"><p><span class="sender">{name}:</span> {message}</p></div>';
            self.manager.send_message(self.user.uid, self.seller, message, False)

        if self.buyer is not None:
            message = f'<div class="message received"><p><span class="sender">{name}:</span> {message}</p></div>';
            self.manager.send_message(self.buyer, self.user.uid, message, True)

        return jsonify({'message': 'Message Send!'})
    
    def get_messages(self):
        if self.seller is not None:
            message = self.manager.fetch_messages(self.user.uid, self.seller)
            return jsonify({'message': message})
        elif self.buyer is not None:
            message = self.manager.fetch_messages(self.buyer, self.user.uid)
            return jsonify({'message': message})
        else:
            return jsonify({'message': 'Error to connect!'})
        
    def get_data(self):
        if self.user is not None:
            return self.manager.get_user_data(self.user)
        else:
            return render_template('login.html')
        
    def run(self):
        self.app.run(port="8080", debug=True)
    
if __name__ == '__main__':
    server = BookHarmonyServer()
    server.run()
