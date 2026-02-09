<?php

/**
 * Script de migration — exécute les fichiers SQL dans migrations/
 * Usage : php scripts/migrate.php
 */

declare(strict_types=1);

require_once dirname(__DIR__) . '/vendor/autoload.php';

use App\Core\Config;
use App\Core\Database;

// Initialiser la configuration
Config::getInstance();

echo "=== Migration Fête du Cidre ===\n\n";

try {
    $db = Database::getInstance();
    $pdo = $db->getPdo();
    echo "✓ Connexion à la base de données réussie\n\n";
} catch (\Exception $e) {
    echo "✗ Erreur de connexion : " . $e->getMessage() . "\n";
    exit(1);
}

// Lire et trier les fichiers de migration
$migrationsDir = dirname(__DIR__) . '/migrations';
$files = glob($migrationsDir . '/*.sql');

if (empty($files)) {
    echo "Aucune migration trouvée dans {$migrationsDir}\n";
    exit(0);
}

sort($files);

$success = 0;
$errors = 0;

foreach ($files as $file) {
    $filename = basename($file);
    $sql = file_get_contents($file);

    if (empty(trim($sql))) {
        echo "⊘ {$filename} — vide, ignoré\n";
        continue;
    }

    try {
        $pdo->exec($sql);
        echo "✓ {$filename} — exécuté avec succès\n";
        $success++;
    } catch (\PDOException $e) {
        echo "✗ {$filename} — ERREUR : " . $e->getMessage() . "\n";
        $errors++;
    }
}

echo "\n=== Résultat ===\n";
echo "Migrations réussies : {$success}\n";
echo "Erreurs : {$errors}\n";

if ($errors > 0) {
    exit(1);
}

echo "\n✓ Toutes les migrations ont été exécutées avec succès !\n";
