<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des pages.
 * Permet de lister, créer, modifier et supprimer les pages du site.
 */
class PageAdminController extends Controller
{
    /**
     * Liste toutes les pages
     */
    public function index(Request $request, array $params = []): void
    {
        $pages = $this->db()->fetchAll(
            "SELECT * FROM pages ORDER BY menu_order ASC, title ASC"
        );

        $this->renderAdmin('templates/admin/pages/index.php', [
            'title' => 'Pages',
            'pages' => $pages,
        ]);
    }

    /**
     * Affiche le formulaire de création d'une page
     */
    public function create(Request $request, array $params = []): void
    {
        $this->renderAdmin('templates/admin/pages/form.php', [
            'title' => 'Nouvelle page',
            'page'  => null,
        ]);
    }

    /**
     * Enregistre une nouvelle page en base
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        // Validation minimale
        if (empty($data['title'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le titre est obligatoire.');
            $this->redirect('/admin/pages/create');
            return;
        }

        // Génération automatique du slug si vide
        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['title']);

        // Vérifier l'unicité du slug
        $existing = $this->db()->fetch("SELECT id FROM pages WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->insert('pages', [
            'title'            => $data['title'],
            'slug'             => $slug,
            'content'          => sanitize($data['content'] ?? ''),
            'excerpt'          => $data['excerpt'] ?? '',
            'template'         => $data['template'] ?? 'default',
            'meta_title'       => $data['meta_title'] ?? '',
            'meta_description' => $data['meta_description'] ?? '',
            'status'           => $data['status'] ?? 'draft',
            'in_menu'          => isset($data['in_menu']) ? 1 : 0,
            'menu_order'       => (int) ($data['menu_order'] ?? 0),
            'created_by'       => (int) ($_SESSION['admin_user']['id'] ?? 0),
        ]);

        // Invalider le cache des pages
        $this->invalidatePageCache();

        set_flash('success', 'Page créée avec succès.');
        $this->redirect('/admin/pages');
    }

    /**
     * Affiche le formulaire de modification d'une page
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $page = $this->db()->fetch("SELECT * FROM pages WHERE id = ?", [$id]);

        if (!$page) {
            set_flash('error', 'Page introuvable.');
            $this->redirect('/admin/pages');
            return;
        }

        $this->renderAdmin('templates/admin/pages/form.php', [
            'title' => 'Modifier : ' . $page['title'],
            'page'  => $page,
        ]);
    }

    /**
     * Met à jour une page existante
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        // Validation
        if (empty($data['title'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le titre est obligatoire.');
            $this->redirect('/admin/pages/' . $id . '/edit');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['title']);

        // Vérifier l'unicité du slug (sauf pour cette page)
        $existing = $this->db()->fetch("SELECT id FROM pages WHERE slug = ? AND id != ?", [$slug, $id]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->update('pages', [
            'title'            => $data['title'],
            'slug'             => $slug,
            'content'          => sanitize($data['content'] ?? ''),
            'excerpt'          => $data['excerpt'] ?? '',
            'template'         => $data['template'] ?? 'default',
            'meta_title'       => $data['meta_title'] ?? '',
            'meta_description' => $data['meta_description'] ?? '',
            'status'           => $data['status'] ?? 'draft',
            'in_menu'          => isset($data['in_menu']) ? 1 : 0,
            'menu_order'       => (int) ($data['menu_order'] ?? 0),
        ], 'id = ?', [$id]);

        $this->invalidatePageCache();

        set_flash('success', 'Page mise à jour avec succès.');
        $this->redirect('/admin/pages');
    }

    /**
     * Supprime une page
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        $this->db()->delete('pages', 'id = ?', [$id]);
        $this->invalidatePageCache();

        set_flash('success', 'Page supprimée.');
        $this->redirect('/admin/pages');
    }

    /**
     * Invalide le cache lié aux pages
     */
    private function invalidatePageCache(): void
    {
        $cacheDir = dirname(__DIR__, 3) . '/cache/pages';
        if (is_dir($cacheDir)) {
            $files = glob($cacheDir . '/*.php');
            if ($files) {
                array_map('unlink', $files);
            }
        }
    }
}
