-- Migration : ajouter palmares_media_id et notes à editions
ALTER TABLE editions
    ADD COLUMN palmares_media_id INT UNSIGNED DEFAULT NULL AFTER programme_image_id,
    ADD COLUMN notes TEXT DEFAULT NULL AFTER stats;
