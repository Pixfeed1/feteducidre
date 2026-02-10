-- Migration : ajout colonne type aux albums
ALTER TABLE albums ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'fete' AFTER description;
