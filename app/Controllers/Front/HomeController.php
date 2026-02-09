<?php

declare(strict_types=1);

namespace App\Controllers\Front;

use App\Core\Controller;
use App\Core\Request;
use App\Core\Theme;

/**
 * Contrôleur de la page d'accueil.
 */
class HomeController extends Controller
{
    public function index(Request $request, array $params = []): void
    {
        $db = $this->db();

        // Récupérer la page d'accueil
        $page = $db->fetch(
            "SELECT id, title, slug, content, meta_title, meta_description, hero_image FROM pages WHERE slug = ? AND status = ?",
            ['accueil', 'published']
        );

        // Récupérer les paramètres du site
        $settings = [];
        $rows = $db->fetchAll("SELECT `group`, `key`, value FROM settings");
        foreach ($rows as $row) {
            $settings[$row['group']][$row['key']] = $row['value'];
        }

        // Produits mis en avant
        $featuredProducts = $db->fetchAll(
            "SELECT id, name, slug, short_description, price, sale_price, volume, category, image_id
             FROM products WHERE is_featured = 1 AND is_active = 1 ORDER BY sort_order ASC LIMIT 6"
        );

        // Dernières éditions
        $editions = $db->fetchAll(
            "SELECT id, year, title, description FROM editions WHERE is_active = 1 ORDER BY year DESC LIMIT 4"
        );

        // Partenaires principaux
        $partners = $db->fetchAll(
            "SELECT id, name, slug, logo_id, category, website FROM partners WHERE is_active = 1 ORDER BY category, sort_order ASC"
        );

        // SEO
        $seo = [
            'title'       => $page['meta_title'] ?? $settings['general']['site_name'] ?? 'Fête du Cidre',
            'description' => $page['meta_description'] ?? $settings['general']['site_description'] ?? '',
            'canonical'   => \App\Core\Config::baseUrl() . '/',
        ];

        $this->render('templates/front/home.php', [
            'page'             => $page,
            'seo'              => $seo,
            'settings'         => $settings,
            'featuredProducts' => $featuredProducts,
            'editions'         => $editions,
            'partners'         => $partners,
        ]);
    }
}
