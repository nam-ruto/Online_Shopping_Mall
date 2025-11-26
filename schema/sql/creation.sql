
-- Drop tables in dependency order (optional, for re-runs)
DROP TABLE IF EXISTS report_content;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS `order`;
DROP TABLE IF EXISTS report;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS account;

-- 1. ACCOUNT
CREATE TABLE account (
    id             CHAR(36)      NOT NULL,          -- UUID
    user_name      VARCHAR(30)   NOT NULL,
    password       VARCHAR(255)  NOT NULL,
    salt           VARBINARY(255) NOT NULL,
    first_name     VARCHAR(50)   NOT NULL,
    last_name      VARCHAR(50)   NOT NULL,
    role           ENUM('Customer', 'Staff', 'CEO') NOT NULL DEFAULT 'Customer',
    email          VARCHAR(50)   NOT NULL,
    country        VARCHAR(50),
    state          VARCHAR(2),
    city           VARCHAR(20),
    address_line   VARCHAR(50),
    zip_code       VARCHAR(10),
    phone          VARCHAR(10),
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_account_username (user_name),
    UNIQUE KEY uq_account_email (email)
);

-- 2. ITEM
CREATE TABLE item (
    id             INT           NOT NULL AUTO_INCREMENT,
    name           VARCHAR(100)  NOT NULL,
    description    VARCHAR(250),
    category       VARCHAR(100),
    price          DECIMAL(10,2) NOT NULL,
    stock_quantity INT           NOT NULL DEFAULT 0,
    like_count     INT           NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

-- 3. REPORT
CREATE TABLE report (
    id             INT           NOT NULL AUTO_INCREMENT,
    type           ENUM('Daily', 'Weekly', 'Monthly') NOT NULL,
    start_date     DATETIME      NOT NULL,
    end_date       DATETIME      NOT NULL,
    created_date   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sold_quantity  INT           NOT NULL DEFAULT 0,
    total_revenue  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (id)
);

-- 4. ORDER
CREATE TABLE `order` (
    id              INT           NOT NULL AUTO_INCREMENT,
    customer_id     CHAR(36)      NOT NULL,
    transaction_id  INT,
    to_state        VARCHAR(2),
    to_city         VARCHAR(20),
    to_address_line VARCHAR(50),
    total_amount    DECIMAL(10,2) NOT NULL,
    order_date      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('In Cart', 'Processing', 'Shipped', 'Delivered', 'Refunded') NOT NULL DEFAULT 'In Cart',
    payment_method  ENUM('Credit', 'Debit') NOT NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_order_customer_id (customer_id),
    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id) REFERENCES account(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 5. MESSAGE
CREATE TABLE message (
    id              INT           NOT NULL AUTO_INCREMENT,
    conversation_id INT           NOT NULL,
    subject         VARCHAR(200)  NOT NULL,
    user_id         CHAR(36)      NOT NULL,
    role            ENUM('Customer', 'Staff', 'System') NOT NULL,
    content         TEXT          NOT NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_read         BOOLEAN       NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id),
    KEY idx_message_user_id (user_id),
    CONSTRAINT fk_message_user
        FOREIGN KEY (user_id) REFERENCES account(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 6. ORDER_ITEM
CREATE TABLE order_item (
    id         INT           NOT NULL AUTO_INCREMENT,
    order_id   INT           NOT NULL,
    item_id    INT           NOT NULL,
    quantity   INT           NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    sub_total  DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id),
    KEY idx_order_item_order_id (order_id),
    KEY idx_order_item_item_id (item_id),
    CONSTRAINT fk_order_item_order
        FOREIGN KEY (order_id) REFERENCES `order`(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_order_item_item
        FOREIGN KEY (item_id) REFERENCES item(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 7. REPORT_CONTENT
CREATE TABLE report_content (
    id         INT           NOT NULL AUTO_INCREMENT,
    report_id  INT           NOT NULL,
    item_id    INT           NOT NULL,
    item_sold  INT           NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    sub_total  DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id),
    KEY idx_report_content_report_id (report_id),
    KEY idx_report_content_item_id (item_id),
    CONSTRAINT fk_report_content_report
        FOREIGN KEY (report_id) REFERENCES report(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_report_content_item
        FOREIGN KEY (item_id) REFERENCES item(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 8. LIKED_ITEM
CREATE TABLE liked_item (
    id           INT           NOT NULL AUTO_INCREMENT,
    customer_id  CHAR(36)      NOT NULL,
    item_id      INT           NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_liked_item_customer_item (customer_id, item_id),
    KEY idx_liked_item_customer_id (customer_id),
    KEY idx_liked_item_item_id (item_id),
    CONSTRAINT fk_liked_item_customer
        FOREIGN KEY (customer_id) REFERENCES account(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_liked_item_item
        FOREIGN KEY (item_id) REFERENCES item(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);