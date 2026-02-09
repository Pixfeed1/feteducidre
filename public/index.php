<?php

/**
 * Front controller unique — Fête du Cidre CMS.
 * Toutes les requêtes passent par ce fichier via .htaccess.
 */

declare(strict_types=1);

// Charger l'autoloader Composer
require_once dirname(__DIR__) . '/vendor/autoload.php';

// Lancer l'application
$app = new \App\Core\App();
$app->run();
