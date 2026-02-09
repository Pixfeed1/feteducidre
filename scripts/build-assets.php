<?php

/**
 * Script de build des assets — minification CSS/JS et génération du manifest.
 * Usage : php scripts/build-assets.php
 */

declare(strict_types=1);

require_once dirname(__DIR__) . '/vendor/autoload.php';

use MatthiasMullie\Minify;

echo "=== Build des assets ===\n\n";

$publicDir = dirname(__DIR__) . '/public';
$distDir = $publicDir . '/assets/dist';
$manifest = [];

// Créer le dossier dist
if (!is_dir($distDir)) {
    mkdir($distDir, 0755, true);
}

// ── CSS ──
echo "→ Minification CSS...\n";
$cssFiles = glob($publicDir . '/assets/css/*.css');
foreach ($cssFiles as $file) {
    $basename = basename($file, '.css');
    $content = file_get_contents($file);

    // Minifier
    $minifier = new Minify\CSS($content);
    $minified = $minifier->minify();

    // Hash du contenu
    $hash = substr(md5($minified), 0, 8);
    $outFile = "{$basename}.{$hash}.css";

    file_put_contents($distDir . '/' . $outFile, $minified);
    $manifest["assets/css/{$basename}.css"] = "assets/dist/{$outFile}";

    $originalSize = round(strlen($content) / 1024, 1);
    $minifiedSize = round(strlen($minified) / 1024, 1);
    echo "  ✓ {$basename}.css → {$outFile} ({$originalSize}KB → {$minifiedSize}KB)\n";
}

// ── JS ──
echo "\n→ Minification JS...\n";
$jsFiles = glob($publicDir . '/assets/js/*.js');
foreach ($jsFiles as $file) {
    $basename = basename($file, '.js');
    $content = file_get_contents($file);

    // Minifier
    $minifier = new Minify\JS($content);
    $minified = $minifier->minify();

    // Hash du contenu
    $hash = substr(md5($minified), 0, 8);
    $outFile = "{$basename}.{$hash}.js";

    file_put_contents($distDir . '/' . $outFile, $minified);
    $manifest["assets/js/{$basename}.js"] = "assets/dist/{$outFile}";

    $originalSize = round(strlen($content) / 1024, 1);
    $minifiedSize = round(strlen($minified) / 1024, 1);
    echo "  ✓ {$basename}.js → {$outFile} ({$originalSize}KB → {$minifiedSize}KB)\n";
}

// ── Manifest ──
$manifestPath = $publicDir . '/assets/manifest.json';
file_put_contents($manifestPath, json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

echo "\n✓ Manifest généré : " . count($manifest) . " fichiers\n";
echo "  {$manifestPath}\n";
