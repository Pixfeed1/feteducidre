-- Hike classement PDF files per edition per category
CREATE TABLE IF NOT EXISTS hike_files (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    hike_edition_id INT UNSIGNED NOT NULL,
    category ENUM('adultes', 'supercool', 'enfants') NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_size INT UNSIGNED NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_edition (hike_edition_id),
    UNIQUE KEY uk_edition_cat (hike_edition_id, category),
    CONSTRAINT fk_hike_files_edition FOREIGN KEY (hike_edition_id) REFERENCES hike_editions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
