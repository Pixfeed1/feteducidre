<?php

/**
 * Script de pré-génération du cache.
 * Visite les pages principales pour générer le cache HTML.
 * Usage : php scripts/cache-warmup.php
 */

declare(strict_types=1);

$baseUrl = 'http://localhost:8080';

echo "=== Pré-génération du cache ===\n\n";

$pages = [
    '/',
    '/origines',
    '/infos-pratiques',
    '/boutique',
    '/galerie',
    '/archives',
    '/concours',
    '/concours/palmares',
    '/randonnee',
    '/remerciements',
    '/mentions-legales',
    '/contact',
];

$success = 0;
$errors = 0;

foreach ($pages as $page) {
    $url = $baseUrl . $page;
    $context = stream_context_create(['http' => ['timeout' => 10]]);

    $start = microtime(true);
    $result = @file_get_contents($url, false, $context);
    $duration = round((microtime(true) - $start) * 1000);

    if ($result !== false) {
        $size = round(strlen($result) / 1024, 1);
        echo "✓ {$page} — {$duration}ms ({$size} KB)\n";
        $success++;
    } else {
        echo "✗ {$page} — ERREUR\n";
        $errors++;
    }
}

echo "\n=== Résultat ===\n";
echo "Pages cachées : {$success}\n";
echo "Erreurs : {$errors}\n";
