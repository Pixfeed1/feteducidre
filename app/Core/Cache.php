<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Cache fichier avec TTL (Time To Live).
 * Stocke les données sérialisées dans des fichiers organisés
 * par sous-répertoires : pages/, fragments/, queries/, config/.
 */
class Cache
{
    private static ?self $instance = null;

    /** Répertoire racine du cache */
    private string $cacheDir;

    /** Sous-répertoires disponibles */
    private const array SUBDIRS = ['pages', 'fragments', 'queries', 'config'];

    private function __construct()
    {
        $this->cacheDir = dirname(__DIR__, 2) . '/cache';
        $this->ensureDirectories();
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
     * Récupère une valeur du cache.
     * Retourne null si la clé n'existe pas ou si l'entrée a expiré.
     *
     * @param string $key     Clé de cache (peut inclure un préfixe de catégorie, ex : "pages:home")
     * @param mixed  $default Valeur par défaut si miss
     * @return mixed La valeur en cache ou $default
     */
    public function get(string $key, mixed $default = null): mixed
    {
        $path = $this->keyToPath($key);

        if (!file_exists($path)) {
            return $default;
        }

        $content = file_get_contents($path);
        if ($content === false) {
            return $default;
        }

        $entry = @unserialize($content);

        // Vérifier la validité de la structure
        if (!is_array($entry) || !isset($entry['expires_at'], $entry['value'])) {
            // Fichier corrompu, le supprimer
            unlink($path);
            return $default;
        }

        // Vérifier l'expiration (0 = pas d'expiration)
        if ($entry['expires_at'] > 0 && $entry['expires_at'] < time()) {
            unlink($path);
            return $default;
        }

        return $entry['value'];
    }

    /**
     * Stocke une valeur dans le cache.
     *
     * @param string $key   Clé de cache
     * @param mixed  $value Valeur à stocker (sera sérialisée)
     * @param int    $ttl   Durée de vie en secondes (0 = pas d'expiration)
     */
    public function set(string $key, mixed $value, int $ttl = 3600): void
    {
        $path = $this->keyToPath($key);
        $dir = dirname($path);

        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }

        $entry = [
            'key'        => $key,
            'value'      => $value,
            'created_at' => time(),
            'expires_at' => $ttl > 0 ? time() + $ttl : 0,
        ];

        file_put_contents($path, serialize($entry), LOCK_EX);
    }

    /**
     * Supprime une entrée du cache
     *
     * @param string $key Clé de cache
     * @return bool Vrai si l'entrée existait et a été supprimée
     */
    public function delete(string $key): bool
    {
        $path = $this->keyToPath($key);

        if (file_exists($path)) {
            return unlink($path);
        }

        return false;
    }

    /**
     * Supprime toutes les entrées dont la clé commence par le préfixe donné.
     * Si le préfixe correspond à un sous-répertoire (pages, fragments, etc.),
     * vide tout le répertoire.
     *
     * @param string $prefix Préfixe de clé (ex : "pages", "queries", "fragments:nav")
     * @return int Nombre de fichiers supprimés
     */
    public function flush(string $prefix = ''): int
    {
        $deleted = 0;

        // Si pas de préfixe, vider tout le cache
        if ($prefix === '') {
            foreach (self::SUBDIRS as $subdir) {
                $deleted += $this->clearDirectory($this->cacheDir . '/' . $subdir);
            }
            return $deleted;
        }

        // Si le préfixe correspond à un sous-répertoire connu
        if (in_array($prefix, self::SUBDIRS, true)) {
            return $this->clearDirectory($this->cacheDir . '/' . $prefix);
        }

        // Sinon, chercher par préfixe dans le sous-répertoire correspondant
        $parts = explode(':', $prefix, 2);
        $subdir = in_array($parts[0], self::SUBDIRS, true) ? $parts[0] : 'fragments';
        $dirPath = $this->cacheDir . '/' . $subdir;

        if (!is_dir($dirPath)) {
            return 0;
        }

        // Parcourir les fichiers et vérifier la clé stockée
        $files = scandir($dirPath);
        foreach ($files as $file) {
            if (str_starts_with($file, '.')) {
                continue;
            }

            $filePath = $dirPath . '/' . $file;
            if (!is_file($filePath)) {
                continue;
            }

            $content = file_get_contents($filePath);
            $entry = @unserialize($content);

            if (is_array($entry) && isset($entry['key']) && str_starts_with($entry['key'], $prefix)) {
                unlink($filePath);
                $deleted++;
            }
        }

        return $deleted;
    }

    /**
     * Cache de fragment : récupère la valeur en cache ou exécute le callback,
     * met le résultat en cache, puis le retourne.
     *
     * Idéal pour les morceaux de template ou les requêtes coûteuses.
     *
     * @param string   $key      Clé de cache
     * @param int      $ttl      Durée de vie en secondes
     * @param callable $callback Fonction qui génère la valeur à mettre en cache
     * @return mixed La valeur (depuis le cache ou fraîchement générée)
     */
    public function fragment(string $key, int $ttl, callable $callback): mixed
    {
        $cached = $this->get($key);

        if ($cached !== null) {
            return $cached;
        }

        $value = $callback();
        $this->set($key, $value, $ttl);

        return $value;
    }

    /**
     * Convertit une clé en chemin de fichier.
     * Le format attendu est "catégorie:identifiant" (ex : "pages:home").
     * La clé est hashée en MD5 pour la sécurité des noms de fichier.
     */
    private function keyToPath(string $key): string
    {
        // Extraire la catégorie si présente
        $parts = explode(':', $key, 2);

        if (count($parts) === 2 && in_array($parts[0], self::SUBDIRS, true)) {
            $subdir = $parts[0];
        } else {
            // Par défaut, stocker dans fragments/
            $subdir = 'fragments';
        }

        $hash = md5($key);
        return $this->cacheDir . '/' . $subdir . '/' . $hash . '.cache';
    }

    /**
     * Vide tous les fichiers d'un répertoire
     *
     * @return int Nombre de fichiers supprimés
     */
    private function clearDirectory(string $dirPath): int
    {
        if (!is_dir($dirPath)) {
            return 0;
        }

        $deleted = 0;
        $files = scandir($dirPath);

        foreach ($files as $file) {
            if (str_starts_with($file, '.')) {
                continue;
            }

            $filePath = $dirPath . '/' . $file;
            if (is_file($filePath)) {
                unlink($filePath);
                $deleted++;
            }
        }

        return $deleted;
    }

    /**
     * Crée les sous-répertoires du cache s'ils n'existent pas
     */
    private function ensureDirectories(): void
    {
        foreach (self::SUBDIRS as $subdir) {
            $path = $this->cacheDir . '/' . $subdir;
            if (!is_dir($path)) {
                mkdir($path, 0755, true);
            }
        }
    }

    /**
     * Réinitialise l'instance (utile pour les tests)
     */
    public static function reset(): void
    {
        self::$instance = null;
    }
}
