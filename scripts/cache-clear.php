<?php

/**
 * Script de vidage du cache
 * Usage : php scripts/cache-clear.php [prefix]
 */

declare(strict_types=1);

$cacheDir = dirname(__DIR__) . '/cache';
$prefix = $argv[1] ?? '';

echo "=== Vidage du cache ===\n\n";

$dirs = ['pages', 'fragments', 'queries', 'config'];
$totalDeleted = 0;

foreach ($dirs as $dir) {
    $path = $cacheDir . '/' . $dir;
    if (!is_dir($path)) {
        continue;
    }

    if ($prefix && $dir !== $prefix) {
        continue;
    }

    $files = glob($path . '/*');
    $count = 0;

    foreach ($files as $file) {
        if (is_file($file)) {
            unlink($file);
            $count++;
        }
    }

    echo "✓ {$dir}/ : {$count} fichiers supprimés\n";
    $totalDeleted += $count;
}

echo "\nTotal : {$totalDeleted} fichiers de cache supprimés.\n";
