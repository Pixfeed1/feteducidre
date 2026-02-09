<?php

declare(strict_types=1);

namespace App\Middleware;

use App\Core\Config;
use App\Core\Middleware;
use App\Core\Request;
use Closure;

/**
 * Middleware de mode maintenance.
 * Affiche une page de maintenance pour tous les visiteurs,
 * sauf les administrateurs authentifiés par secret ou les routes admin.
 */
class MaintenanceMiddleware implements Middleware
{
    /**
     * Vérifie si le site est en maintenance et bloque l'accès si nécessaire.
     */
    public function handle(Request $request, Closure $next): void
    {
        // Vérifier si le mode maintenance est activé
        if (Config::get('MAINTENANCE_ENABLED') !== 'true') {
            $next();
            return;
        }

        // Toujours autoriser les routes admin
        $path = $request->path();
        if (str_starts_with($path, '/admin')) {
            $next();
            return;
        }

        // Vérifier le bypass par paramètre GET
        $secret = Config::get('MAINTENANCE_SECRET', '');
        if ($secret !== '') {
            $bypassParam = $_GET['bypass'] ?? '';

            if ($bypassParam === $secret) {
                // Poser un cookie pour les requêtes suivantes
                setcookie('maintenance_bypass', $secret, [
                    'expires'  => time() + 86400,
                    'path'     => '/',
                    'httponly'  => true,
                    'samesite' => 'Lax',
                ]);

                $next();
                return;
            }

            // Vérifier le cookie de bypass
            $bypassCookie = $_COOKIE['maintenance_bypass'] ?? '';
            if ($bypassCookie === $secret) {
                $next();
                return;
            }
        }

        // Afficher la page de maintenance
        $this->renderMaintenancePage();
    }

    /**
     * Affiche la page de maintenance et arrête l'exécution.
     */
    private function renderMaintenancePage(): void
    {
        http_response_code(503);
        header('Content-Type: text/html; charset=UTF-8');
        header('Retry-After: 3600');

        // Variables disponibles dans le template
        $estimatedReturn = Config::get('MAINTENANCE_RETURN_TIME', '');
        $siteName = Config::get('APP_NAME', 'Fête du Cidre');

        $templatePath = dirname(__DIR__, 2) . '/templates/front/maintenance.php';

        if (file_exists($templatePath)) {
            include $templatePath;
        } else {
            echo '<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
                . '<title>Maintenance — ' . htmlspecialchars($siteName) . '</title></head>'
                . '<body><h1>Site en maintenance</h1>'
                . '<p>Nous effectuons une mise à jour. Veuillez réessayer ultérieurement.</p>'
                . '</body></html>';
        }

        exit;
    }
}
