<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Cache;
use App\Core\Request;
use App\Core\Theme;

/**
 * Contrôleur de gestion des paramètres du site.
 */
class SettingsAdminController extends Controller
{
    private const TABS = [
        'general'  => 'Général',
        'identity' => 'Identité',
        'seo'      => 'SEO',
        'social'   => 'Réseaux',
        'email'    => 'E-mails',
        'legal'    => 'Légal',
        'scripts'  => 'Scripts',
        'advanced' => 'Avancé',
    ];

    private const TAB_ICONS = [
        'general'  => 'building-2',
        'identity' => 'palette',
        'seo'      => 'globe',
        'social'   => 'share-2',
        'email'    => 'send',
        'legal'    => 'scale',
        'scripts'  => 'code',
        'advanced' => 'wrench',
    ];

    public function index(Request $request, array $params = []): void
    {
        $rows = $this->db()->fetchAll(
            "SELECT `group`, `key`, value, type, label FROM settings ORDER BY `group` ASC, `key` ASC"
        );

        $settings = [];
        foreach ($rows as $row) {
            $settings[$row['group']][$row['key']] = $row;
        }

        $colors = Theme::getColors();
        $defaultColors = Theme::getDefaultColors();

        $activeTab = $request->get('tab', 'general');
        if (!array_key_exists($activeTab, self::TABS)) {
            $activeTab = 'general';
        }

        $this->renderAdmin('templates/admin/settings/index.php', [
            'title'         => 'Paramètres',
            'settings'      => $settings,
            'colors'        => $colors,
            'defaultColors' => $defaultColors,
            'currentTab'    => $activeTab,
            'tabs'          => self::TABS,
            'tabIcons'      => self::TAB_ICONS,
        ]);
    }

    public function update(Request $request, array $params = []): void
    {
        $data = $request->all();
        $tab = $data['_tab'] ?? 'general';

        $reserved = ['_csrf_token', '_tab'];

        // Colors tab — delegate to Theme
        if ($tab === 'colors') {
            $defaultColors = Theme::getDefaultColors();
            foreach ($data as $key => $value) {
                if (in_array($key, $reserved, true)) continue;
                if (isset($defaultColors[$key])) {
                    Theme::saveColor($key, $value);
                }
            }
            $this->invalidateCache();
            set_flash('success', 'Couleurs mises à jour.');
            $this->redirect('/admin/settings?tab=identity');
            return;
        }

        // Standard settings
        foreach ($data as $key => $value) {
            if (in_array($key, $reserved, true)) continue;

            $existing = $this->db()->fetch(
                "SELECT id FROM settings WHERE `group` = ? AND `key` = ?",
                [$tab, $key]
            );

            if ($existing) {
                $this->db()->update(
                    'settings',
                    ['value' => $value],
                    '`group` = ? AND `key` = ?',
                    [$tab, $key]
                );
            } else {
                $this->db()->insert('settings', [
                    'group' => $tab,
                    'key'   => $key,
                    'value' => $value,
                    'type'  => 'text',
                    'label' => ucfirst(str_replace('_', ' ', $key)),
                ]);
            }
        }

        $this->invalidateCache();
        set_flash('success', 'Paramètres enregistrés.');
        $this->redirect('/admin/settings?tab=' . urlencode($tab));
    }

    public function resetColors(Request $request, array $params = []): void
    {
        Theme::resetColors();
        $this->invalidateCache();
        set_flash('success', 'Couleurs réinitialisées aux valeurs par défaut.');
        $this->redirect('/admin/settings?tab=identity');
    }

    public function uploadLogo(Request $request, array $params = []): void
    {
        $field = $params['type'] ?? 'logo'; // 'logo' or 'favicon'
        $fileKey = $field === 'favicon' ? 'favicon_file' : 'logo_file';

        if (empty($_FILES[$fileKey]['tmp_name'])) {
            set_flash('error', 'Aucun fichier sélectionné.');
            $this->redirect('/admin/settings?tab=identity');
            return;
        }

        $file = $_FILES[$fileKey];
        $allowed = ['image/png', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp', 'image/x-icon', 'image/vnd.microsoft.icon'];
        $detectedMime = (new \finfo(FILEINFO_MIME_TYPE))->file($file['tmp_name']);
        if (!in_array($detectedMime, $allowed, true)) {
            set_flash('error', 'Format de fichier non autorisé.');
            $this->redirect('/admin/settings?tab=identity');
            return;
        }

        if ($file['size'] > 5 * 1024 * 1024) {
            set_flash('error', 'Fichier trop volumineux (max 5 Mo).');
            $this->redirect('/admin/settings?tab=identity');
            return;
        }

        $dir = $this->getUploadDir();
        $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
        $filename = $field . '_' . uniqid() . '.' . strtolower($ext);

        if (!move_uploaded_file($file['tmp_name'], $dir . $filename)) {
            set_flash('error', 'Erreur lors de l\'upload.');
            $this->redirect('/admin/settings?tab=identity');
            return;
        }

        // Remove old file
        $settingKey = $field === 'favicon' ? 'favicon_filename' : 'logo_filename';
        $old = $this->db()->fetch(
            "SELECT value FROM settings WHERE `group` = 'identity' AND `key` = ?",
            [$settingKey]
        );
        if ($old && !empty($old['value'])) {
            $oldPath = $dir . $old['value'];
            if (file_exists($oldPath)) unlink($oldPath);
        }

        // Save setting
        $existing = $this->db()->fetch(
            "SELECT id FROM settings WHERE `group` = 'identity' AND `key` = ?",
            [$settingKey]
        );
        if ($existing) {
            $this->db()->update('settings', ['value' => $filename], '`group` = ? AND `key` = ?', ['identity', $settingKey]);
        } else {
            $this->db()->insert('settings', [
                'group' => 'identity',
                'key'   => $settingKey,
                'value' => $filename,
                'type'  => 'image',
                'label' => $field === 'favicon' ? 'Favicon' : 'Logo',
            ]);
        }

        $this->invalidateCache();
        set_flash('success', ucfirst($field) . ' mis à jour.');
        $this->redirect('/admin/settings?tab=identity');
    }

    public function removeLogo(Request $request, array $params = []): void
    {
        $field = $params['type'] ?? 'logo';
        $settingKey = $field === 'favicon' ? 'favicon_filename' : 'logo_filename';

        $setting = $this->db()->fetch(
            "SELECT value FROM settings WHERE `group` = 'identity' AND `key` = ?",
            [$settingKey]
        );

        if ($setting && !empty($setting['value'])) {
            $path = $this->getUploadDir() . $setting['value'];
            if (file_exists($path)) unlink($path);

            $this->db()->update('settings', ['value' => ''], '`group` = ? AND `key` = ?', ['identity', $settingKey]);
        }

        $this->invalidateCache();
        set_flash('success', ucfirst($field) . ' supprimé.');
        $this->redirect('/admin/settings?tab=identity');
    }

    public function clearCache(Request $request, array $params = []): void
    {
        $basePath = dirname(__DIR__, 3);
        $cacheDir = $basePath . '/cache';
        $deleted = 0;

        $subdirs = ['pages', 'fragments', 'queries', 'config', 'ratelimit'];
        foreach ($subdirs as $subdir) {
            $dirPath = $cacheDir . '/' . $subdir;
            if (!is_dir($dirPath)) continue;

            $files = scandir($dirPath);
            foreach ($files as $file) {
                if (str_starts_with($file, '.')) continue;
                $filePath = $dirPath . '/' . $file;
                if (is_file($filePath)) {
                    unlink($filePath);
                    $deleted++;
                }
            }
        }

        set_flash('success', 'Cache vidé (' . $deleted . ' fichier(s) supprimé(s)).');
        $this->redirect('/admin/settings?tab=advanced');
    }

    public function exportDb(Request $request, array $params = []): void
    {
        $dbName = $_ENV['DB_DATABASE'] ?? 'fete_cidre';
        $dbUser = $_ENV['DB_USERNAME'] ?? 'root';
        $dbPass = $_ENV['DB_PASSWORD'] ?? '';
        $dbHost = $_ENV['DB_HOST'] ?? 'localhost';

        $filename = $dbName . '_' . date('Y-m-d_His') . '.sql';
        $tmpPath = sys_get_temp_dir() . '/' . $filename;

        $passArg = $dbPass ? '-p' . escapeshellarg($dbPass) : '';
        $cmd = sprintf(
            'mysqldump -h %s -u %s %s %s > %s 2>&1',
            escapeshellarg($dbHost),
            escapeshellarg($dbUser),
            $passArg,
            escapeshellarg($dbName),
            escapeshellarg($tmpPath)
        );

        exec($cmd, $output, $returnVar);

        if ($returnVar !== 0 || !file_exists($tmpPath)) {
            set_flash('error', 'Erreur lors de l\'export de la base de données.');
            $this->redirect('/admin/settings?tab=advanced');
            return;
        }

        $safeFilename = preg_replace('/[^a-zA-Z0-9._-]/', '_', $filename);
        header('Content-Type: application/sql');
        header('Content-Disposition: attachment; filename="' . $safeFilename . '"');
        header('Content-Length: ' . filesize($tmpPath));
        readfile($tmpPath);
        unlink($tmpPath);
        exit;
    }

    private function getUploadDir(): string
    {
        $dir = dirname(__DIR__, 3) . '/public/uploads/settings/';
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        return $dir;
    }

    private function invalidateCache(): void
    {
        Cache::getInstance()->flush();
    }
}
