<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;
use App\Core\Database;

/**
 * Service de génération du sitemap XML.
 */
class SitemapService
{
    /**
     * Génère le sitemap XML complet
     */
    public static function generate(): string
    {
        $baseUrl = Config::baseUrl();
        $db = Database::getInstance();

        $urls = [];

        // Page d'accueil
        $urls[] = [
            'loc'        => $baseUrl . '/',
            'changefreq' => 'weekly',
            'priority'   => '1.0',
        ];

        // Pages publiées
        $pages = $db->fetchAll(
            "SELECT slug, updated_at FROM pages WHERE status = 'published' AND slug != 'accueil'"
        );
        foreach ($pages as $page) {
            $urls[] = [
                'loc'        => $baseUrl . '/' . $page['slug'],
                'lastmod'    => date('Y-m-d', strtotime($page['updated_at'])),
                'changefreq' => 'monthly',
                'priority'   => '0.7',
            ];
        }

        // Produits actifs
        $products = $db->fetchAll(
            "SELECT slug, updated_at FROM products WHERE is_active = 1"
        );
        foreach ($products as $product) {
            $urls[] = [
                'loc'        => $baseUrl . '/boutique/' . $product['slug'],
                'lastmod'    => date('Y-m-d', strtotime($product['updated_at'])),
                'changefreq' => 'monthly',
                'priority'   => '0.6',
            ];
        }

        // Boutique
        $urls[] = [
            'loc'        => $baseUrl . '/boutique',
            'changefreq' => 'weekly',
            'priority'   => '0.8',
        ];

        // Galerie
        $urls[] = [
            'loc'        => $baseUrl . '/galerie',
            'changefreq' => 'monthly',
            'priority'   => '0.6',
        ];

        // Albums
        $albums = $db->fetchAll(
            "SELECT slug, updated_at FROM albums WHERE is_active = 1"
        );
        foreach ($albums as $album) {
            $urls[] = [
                'loc'        => $baseUrl . '/galerie/' . $album['slug'],
                'lastmod'    => date('Y-m-d', strtotime($album['updated_at'])),
                'changefreq' => 'monthly',
                'priority'   => '0.5',
            ];
        }

        // Archives
        $urls[] = [
            'loc'        => $baseUrl . '/archives',
            'changefreq' => 'yearly',
            'priority'   => '0.5',
        ];

        // Éditions
        $editions = $db->fetchAll(
            "SELECT year FROM editions WHERE is_active = 1"
        );
        foreach ($editions as $edition) {
            $urls[] = [
                'loc'        => $baseUrl . '/archives/' . $edition['year'],
                'changefreq' => 'yearly',
                'priority'   => '0.4',
            ];
        }

        // Générer le XML
        $xml = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        $xml .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";

        foreach ($urls as $url) {
            $xml .= "  <url>\n";
            $xml .= "    <loc>" . htmlspecialchars($url['loc']) . "</loc>\n";
            if (isset($url['lastmod'])) {
                $xml .= "    <lastmod>" . $url['lastmod'] . "</lastmod>\n";
            }
            $xml .= "    <changefreq>" . $url['changefreq'] . "</changefreq>\n";
            $xml .= "    <priority>" . $url['priority'] . "</priority>\n";
            $xml .= "  </url>\n";
        }

        $xml .= '</urlset>';

        return $xml;
    }

    /**
     * Génère et sauvegarde le sitemap dans public/sitemap.xml
     */
    public static function save(): string
    {
        $xml = self::generate();
        $path = dirname(__DIR__, 2) . '/public/sitemap.xml';
        file_put_contents($path, $xml, LOCK_EX);
        return $path;
    }
}
