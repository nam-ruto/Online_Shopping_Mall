-- ================
-- 1. ACCOUNTS
-- ================
INSERT INTO account (
    id, user_name, password, salt, first_name, last_name,
    role, email, country, state, city, address_line,
    zip_code, phone
) VALUES
('11111111-1111-1111-1111-111111111111', 'namruto', 'hashed_pw_1', 0x1234,
 'Nam', 'Hoang', 'Customer', 'nam@example.com',
 'USA', 'AL', 'Troy', '123 University Ave', '36082', '3345550001'),

('22222222-2222-2222-2222-222222222222', 'bob02', 'hashed_pw_2', 0x5678,
 'Bob', 'Dylan', 'Customer', 'bob@example.com',
 'USA', 'AL', 'Montgomery', '456 Market St', '36104', '3345550002'),

('33333333-3333-3333-3333-333333333333', 'mike123', 'hashed_pw_3', 0x9ABC,
 'Michael', 'Jordan', 'CEO', 'ceo@shoppingmall.com',
 'USA', 'AL', 'Troy', '1 Admin Plaza', '36082', '3345550003');

-- ================
-- 2. ITEMS
-- ================
INSERT INTO item (id, name, description, category, price, stock_quantity, like_count) VALUES
(1, 'Wireless Mouse',
 'Ergonomic 2.4G wireless mouse with USB receiver',
 'Electronics', 25.99, 100, 12),

(2, 'Mechanical Keyboard',
 'RGB mechanical keyboard with blue switches',
 'Electronics', 79.99, 50, 25),

(3, 'USB-C Charger',
 '45W fast-charging USB-C wall adapter',
 'Accessories', 19.99, 200, 8),

(4, 'Noise Cancelling Headphones',
 'Over-ear Bluetooth headphones with active noise cancelling',
 'Electronics', 129.99, 30, 30);

-- ================
-- 3. ORDERS
-- ================
INSERT INTO `order` (
    id, customer_id, transaction_id,
    to_state, to_city, to_address_line,
    total_amount, order_date, status, payment_method
) VALUES
(1, '11111111-1111-1111-1111-111111111111', 1001,
 'AL', 'Troy', '123 University Ave',
 71.97, '2025-11-15 10:00:00', 'Processing', 'Credit'),

(2, '22222222-2222-2222-2222-222222222222', 1002,
 'AL', 'Montgomery', '456 Market St',
 209.98, '2025-11-16 14:30:00', 'Shipped', 'Debit');

-- ================
-- 4. ORDER ITEMS
-- Order 1: 2x Mouse, 1x USB-C Charger = 71.97
-- Order 2: 1x Mechanical Keyboard, 1x Headphones = 209.98
-- ================
INSERT INTO order_item (
    id, order_id, item_id, quantity, unit_price, sub_total
) VALUES
(1, 1, 1, 2, 25.99, 51.98),
(2, 1, 3, 1, 19.99, 19.99),
(3, 2, 2, 1, 79.99, 79.99),
(4, 2, 4, 1, 129.99, 129.99);

-- ================
-- 5. MESSAGES (simple customer–staff chat)
-- ================
INSERT INTO message (
    id, conversation_id, user_id, role, content, is_read
) VALUES
(1, 1, '11111111-1111-1111-1111-111111111111', 'customer',
 'Hi, can I change the shipping address for my order?', 0),

(2, 1, '33333333-3333-3333-3333-333333333333', 'staff',
 'Sure! Please send me the new address and I will update it.', 0),

(3, 1, '11111111-1111-1111-1111-111111111111', 'customer',
 'New address is 789 New Street, Troy, AL 36082.', 0);

-- ================
-- 6. REPORT (Daily sales report)
-- Total sold quantity: 2 + 1 + 1 + 1 = 5
-- Total revenue: 51.98 + 19.99 + 79.99 + 129.99 = 281.95
-- ================
INSERT INTO report (
    id, type, start_date, end_date, sold_quantity, total_revenue
) VALUES
(1, 'Daily', '2025-11-15 00:00:00', '2025-11-15 23:59:59', 5, 281.95);

-- ================
-- 7. REPORT CONTENT (per-item breakdown for that report)
-- ================
INSERT INTO report_content (
    id, report_id, item_id, item_sold, unit_price, sub_total
) VALUES
(1, 1, 1, 2, 25.99, 51.98),   -- Wireless Mouse
(2, 1, 3, 1, 19.99, 19.99),   -- USB-C Charger
(3, 1, 2, 1, 79.99, 79.99),   -- Mechanical Keyboard
(4, 1, 4, 1, 129.99, 129.99); -- Headphones
