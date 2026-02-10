<?php

/**
 * Script de seed — insère les données de démo
 * Usage : php scripts/seed.php
 */

declare(strict_types=1);

require_once dirname(__DIR__) . '/vendor/autoload.php';

use App\Core\Config;
use App\Core\Database;

Config::getInstance();

echo "=== Seed Fête du Cidre ===\n\n";

try {
    $db = Database::getInstance();
    echo "✓ Connexion à la base de données réussie\n\n";
} catch (\Exception $e) {
    echo "✗ Erreur de connexion : " . $e->getMessage() . "\n";
    exit(1);
}

// --- Utilisateur admin ---
echo "→ Création de l'utilisateur admin...\n";
$db->query("DELETE FROM users WHERE email = ?", ['admin@fetecidre.fr']);
$db->insert('users', [
    'email'      => 'admin@fetecidre.fr',
    'password'   => password_hash('Admin1234!', PASSWORD_BCRYPT, ['cost' => 12]),
    'first_name' => 'Admin',
    'last_name'  => 'Fête du Cidre',
    'role'       => 'admin',
    'is_active'  => 1,
]);
echo "✓ Admin créé (admin@fetecidre.fr / Admin1234!)\n\n";

// --- Pages ---
echo "→ Insertion des pages...\n";
$pages = [
    ['Accueil', 'accueil', 'home', 0, 0, 'Fête du Cidre — L\'Hôtellerie de Flée', 'Découvrez la Fête du Cidre, événement incontournable du Maine-et-Loire depuis 1989.'],
    ['Nos Origines', 'origines', 'page', 1, 1, 'Nos Origines — Fête du Cidre', 'L\'histoire de la Fête du Cidre depuis sa création en 1989 à L\'Hôtellerie de Flée.'],
    ['Infos Pratiques', 'infos-pratiques', 'page', 1, 2, 'Infos Pratiques — Fête du Cidre', 'Horaires, tarifs, accès et informations pratiques pour la Fête du Cidre.'],
    ['Programme', 'programme', 'page', 1, 3, 'Programme — Fête du Cidre', 'Le programme complet de la Fête du Cidre.'],
    ['Boutique', 'boutique', 'shop', 1, 4, 'Boutique — Fête du Cidre', 'Achetez nos cidres, jus de pomme et produits du terroir en ligne.'],
    ['Galerie Photos', 'galerie', 'gallery', 1, 5, 'Galerie Photos — Fête du Cidre', 'Retrouvez les photos des éditions passées de la Fête du Cidre.'],
    ['Archives', 'archives', 'archive', 1, 6, 'Archives — Fête du Cidre', 'Les archives de toutes les éditions de la Fête du Cidre depuis 1989.'],
    ['Concours', 'concours', 'contest', 1, 7, 'Concours de Cidre — Fête du Cidre', 'Le concours de cidre : règlement, inscriptions et palmarès.'],
    ['Randonnée', 'randonnee', 'hike', 0, 0, 'Randonnée — Fête du Cidre', 'La randonnée pédestre de la Fête du Cidre.'],
    ['Remerciements', 'remerciements', 'page', 0, 0, 'Remerciements — Fête du Cidre', 'Nos remerciements à tous les bénévoles et partenaires.'],
    ['Mentions Légales', 'mentions-legales', 'legal', 0, 0, 'Mentions Légales — Fête du Cidre', 'Mentions légales du site de la Fête du Cidre.'],
    ['Contact', 'contact', 'contact', 0, 0, 'Contact — Fête du Cidre', 'Contactez l\'association Fête du Cidre.'],
];

foreach ($pages as $p) {
    $db->insert('pages', [
        'title'            => $p[0],
        'slug'             => $p[1],
        'template'         => $p[2],
        'in_menu'          => $p[3],
        'menu_order'       => $p[4],
        'meta_title'       => $p[5],
        'meta_description' => $p[6],
        'status'           => 'published',
        'content'          => '<p>Contenu de la page ' . $p[0] . ' à rédiger.</p>',
        'created_by'       => 1,
    ]);
}
echo "✓ " . count($pages) . " pages insérées\n\n";

// --- Produits ---
echo "→ Insertion des produits...\n";
$products = [
    ['Cidre Brut Fermier', 'cidre-brut-fermier', 'Cidre brut traditionnel élaboré à partir de pommes du verger.', 4.50, 'CID-001', 50, '75cl', 5.5, 'cidre', 1],
    ['Cidre Demi-Sec', 'cidre-demi-sec', 'Cidre demi-sec fruité et équilibré, idéal pour l\'apéritif.', 4.50, 'CID-002', 45, '75cl', 4.5, 'cidre', 1],
    ['Cidre Doux', 'cidre-doux', 'Cidre doux et moelleux, parfait pour les desserts.', 4.50, 'CID-003', 40, '75cl', 3.0, 'cidre', 1],
    ['Jus de Pomme Pur', 'jus-de-pomme-pur', 'Jus de pomme non filtré, pressé à froid, sans sucre ajouté.', 3.80, 'JUS-001', 60, '1L', null, 'jus', 1],
    ['Pommeau du Maine', 'pommeau-du-maine', 'Pommeau de Maine AOC, mariage de jus de pomme et d\'eau-de-vie.', 12.00, 'POM-001', 25, '70cl', 17.0, 'spiritueux', 1],
    ['Coffret Découverte', 'coffret-decouverte', 'Coffret de 3 bouteilles : cidre brut, demi-sec et jus de pomme.', 11.90, 'COF-001', 20, null, null, 'coffret', 1],
];

foreach ($products as $p) {
    $db->insert('products', [
        'name'               => $p[0],
        'slug'               => $p[1],
        'description'        => $p[2],
        'short_description'  => $p[2],
        'price'              => $p[3],
        'sku'                => $p[4],
        'stock'              => $p[5],
        'volume'             => $p[6],
        'alcohol_percentage' => $p[7],
        'category'           => $p[8],
        'is_featured'        => $p[9],
        'is_active'          => 1,
    ]);
}
echo "✓ " . count($products) . " produits insérés\n\n";

// --- Commandes ---
echo "→ Insertion des commandes de démo...\n";
$orderStatuses = ['paid', 'processing', 'shipped', 'delivered', 'pending'];
for ($i = 1; $i <= 5; $i++) {
    $orderId = $db->insert('orders', [
        'reference'           => 'CMD-2025-' . str_pad((string)$i, 3, '0', STR_PAD_LEFT),
        'status'              => $orderStatuses[$i - 1],
        'customer_email'      => "client{$i}@example.com",
        'customer_first_name' => "Prénom{$i}",
        'customer_last_name'  => "Nom{$i}",
        'customer_phone'      => '06 12 34 56 7' . $i,
        'shipping_address'    => "{$i} rue du Cidre",
        'shipping_city'       => 'L\'Hôtellerie de Flée',
        'shipping_postal_code'=> '49500',
        'subtotal'            => 13.50 * $i,
        'shipping_cost'       => $i > 3 ? 0.00 : 5.90,
        'tax_amount'          => round(13.50 * $i * 0.20, 2),
        'total'               => round(13.50 * $i * 1.20 + ($i > 3 ? 0.00 : 5.90), 2),
        'payment_method'      => 'stripe',
    ]);

    // Ajouter des items à la commande
    $db->insert('order_items', [
        'order_id'     => $orderId,
        'product_id'   => 1,
        'product_name' => 'Cidre Brut Fermier',
        'product_sku'  => 'CID-001',
        'quantity'     => $i,
        'unit_price'   => 4.50,
        'total_price'  => 4.50 * $i,
    ]);
    $db->insert('order_items', [
        'order_id'     => $orderId,
        'product_id'   => 4,
        'product_name' => 'Jus de Pomme Pur',
        'product_sku'  => 'JUS-001',
        'quantity'     => $i,
        'unit_price'   => 3.80,
        'total_price'  => 3.80 * $i,
    ]);
}
echo "✓ 5 commandes de démo insérées\n\n";

// --- Albums ---
echo "→ Insertion des albums...\n";
$albums = [
    ['Édition 2018', 'edition-2018', 'Photos de l\'édition 2018', 2018],
    ['Édition 2016', 'edition-2016', 'Photos de l\'édition 2016', 2016],
    ['Édition 2014', 'edition-2014', 'Photos de l\'édition 2014', 2014],
];
foreach ($albums as $a) {
    $db->insert('albums', [
        'title'       => $a[0],
        'slug'        => $a[1],
        'description' => $a[2],
        'year'        => $a[3],
        'is_active'   => 1,
    ]);
}
echo "✓ " . count($albums) . " albums insérés\n\n";

// --- Éditions ---
echo "→ Insertion des éditions...\n";
$years = [1989, 1991, 1993, 1995, 1999, 2002, 2005, 2008, 2011, 2014, 2016, 2018];
foreach ($years as $year) {
    $db->insert('editions', [
        'year'        => $year,
        'title'       => "Édition {$year}",
        'description' => "La Fête du Cidre édition {$year}.",
        'is_active'   => 1,
    ]);
}
echo "✓ " . count($years) . " éditions insérées\n\n";

// --- Résultats concours ---
echo "→ Insertion des résultats de concours...\n";
$contestData = [
    [2018, 'Cidre Brut', 1, 'Ferme des Pommiers', 'Segré', 'Brut Tradition', 18.5, 'or'],
    [2018, 'Cidre Brut', 2, 'Cidrerie du Maine', 'Angers', 'Brut Fermier', 17.2, 'argent'],
    [2018, 'Cidre Brut', 3, 'Les Vergers d\'Anjou', 'Saumur', 'Brut Artisanal', 16.8, 'bronze'],
    [2018, 'Cidre Doux', 1, 'Domaine de la Pommeraie', 'Flée', 'Doux Naturel', 18.0, 'or'],
    [2018, 'Cidre Doux', 2, 'Ferme des Pommiers', 'Segré', 'Doux Tradition', 17.5, 'argent'],
    [2016, 'Cidre Brut', 1, 'Cidrerie du Maine', 'Angers', 'Brut Premium', 18.8, 'or'],
    [2016, 'Cidre Brut', 2, 'Les Vergers d\'Anjou', 'Saumur', 'Brut de Pomme', 17.0, 'argent'],
    [2016, 'Cidre Doux', 1, 'Domaine de la Pommeraie', 'Flée', 'Doux de Flée', 18.2, 'or'],
    [2016, 'Jus de Pomme', 1, 'Ferme des Pommiers', 'Segré', 'Jus Pur Pomme', 19.0, 'or'],
    [2016, 'Jus de Pomme', 2, 'Verger Bio du Loir', 'La Flèche', 'Jus Bio', 17.8, 'argent'],
];
foreach ($contestData as $c) {
    $db->insert('contest_results', [
        'year'          => $c[0],
        'category'      => $c[1],
        'rank'          => $c[2],
        'producer_name' => $c[3],
        'producer_city' => $c[4],
        'product_name'  => $c[5],
        'score'         => $c[6],
        'medal'         => $c[7],
    ]);
}
echo "✓ " . count($contestData) . " résultats de concours insérés\n\n";

// --- Partenaires ---
echo "→ Insertion des partenaires...\n";
$partners = [
    ['Conseil Départemental 49', 'conseil-departemental-49', 'institutionnel', 1],
    ['Communauté de Communes', 'communaute-communes', 'institutionnel', 2],
    ['Mairie de L\'Hôtellerie de Flée', 'mairie-hotellerie-flee', 'institutionnel', 3],
    ['Crédit Agricole Anjou Maine', 'credit-agricole', 'entreprise', 1],
    ['Super U Baugé', 'super-u-bauge', 'entreprise', 2],
    ['Boulangerie Martin', 'boulangerie-martin', 'entreprise', 3],
    ['Garage Dupont', 'garage-dupont', 'entreprise', 4],
    ['Pharmacie de Flée', 'pharmacie-flee', 'entreprise', 5],
    ['Ouest France', 'ouest-france', 'media', 1],
    ['Le Courrier de l\'Ouest', 'courrier-ouest', 'media', 2],
    ['France Bleu Maine', 'france-bleu-maine', 'media', 3],
    ['Comité des Fêtes de Flée', 'comite-fetes-flee', 'associatif', 1],
    ['Club de Randonnée', 'club-randonnee', 'associatif', 2],
    ['Les Amis du Patrimoine', 'amis-patrimoine', 'associatif', 3],
];
foreach ($partners as $p) {
    $db->insert('partners', [
        'name'       => $p[0],
        'slug'       => $p[1],
        'category'   => $p[2],
        'sort_order' => $p[3],
        'is_active'  => 1,
    ]);
}
echo "✓ " . count($partners) . " partenaires insérés\n\n";

// --- Settings ---
echo "→ Insertion des paramètres...\n";
$settings = [
    // Général
    ['general', 'site_name', 'Fête du Cidre', 'text', 'Nom du site'],
    ['general', 'site_description', 'Fête du Cidre — L\'Hôtellerie de Flée, Maine-et-Loire', 'text', 'Description du site'],
    ['general', 'association_name', 'Association Fête du Cidre', 'text', 'Nom de l\'association'],
    ['general', 'association_address', 'L\'Hôtellerie de Flée, 49500', 'text', 'Adresse'],
    ['general', 'association_email', 'contact@fetecidre.fr', 'text', 'Email de contact'],
    ['general', 'association_phone', '02 41 XX XX XX', 'text', 'Téléphone'],
    ['general', 'next_event_date', 'Dimanche 14 Juin 2026', 'text', 'Date(s) du prochain événement'],
    ['general', 'next_event_time', '10h00 - 19h00', 'text', 'Horaires'],
    ['general', 'next_event_price', 'Gratuit', 'text', 'Tarif entrée'],

    // Réseaux sociaux
    ['social', 'facebook_url', 'https://facebook.com/fetecidre', 'text', 'Page Facebook'],
    ['social', 'instagram_url', '', 'text', 'Compte Instagram'],
    ['social', 'youtube_url', '', 'text', 'Chaîne YouTube'],

    // Boutique
    ['shop', 'shop_enabled', '1', 'boolean', 'Boutique activée'],
    ['shop', 'shipping_cost', '5.90', 'number', 'Frais de port (€)'],
    ['shop', 'free_shipping_threshold', '50.00', 'number', 'Franco de port (€)'],
    ['shop', 'tax_rate', '20', 'number', 'Taux de TVA (%)'],

    // Couleurs (charte graphique)
    ['colors', 'vert-profond', '#2C4A2E', 'color', 'Vert profond'],
    ['colors', 'vert-mousse', '#4A6B3E', 'color', 'Vert mousse'],
    ['colors', 'vert-clair', '#7A9E6B', 'color', 'Vert clair'],
    ['colors', 'orange-cidre', '#D4833B', 'color', 'Orange cidre'],
    ['colors', 'orange-doux', '#E8A95B', 'color', 'Orange doux'],
    ['colors', 'creme', '#FAF5EC', 'color', 'Crème'],
    ['colors', 'creme-fonce', '#F0E8D8', 'color', 'Crème foncé'],
    ['colors', 'brun', '#5C3D2E', 'color', 'Brun'],
    ['colors', 'texte', '#2A2318', 'color', 'Texte'],
    ['colors', 'blanc', '#FFFDF8', 'color', 'Blanc'],

    // Actualités (redirection externe)
    ['news', 'redirect_url', 'https://www.helloasso.com/associations/cidre-du-haut-anjou', 'text', 'URL de redirection'],
    ['news', 'open_new_tab', '1', 'boolean', 'Ouvrir dans un nouvel onglet'],
    ['news', 'show_in_menu', '1', 'boolean', 'Afficher dans le menu'],
    ['news', 'menu_label', 'Actualités', 'text', 'Libellé du menu'],

    // SEO
    ['seo', 'google_analytics', '', 'text', 'ID Google Analytics'],
    ['seo', 'google_tag_manager', '', 'text', 'ID Google Tag Manager'],

    // Scripts personnalisés
    ['scripts', 'head_scripts', '', 'textarea', 'Scripts dans le <head>'],
    ['scripts', 'body_start_scripts', '', 'textarea', 'Scripts après <body>'],
    ['scripts', 'body_end_scripts', '', 'textarea', 'Scripts avant </body>'],
];

foreach ($settings as $s) {
    $db->insert('settings', [
        'group'       => $s[0],
        'key'         => $s[1],
        'value'       => $s[2],
        'type'        => $s[3],
        'label'       => $s[4],
    ]);
}
echo "✓ " . count($settings) . " paramètres insérés\n\n";

echo "=== Seed terminé avec succès ! ===\n";
