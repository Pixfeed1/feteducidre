<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des partenaires.
 * Gère les sponsors institutionnels, entreprises, médias et associatifs.
 */
class PartnerAdminController extends Controller
{
    /**
     * Liste tous les partenaires
     */
    public function index(Request $request, array $params = []): void
    {
        $category = $request->get('category');

        $sql = "SELECT * FROM partners";
        $sqlParams = [];

        if ($category) {
            $sql .= " WHERE category = ?";
            $sqlParams[] = $category;
        }

        $sql .= " ORDER BY category ASC, sort_order ASC, name ASC";

        $partners = $this->db()->fetchAll($sql, $sqlParams);

        $this->renderAdmin('templates/admin/partners/index.php', [
            'title'           => 'Partenaires',
            'partners'        => $partners,
            'currentCategory' => $category,
        ]);
    }

    /**
     * Affiche le formulaire de création d'un partenaire
     */
    public function create(Request $request, array $params = []): void
    {
        $this->renderAdmin('templates/admin/partners/form.php', [
            'title'   => 'Nouveau partenaire',
            'partner' => null,
        ]);
    }

    /**
     * Enregistre un nouveau partenaire
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['name'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le nom est obligatoire.');
            $this->redirect('/admin/partners/create');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['name']);

        $existing = $this->db()->fetch("SELECT id FROM partners WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->insert('partners', [
            'name'        => $data['name'],
            'slug'        => $slug,
            'description' => $data['description'] ?? '',
            'website'     => $data['website'] ?? null,
            'category'    => $data['category'] ?? 'autre',
            'sort_order'  => (int) ($data['sort_order'] ?? 0),
            'is_active'   => isset($data['is_active']) ? 1 : 0,
        ]);

        set_flash('success', 'Partenaire créé avec succès.');
        $this->redirect('/admin/partners');
    }

    /**
     * Affiche le formulaire de modification d'un partenaire
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $partner = $this->db()->fetch("SELECT * FROM partners WHERE id = ?", [$id]);

        if (!$partner) {
            set_flash('error', 'Partenaire introuvable.');
            $this->redirect('/admin/partners');
            return;
        }

        $this->renderAdmin('templates/admin/partners/form.php', [
            'title'   => 'Modifier : ' . $partner['name'],
            'partner' => $partner,
        ]);
    }

    /**
     * Met à jour un partenaire existant
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['name'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le nom est obligatoire.');
            $this->redirect('/admin/partners/' . $id . '/edit');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['name']);

        $existing = $this->db()->fetch("SELECT id FROM partners WHERE slug = ? AND id != ?", [$slug, $id]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->update('partners', [
            'name'        => $data['name'],
            'slug'        => $slug,
            'description' => $data['description'] ?? '',
            'website'     => $data['website'] ?? null,
            'category'    => $data['category'] ?? 'autre',
            'sort_order'  => (int) ($data['sort_order'] ?? 0),
            'is_active'   => isset($data['is_active']) ? 1 : 0,
        ], 'id = ?', [$id]);

        set_flash('success', 'Partenaire mis à jour avec succès.');
        $this->redirect('/admin/partners');
    }

    /**
     * Supprime un partenaire
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $this->db()->delete('partners', 'id = ?', [$id]);

        set_flash('success', 'Partenaire supprimé.');
        $this->redirect('/admin/partners');
    }
}
