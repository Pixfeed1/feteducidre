<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur de gestion des randonnées.
 * Gère les éditions, classements PDF par catégorie et réponses aux questionnaires.
 */
class HikeAdminController extends Controller
{
    /** Catégories de classement avec métadonnées */
    private const CATEGORIES = [
        'adultes'   => ['title' => 'Adultes',   'icon' => 'users', 'bg' => 'rgba(44,74,46,0.1)',    'color' => 'var(--vert-profond)'],
        'supercool' => ['title' => 'SuperCool',  'icon' => 'zap',   'bg' => 'rgba(212,131,59,0.1)',  'color' => 'var(--orange-cidre)'],
        'enfants'   => ['title' => 'Enfants',    'icon' => 'baby',  'bg' => 'rgba(122,158,107,0.12)', 'color' => 'var(--vert-mousse)'],
    ];

    /**
     * Page principale des randonnées
     */
    public function index(Request $request, array $params = []): void
    {
        // Éditions
        $editions = $this->db()->fetchAll(
            "SELECT * FROM hike_editions ORDER BY year DESC"
        );

        // Fichiers de classement groupés par édition
        $allFiles = $this->db()->fetchAll(
            "SELECT * FROM hike_files ORDER BY hike_edition_id, category"
        );
        $filesByEdition = [];
        foreach ($allFiles as $f) {
            $filesByEdition[$f['hike_edition_id']][$f['category']] = $f;
        }

        // Enrichir les éditions avec les catégories et fichiers
        $totalFiles = 0;
        $totalClassements = 0;
        foreach ($editions as &$ed) {
            $cats = $ed['categories'] ? json_decode($ed['categories'], true) : ['adultes', 'supercool', 'enfants'];
            $ed['cats'] = $cats;
            $ed['files'] = $filesByEdition[$ed['id']] ?? [];
            $filledCount = count($ed['files']);
            $totalCount = count($cats);
            $ed['filled'] = $filledCount;
            $ed['total'] = $totalCount;
            $ed['complete'] = $filledCount >= $totalCount;
            $totalClassements += $filledCount;
            $totalFiles += $filledCount;
        }
        unset($ed);

        // Réponses
        $responses = $this->db()->fetchAll(
            "SELECT * FROM hike_responses ORDER BY year DESC"
        );
        $totalFiles += count($responses);

        // Settings
        $settingsRows = $this->db()->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'hike'"
        );
        $settings = [];
        foreach ($settingsRows as $row) {
            $settings[$row['key']] = $row['value'];
        }

        $this->renderAdmin('templates/admin/hikes/index.php', [
            'title'            => 'Randonnées',
            'editions'         => $editions,
            'responses'        => $responses,
            'categories'       => self::CATEGORIES,
            'editionCount'     => count($editions),
            'classementCount'  => $totalClassements,
            'responseCount'    => count($responses),
            'fileCount'        => $totalFiles,
            'settings'         => $settings,
        ]);
    }

    /**
     * Crée une nouvelle édition
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();
        $year = (int) ($data['year'] ?? date('Y'));

        // Catégories sélectionnées
        $selectedCats = [];
        if (!empty($data['cat_adultes'])) $selectedCats[] = 'adultes';
        if (!empty($data['cat_supercool'])) $selectedCats[] = 'supercool';
        if (!empty($data['cat_enfants'])) $selectedCats[] = 'enfants';
        if (empty($selectedCats)) {
            $selectedCats = ['adultes', 'supercool', 'enfants'];
        }

        $includeResponses = ($data['include_responses'] ?? '0') === '1' ? 1 : 0;
        $isActive = ($data['is_active'] ?? '0') === '1' ? 1 : 0;

        $this->db()->insert('hike_editions', [
            'year'              => $year,
            'title'             => 'Randonnée ' . $year,
            'categories'        => json_encode($selectedCats),
            'include_responses' => $includeResponses,
            'is_active'         => $isActive,
        ]);

        set_flash('success', 'Édition ' . $year . ' créée.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Supprime une édition et ses fichiers
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        // Supprimer les fichiers physiques
        $files = $this->db()->fetchAll(
            "SELECT filename FROM hike_files WHERE hike_edition_id = ?",
            [$id]
        );
        foreach ($files as $f) {
            $this->removeUpload($f['filename']);
        }

        $this->db()->delete('hike_editions', 'id = ?', [$id]);
        set_flash('success', 'Édition supprimée.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Upload un PDF de classement pour une édition/catégorie
     */
    public function uploadFile(Request $request, array $params = []): void
    {
        $editionId = (int) ($params['id'] ?? 0);
        $data = $request->all();
        $category = $data['category'] ?? '';

        if (!array_key_exists($category, self::CATEGORIES)) {
            set_flash('error', 'Catégorie invalide.');
            $this->redirect('/admin/hikes');
            return;
        }

        $edition = $this->db()->fetch("SELECT * FROM hike_editions WHERE id = ?", [$editionId]);
        if (!$edition) {
            set_flash('error', 'Édition introuvable.');
            $this->redirect('/admin/hikes');
            return;
        }

        if (empty($_FILES['pdf_file']) || $_FILES['pdf_file']['error'] !== UPLOAD_ERR_OK) {
            set_flash('error', 'Veuillez sélectionner un fichier PDF.');
            $this->redirect('/admin/hikes');
            return;
        }

        $file = $_FILES['pdf_file'];
        $detectedMime = (new \finfo(FILEINFO_MIME_TYPE))->file($file['tmp_name']);
        if ($detectedMime !== 'application/pdf') {
            set_flash('error', 'Seuls les fichiers PDF sont acceptés.');
            $this->redirect('/admin/hikes');
            return;
        }

        if ($file['size'] > 10 * 1024 * 1024) {
            set_flash('error', 'Le fichier ne doit pas dépasser 10 Mo.');
            $this->redirect('/admin/hikes');
            return;
        }

        $uploadDir = $this->getUploadDir();
        $filename = 'classement-' . $category . '-' . $edition['year'] . '-' . time() . '.pdf';

        if (!move_uploaded_file($file['tmp_name'], $uploadDir . $filename)) {
            set_flash('error', 'Erreur lors de l\'enregistrement du fichier.');
            $this->redirect('/admin/hikes');
            return;
        }

        // Supprimer l'ancien fichier s'il existe
        $existing = $this->db()->fetch(
            "SELECT * FROM hike_files WHERE hike_edition_id = ? AND category = ?",
            [$editionId, $category]
        );
        if ($existing) {
            $this->removeUpload($existing['filename']);
            $this->db()->update('hike_files', [
                'filename'      => $filename,
                'original_name' => $file['name'],
                'file_size'     => (int) $file['size'],
            ], "id = ?", [$existing['id']]);
        } else {
            $this->db()->insert('hike_files', [
                'hike_edition_id' => $editionId,
                'category'        => $category,
                'filename'        => $filename,
                'original_name'   => $file['name'],
                'file_size'       => (int) $file['size'],
            ]);
        }

        set_flash('success', 'Classement ' . self::CATEGORIES[$category]['title'] . ' ajouté.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Supprime un fichier de classement
     */
    public function deleteFile(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $file = $this->db()->fetch("SELECT * FROM hike_files WHERE id = ?", [$id]);

        if ($file) {
            $this->removeUpload($file['filename']);
            $this->db()->delete('hike_files', 'id = ?', [$id]);
            set_flash('success', 'Fichier supprimé.');
        } else {
            set_flash('error', 'Fichier introuvable.');
        }

        $this->redirect('/admin/hikes');
    }

    /**
     * Upload une réponse au questionnaire
     */
    public function storeResponse(Request $request, array $params = []): void
    {
        $data = $request->all();
        $year = (int) ($data['year'] ?? date('Y'));

        if (empty($_FILES['pdf_file']) || $_FILES['pdf_file']['error'] !== UPLOAD_ERR_OK) {
            set_flash('error', 'Veuillez sélectionner un fichier PDF.');
            $this->redirect('/admin/hikes');
            return;
        }

        $file = $_FILES['pdf_file'];
        $detectedMime = (new \finfo(FILEINFO_MIME_TYPE))->file($file['tmp_name']);
        if ($detectedMime !== 'application/pdf') {
            set_flash('error', 'Seuls les fichiers PDF sont acceptés.');
            $this->redirect('/admin/hikes');
            return;
        }

        if ($file['size'] > 10 * 1024 * 1024) {
            set_flash('error', 'Le fichier ne doit pas dépasser 10 Mo.');
            $this->redirect('/admin/hikes');
            return;
        }

        $uploadDir = $this->getUploadDir();
        $filename = 'reponses-' . $year . '-' . time() . '.pdf';

        if (!move_uploaded_file($file['tmp_name'], $uploadDir . $filename)) {
            set_flash('error', 'Erreur lors de l\'enregistrement du fichier.');
            $this->redirect('/admin/hikes');
            return;
        }

        $maxSort = $this->db()->fetch("SELECT MAX(sort_order) AS max_sort FROM hike_responses");
        $sortOrder = ((int) ($maxSort['max_sort'] ?? 0)) + 1;

        $this->db()->insert('hike_responses', [
            'year'          => $year,
            'filename'      => $filename,
            'original_name' => $file['name'],
            'file_size'     => (int) $file['size'],
            'sort_order'    => $sortOrder,
        ]);

        set_flash('success', 'Réponse ' . $year . ' ajoutée.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Supprime une réponse
     */
    public function deleteResponse(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $response = $this->db()->fetch("SELECT * FROM hike_responses WHERE id = ?", [$id]);

        if ($response) {
            $this->removeUpload($response['filename']);
            $this->db()->delete('hike_responses', 'id = ?', [$id]);
            set_flash('success', 'Réponse supprimée.');
        } else {
            set_flash('error', 'Réponse introuvable.');
        }

        $this->redirect('/admin/hikes');
    }

    /**
     * Sauvegarde les paramètres des randonnées
     */
    public function saveSettings(Request $request, array $params = []): void
    {
        $data = $request->all();

        $keys = [
            'stats_url'     => $data['hike_stats_url'] ?? '',
            'stats_visible' => ($data['hike_stats_visible'] ?? '0') === '1' ? '1' : '0',
        ];

        foreach ($keys as $key => $value) {
            $existing = $this->db()->fetch(
                "SELECT id FROM settings WHERE `group` = 'hike' AND `key` = ?",
                [$key]
            );

            if ($existing) {
                $this->db()->update('settings', [
                    'value' => $value,
                ], "`group` = 'hike' AND `key` = ?", [$key]);
            } else {
                $this->db()->insert('settings', [
                    'group' => 'hike',
                    'key'   => $key,
                    'value' => $value,
                    'type'  => $key === 'stats_visible' ? 'boolean' : 'text',
                ]);
            }
        }

        set_flash('success', 'Paramètres enregistrés.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Répertoire d'upload pour les fichiers rando
     */
    private function getUploadDir(): string
    {
        $dir = rtrim($_SERVER['DOCUMENT_ROOT'] ?? 'public', '/') . '/uploads/randonnees/';
        if (!is_dir($dir)) {
            mkdir($dir, 0775, true);
        }
        return $dir;
    }

    /**
     * Supprime un fichier uploadé
     */
    private function removeUpload(string $filename): void
    {
        $path = rtrim($_SERVER['DOCUMENT_ROOT'] ?? 'public', '/') . '/uploads/randonnees/' . $filename;
        if (file_exists($path)) {
            unlink($path);
        }
    }
}
