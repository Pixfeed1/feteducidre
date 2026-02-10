<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Wrapper autour de la requête HTTP.
 * Encapsule $_SERVER, $_GET, $_POST, $_FILES avec sanitisation.
 */
class Request
{
    private array $get;
    private array $post;
    private array $files;
    private array $server;

    public function __construct()
    {
        $this->server = $_SERVER;
        $this->get = $this->sanitizeArray($_GET);
        $this->post = $this->sanitizeArray($_POST);
        $this->files = $_FILES;
    }

    /**
     * Retourne le chemin de l'URL (sans query string)
     */
    public function path(): string
    {
        $path = parse_url($this->server['REQUEST_URI'] ?? '/', PHP_URL_PATH);
        return rtrim($path, '/') ?: '/';
    }

    /**
     * Retourne la méthode HTTP
     */
    public function method(): string
    {
        return strtoupper($this->server['REQUEST_METHOD'] ?? 'GET');
    }

    /**
     * Vérifie si c'est une requête POST
     */
    public function isPost(): bool
    {
        return $this->method() === 'POST';
    }

    /**
     * Vérifie si c'est une requête AJAX
     */
    public function isAjax(): bool
    {
        return ($this->server['HTTP_X_REQUESTED_WITH'] ?? '') === 'XMLHttpRequest'
            || str_contains($this->server['HTTP_ACCEPT'] ?? '', 'application/json');
    }

    /**
     * Récupère un paramètre GET
     */
    public function get(string $key, mixed $default = null): mixed
    {
        return $this->get[$key] ?? $default;
    }

    /**
     * Récupère un paramètre POST
     */
    public function post(string $key, mixed $default = null): mixed
    {
        return $this->post[$key] ?? $default;
    }

    /**
     * Récupère tous les paramètres POST
     */
    public function all(): array
    {
        return $this->post;
    }

    /**
     * Récupère un fichier uploadé
     */
    public function file(string $key): ?array
    {
        return $this->files[$key] ?? null;
    }

    /**
     * Retourne l'adresse IP du client
     */
    public function ip(): string
    {
        return $this->server['REMOTE_ADDR'] ?? '127.0.0.1';
    }

    /**
     * Récupère un header HTTP
     */
    public function header(string $name): ?string
    {
        $key = 'HTTP_' . strtoupper(str_replace('-', '_', $name));
        return $this->server[$key] ?? null;
    }

    /**
     * Récupère l'URL complète
     */
    public function fullUrl(): string
    {
        $scheme = (!empty($this->server['HTTPS']) && $this->server['HTTPS'] !== 'off') ? 'https' : 'http';
        $host = $this->server['HTTP_HOST'] ?? 'localhost';
        $uri = $this->server['REQUEST_URI'] ?? '/';
        return "{$scheme}://{$host}{$uri}";
    }

    /**
     * Sanitise récursivement un tableau d'inputs
     */
    private function sanitizeArray(array $data): array
    {
        $clean = [];
        foreach ($data as $key => $value) {
            if (is_array($value)) {
                $clean[$key] = $this->sanitizeArray($value);
            } elseif (is_string($value)) {
                $clean[$key] = trim($value);
            } else {
                $clean[$key] = $value;
            }
        }
        return $clean;
    }
}
