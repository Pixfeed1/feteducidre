<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Utilitaires de sécurité — méthodes statiques.
 * Gestion des tokens CSRF, sanitisation des entrées
 * et limitation de débit (rate limiting) basé sur fichiers.
 */
class Security
{
    /** Longueur du token CSRF en octets (sera encodé en hex = 64 caractères) */
    private const int CSRF_TOKEN_BYTES = 32;

    /** Répertoire de stockage du rate limiting */
    private const string RATE_LIMIT_DIR = 'cache/ratelimit';

    /**
     * Génère un token CSRF et le stocke en session.
     * Si un token existe déjà en session, le retourne directement.
     *
     * @return string Le token CSRF
     */
    public static function generateCsrfToken(): string
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }

        // Générer un nouveau token s'il n'en existe pas
        if (empty($_SESSION['csrf_token'])) {
            $_SESSION['csrf_token'] = bin2hex(random_bytes(self::CSRF_TOKEN_BYTES));
        }

        return $_SESSION['csrf_token'];
    }

    /**
     * Valide un token CSRF contre celui stocké en session.
     * Utilise hash_equals pour éviter les attaques par timing.
     *
     * @param string $token Le token à valider
     * @return bool Vrai si le token est valide
     */
    public static function validateCsrfToken(string $token): bool
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }

        $sessionToken = $_SESSION['csrf_token'] ?? '';

        if ($sessionToken === '' || $token === '') {
            return false;
        }

        return hash_equals($sessionToken, $token);
    }

    /**
     * Nettoie une entrée utilisateur : supprime les balises HTML
     * et encode les caractères spéciaux.
     *
     * Accepte une chaîne ou un tableau (traitement récursif).
     *
     * @param string|array $input Donnée à nettoyer
     * @return string|array Donnée nettoyée
     */
    public static function sanitize(string|array $input): string|array
    {
        if (is_array($input)) {
            return array_map([self::class, 'sanitize'], $input);
        }

        $cleaned = strip_tags($input);
        return htmlspecialchars($cleaned, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    /**
     * Vérifie si une action est autorisée selon la limite de débit.
     * Utilise un stockage fichier dans cache/ratelimit/.
     *
     * @param string $key           Identifiant unique (ex : "login_192.168.1.1")
     * @param int    $maxAttempts   Nombre maximum de tentatives dans la fenêtre
     * @param int    $windowSeconds Durée de la fenêtre en secondes
     * @return bool Vrai si l'action est autorisée, faux si la limite est atteinte
     */
    public static function rateLimit(string $key, int $maxAttempts, int $windowSeconds): bool
    {
        $basePath = dirname(__DIR__, 2);
        $rateLimitDir = $basePath . '/' . self::RATE_LIMIT_DIR;

        // Créer le répertoire si nécessaire
        if (!is_dir($rateLimitDir)) {
            mkdir($rateLimitDir, 0755, true);
        }

        $filePath = $rateLimitDir . '/' . md5($key) . '.json';
        $now = time();

        // Charger les tentatives existantes
        $attempts = self::loadAttempts($filePath);

        // Supprimer les tentatives hors de la fenêtre
        $attempts = array_filter(
            $attempts,
            fn(int $timestamp): bool => ($now - $timestamp) < $windowSeconds
        );

        // Vérifier si la limite est atteinte
        if (count($attempts) >= $maxAttempts) {
            // Sauvegarder l'état nettoyé
            self::saveAttempts($filePath, $attempts);
            return false;
        }

        // Enregistrer la tentative courante
        $attempts[] = $now;
        self::saveAttempts($filePath, $attempts);

        return true;
    }

    /**
     * Charge les tentatives depuis un fichier JSON
     *
     * @return int[] Tableau de timestamps
     */
    private static function loadAttempts(string $filePath): array
    {
        if (!file_exists($filePath)) {
            return [];
        }

        $content = file_get_contents($filePath);
        if ($content === false) {
            return [];
        }

        $data = json_decode($content, true);

        if (!is_array($data)) {
            return [];
        }

        return array_map('intval', $data);
    }

    /**
     * Sauvegarde les tentatives dans un fichier JSON
     *
     * @param int[] $attempts Tableau de timestamps
     */
    private static function saveAttempts(string $filePath, array $attempts): void
    {
        // Ré-indexer le tableau pour un JSON propre
        $attempts = array_values($attempts);

        file_put_contents(
            $filePath,
            json_encode($attempts, JSON_THROW_ON_ERROR),
            LOCK_EX
        );
    }

    /**
     * Nettoie les fichiers de rate limiting expirés.
     * À appeler périodiquement (cron ou fin de requête).
     *
     * @param int $maxAge Âge maximum des fichiers en secondes (défaut : 1 heure)
     * @return int Nombre de fichiers supprimés
     */
    public static function cleanRateLimitFiles(int $maxAge = 3600): int
    {
        $basePath = dirname(__DIR__, 2);
        $rateLimitDir = $basePath . '/' . self::RATE_LIMIT_DIR;

        if (!is_dir($rateLimitDir)) {
            return 0;
        }

        $deleted = 0;
        $now = time();
        $files = scandir($rateLimitDir);

        foreach ($files as $file) {
            if (str_starts_with($file, '.')) {
                continue;
            }

            $filePath = $rateLimitDir . '/' . $file;

            if (is_file($filePath) && ($now - filemtime($filePath)) > $maxAge) {
                unlink($filePath);
                $deleted++;
            }
        }

        return $deleted;
    }
}
