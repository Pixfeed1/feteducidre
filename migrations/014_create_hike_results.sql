-- Migration : table hike_results
CREATE TABLE IF NOT EXISTS hike_results (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    hike_edition_id INT UNSIGNED NOT NULL,
    `rank` INT NOT NULL,
    participant_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT NULL,
    time_seconds INT DEFAULT NULL,
    bib_number INT DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hike (hike_edition_id),
    INDEX idx_rank (`rank`),
    CONSTRAINT fk_hike_results_edition FOREIGN KEY (hike_edition_id) REFERENCES hike_editions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
