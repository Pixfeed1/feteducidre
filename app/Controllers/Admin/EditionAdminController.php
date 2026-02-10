<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des éditions de la Fête du Cidre.
 * Chaque édition correspond à une année d'événement.
 * Gère aussi la section "Origines" via les settings.
 */
class EditionAdminController extends Controller
{
    /**
     * Liste toutes les éditions avec statistiques et section Origines
     */
    public function index(Request $request, array $params = []): void
    {
        // Récupérer les éditions avec les infos médias
        $editions = $this->db()->fetchAll(
            "SELECT e.*,
                    mp.filename AS poster_filename, mp.original_name AS poster_original,
                    mpr.filename AS programme_filename, mpr.original_name AS programme_original,
                    mpa.filename AS palmares_filename, mpa.original_name AS palmares_original
             FROM editions e
             LEFT JOIN media mp  ON mp.id = e.poster_image_id
             LEFT JOIN media mpr ON mpr.id = e.programme_image_id
             LEFT JOIN media mpa ON mpa.id = e.palmares_media_id
             ORDER BY e.year DESC"
        );

        // Stats
        $totalEditions = count($editions);
        $totalPosters = 0;
        $totalProgrammes = 0;
        $totalPalmares = 0;
        foreach ($editions as $ed) {
            if ($ed['poster_image_id']) $totalPosters++;
            if ($ed['programme_image_id']) $totalProgrammes++;
            if ($ed['palmares_media_id']) $totalPalmares++;
        }

        // Origines settings
        $originesRows = $this->db()->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'origines'"
        );
        $origines = [];
        foreach ($originesRows as $row) {
            $origines[$row['key']] = $row['value'];
        }

        $this->renderAdmin('templates/admin/editions/index.php', [
            'title'           => 'Archives',
            'editions'        => $editions,
            'totalEditions'   => $totalEditions,
            'totalPosters'    => $totalPosters,
            'totalProgrammes' => $totalProgrammes,
            'totalPalmares'   => $totalPalmares,
            'origines'        => $origines,
        ]);
    }

    /**
     * Affiche le formulaire de création d'une édition
     */
    public function create(Request $request, array $params = []): void
    {
        $this->renderAdmin('templates/admin/editions/form.php', [
            'title'   => 'Nouvelle édition',
            'edition' => null,
        ]);
    }

    /**
     * Enregistre une nouvelle édition avec gestion des fichiers
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['year'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'L\'année est obligatoire.');
            $this->redirect('/admin/editions/create');
            return;
        }

        // Vérifier l'unicité de l'année
        $existing = $this->db()->fetch("SELECT id FROM editions WHERE year = ?", [(int) $data['year']]);
        if ($existing) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Une édition existe déjà pour cette année.');
            $this->redirect('/admin/editions/create');
            return;
        }

        $posterMediaId = $this->handleFileUpload('poster', ['image/jpeg', 'image/png', 'image/webp']);
        $programmeMediaId = $this->handleFileUpload('programme', ['application/pdf']);
        $palmaresMediaId = $this->handleFileUpload('palmares', ['application/pdf']);

        $this->db()->insert('editions', [
            'year'               => (int) $data['year'],
            'title'              => $data['title'] ?? 'Édition ' . $data['year'],
            'description'        => sanitize($data['description'] ?? ''),
            'poster_image_id'    => $posterMediaId,
            'programme_image_id' => $programmeMediaId,
            'palmares_media_id'  => $palmaresMediaId,
            'highlights'         => $data['highlights'] ?? null,
            'stats'              => $data['stats'] ?? null,
            'notes'              => $data['notes'] ?? null,
            'is_active'          => isset($data['is_active']) ? 1 : 0,
        ]);

        set_flash('success', 'Édition créée avec succès.');
        $this->redirect('/admin/editions');
    }

    /**
     * Affiche le formulaire de modification d'une édition
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $edition = $this->db()->fetch(
            "SELECT e.*,
                    mp.filename AS poster_filename, mp.original_name AS poster_original,
                    mpr.filename AS programme_filename, mpr.original_name AS programme_original,
                    mpa.filename AS palmares_filename, mpa.original_name AS palmares_original
             FROM editions e
             LEFT JOIN media mp  ON mp.id = e.poster_image_id
             LEFT JOIN media mpr ON mpr.id = e.programme_image_id
             LEFT JOIN media mpa ON mpa.id = e.palmares_media_id
             WHERE e.id = ?",
            [$id]
        );

        if (!$edition) {
            set_flash('error', 'Édition introuvable.');
            $this->redirect('/admin/editions');
            return;
        }

        $this->renderAdmin('templates/admin/editions/form.php', [
            'title'   => 'Modifier : Édition ' . $edition['year'],
            'edition' => $edition,
        ]);
    }

    /**
     * Met à jour une édition existante
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['year'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'L\'année est obligatoire.');
            $this->redirect('/admin/editions/' . $id . '/edit');
            return;
        }

        // Vérifier l'unicité de l'année (sauf pour cette édition)
        $existing = $this->db()->fetch("SELECT id FROM editions WHERE year = ? AND id != ?", [(int) $data['year'], $id]);
        if ($existing) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Une autre édition existe déjà pour cette année.');
            $this->redirect('/admin/editions/' . $id . '/edit');
            return;
        }

        $updateData = [
            'year'        => (int) $data['year'],
            'title'       => $data['title'] ?? 'Édition ' . $data['year'],
            'description' => sanitize($data['description'] ?? ''),
            'highlights'  => $data['highlights'] ?? null,
            'stats'       => $data['stats'] ?? null,
            'notes'       => $data['notes'] ?? null,
            'is_active'   => isset($data['is_active']) ? 1 : 0,
        ];

        // Gérer les uploads de fichiers (uniquement si un nouveau fichier est envoyé)
        $posterMediaId = $this->handleFileUpload('poster', ['image/jpeg', 'image/png', 'image/webp']);
        if ($posterMediaId) {
            $updateData['poster_image_id'] = $posterMediaId;
        }

        $programmeMediaId = $this->handleFileUpload('programme', ['application/pdf']);
        if ($programmeMediaId) {
            $updateData['programme_image_id'] = $programmeMediaId;
        }

        $palmaresMediaId = $this->handleFileUpload('palmares', ['application/pdf']);
        if ($palmaresMediaId) {
            $updateData['palmares_media_id'] = $palmaresMediaId;
        }

        // Supprimer les fichiers si demandé
        if (!empty($data['remove_poster'])) {
            $updateData['poster_image_id'] = null;
        }
        if (!empty($data['remove_programme'])) {
            $updateData['programme_image_id'] = null;
        }
        if (!empty($data['remove_palmares'])) {
            $updateData['palmares_media_id'] = null;
        }

        $this->db()->update('editions', $updateData, 'id = ?', [$id]);

        set_flash('success', 'Édition mise à jour avec succès.');
        $this->redirect('/admin/editions/' . $id . '/edit');
    }

    /**
     * Supprime une édition
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $this->db()->delete('editions', 'id = ?', [$id]);

        set_flash('success', 'Édition supprimée.');
        $this->redirect('/admin/editions');
    }

    /**
     * Sauvegarde les paramètres de la section Origines
     */
    public function saveOrigines(Request $request, array $params = []): void
    {
        $data = $request->all();

        $keys = [
            'title'        => $data['origines_title'] ?? '',
            'subtitle'     => $data['origines_subtitle'] ?? '',
            'text'         => $data['origines_text'] ?? '',
            'link'         => $data['origines_link'] ?? '',
            'is_published' => !empty($data['origines_published']) ? '1' : '0',
        ];

        foreach ($keys as $key => $value) {
            $existing = $this->db()->fetch(
                "SELECT id FROM settings WHERE `group` = 'origines' AND `key` = ?",
                [$key]
            );

            if ($existing) {
                $this->db()->update('settings', [
                    'value' => $value,
                ], "`group` = 'origines' AND `key` = ?", [$key]);
            } else {
                $this->db()->insert('settings', [
                    'group' => 'origines',
                    'key'   => $key,
                    'value' => $value,
                    'type'  => $key === 'text' ? 'textarea' : ($key === 'is_published' ? 'boolean' : 'text'),
                ]);
            }
        }

        set_flash('success', 'Section Origines enregistrée.');
        $this->redirect('/admin/editions');
    }

    /**
     * Upload de l'image d'illustration Origines
     */
    public function uploadOriginesImage(Request $request, array $params = []): void
    {
        $file = $_FILES['origines_image'] ?? null;
        if (!$file || $file['error'] !== UPLOAD_ERR_OK) {
            set_flash('error', 'Aucun fichier sélectionné.');
            $this->redirect('/admin/editions');
            return;
        }

        $allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        if (!in_array($file['type'], $allowedTypes, true)) {
            set_flash('error', 'Format d\'image non supporté.');
            $this->redirect('/admin/editions');
            return;
        }

        $uploadDir = dirname(__DIR__, 3) . '/storage/uploads/large';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0755, true);
        }

        $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
        $filename = 'origines_' . time() . '.' . strtolower($ext);
        $destination = $uploadDir . '/' . $filename;

        if (!move_uploaded_file($file['tmp_name'], $destination)) {
            set_flash('error', 'Erreur lors de l\'upload.');
            $this->redirect('/admin/editions');
            return;
        }

        // Sauvegarder le nom du fichier en settings
        $existing = $this->db()->fetch(
            "SELECT id FROM settings WHERE `group` = 'origines' AND `key` = 'image'",
        );

        if ($existing) {
            $this->db()->update('settings', [
                'value' => $filename,
            ], "`group` = 'origines' AND `key` = 'image'", []);
        } else {
            $this->db()->insert('settings', [
                'group' => 'origines',
                'key'   => 'image',
                'value' => $filename,
                'type'  => 'image',
            ]);
        }

        set_flash('success', 'Image Origines mise à jour.');
        $this->redirect('/admin/editions');
    }

    /**
     * Gère l'upload d'un fichier et l'insertion dans la table media.
     * Retourne l'ID du média inséré, ou null si aucun fichier.
     */
    private function handleFileUpload(string $fieldName, array $allowedTypes): ?int
    {
        $file = $_FILES[$fieldName] ?? null;
        if (!$file || $file['error'] !== UPLOAD_ERR_OK) {
            return null;
        }

        if (!in_array($file['type'], $allowedTypes, true)) {
            return null;
        }

        $uploadDir = dirname(__DIR__, 3) . '/storage/uploads/large';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0755, true);
        }

        $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
        $filename = $fieldName . '_' . uniqid() . '.' . strtolower($ext);
        $destination = $uploadDir . '/' . $filename;

        if (!move_uploaded_file($file['tmp_name'], $destination)) {
            return null;
        }

        $width = null;
        $height = null;
        if (str_starts_with($file['type'], 'image/')) {
            $imageInfo = @getimagesize($destination);
            $width = $imageInfo[0] ?? null;
            $height = $imageInfo[1] ?? null;
        }

        return $this->db()->insert('media', [
            'filename'      => $filename,
            'original_name' => $file['name'],
            'mime_type'     => $file['type'],
            'file_size'     => $file['size'],
            'width'         => $width,
            'height'        => $height,
            'disk_path'     => 'storage/uploads/large/' . $filename,
            'uploaded_by'   => (int) ($_SESSION['admin_user']['id'] ?? 0),
        ]);
    }
}
