<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des résultats de concours.
 * Gère le palmarès des concours de cidre de chaque édition.
 */
class ContestAdminController extends Controller
{
    /**
     * Liste tous les résultats de concours
     */
    public function index(Request $request, array $params = []): void
    {
        $year = $request->get('year');

        $sql = "SELECT * FROM contest_results";
        $sqlParams = [];

        if ($year) {
            $sql .= " WHERE year = ?";
            $sqlParams[] = (int) $year;
        }

        $sql .= " ORDER BY year DESC, category ASC, `rank` ASC";

        $results = $this->db()->fetchAll($sql, $sqlParams);

        // Récupérer les années disponibles pour le filtre
        $years = $this->db()->fetchAll(
            "SELECT DISTINCT year FROM contest_results ORDER BY year DESC"
        );

        $this->renderAdmin('templates/admin/contests/index.php', [
            'title'       => 'Concours',
            'results'     => $results,
            'years'       => array_column($years, 'year'),
            'currentYear' => $year,
        ]);
    }

    /**
     * Affiche le formulaire de création d'un résultat
     */
    public function create(Request $request, array $params = []): void
    {
        $editions = $this->db()->fetchAll("SELECT id, year FROM editions ORDER BY year DESC");

        $this->renderAdmin('templates/admin/contests/form.php', [
            'title'    => 'Nouveau résultat',
            'result'   => null,
            'editions' => $editions,
        ]);
    }

    /**
     * Enregistre un nouveau résultat de concours
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['year']) || empty($data['category']) || empty($data['producer_name'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'L\'année, la catégorie et le nom du producteur sont obligatoires.');
            $this->redirect('/admin/contests/create');
            return;
        }

        $this->db()->insert('contest_results', [
            'year'          => (int) $data['year'],
            'category'      => $data['category'],
            'rank'          => (int) ($data['rank'] ?? 1),
            'producer_name' => $data['producer_name'],
            'producer_city' => $data['producer_city'] ?? null,
            'product_name'  => $data['product_name'] ?? null,
            'score'         => !empty($data['score']) ? (float) $data['score'] : null,
            'medal'         => $data['medal'] ?? null,
            'notes'         => $data['notes'] ?? null,
            'edition_id'    => !empty($data['edition_id']) ? (int) $data['edition_id'] : null,
        ]);

        set_flash('success', 'Résultat ajouté avec succès.');
        $this->redirect('/admin/contests');
    }

    /**
     * Affiche le formulaire de modification d'un résultat
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $result = $this->db()->fetch("SELECT * FROM contest_results WHERE id = ?", [$id]);

        if (!$result) {
            set_flash('error', 'Résultat introuvable.');
            $this->redirect('/admin/contests');
            return;
        }

        $editions = $this->db()->fetchAll("SELECT id, year FROM editions ORDER BY year DESC");

        $this->renderAdmin('templates/admin/contests/form.php', [
            'title'    => 'Modifier le résultat',
            'result'   => $result,
            'editions' => $editions,
        ]);
    }

    /**
     * Met à jour un résultat de concours
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['year']) || empty($data['category']) || empty($data['producer_name'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'L\'année, la catégorie et le nom du producteur sont obligatoires.');
            $this->redirect('/admin/contests/' . $id . '/edit');
            return;
        }

        $this->db()->update('contest_results', [
            'year'          => (int) $data['year'],
            'category'      => $data['category'],
            'rank'          => (int) ($data['rank'] ?? 1),
            'producer_name' => $data['producer_name'],
            'producer_city' => $data['producer_city'] ?? null,
            'product_name'  => $data['product_name'] ?? null,
            'score'         => !empty($data['score']) ? (float) $data['score'] : null,
            'medal'         => $data['medal'] ?? null,
            'notes'         => $data['notes'] ?? null,
            'edition_id'    => !empty($data['edition_id']) ? (int) $data['edition_id'] : null,
        ], 'id = ?', [$id]);

        set_flash('success', 'Résultat mis à jour avec succès.');
        $this->redirect('/admin/contests');
    }

    /**
     * Supprime un résultat de concours
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $this->db()->delete('contest_results', 'id = ?', [$id]);

        set_flash('success', 'Résultat supprimé.');
        $this->redirect('/admin/contests');
    }
}
