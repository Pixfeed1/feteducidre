-- Rendre la page programme dynamique (slug sans année)
UPDATE pages SET slug = 'programme', title = 'Programme', meta_title = 'Programme — Fête du Cidre', meta_description = 'Le programme complet de la Fête du Cidre.' WHERE slug LIKE 'programme-%';
