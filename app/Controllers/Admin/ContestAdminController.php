<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur de gestion du concours.
 * Gère les palmarès PDF, les documents d'inscription et les paramètres du concours.
 */
class ContestAdminController extends Controller
{
    /** Catégories d'inscription avec métadonnées */
    private const CATEGORIES = [
        'professionnels' => [
            'title' => 'Professionnels',
            'desc'  => 'Cidriers du Grand Ouest',
            'icon'  => 'trophy',
            'color' => 'var(--orange-cidre)',
        ],
        'amateurs' => [
            'title' => 'Amateurs',
            'desc'  => 'Cidre maison',
            'icon'  => 'apple',
            'color' => 'var(--vert-mousse)',
        ],
        'producteurs' => [
            'title' => 'Producteurs',
            'desc'  => 'Producteurs locaux',
            'icon'  => 'tree-deciduous',
            'color' => 'var(--brun)',
        ],
    ];

    /**
     * Page principale du concours : inscriptions, palmarès, paramètres
     */
    public function index(Request $request, array $params = []): void
    {
        // Palmarès documents
        $palmares = $this->db()->fetchAll(
            "SELECT * FROM contest_palmares ORDER BY year DESC, type ASC"
        );

        // Inscription documents groupés par catégorie
        $allDocs = $this->db()->fetchAll(
            "SELECT * FROM contest_documents ORDER BY category ASC, sort_order ASC, id ASC"
        );
        $documents = ['professionnels' => [], 'amateurs' => [], 'producteurs' => []];
        foreach ($allDocs as $doc) {
            $documents[$doc['category']][] = $doc;
        }

        // Stats
        $cidreCount = 0;
        $affichesCount = 0;
        foreach ($palmares as $p) {
            if ($p['type'] === 'cidre') {
                $cidreCount++;
            } else {
                $affichesCount++;
            }
        }
        $docCount = count($allDocs);

        // Contest settings
        $settingsRows = $this->db()->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'contest'"
        );
        $settings = [];
        foreach ($settingsRows as $row) {
            $settings[$row['key']] = $row['value'];
        }

        $registrationsOpen = ($settings['registrations_open'] ?? '0') === '1';
        $year = date('Y');

        $this->renderAdmin('templates/admin/contests/index.php', [
            'title'             => 'Concours',
            'palmares'          => $palmares,
            'documents'         => $documents,
            'categories'        => self::CATEGORIES,
            'cidreCount'        => $cidreCount,
            'affichesCount'     => $affichesCount,
            'docCount'          => $docCount,
            'settings'          => $settings,
            'registrationsOpen' => $registrationsOpen,
            'currentYear'       => $year,
        ]);
    }

    /**
     * Ajoute un palmarès PDF
     */
    public function storePalmares(Request $request, array $params = []): void
    {
        $data = $request->all();
        $year = (int) ($data['year'] ?? date('Y'));
        $type = in_array($data['type'] ?? '', ['cidre', 'affiches']) ? $data['type'] : 'cidre';
        $label = trim($data['label'] ?? '');

        // Gérer le fichier uploadé
        if (empty($_FILES['pdf_file']) || $_FILES['pdf_file']['error'] !== UPLOAD_ERR_OK) {
            set_flash('error', 'Veuillez sélectionner un fichier PDF.');
            $this->redirect('/admin/contests');
            return;
        }

        $file = $_FILES['pdf_file'];
        $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if ($ext !== 'pdf') {
            set_flash('error', 'Seuls les fichiers PDF sont acceptés.');
            $this->redirect('/admin/contests');
            return;
        }

        if ($file['size'] > 10 * 1024 * 1024) {
            set_flash('error', 'Le fichier ne doit pas dépasser 10 Mo.');
            $this->redirect('/admin/contests');
            return;
        }

        $uploadDir = rtrim($_SERVER['DOCUMENT_ROOT'] ?? 'public', '/') . '/uploads/concours/';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0775, true);
        }

        $filename = 'palmares-' . $type . '-' . $year . '-' . time() . '.pdf';
        $destPath = $uploadDir . $filename;

        if (!move_uploaded_file($file['tmp_name'], $destPath)) {
            set_flash('error', 'Erreur lors de l\'enregistrement du fichier.');
            $this->redirect('/admin/contests');
            return;
        }

        // Calculer le sort_order
        $maxSort = $this->db()->fetch(
            "SELECT MAX(sort_order) AS max_sort FROM contest_palmares"
        );
        $sortOrder = ((int) ($maxSort['max_sort'] ?? 0)) + 1;

        $this->db()->insert('contest_palmares', [
            'year'          => $year,
            'type'          => $type,
            'filename'      => $filename,
            'original_name' => $file['name'],
            'file_size'     => (int) $file['size'],
            'label'         => $label ?: null,
            'sort_order'    => $sortOrder,
        ]);

        set_flash('success', 'Palmarès ajouté avec succès.');
        $this->redirect('/admin/contests');
    }

    /**
     * Supprime un palmarès
     */
    public function deletePalmares(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $palmares = $this->db()->fetch("SELECT * FROM contest_palmares WHERE id = ?", [$id]);

        if ($palmares) {
            $filePath = rtrim($_SERVER['DOCUMENT_ROOT'] ?? 'public', '/') . '/uploads/concours/' . $palmares['filename'];
            if (file_exists($filePath)) {
                unlink($filePath);
            }
            $this->db()->delete('contest_palmares', 'id = ?', [$id]);
            set_flash('success', 'Palmarès supprimé.');
        } else {
            set_flash('error', 'Palmarès introuvable.');
        }

        $this->redirect('/admin/contests');
    }

    /**
     * Ajoute un document d'inscription
     */
    public function storeDocument(Request $request, array $params = []): void
    {
        $data = $request->all();
        $category = $data['category'] ?? '';
        $name = trim($data['name'] ?? '');

        if (!array_key_exists($category, self::CATEGORIES)) {
            set_flash('error', 'Catégorie invalide.');
            $this->redirect('/admin/contests');
            return;
        }

        if (empty($name)) {
            set_flash('error', 'Le nom du document est obligatoire.');
            $this->redirect('/admin/contests');
            return;
        }

        if (empty($_FILES['doc_file']) || $_FILES['doc_file']['error'] !== UPLOAD_ERR_OK) {
            set_flash('error', 'Veuillez sélectionner un fichier PDF.');
            $this->redirect('/admin/contests');
            return;
        }

        $file = $_FILES['doc_file'];
        $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if ($ext !== 'pdf') {
            set_flash('error', 'Seuls les fichiers PDF sont acceptés.');
            $this->redirect('/admin/contests');
            return;
        }

        if ($file['size'] > 10 * 1024 * 1024) {
            set_flash('error', 'Le fichier ne doit pas dépasser 10 Mo.');
            $this->redirect('/admin/contests');
            return;
        }

        $uploadDir = rtrim($_SERVER['DOCUMENT_ROOT'] ?? 'public', '/') . '/uploads/concours/';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0775, true);
        }

        $filename = 'doc-' . $category . '-' . time() . '.pdf';
        $destPath = $uploadDir . $filename;

        if (!move_uploaded_file($file['tmp_name'], $destPath)) {
            set_flash('error', 'Erreur lors de l\'enregistrement du fichier.');
            $this->redirect('/admin/contests');
            return;
        }

        $maxSort = $this->db()->fetch(
            "SELECT MAX(sort_order) AS max_sort FROM contest_documents WHERE category = ?",
            [$category]
        );
        $sortOrder = ((int) ($maxSort['max_sort'] ?? 0)) + 1;

        $this->db()->insert('contest_documents', [
            'category'      => $category,
            'name'          => $name,
            'filename'      => $filename,
            'original_name' => $file['name'],
            'file_size'     => (int) $file['size'],
            'sort_order'    => $sortOrder,
        ]);

        set_flash('success', 'Document ajouté avec succès.');
        $this->redirect('/admin/contests');
    }

    /**
     * Supprime un document d'inscription
     */
    public function deleteDocument(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $doc = $this->db()->fetch("SELECT * FROM contest_documents WHERE id = ?", [$id]);

        if ($doc) {
            $filePath = rtrim($_SERVER['DOCUMENT_ROOT'] ?? 'public', '/') . '/uploads/concours/' . $doc['filename'];
            if (file_exists($filePath)) {
                unlink($filePath);
            }
            $this->db()->delete('contest_documents', 'id = ?', [$id]);
            set_flash('success', 'Document supprimé.');
        } else {
            set_flash('error', 'Document introuvable.');
        }

        $this->redirect('/admin/contests');
    }

    /**
     * Sauvegarde les paramètres du concours
     */
    public function saveSettings(Request $request, array $params = []): void
    {
        $data = $request->all();

        $keys = [
            'edition_name'          => $data['contest_edition_name'] ?? '',
            'contest_date'          => $data['contest_date'] ?? '',
            'registration_deadline' => $data['contest_registration_deadline'] ?? '',
            'contact_email'         => $data['contest_contact_email'] ?? '',
            'info_message'          => $data['contest_info_message'] ?? '',
            'registrations_open'    => ($data['contest_registrations_open'] ?? '0') === '1' ? '1' : '0',
            'show_palmares'         => ($data['contest_show_palmares'] ?? '0') === '1' ? '1' : '0',
            'show_info_banner'      => ($data['contest_show_info_banner'] ?? '0') === '1' ? '1' : '0',
        ];

        foreach ($keys as $key => $value) {
            $existing = $this->db()->fetch(
                "SELECT id FROM settings WHERE `group` = 'contest' AND `key` = ?",
                [$key]
            );

            if ($existing) {
                $this->db()->update('settings', [
                    'value' => $value,
                ], "`group` = 'contest' AND `key` = ?", [$key]);
            } else {
                $this->db()->insert('settings', [
                    'group' => 'contest',
                    'key'   => $key,
                    'value' => $value,
                    'type'  => in_array($key, ['info_message']) ? 'textarea' : (in_array($key, ['registrations_open', 'show_palmares', 'show_info_banner']) ? 'boolean' : 'text'),
                ]);
            }
        }

        set_flash('success', 'Paramètres du concours enregistrés.');
        $this->redirect('/admin/contests');
    }
}
