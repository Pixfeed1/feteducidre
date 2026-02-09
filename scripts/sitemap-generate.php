<?php

/**
 * Génère le sitemap.xml
 * Usage : php scripts/sitemap-generate.php
 */

declare(strict_types=1);

require_once dirname(__DIR__) . '/vendor/autoload.php';

use App\Core\Config;
use App\Services\SitemapService;

Config::getInstance();

echo "=== Génération du sitemap ===\n\n";

try {
    $path = SitemapService::save();
    echo "✓ Sitemap généré : {$path}\n";

    // Compter les URLs
    $xml = file_get_contents($path);
    $count = substr_count($xml, '<url>');
    echo "  {$count} URLs dans le sitemap\n";
} catch (\Exception $e) {
    echo "✗ Erreur : " . $e->getMessage() . "\n";
    exit(1);
}
