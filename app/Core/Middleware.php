<?php

declare(strict_types=1);

namespace App\Core;

use Closure;

/**
 * Interface pour les middlewares.
 * Chaque middleware traite la requête puis passe au suivant.
 */
interface Middleware
{
    /**
     * Traite la requête
     *
     * @param Request $request La requête entrante
     * @param Closure $next Le prochain middleware ou le handler final
     */
    public function handle(Request $request, Closure $next): void;
}
