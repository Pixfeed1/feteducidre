-- Add categories and include_responses fields to hike_editions
ALTER TABLE hike_editions
    ADD COLUMN `categories` TEXT DEFAULT NULL AFTER `is_active`,
    ADD COLUMN `include_responses` TINYINT(1) NOT NULL DEFAULT 1 AFTER `categories`;
