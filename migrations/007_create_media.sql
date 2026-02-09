-- Migration : table media
CREATE TABLE IF NOT EXISTS media (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size INT UNSIGNED NOT NULL DEFAULT 0,
    width INT UNSIGNED DEFAULT NULL,
    height INT UNSIGNED DEFAULT NULL,
    dominant_color VARCHAR(7) DEFAULT NULL COMMENT 'Couleur dominante hex pour placeholder',
    alt_text VARCHAR(255) DEFAULT NULL,
    caption TEXT DEFAULT NULL,
    disk_path VARCHAR(500) NOT NULL,
    has_webp TINYINT(1) NOT NULL DEFAULT 0,
    has_avif TINYINT(1) NOT NULL DEFAULT 0,
    sizes TEXT DEFAULT NULL COMMENT 'JSON des tailles générées',
    uploaded_by INT UNSIGNED DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_filename (filename),
    INDEX idx_mime (mime_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
