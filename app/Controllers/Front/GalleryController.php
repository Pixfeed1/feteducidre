<?php

declare(strict_types=1);

namespace App\Controllers\Front;

use App\Core\Controller;
use App\Core\Config;
use App\Core\Request;
use App\Core\Response;

/**
 * Contrôleur de la galerie photo.
 * Gère la liste des albums et l'affichage des photos.
 */
class GalleryController extends Controller
{
    /**
     * Galerie photos — albums groupés par année avec filtre par type.
     */
    public function index(Request $request, array $params = []): void
    {
        $db = $this->db();

        // Récupérer les albums actifs avec l'image de couverture
        $albums = $db->fetchAll(
            "SELECT a.id, a.title, a.slug, a.description, a.type, a.year, a.photo_count, a.cover_image_id,
                    m.filename AS cover_filename, m.alt_text AS cover_alt,
                    m.width AS cover_width, m.height AS cover_height,
                    m.dominant_color AS cover_color, m.has_webp AS cover_webp,
                    m.has_avif AS cover_avif, m.sizes AS cover_sizes
             FROM albums a
             LEFT JOIN media m ON a.cover_image_id = m.id
             WHERE a.is_active = 1
             ORDER BY a.year DESC, a.sort_order ASC"
        );

        // Construire les objets image de couverture et grouper par année
        $albumsByYear = [];
        $typesSet = [];
        foreach ($albums as &$album) {
            $album['cover_image'] = null;
            if ($album['cover_filename']) {
                $album['cover_image'] = [
                    'filename'       => $album['cover_filename'],
                    'alt_text'       => $album['cover_alt'],
                    'width'          => $album['cover_width'],
                    'height'         => $album['cover_height'],
                    'dominant_color' => $album['cover_color'],
                    'has_webp'       => $album['cover_webp'],
                    'has_avif'       => $album['cover_avif'],
                    'sizes'          => $album['cover_sizes'],
                ];
            }
            $year = (int) ($album['year'] ?? 0);
            $albumsByYear[$year][] = $album;
            if (!empty($album['type'])) {
                $typesSet[$album['type']] = true;
            }
        }
        unset($album);

        $types = array_keys($typesSet);

        // SEO
        $seo = [
            'title'       => 'Galerie Photos — Archives — Fête du Cidre',
            'description' => 'Retrouvez en images les plus beaux moments de la Fête du Cidre à L\'Hôtellerie de Flée.',
            'canonical'   => Config::baseUrl() . '/galerie',
        ];

        $this->render('templates/front/gallery/index.php', [
            'albumsByYear' => $albumsByYear,
            'types'        => $types,
            'seo'          => $seo,
        ]);
    }

    /**
     * Affiche les photos d'un album par son slug.
     */
    public function album(Request $request, array $params = []): void
    {
        $slug = $params['slug'] ?? '';
        $db = $this->db();

        // Récupérer l'album
        $album = $db->fetch(
            "SELECT id, title, slug, description, type, year, photo_count
             FROM albums WHERE slug = ? AND is_active = 1",
            [$slug]
        );

        if (!$album) {
            Response::notFound();
            return;
        }

        // Récupérer les photos de l'album avec les données média
        $photos = $db->fetchAll(
            "SELECT p.id, p.title, p.description, p.sort_order,
                    m.id AS media_id, m.filename, m.alt_text, m.width, m.height,
                    m.dominant_color, m.has_webp, m.has_avif, m.sizes
             FROM photos p
             JOIN media m ON p.media_id = m.id
             WHERE p.album_id = ?
             ORDER BY p.sort_order ASC, p.id ASC",
            [(int) $album['id']]
        );

        // Construire les objets image pour chaque photo
        foreach ($photos as &$photo) {
            $photo['image'] = [
                'filename'       => $photo['filename'],
                'alt_text'       => $photo['alt_text'] ?? $photo['title'],
                'width'          => $photo['width'],
                'height'         => $photo['height'],
                'dominant_color' => $photo['dominant_color'],
                'has_webp'       => $photo['has_webp'],
                'has_avif'       => $photo['has_avif'],
                'sizes'          => $photo['sizes'],
            ];
        }
        unset($photo);

        // SEO
        $seo = [
            'title'       => $album['title'] . ' — Galerie Fête du Cidre',
            'description' => $album['description']
                ? excerpt($album['description'], 160)
                : 'Photos de l\'album ' . $album['title'] . ' de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/galerie/' . $album['slug'],
        ];

        $this->render('templates/front/gallery/album.php', [
            'album'  => $album,
            'photos' => $photos,
            'seo'    => $seo,
        ]);
    }
}
