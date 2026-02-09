<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Routeur simple basé sur regex.
 * Supporte les paramètres dynamiques, les groupes avec préfixe et les middlewares.
 */
class Router
{
    private array $routes = [];
    private array $groupStack = [];

    /**
     * Ajoute une route GET
     */
    public function get(string $path, array|string $handler): self
    {
        return $this->addRoute('GET', $path, $handler);
    }

    /**
     * Ajoute une route POST
     */
    public function post(string $path, array|string $handler): self
    {
        return $this->addRoute('POST', $path, $handler);
    }

    /**
     * Génère les routes CRUD standard pour une ressource
     */
    public function resource(string $prefix, string $controller): self
    {
        $this->get($prefix, [$controller, 'index']);
        $this->get($prefix . '/create', [$controller, 'create']);
        $this->post($prefix . '/store', [$controller, 'store']);
        $this->get($prefix . '/{id}/edit', [$controller, 'edit']);
        $this->post($prefix . '/{id}/update', [$controller, 'update']);
        $this->post($prefix . '/{id}/delete', [$controller, 'destroy']);
        return $this;
    }

    /**
     * Groupe de routes avec préfixe et middlewares communs
     */
    public function group(string $prefix, array|string $middleware, callable $callback): self
    {
        $this->groupStack[] = [
            'prefix'     => $prefix,
            'middleware' => is_array($middleware) ? $middleware : [$middleware],
        ];

        $callback($this);

        array_pop($this->groupStack);
        return $this;
    }

    /**
     * Dispatch la requête vers le bon handler
     */
    public function dispatch(Request $request): void
    {
        $method = $request->method();
        $path = $request->path();

        foreach ($this->routes as $route) {
            if ($route['method'] !== $method) {
                continue;
            }

            $pattern = $this->buildPattern($route['path']);

            if (preg_match($pattern, $path, $matches)) {
                // Extraire les paramètres nommés
                $params = array_filter($matches, 'is_string', ARRAY_FILTER_USE_KEY);

                // Exécuter les middlewares
                $this->runMiddlewares($route['middleware'], $request, function () use ($route, $request, $params) {
                    $this->callHandler($route['handler'], $request, $params);
                });
                return;
            }
        }

        // Aucune route trouvée → 404
        Response::notFound();
    }

    /**
     * Ajoute une route au registre
     */
    private function addRoute(string $method, string $path, array|string $handler): self
    {
        $prefix = '';
        $middleware = [];

        foreach ($this->groupStack as $group) {
            $prefix .= $group['prefix'];
            $middleware = array_merge($middleware, $group['middleware']);
        }

        $this->routes[] = [
            'method'     => $method,
            'path'       => $prefix . $path,
            'handler'    => $handler,
            'middleware'  => $middleware,
        ];

        return $this;
    }

    /**
     * Convertit un chemin avec paramètres en regex
     * Ex: /boutique/{slug} → #^/boutique/(?P<slug>[^/]+)$#
     */
    private function buildPattern(string $path): string
    {
        $pattern = preg_replace('#\{([a-zA-Z_]+)\}#', '(?P<$1>[^/]+)', $path);
        return '#^' . $pattern . '$#';
    }

    /**
     * Exécute la pipeline de middlewares
     */
    private function runMiddlewares(array $middlewares, Request $request, callable $final): void
    {
        if (empty($middlewares)) {
            $final();
            return;
        }

        $middleware = array_shift($middlewares);

        if (is_string($middleware)) {
            $middleware = new $middleware();
        }

        $middleware->handle($request, function () use ($middlewares, $request, $final) {
            $this->runMiddlewares($middlewares, $request, $final);
        });
    }

    /**
     * Appelle le handler (controller@method ou callable)
     */
    private function callHandler(array|string $handler, Request $request, array $params): void
    {
        if (is_array($handler)) {
            [$class, $method] = $handler;
            $controller = new $class();
            $controller->$method($request, $params);
        } elseif (is_callable($handler)) {
            $handler($request, $params);
        }
    }
}
