<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Cache;
use App\Core\Request;
use App\Core\Theme;

/**
 * Contrôleur de gestion des paramètres du site.
 * Permet de configurer les réglages généraux, sociaux, boutique,
 * couleurs du thème, scripts personnalisés et SEO.
 */
class SettingsAdminController extends Controller
{
    /** Onglets disponibles dans la page de paramètres */
    private const TABS = ['general', 'social', 'shop', 'colors', 'scripts', 'seo'];

    /**
     * Affiche la page de paramètres avec onglets
     */
    public function index(Request $request, array $params = []): void
    {
        // Récupérer tous les paramètres groupés
        $rows = $this->db()->fetchAll(
            "SELECT `group`, `key`, value, type, label FROM settings ORDER BY `group` ASC, `key` ASC"
        );

        // Organiser par groupe
        $settings = [];
        foreach ($rows as $row) {
            $settings[$row['group']][$row['key']] = $row;
        }

        // Récupérer les couleurs du thème
        $colors = Theme::getColors();
        $defaultColors = Theme::getDefaultColors();

        // Onglet actif (via query string)
        $activeTab = $request->get('tab', 'general');
        if (!in_array($activeTab, self::TABS, true)) {
            $activeTab = 'general';
        }

        $this->renderAdmin('templates/admin/settings/index.php', [
            'title'         => 'Paramètres',
            'settings'      => $settings,
            'colors'        => $colors,
            'defaultColors' => $defaultColors,
            'currentTab'    => $activeTab,
            'tabs'          => self::TABS,
        ]);
    }

    /**
     * Enregistre les paramètres modifiés.
     * Le template envoie des champs plats (name="site_name") et non
     * un tableau (name="settings[site_name]").
     */
    public function update(Request $request, array $params = []): void
    {
        $data = $request->all();
        $tab = $data['_tab'] ?? 'general';

        // Champs réservés à ne pas persister comme paramètres
        $reserved = ['_csrf_token', '_tab'];

        // Traitement spécifique pour les couleurs
        if ($tab === 'colors') {
            $defaultColors = Theme::getDefaultColors();
            foreach ($data as $key => $value) {
                if (in_array($key, $reserved, true)) {
                    continue;
                }
                if (isset($defaultColors[$key])) {
                    Theme::saveColor($key, $value);
                }
            }

            $this->invalidateCache();
            set_flash('success', 'Couleurs mises à jour avec succès.');
            $this->redirect('/admin/settings?tab=colors');
            return;
        }

        // Traitement des paramètres standards (champs plats)
        foreach ($data as $key => $value) {
            if (in_array($key, $reserved, true)) {
                continue;
            }

            // Vérifier si le paramètre existe déjà
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

        set_flash('success', 'Paramètres enregistrés avec succès.');
        $this->redirect('/admin/settings?tab=' . urlencode($tab));
    }

    /**
     * Réinitialise les couleurs du thème aux valeurs par défaut
     */
    public function resetColors(Request $request, array $params = []): void
    {
        Theme::resetColors();
        $this->invalidateCache();

        set_flash('success', 'Les couleurs ont été réinitialisées aux valeurs par défaut.');
        $this->redirect('/admin/settings?tab=colors');
    }

    /**
     * Vide le cache de l'application
     */
    public function clearCache(Request $request, array $params = []): void
    {
        $basePath = dirname(__DIR__, 3);
        $cacheDir = $basePath . '/cache';
        $deleted = 0;

        // Parcourir les sous-répertoires du cache
        $subdirs = ['pages', 'fragments', 'queries', 'config'];
        foreach ($subdirs as $subdir) {
            $dirPath = $cacheDir . '/' . $subdir;
            if (!is_dir($dirPath)) {
                continue;
            }

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
        }

        // Vider aussi le cache rate limit
        $rateLimitDir = $cacheDir . '/ratelimit';
        if (is_dir($rateLimitDir)) {
            $files = scandir($rateLimitDir);
            foreach ($files as $file) {
                if (str_starts_with($file, '.')) {
                    continue;
                }
                $filePath = $rateLimitDir . '/' . $file;
                if (is_file($filePath)) {
                    unlink($filePath);
                    $deleted++;
                }
            }
        }

        set_flash('success', 'Cache vidé avec succès (' . $deleted . ' fichier(s) supprimé(s)).');
        $this->redirect('/admin/settings?tab=general');
    }

    /**
     * Invalide le cache global
     */
    private function invalidateCache(): void
    {
        Cache::getInstance()->flush();
    }
}
