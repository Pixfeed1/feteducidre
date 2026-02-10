<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;
use App\Core\Database;
use Intervention\Image\ImageManager;
use Intervention\Image\Drivers\Gd\Driver as GdDriver;

/**
 * Service de traitement d'images.
 * Gère l'upload, le redimensionnement multi-format (WebP, AVIF, JPG)
 * et l'extraction de métadonnées (dimensions, couleur dominante).
 */
class ImageService
{
    /** Largeurs des variantes générées (en pixels) */
    private const array VARIANT_WIDTHS = [800, 400, 200];

    /** Formats de sortie supportés */
    private const array OUTPUT_FORMATS = ['webp', 'avif', 'jpg'];

    /** Correspondance taille → nom du sous-dossier */
    private const array SIZE_LABELS = [
        800 => 'large',
        400 => 'medium',
        200 => 'thumb',
    ];

    private ImageManager $manager;
    private Database $db;
    private string $basePath;
    private string $uploadsPath;
    private int $qualityWebp;
    private int $qualityAvif;
    private int $qualityJpg;
    private int $maxWidth;

    public function __construct()
    {
        $this->manager = new ImageManager(new GdDriver());
        $this->db = Database::getInstance();
        $this->basePath = dirname(__DIR__, 2);
        $this->uploadsPath = $this->basePath . '/storage/uploads';

        // Qualités par défaut configurables via .env
        $this->qualityWebp = (int) Config::get('IMAGE_QUALITY_WEBP', '82');
        $this->qualityAvif = (int) Config::get('IMAGE_QUALITY_AVIF', '68');
        $this->qualityJpg  = (int) Config::get('IMAGE_QUALITY_JPG', '85');
        $this->maxWidth    = (int) Config::get('IMAGE_MAX_WIDTH', '1920');
    }

    /**
     * Traite un fichier uploadé : sauvegarde l'original, génère les variantes,
     * extrait les métadonnées et enregistre en base de données.
     *
     * @param array $uploadedFile Entrée $_FILES (tmp_name, name, size, type, error)
     * @return array{id: int, metadata: array} Identifiant média et métadonnées
     * @throws \RuntimeException En cas d'erreur de traitement
     */
    public function process(array $uploadedFile): array
    {
        // Vérifier les erreurs d'upload
        $this->validateUpload($uploadedFile);

        // Générer un nom de fichier unique
        $uniqueName = $this->generateFilename($uploadedFile['name']);
        $extension = pathinfo($uploadedFile['name'], PATHINFO_EXTENSION);
        $originalFilename = $uniqueName . '.' . strtolower($extension);

        // Sauvegarder l'original
        $originalDir = $this->uploadsPath . '/original';
        $this->ensureDirectory($originalDir);
        $originalPath = $originalDir . '/' . $originalFilename;

        if (!move_uploaded_file($uploadedFile['tmp_name'], $originalPath)) {
            throw new \RuntimeException('Impossible de déplacer le fichier uploadé.');
        }

        try {
            // Charger l'image avec Intervention
            $image = $this->manager->read($originalPath);

            // Redimensionner l'original si trop large
            $originalWidth = $image->width();
            $originalHeight = $image->height();

            if ($originalWidth > $this->maxWidth) {
                $image->scale(width: $this->maxWidth);
                $image->save($originalPath);
                $originalWidth = $image->width();
                $originalHeight = $image->height();
            }

            // Extraire la couleur dominante
            $dominantColor = $this->extractDominantColor($originalPath);

            // Générer toutes les variantes (formats x tailles)
            $variants = $this->generateVariants($originalPath, $uniqueName);

            // Préparer les métadonnées
            $metadata = [
                'original_name'  => $uploadedFile['name'],
                'filename'       => $originalFilename,
                'unique_name'    => $uniqueName,
                'mime_type'      => $uploadedFile['type'],
                'file_size'      => filesize($originalPath),
                'width'          => $originalWidth,
                'height'         => $originalHeight,
                'dominant_color' => $dominantColor,
                'variants'       => $variants,
            ];

            // Enregistrer en base de données
            $mediaId = $this->db->insert('media', [
                'original_name'  => $uploadedFile['name'],
                'filename'       => $originalFilename,
                'unique_name'    => $uniqueName,
                'mime_type'      => $uploadedFile['type'],
                'file_size'      => filesize($originalPath),
                'width'          => $originalWidth,
                'height'         => $originalHeight,
                'dominant_color' => $dominantColor,
                'variants'       => json_encode($variants, JSON_UNESCAPED_SLASHES),
                'created_at'     => date('Y-m-d H:i:s'),
            ]);

            return [
                'id'       => $mediaId,
                'metadata' => $metadata,
            ];
        } catch (\Throwable $e) {
            // Nettoyer le fichier original et les variantes déjà générées
            if (file_exists($originalPath)) {
                unlink($originalPath);
            }
            if (!empty($variants)) {
                foreach ($variants as $variant) {
                    $variantPath = $this->basePath . '/' . ltrim($variant['path'], '/');
                    if (file_exists($variantPath)) {
                        unlink($variantPath);
                    }
                }
            }
            throw new \RuntimeException(
                'Erreur lors du traitement de l\'image : ' . $e->getMessage(),
                0,
                $e
            );
        }
    }

    /**
     * Supprime un média : fichier original, toutes les variantes et l'entrée en base.
     *
     * @param int $mediaId Identifiant du média
     * @return bool Vrai si la suppression a réussi
     */
    public function delete(int $mediaId): bool
    {
        $media = $this->db->fetch('SELECT * FROM `media` WHERE `id` = ?', [$mediaId]);

        if ($media === null) {
            return false;
        }

        // Supprimer le fichier original
        $originalPath = $this->uploadsPath . '/original/' . $media['filename'];
        if (file_exists($originalPath)) {
            unlink($originalPath);
        }

        // Supprimer toutes les variantes
        $variants = json_decode($media['variants'] ?? '[]', true);
        if (is_array($variants)) {
            foreach ($variants as $variant) {
                $variantPath = $this->basePath . '/' . ltrim($variant['path'], '/');
                if (file_exists($variantPath)) {
                    unlink($variantPath);
                }
            }
        }

        // Supprimer l'entrée en base
        $this->db->delete('media', '`id` = ?', [$mediaId]);

        return true;
    }

    /**
     * Valide le fichier uploadé
     *
     * @throws \RuntimeException Si le fichier est invalide
     */
    private function validateUpload(array $uploadedFile): void
    {
        if (!isset($uploadedFile['error']) || $uploadedFile['error'] !== UPLOAD_ERR_OK) {
            $errorMessages = [
                UPLOAD_ERR_INI_SIZE   => 'Le fichier dépasse la taille maximale autorisée par le serveur.',
                UPLOAD_ERR_FORM_SIZE  => 'Le fichier dépasse la taille maximale autorisée par le formulaire.',
                UPLOAD_ERR_PARTIAL    => 'Le fichier n\'a été que partiellement uploadé.',
                UPLOAD_ERR_NO_FILE    => 'Aucun fichier n\'a été uploadé.',
                UPLOAD_ERR_NO_TMP_DIR => 'Dossier temporaire manquant sur le serveur.',
                UPLOAD_ERR_CANT_WRITE => 'Impossible d\'écrire le fichier sur le disque.',
                UPLOAD_ERR_EXTENSION  => 'Upload bloqué par une extension PHP.',
            ];

            $code = $uploadedFile['error'] ?? -1;
            $message = $errorMessages[$code] ?? 'Erreur inconnue lors de l\'upload.';
            throw new \RuntimeException($message);
        }

        // Vérifier que c'est bien une image
        $allowedMimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/avif'];
        $finfo = new \finfo(FILEINFO_MIME_TYPE);
        $detectedMime = $finfo->file($uploadedFile['tmp_name']);

        if (!in_array($detectedMime, $allowedMimes, true)) {
            throw new \RuntimeException(
                'Type de fichier non autorisé : ' . $detectedMime . '. Formats acceptés : JPEG, PNG, GIF, WebP, AVIF.'
            );
        }
    }

    /**
     * Génère un nom de fichier unique basé sur le timestamp et une chaîne aléatoire
     */
    private function generateFilename(string $originalName): string
    {
        $timestamp = date('Ymd_His');
        $random = bin2hex(random_bytes(8));
        $slug = slugify(pathinfo($originalName, PATHINFO_FILENAME));

        return $timestamp . '_' . $random . '_' . $slug;
    }

    /**
     * Génère les variantes de l'image dans tous les formats et toutes les tailles
     *
     * @return array Liste des variantes générées avec chemin et métadonnées
     */
    private function generateVariants(string $originalPath, string $uniqueName): array
    {
        $variants = [];

        foreach (self::VARIANT_WIDTHS as $width) {
            $sizeLabel = self::SIZE_LABELS[$width];
            $sizeDir = $this->uploadsPath . '/' . $sizeLabel;
            $this->ensureDirectory($sizeDir);

            foreach (self::OUTPUT_FORMATS as $format) {
                $variantFilename = $uniqueName . '.' . $format;
                $variantPath = $sizeDir . '/' . $variantFilename;
                $quality = $this->getQualityForFormat($format);

                try {
                    // Charger une copie fraîche pour chaque variante
                    $variant = $this->manager->read($originalPath);
                    $variant->scaleDown(width: $width);

                    // Encoder dans le format cible
                    $encoded = match ($format) {
                        'webp' => $variant->toWebp($quality),
                        'avif' => $variant->toAvif($quality),
                        'jpg'  => $variant->toJpeg($quality),
                    };

                    $encoded->save($variantPath);

                    $variants[] = [
                        'format' => $format,
                        'width'  => $width,
                        'size'   => $sizeLabel,
                        'path'   => 'storage/uploads/' . $sizeLabel . '/' . $variantFilename,
                    ];
                } catch (\Throwable $e) {
                    // Si un format échoue (ex : AVIF non supporté), on continue
                    error_log(
                        "ImageService : impossible de générer la variante {$format}/{$sizeLabel} "
                        . "pour {$uniqueName} — " . $e->getMessage()
                    );
                }
            }
        }

        return $variants;
    }

    /**
     * Retourne la qualité de compression pour un format donné
     */
    private function getQualityForFormat(string $format): int
    {
        return match ($format) {
            'webp' => $this->qualityWebp,
            'avif' => $this->qualityAvif,
            'jpg'  => $this->qualityJpg,
            default => 80,
        };
    }

    /**
     * Extrait la couleur dominante en échantillonnant les pixels centraux de l'image.
     * Retourne une couleur hexadécimale (ex : #a3b24f).
     */
    private function extractDominantColor(string $imagePath): string
    {
        try {
            $image = $this->manager->read($imagePath);

            // Réduire l'image à une petite taille pour accélérer l'échantillonnage
            $sample = $image->scale(width: 50);
            $sampleWidth = $sample->width();
            $sampleHeight = $sample->height();

            // Échantillonner les pixels autour du centre
            $centerX = (int) ($sampleWidth / 2);
            $centerY = (int) ($sampleHeight / 2);
            $radius = 5;

            $totalR = 0;
            $totalG = 0;
            $totalB = 0;
            $count = 0;

            for ($x = max(0, $centerX - $radius); $x <= min($sampleWidth - 1, $centerX + $radius); $x++) {
                for ($y = max(0, $centerY - $radius); $y <= min($sampleHeight - 1, $centerY + $radius); $y++) {
                    $color = $sample->pickColor($x, $y);
                    $totalR += $color->red()->toInt();
                    $totalG += $color->green()->toInt();
                    $totalB += $color->blue()->toInt();
                    $count++;
                }
            }

            if ($count === 0) {
                return '#888888';
            }

            $avgR = (int) round($totalR / $count);
            $avgG = (int) round($totalG / $count);
            $avgB = (int) round($totalB / $count);

            return sprintf('#%02x%02x%02x', $avgR, $avgG, $avgB);
        } catch (\Throwable) {
            return '#888888';
        }
    }

    /**
     * Crée un répertoire s'il n'existe pas
     */
    private function ensureDirectory(string $path): void
    {
        if (!is_dir($path)) {
            mkdir($path, 0755, true);
        }
    }
}
