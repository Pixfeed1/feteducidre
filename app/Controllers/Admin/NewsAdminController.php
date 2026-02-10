<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Cache;
use App\Core\Request;

/**
 * Contrôleur de gestion de la page Actualités.
 * Configure la redirection externe et les options d'affichage dans le menu.
 */
class NewsAdminController extends Controller
{
    /** Clés de paramètres gérées */
    private const KEYS = ['redirect_url', 'open_new_tab', 'show_in_menu', 'menu_label'];

    /**
     * Affiche le formulaire de paramétrage
     */
    public function index(Request $request, array $params = []): void
    {
        $rows = $this->db()->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'news' ORDER BY `key`"
        );

        $settings = [];
        foreach ($rows as $row) {
            $settings[$row['key']] = $row['value'];
        }

        // Valeurs par défaut
        $settings += [
            'redirect_url' => '',
            'open_new_tab' => '1',
            'show_in_menu' => '1',
            'menu_label'   => 'Actualités',
        ];

        $this->renderAdmin('templates/admin/news/index.php', [
            'title'    => 'Actualités',
            'settings' => $settings,
        ]);
    }

    /**
     * Enregistre les paramètres
     */
    public function update(Request $request, array $params = []): void
    {
        $data = $request->all();

        // Champs de formulaire attendus
        $values = [
            'redirect_url' => trim($data['redirect_url'] ?? ''),
            'open_new_tab' => isset($data['open_new_tab']) ? '1' : '0',
            'show_in_menu' => isset($data['show_in_menu']) ? '1' : '0',
            'menu_label'   => trim($data['menu_label'] ?? 'Actualités'),
        ];

        foreach ($values as $key => $value) {
            $existing = $this->db()->fetch(
                "SELECT id FROM settings WHERE `group` = 'news' AND `key` = ?",
                [$key]
            );

            if ($existing) {
                $this->db()->update(
                    'settings',
                    ['value' => $value],
                    '`group` = ? AND `key` = ?',
                    ['news', $key]
                );
            } else {
                $this->db()->insert('settings', [
                    'group' => 'news',
                    'key'   => $key,
                    'value' => $value,
                    'type'  => $key === 'redirect_url' ? 'text' : ($key === 'menu_label' ? 'text' : 'boolean'),
                    'label' => ucfirst(str_replace('_', ' ', $key)),
                ]);
            }
        }

        Cache::getInstance()->flush();

        set_flash('success', 'Paramètres des actualités enregistrés avec succès.');
        $this->redirect('/admin/news');
    }
}
