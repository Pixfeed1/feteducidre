-- Contest inscription documents (PDFs for rules, forms, etc.)
CREATE TABLE IF NOT EXISTS contest_documents (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category ENUM('professionnels', 'amateurs', 'producteurs') NOT NULL,
    name VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_size INT UNSIGNED NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
