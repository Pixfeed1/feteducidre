-- Migration : add category_id FK and logo_filename to partners
ALTER TABLE partners
    ADD COLUMN category_id INT UNSIGNED DEFAULT NULL AFTER logo_id,
    ADD COLUMN logo_filename VARCHAR(255) DEFAULT NULL AFTER category_id,
    ADD INDEX idx_category_id (category_id);

-- Migrate existing ENUM data to category_id
UPDATE partners SET category_id = (SELECT id FROM partner_categories WHERE slug = 'institutions') WHERE category = 'institutionnel';
UPDATE partners SET category_id = (SELECT id FROM partner_categories WHERE slug = 'services') WHERE category IN ('entreprise', 'autre');
UPDATE partners SET category_id = (SELECT id FROM partner_categories WHERE slug = 'media') WHERE category = 'media';
UPDATE partners SET category_id = (SELECT id FROM partner_categories WHERE slug = 'locaux') WHERE category = 'associatif';

-- Drop old ENUM column
ALTER TABLE partners DROP COLUMN category;
