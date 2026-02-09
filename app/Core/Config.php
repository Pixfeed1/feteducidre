<?php

declare(strict_types=1);

namespace App\Core;

use Dotenv\Dotenv;

/**
 * Gestionnaire de configuration — singleton.
 * Charge le .env une seule fois et met en cache le résultat.
 */
class Config
{
    private static ?self $instance = null;
    private array $data = [];
    private string $cacheFile;

    private function __construct()
    {
        $basePath = dirname(__DIR__, 2);
        $this->cacheFile = $basePath . '/cache/config/env.php';

        // En mode debug, toujours re-parser le .env
        if ($this->shouldUseCache()) {
            $this->data = require $this->cacheFile;
            return;
        }

        // Charger le .env
        if (file_exists($basePath . '/.env')) {
            $dotenv = Dotenv::createImmutable($basePath);
            $dotenv->load();
        }

        $this->data = $_ENV;

        // Mettre en cache si pas en mode debug
        $this->writeCache();
    }

    /**
     * Vérifie si le cache est utilisable
     */
    private function shouldUseCache(): bool
    {
        if (!file_exists($this->cacheFile)) {
            return false;
        }

        // Lire le fichier cache pour vérifier APP_DEBUG
        $cached = require $this->cacheFile;
        if (($cached['APP_DEBUG'] ?? 'true') === 'true') {
            return false;
        }

        // Vérifier que le cache n'est pas plus ancien que le .env
        $basePath = dirname(__DIR__, 2);
        $envFile = $basePath . '/.env';
        if (file_exists($envFile) && filemtime($envFile) > filemtime($this->cacheFile)) {
            return false;
        }

        return true;
    }

    /**
     * Écrit le cache de configuration
     */
    private function writeCache(): void
    {
        if (($this->data['APP_DEBUG'] ?? 'true') === 'true') {
            return;
        }

        $dir = dirname($this->cacheFile);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }

        file_put_contents(
            $this->cacheFile,
            '<?php return ' . var_export($this->data, true) . ';',
            LOCK_EX
        );
    }

    /**
     * Récupère l'instance singleton
     */
    public static function getInstance(): self
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * Récupère une valeur de configuration
     */
    public static function get(string $key, mixed $default = null): mixed
    {
        $instance = self::getInstance();
        return $instance->data[$key] ?? $default;
    }

    /**
     * Vérifie si une clé existe
     */
    public static function has(string $key): bool
    {
        $instance = self::getInstance();
        return isset($instance->data[$key]);
    }

    /**
     * Vérifie si l'application est en mode debug
     */
    public static function isDebug(): bool
    {
        return self::get('APP_DEBUG', 'false') === 'true';
    }

    /**
     * Récupère l'URL de base de l'application
     */
    public static function baseUrl(): string
    {
        return rtrim(self::get('APP_URL', 'http://localhost:8080'), '/');
    }

    /**
     * Réinitialise l'instance (utile pour les tests)
     */
    public static function reset(): void
    {
        self::$instance = null;
    }
}
