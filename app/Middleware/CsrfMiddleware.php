<?php

declare(strict_types=1);

namespace App\Middleware;

use App\Core\Middleware;
use App\Core\Request;
use App\Core\Response;
use Closure;

/**
 * Middleware CSRF — vérifie le token sur toutes les requêtes POST.
 */
class CsrfMiddleware implements Middleware
{
    public function handle(Request $request, Closure $next): void
    {
        if ($request->isPost()) {
            $token = $request->post('_csrf_token');
            $sessionToken = $_SESSION['csrf_token'] ?? '';

            if (empty($token) || !hash_equals($sessionToken, $token)) {
                if ($request->isAjax()) {
                    Response::json(['error' => 'Token CSRF invalide'], 403);
                    return;
                }
                set_flash('error', 'Le formulaire a expiré. Veuillez réessayer.');
                Response::redirect($request->path());
                return;
            }
        }

        $next();
    }
}
