<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des albums photos.
 * Gère les albums et l'upload de photos associées.
 */
class AlbumAdminController extends Controller
{
    /**
     * Liste tous les albums
     */
    public function index(Request $request, array $params = []): void
    {
        $albums = $this->db()->fetchAll(
            "SELECT * FROM albums ORDER BY year DESC, title ASC"
        );

        $this->renderAdmin('templates/admin/albums/index.php', [
            'title'  => 'Galerie',
            'albums' => $albums,
        ]);
    }

    /**
     * Affiche le formulaire de création d'un album
     */
    public function create(Request $request, array $params = []): void
    {
        $this->renderAdmin('templates/admin/albums/form.php', [
            'title'  => 'Nouvel album',
            'album'  => null,
            'photos' => [],
        ]);
    }

    /**
     * Enregistre un nouvel album
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['title'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le titre est obligatoire.');
            $this->redirect('/admin/albums/create');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['title']);

        $existing = $this->db()->fetch("SELECT id FROM albums WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->insert('albums', [
            'title'       => $data['title'],
            'slug'        => $slug,
            'description' => $data['description'] ?? '',
            'year'        => !empty($data['year']) ? (int) $data['year'] : null,
            'sort_order'  => (int) ($data['sort_order'] ?? 0),
            'is_active'   => isset($data['is_active']) ? 1 : 0,
        ]);

        set_flash('success', 'Album créé avec succès.');
        $this->redirect('/admin/albums');
    }

    /**
     * Affiche le formulaire de modification d'un album avec ses photos
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $album = $this->db()->fetch("SELECT * FROM albums WHERE id = ?", [$id]);

        if (!$album) {
            set_flash('error', 'Album introuvable.');
            $this->redirect('/admin/albums');
            return;
        }

        // Récupérer les photos de l'album avec les infos média
        $photos = $this->db()->fetchAll(
            "SELECT p.*, m.filename, m.original_name, m.width, m.height
             FROM photos p
             JOIN media m ON m.id = p.media_id
             WHERE p.album_id = ?
             ORDER BY p.sort_order ASC",
            [$id]
        );

        $this->renderAdmin('templates/admin/albums/form.php', [
            'title'  => 'Modifier : ' . $album['title'],
            'album'  => $album,
            'photos' => $photos,
        ]);
    }

    /**
     * Met à jour un album existant
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['title'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le titre est obligatoire.');
            $this->redirect('/admin/albums/' . $id . '/edit');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['title']);

        $existing = $this->db()->fetch("SELECT id FROM albums WHERE slug = ? AND id != ?", [$slug, $id]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->update('albums', [
            'title'       => $data['title'],
            'slug'        => $slug,
            'description' => $data['description'] ?? '',
            'year'        => !empty($data['year']) ? (int) $data['year'] : null,
            'sort_order'  => (int) ($data['sort_order'] ?? 0),
            'is_active'   => isset($data['is_active']) ? 1 : 0,
        ], 'id = ?', [$id]);

        set_flash('success', 'Album mis à jour avec succès.');
        $this->redirect('/admin/albums/' . $id . '/edit');
    }

    /**
     * Supprime un album et toutes ses photos associées
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        // Les photos sont supprimées en cascade grâce à la clé étrangère
        $this->db()->delete('albums', 'id = ?', [$id]);

        set_flash('success', 'Album supprimé.');
        $this->redirect('/admin/albums');
    }

    /**
     * Upload de photos multiples pour un album
     */
    public function uploadPhotos(Request $request, array $params = []): void
    {
        $albumId = (int) ($params['id'] ?? 0);

        $album = $this->db()->fetch("SELECT id FROM albums WHERE id = ?", [$albumId]);
        if (!$album) {
            if ($request->isAjax()) {
                $this->json(['error' => 'Album introuvable.'], 404);
                return;
            }
            set_flash('error', 'Album introuvable.');
            $this->redirect('/admin/albums');
            return;
        }

        $files = $_FILES['photos'] ?? null;
        if (!$files || empty($files['name'][0])) {
            set_flash('error', 'Aucun fichier sélectionné.');
            $this->redirect('/admin/albums/' . $albumId . '/edit');
            return;
        }

        $uploadDir = dirname(__DIR__, 3) . '/storage/uploads/large';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0755, true);
        }

        $uploadCount = 0;
        $fileCount = count($files['name']);

        for ($i = 0; $i < $fileCount; $i++) {
            if ($files['error'][$i] !== UPLOAD_ERR_OK) {
                continue;
            }

            $originalName = $files['name'][$i];
            $tmpFile = $files['tmp_name'][$i];
            $mimeType = $files['type'][$i];
            $fileSize = $files['size'][$i];

            // Vérifier le type MIME
            $allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/avif'];
            if (!in_array($mimeType, $allowedTypes, true)) {
                continue;
            }

            // Générer un nom unique
            $ext = pathinfo($originalName, PATHINFO_EXTENSION);
            $filename = uniqid('photo_') . '.' . strtolower($ext);
            $destination = $uploadDir . '/' . $filename;

            if (!move_uploaded_file($tmpFile, $destination)) {
                continue;
            }

            // Récupérer les dimensions
            $imageInfo = @getimagesize($destination);
            $width = $imageInfo[0] ?? null;
            $height = $imageInfo[1] ?? null;

            // Insérer dans la table media
            $mediaId = $this->db()->insert('media', [
                'filename'      => $filename,
                'original_name' => $originalName,
                'mime_type'     => $mimeType,
                'file_size'     => $fileSize,
                'width'         => $width,
                'height'        => $height,
                'disk_path'     => 'storage/uploads/large/' . $filename,
                'uploaded_by'   => (int) ($_SESSION['admin_user']['id'] ?? 0),
            ]);

            // Insérer dans la table photos
            $this->db()->insert('photos', [
                'album_id'   => $albumId,
                'media_id'   => $mediaId,
                'title'      => pathinfo($originalName, PATHINFO_FILENAME),
                'sort_order' => $uploadCount,
            ]);

            $uploadCount++;
        }

        // Mettre à jour le compteur de photos de l'album
        $photoCount = (int) ($this->db()->fetch(
            "SELECT COUNT(*) AS total FROM photos WHERE album_id = ?",
            [$albumId]
        )['total'] ?? 0);

        $this->db()->update('albums', ['photo_count' => $photoCount], 'id = ?', [$albumId]);

        if ($uploadCount > 0) {
            set_flash('success', $uploadCount . ' photo(s) ajoutée(s) avec succès.');
        } else {
            set_flash('error', 'Aucune photo n\'a pu être uploadée.');
        }

        $this->redirect('/admin/albums/' . $albumId . '/edit');
    }

    /**
     * Supprime une photo d'un album
     */
    public function deletePhoto(Request $request, array $params = []): void
    {
        $photoId = (int) ($params['id'] ?? 0);

        $photo = $this->db()->fetch(
            "SELECT p.*, m.disk_path FROM photos p JOIN media m ON m.id = p.media_id WHERE p.id = ?",
            [$photoId]
        );

        if (!$photo) {
            set_flash('error', 'Photo introuvable.');
            $this->redirect('/admin/albums');
            return;
        }

        $albumId = (int) $photo['album_id'];

        // Supprimer le fichier physique
        $filePath = dirname(__DIR__, 3) . '/' . $photo['disk_path'];
        if (file_exists($filePath)) {
            unlink($filePath);
        }

        // Supprimer le média et la photo
        $this->db()->delete('photos', 'id = ?', [$photoId]);
        $this->db()->delete('media', 'id = ?', [(int) $photo['media_id']]);

        // Mettre à jour le compteur
        $photoCount = (int) ($this->db()->fetch(
            "SELECT COUNT(*) AS total FROM photos WHERE album_id = ?",
            [$albumId]
        )['total'] ?? 0);

        $this->db()->update('albums', ['photo_count' => $photoCount], 'id = ?', [$albumId]);

        set_flash('success', 'Photo supprimée.');
        $this->redirect('/admin/albums/' . $albumId . '/edit');
    }
}
