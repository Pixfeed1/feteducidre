<?php

declare(strict_types=1);

namespace App\Middleware;

use App\Core\Cache;
use App\Core\Config;
use App\Core\Middleware;
use App\Core\Request;
use Closure;

/**
 * Middleware de cache HTTP pleine page.
 * Met en cache le HTML généré par les contrôleurs pour les requêtes GET
 * des visiteurs anonymes sur les pages publiques.
 */
class CacheMiddleware implements Middleware
{
    /** Routes à ne jamais mettre en cache */
    private const array EXCLUDED_PREFIXES = [
        '/admin',
        '/panier',
        '/commande',
    ];

    /**
     * Traite la requête : sert le cache si disponible,
     * sinon capture la sortie et la met en cache.
     */
    public function handle(Request $request, Closure $next): void
    {
        // Vérifier si le cache est activé
        if (Config::get('CACHE_ENABLED') !== 'true') {
            $next();
            return;
        }

        // Ne pas mettre en cache les requêtes POST
        if ($request->isPost()) {
            $next();
            return;
        }

        // Ne pas mettre en cache les routes exclues
        $path = $request->path();
        foreach (self::EXCLUDED_PREFIXES as $prefix) {
            if (str_starts_with($path, $prefix)) {
                $next();
                return;
            }
        }

        // Ne pas mettre en cache pour les utilisateurs connectés
        if (!empty($_SESSION['admin_user'])) {
            $next();
            return;
        }

        // Générer la clé de cache basée sur l'URL complète
        $cacheKey = 'pages:' . $this->buildCacheKey($request);
        $cache = Cache::getInstance();
        $ttl = (int) Config::get('CACHE_PAGES_TTL', '86400');

        // Vérifier si une version en cache existe
        $cached = $cache->get($cacheKey);

        if ($cached !== null) {
            // Cache HIT : servir directement le HTML en cache
            header('X-Cache: HIT');
            echo $cached;
            return;
        }

        // Cache MISS : capturer la sortie du contrôleur
        header('X-Cache: MISS');
        ob_start();

        $next();

        $output = ob_get_clean();

        // Ne mettre en cache que les réponses non vides avec un code 200
        if ($output !== false && $output !== '' && http_response_code() === 200) {
            $cache->set($cacheKey, $output, $ttl);
        }

        echo $output;
    }

    /**
     * Construit une clé de cache unique pour la requête courante.
     * Inclut le chemin et les paramètres GET triés.
     */
    private function buildCacheKey(Request $request): string
    {
        $path = $request->path();

        // Inclure les paramètres GET significatifs (pagination, filtres, etc.)
        $queryString = $_GET;
        ksort($queryString);

        if (!empty($queryString)) {
            $path .= '?' . http_build_query($queryString);
        }

        return $path;
    }
}
