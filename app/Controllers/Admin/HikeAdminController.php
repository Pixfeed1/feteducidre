<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Cache;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des éditions de randonnée.
 * Gère les parcours et résultats de la randonnée associée à la Fête du Cidre.
 */
class HikeAdminController extends Controller
{
    /**
     * Liste toutes les éditions de randonnée
     */
    public function index(Request $request, array $params = []): void
    {
        $hikes = $this->db()->fetchAll(
            "SELECT * FROM hike_editions ORDER BY year DESC"
        );

        $this->renderAdmin('templates/admin/hikes/index.php', [
            'title' => 'Randonnées',
            'hikes' => $hikes,
        ]);
    }

    /**
     * Affiche le formulaire de création d'une édition de randonnée
     */
    public function create(Request $request, array $params = []): void
    {
        $editions = $this->db()->fetchAll(
            "SELECT id, year, title FROM editions ORDER BY year DESC"
        );

        $this->renderAdmin('templates/admin/hikes/form.php', [
            'title'    => 'Nouvelle randonnée',
            'hike'     => null,
            'editions' => $editions,
        ]);
    }

    /**
     * Enregistre une nouvelle édition de randonnée
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['year'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'L\'année est obligatoire.');
            $this->redirect('/admin/hikes/create');
            return;
        }

        $this->db()->insert('hike_editions', [
            'year'           => (int) $data['year'],
            'title'          => $data['title'] ?? 'Randonnée ' . $data['year'],
            'description'    => sanitize($data['description'] ?? ''),
            'date'           => !empty($data['date']) ? $data['date'] : null,
            'distance_km'    => !empty($data['distance_km']) ? (float) $data['distance_km'] : null,
            'elevation_gain' => !empty($data['elevation_gain']) ? (int) $data['elevation_gain'] : null,
            'participant_count' => !empty($data['participant_count']) ? (int) $data['participant_count'] : null,
            'gpx_file'          => $data['gpx_file'] ?? '',
            'is_active'         => isset($data['is_active']) ? 1 : 0,
        ]);

        $this->invalidateCache();

        set_flash('success', 'Randonnée créée avec succès.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Affiche le formulaire de modification d'une édition de randonnée
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $hike = $this->db()->fetch("SELECT * FROM hike_editions WHERE id = ?", [$id]);

        if (!$hike) {
            set_flash('error', 'Randonnée introuvable.');
            $this->redirect('/admin/hikes');
            return;
        }

        $editions = $this->db()->fetchAll(
            "SELECT id, year, title FROM editions ORDER BY year DESC"
        );

        // Récupérer les résultats / classement de cette randonnée
        $results = $this->db()->fetchAll(
            "SELECT * FROM hike_results WHERE hike_edition_id = ? ORDER BY `rank` ASC",
            [$id]
        );

        $this->renderAdmin('templates/admin/hikes/form.php', [
            'title'    => 'Modifier : ' . $hike['title'],
            'hike'     => $hike,
            'editions' => $editions,
            'results'  => $results,
        ]);
    }

    /**
     * Met à jour une édition de randonnée existante
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['year'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'L\'année est obligatoire.');
            $this->redirect('/admin/hikes/' . $id . '/edit');
            return;
        }

        $this->db()->update('hike_editions', [
            'year'           => (int) $data['year'],
            'title'          => $data['title'] ?? 'Randonnée ' . $data['year'],
            'description'    => sanitize($data['description'] ?? ''),
            'date'           => !empty($data['date']) ? $data['date'] : null,
            'distance_km'    => !empty($data['distance_km']) ? (float) $data['distance_km'] : null,
            'elevation_gain' => !empty($data['elevation_gain']) ? (int) $data['elevation_gain'] : null,
            'participant_count' => !empty($data['participant_count']) ? (int) $data['participant_count'] : null,
            'gpx_file'          => $data['gpx_file'] ?? '',
            'is_active'         => isset($data['is_active']) ? 1 : 0,
        ], 'id = ?', [$id]);

        $this->invalidateCache();

        set_flash('success', 'Randonnée mise à jour avec succès.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Supprime une édition de randonnée
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $this->db()->delete('hike_editions', 'id = ?', [$id]);

        $this->invalidateCache();

        set_flash('success', 'Randonnée supprimée.');
        $this->redirect('/admin/hikes');
    }

    /**
     * Invalide le cache lié aux randonnées
     */
    private function invalidateCache(): void
    {
        Cache::getInstance()->flush('pages');
        Cache::getInstance()->flush('fragments');
    }
}
