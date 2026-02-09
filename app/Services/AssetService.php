<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;

/**
 * Service de gestion des assets front-end (CSS, JS).
 * En production, utilise un manifeste de versions (hash de contenu)
 * pour le cache-busting navigateur. En développement, ajoute un
 * paramètre ?v= basé sur la date de modification du fichier.
 */
class AssetService
{
    private static ?self $instance = null;

    /** Manifeste chargé en mémoire (chemin original → chemin versionné) */
    private ?array $manifest = null;

    private string $basePath;
    private string $publicPath;
    private string $manifestPath;

    private function __construct()
    {
        $this->basePath = dirname(__DIR__, 2);
        $this->publicPath = $this->basePath . '/public';
        $this->manifestPath = $this->publicPath . '/assets/manifest.json';
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
     * Retourne le chemin versionné d'un asset.
     *
     * En production : utilise le manifeste pour retourner le fichier hashé.
     * En développement : ajoute un paramètre ?v= basé sur filemtime.
     *
     * @param string $asset Chemin relatif de l'asset (ex : "css/style.css")
     * @return string Chemin versionné prêt à être utilisé dans le HTML
     */
    public function getPath(string $asset): string
    {
        // Normaliser le chemin (retirer /assets/ s'il est déjà présent)
        $asset = ltrim($asset, '/');
        if (str_starts_with($asset, 'assets/')) {
            $asset = substr($asset, 7);
        }

        // En production, utiliser le manifeste
        if (!Config::isDebug()) {
            $manifest = $this->loadManifest();
            if ($manifest !== null && isset($manifest[$asset])) {
                return '/assets/' . $manifest[$asset];
            }
        }

        // Fallback : ajouter ?v= avec le timestamp de modification
        $fullPath = $this->publicPath . '/assets/' . $asset;
        $version = file_exists($fullPath) ? filemtime($fullPath) : time();

        return '/assets/' . $asset . '?v=' . $version;
    }

    /**
     * Construit le manifeste de versions : copie chaque fichier CSS/JS
     * avec un hash de contenu dans le nom, puis génère manifest.json.
     *
     * À exécuter lors du déploiement ou via un script de build.
     *
     * @return array Le manifeste généré (chemin original → chemin versionné)
     */
    public function buildManifest(): array
    {
        $assetsDir = $this->publicPath . '/assets';
        $manifest = [];

        // Parcourir les répertoires CSS et JS
        $directories = ['css', 'js'];

        foreach ($directories as $dir) {
            $dirPath = $assetsDir . '/' . $dir;
            if (!is_dir($dirPath)) {
                continue;
            }

            $files = scandir($dirPath);
            foreach ($files as $file) {
                // Ignorer les fichiers cachés et les fichiers déjà hashés
                if (str_starts_with($file, '.')) {
                    continue;
                }

                $ext = pathinfo($file, PATHINFO_EXTENSION);
                if (!in_array($ext, ['css', 'js'], true)) {
                    continue;
                }

                // Ignorer les fichiers qui contiennent déjà un hash (pattern: name.hash.ext)
                $basename = pathinfo($file, PATHINFO_FILENAME);
                if (preg_match('/\.[a-f0-9]{8,}$/', $basename)) {
                    continue;
                }

                $filePath = $dirPath . '/' . $file;
                $content = file_get_contents($filePath);
                $hash = substr(md5($content), 0, 10);

                // Nom du fichier versionné : style.a1b2c3d4e5.css
                $versionedName = $basename . '.' . $hash . '.' . $ext;
                $versionedPath = $dirPath . '/' . $versionedName;

                // Copier le fichier avec le nom versionné
                copy($filePath, $versionedPath);

                // Enregistrer dans le manifeste
                $relativeOriginal = $dir . '/' . $file;
                $relativeVersioned = $dir . '/' . $versionedName;
                $manifest[$relativeOriginal] = $relativeVersioned;
            }
        }

        // Écrire le manifeste JSON
        file_put_contents(
            $this->manifestPath,
            json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES),
            LOCK_EX
        );

        // Mettre à jour le cache en mémoire
        $this->manifest = $manifest;

        return $manifest;
    }

    /**
     * Charge le manifeste depuis le fichier JSON (une seule fois par requête)
     *
     * @return array|null Le manifeste ou null s'il n'existe pas
     */
    private function loadManifest(): ?array
    {
        if ($this->manifest !== null) {
            return $this->manifest;
        }

        if (!file_exists($this->manifestPath)) {
            return null;
        }

        $content = file_get_contents($this->manifestPath);
        $decoded = json_decode($content, true);

        if (!is_array($decoded)) {
            return null;
        }

        $this->manifest = $decoded;
        return $this->manifest;
    }

    /**
     * Nettoie les anciens fichiers versionnés qui ne sont plus dans le manifeste
     */
    public function cleanOldVersions(): int
    {
        $assetsDir = $this->publicPath . '/assets';
        $manifest = $this->loadManifest();
        $versionedFiles = $manifest !== null ? array_values($manifest) : [];
        $deleted = 0;

        foreach (['css', 'js'] as $dir) {
            $dirPath = $assetsDir . '/' . $dir;
            if (!is_dir($dirPath)) {
                continue;
            }

            $files = scandir($dirPath);
            foreach ($files as $file) {
                if (str_starts_with($file, '.')) {
                    continue;
                }

                $basename = pathinfo($file, PATHINFO_FILENAME);

                // Vérifier si c'est un fichier versionné (contient un hash)
                if (!preg_match('/\.[a-f0-9]{8,}$/', $basename)) {
                    continue;
                }

                $relativePath = $dir . '/' . $file;

                // Supprimer si pas dans le manifeste actuel
                if (!in_array($relativePath, $versionedFiles, true)) {
                    unlink($dirPath . '/' . $file);
                    $deleted++;
                }
            }
        }

        return $deleted;
    }

    /**
     * Réinitialise l'instance (utile pour les tests)
     */
    public static function reset(): void
    {
        self::$instance = null;
    }
}
