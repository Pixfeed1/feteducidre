-- Migration : table contest_results
CREATE TABLE IF NOT EXISTS contest_results (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    edition_id INT UNSIGNED DEFAULT NULL,
    year INT NOT NULL,
    category VARCHAR(255) NOT NULL,
    `rank` INT NOT NULL DEFAULT 1,
    producer_name VARCHAR(255) NOT NULL,
    producer_city VARCHAR(255) DEFAULT NULL,
    product_name VARCHAR(255) DEFAULT NULL,
    score DECIMAL(5,2) DEFAULT NULL,
    medal ENUM('or', 'argent', 'bronze', 'mention') DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_year (year),
    INDEX idx_category (category),
    INDEX idx_edition (edition_id),
    CONSTRAINT fk_contest_edition FOREIGN KEY (edition_id) REFERENCES editions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
