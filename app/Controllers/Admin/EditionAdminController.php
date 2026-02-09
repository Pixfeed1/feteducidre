<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des éditions de la Fête du Cidre.
 * Chaque édition correspond à une année d'événement.
 */
class EditionAdminController extends Controller
{
    /**
     * Liste toutes les éditions
     */
    public function index(Request $request, array $params = []): void
    {
        $editions = $this->db()->fetchAll(
            "SELECT * FROM editions ORDER BY year DESC"
        );

        $this->renderAdmin('templates/admin/editions/index.php', [
            'title'    => 'Éditions',
            'editions' => $editions,
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
     * Enregistre une nouvelle édition
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

        $this->db()->insert('editions', [
            'year'        => (int) $data['year'],
            'title'       => $data['title'] ?? 'Édition ' . $data['year'],
            'description' => sanitize($data['description'] ?? ''),
            'highlights'  => $data['highlights'] ?? null,
            'stats'       => $data['stats'] ?? null,
            'is_active'   => isset($data['is_active']) ? 1 : 0,
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
        $edition = $this->db()->fetch("SELECT * FROM editions WHERE id = ?", [$id]);

        if (!$edition) {
            set_flash('error', 'Édition introuvable.');
            $this->redirect('/admin/editions');
            return;
        }

        $this->renderAdmin('templates/admin/editions/form.php', [
            'title'   => 'Modifier : ' . $edition['title'],
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

        $this->db()->update('editions', [
            'year'        => (int) $data['year'],
            'title'       => $data['title'] ?? 'Édition ' . $data['year'],
            'description' => sanitize($data['description'] ?? ''),
            'highlights'  => $data['highlights'] ?? null,
            'stats'       => $data['stats'] ?? null,
            'is_active'   => isset($data['is_active']) ? 1 : 0,
        ], 'id = ?', [$id]);

        set_flash('success', 'Édition mise à jour avec succès.');
        $this->redirect('/admin/editions');
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
}
