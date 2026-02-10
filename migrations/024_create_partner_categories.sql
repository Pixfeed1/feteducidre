-- Migration : table partner_categories
CREATE TABLE IF NOT EXISTS partner_categories (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    icon VARCHAR(50) NOT NULL DEFAULT 'heart',
    color VARCHAR(20) NOT NULL DEFAULT '#3B82F6',
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed default categories
INSERT INTO partner_categories (name, slug, icon, color, sort_order) VALUES
('Médias', 'media', 'radio', '#3B82F6', 1),
('Partenaires financiers', 'banques', 'landmark', '#2C4A2E', 2),
('Institutions & collectivités', 'institutions', 'building', '#D4833B', 3),
('Services & entreprises', 'services', 'briefcase', '#5C3D2E', 4),
('Partenaires locaux', 'locaux', 'apple', '#7A9E6B', 5);
