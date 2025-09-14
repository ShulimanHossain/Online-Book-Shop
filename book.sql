CREATE DATABASE bookstore_online;
USE bookstore_online;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Admin(
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_name VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    admin_password VARCHAR(255) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20),
    rating DECIMAL (3,2) DEFAULT 0
);

CREATE TABLE Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating DECIMAL(3,2) DEFAULT 0
);

CREATE TABLE Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    published_date DATE,
    stock INT DEFAULT 0 CHECK (stock >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating DECIMAL(3,2) DEFAULT 0,
    author_id INT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE CASCADE
);

CREATE TABLE Orders(
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_bill DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Order_details(
    order_details_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE
);


CREATE TABLE Review_book(
    book_review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    rating DECIMAL(3,2) NOT NULL CHECK (rating>=0 AND rating <=5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    UNIQUE KEY unique_review (user_id,book_id)
);

CREATE TABLE upcoming_books (
    upcoming_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL
);


CREATE VIEW v_top_selling_books AS
SELECT b.book_id, b.title,a.name, SUM(p.quantity) AS total_sold
FROM Books b
JOIN Authors a ON b.author_id=a.author_id
JOIN Order_details p ON b.book_id = p.book_id
JOIN Orders o ON p.order_id=o.order_id
GROUP BY b.book_id, b.title,a.name
ORDER BY total_sold DESC
LIMIT 5;

CREATE OR REPLACE VIEW v_revenue AS
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    SUM(total_bill) AS revenue
FROM Orders
WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY DATE_FORMAT(order_date, '%Y-%m');



CREATE VIEW top_four_author AS 
SELECT a.author_id,
a.name AS author_name,
ROUND (AVG(b.rating), 2) AS avg_rating
FROM Authors a 
JOIN Books b ON a.author_id=b.author_id
GROUP BY a.author_id, a.name
ORDER BY avg_rating DESC
LIMIT 4;

CREATE VIEW v_user_order_details AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    u.phone_number,
    o.order_id,
    o.order_date,
    o.total_bill,
    od.book_id,
    b.title AS book_title,
    od.quantity,
    (od.quantity * b.price) AS subtotal
FROM Users u
JOIN Orders o ON u.user_id = o.user_id
JOIN Order_details od ON o.order_id = od.order_id
JOIN Books b ON od.book_id = b.book_id;


CREATE VIEW v_order_summary AS
SELECT 
    o.order_id,
    o.user_id,
    o.total_bill,
    o.order_date
FROM Orders o
WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);

CREATE VIEW v_user_orders AS
SELECT 
    o.order_id,
    o.user_id,
    o.total_bill,
    o.order_date
FROM Orders o
ORDER BY o.user_id, o.order_date DESC;


CREATE VIEW v_user_info AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    u.phone_number,
    u.address,
    u.date_of_birth,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(od.quantity),0) AS total_books_purchased,
    COALESCE(SUM(o.total_bill),0) AS total_spent
FROM Users u
LEFT JOIN Orders o ON u.user_id = o.user_id
LEFT JOIN Order_details od ON o.order_id = od.order_id
GROUP BY u.user_id, u.username, u.email, u.phone_number, u.address, u.date_of_birth;

CREATE VIEW bookDetails AS
SELECT 
    b.book_id,
    b.title,
    b.price,
    b.stock,
    a.author_id,
    a.name AS author_name,
    a.rating AS author_rating
FROM Books b
JOIN Authors a ON b.author_id = a.author_id;


CREATE VIEW bookDetailsReview AS
SELECT 
    b.book_id,
    b.title,
    a.name AS author_name,
    a.rating AS author_rating,
    r.rating AS review_rating,
    r.review_text,
    u.username AS reviewer
FROM Books b
JOIN Authors a ON b.author_id = a.author_id
LEFT JOIN Review_book r ON b.book_id = r.book_id
LEFT JOIN Users u ON r.user_id = u.user_id;


CREATE USER 'admin'@'localhost' IDENTIFIED BY 'Admin@123';

GRANT ALL PRIVILEGES ON bookstore_online.* TO 'admin'@'localhost';


CREATE USER 'customer'@'localhost' IDENTIFIED BY 'Customer@123';

GRANT SELECT ON bookstore_online.Books TO 'customer'@'localhost';
GRANT SELECT ON bookstore_online.Authors TO 'customer'@'localhost';
GRANT INSERT ON bookstore_online.Orders TO 'customer'@'localhost';
GRANT INSERT ON bookstore_online.Order_details TO 'customer'@'localhost';
GRANT INSERT, SELECT ON bookstore_online.Review_book TO 'customer'@'localhost';
GRANT SELECT ON bookstore_online.v_user_order_details TO 'customer'@'localhost';
GRANT SELECT ON bookstore_online.v_user_orders TO 'customer'@'localhost';












