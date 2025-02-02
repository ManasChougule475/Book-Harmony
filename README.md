# Book-Harmony: E-Commerce for Exchange of Pre-owned Books

**Book-Harmony** is an innovative web platform that revolutionizes the way people buy, sell, and exchange pre-owned books. It allows users to easily list and discover books at discounted prices, manage their personal libraries, and receive personalized book recommendations tailored to their preferences. The platform fosters a community-driven experience by enabling users to conenct, chat, negotiate, and share recommendations with fellow book lovers. Unlock new reading opportunities, monetize your old books, and engage with a vibrant community of readers!

---

## 📋 **Features**
- **Authentication**: Secure login and registration for users.
- **Personalized Dashboard**: Users can register books, view registered and sold books.
- **Book Management**:
  - Register books for sale.
  - Update book prices.
  - Remove books from listings.
- **Shopping Cart**:
  - Add or remove books.
  - Proceed to payment and place orders.
- **Orders Management**: View order history , ratings and transaction details.
- **Recommendation Engine**: Suggests books based on user preferences.
- **Search & Filters**: Easily find books by categories or keywords.
- **Chat Engine**: 
  - Communicate with buyers and sellers in real-time.
- **Admin Features**:
  - Delivery management, where admin can check all the transactions
  - Verify and mark orders as delivered.

---

## 🛠️ **Tech Stack**
- **Backend**: Flask
- **Database**: Firebase Realtime Database (via Firebase Admin SDK)
- **Frontend**: HTML, CSS, JavaScript
- **Environment Configuration**: `python-dotenv`

---

## 🚀 **Getting Started**
Follow these steps to set up and run the project locally.

### Prerequisites
1. Python 3.x
2. Firebase account with a configured Realtime Database.
3. Install necessary Python libraries:
   ```bash
   pip install flask python-dotenv firebase-admin

### Installation
git clone https://github.com/your-repo/book-harmony.git
cd book-harmony

### Configure environment variables & Set up Firebase
FIREBASE_STORAGE_BUCKET
FIREBASE_DATABASE_URL
ADMIN_PASSWORD 
