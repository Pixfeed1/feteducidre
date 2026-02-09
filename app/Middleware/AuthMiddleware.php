<?php

declare(strict_types=1);

namespace App\Middleware;

use App\Core\Config;
use App\Core\Middleware;
use App\Core\Request;
use App\Core\Response;
use Closure;

/**
 * Middleware d'authentification admin.
 * Vérifie la session et redirige vers le login si nécessaire.
 */
class AuthMiddleware implements Middleware
{
    public function handle(Request $request, Closure $next): void
    {
        // Vérifier la session admin
        if (empty($_SESSION['admin_user'])) {
            Response::redirect('/admin/login');
            return;
        }

        // Vérifier l'expiration de la session
        $lifetime = (int) Config::get('ADMIN_SESSION_LIFETIME', '7200');
        if (isset($_SESSION['admin_last_activity'])) {
            if (time() - $_SESSION['admin_last_activity'] > $lifetime) {
                session_destroy();
                session_start();
                set_flash('error', 'Votre session a expiré. Veuillez vous reconnecter.');
                Response::redirect('/admin/login');
                return;
            }
        }

        // Mettre à jour le timestamp d'activité
        $_SESSION['admin_last_activity'] = time();

        $next();
    }
}
