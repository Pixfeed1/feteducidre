<?php
/**
 * Formulaire de création/modification d'une randonnée avec résultats.
 * Variables : $hike (null si création), $results
 */

$isEdit = $hike !== null;
$action = $isEdit ? '/admin/hikes/' . (int) $hike['id'] . '/update' : '/admin/hikes/store';
$results = $results ?? [];
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier la randonnée' : icon('plus', 24) . ' Nouvelle randonnée' ?></h1>
    <a href="/admin/hikes" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-header">
            <h2>Informations générales</h2>
        </div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="year">Année *</label>
                    <input type="number" id="year" name="year" class="form-control"
                           value="<?= e($isEdit ? (string) $hike['year'] : old('year')) ?>"
                           min="1989" max="<?= date('Y') + 2 ?>" required>
                </div>
                <div class="form-group">
                    <label for="title">Titre</label>
                    <input type="text" id="title" name="title" class="form-control"
                           value="<?= e($isEdit ? ($hike['title'] ?? '') : old('title')) ?>"
                           placeholder="Ex : Randonnée 2025">
                </div>
                <div class="form-group">
                    <label for="date">Date</label>
                    <input type="date" id="date" name="date" class="form-control"
                           value="<?= e($isEdit ? ($hike['date'] ?? '') : old('date')) ?>">
                </div>
            </div>

            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" class="form-control" rows="5"><?= e($isEdit ? ($hike['description'] ?? '') : old('description')) ?></textarea>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="distance_km">Distance (km)</label>
                    <input type="number" id="distance_km" name="distance_km" class="form-control"
                           value="<?= e($isEdit ? (string) ($hike['distance_km'] ?? '') : old('distance_km')) ?>"
                           step="0.1" min="0">
                </div>
                <div class="form-group">
                    <label for="elevation_gain">Dénivelé positif (m)</label>
                    <input type="number" id="elevation_gain" name="elevation_gain" class="form-control"
                           value="<?= e($isEdit ? (string) ($hike['elevation_gain'] ?? '') : old('elevation_gain')) ?>"
                           min="0">
                </div>
                <div class="form-group">
                    <label for="participant_count">Nombre de participants</label>
                    <input type="number" id="participant_count" name="participant_count" class="form-control"
                           value="<?= e($isEdit ? (string) ($hike['participant_count'] ?? '') : old('participant_count')) ?>"
                           min="0">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="gpx_file">Fichier GPX (nom du fichier)</label>
                    <input type="text" id="gpx_file" name="gpx_file" class="form-control"
                           value="<?= e($isEdit ? ($hike['gpx_file'] ?? '') : old('gpx_file')) ?>"
                           placeholder="parcours-2025.gpx">
                </div>
                <div class="form-group">
                    <div class="form-check" style="margin-top: 1.75rem;">
                        <input type="checkbox" id="is_active" name="is_active" value="1"
                               <?= ($isEdit ? $hike['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                        <label for="is_active">Active (visible sur le site)</label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <?php if ($isEdit): ?>
        <!-- Résultats / Classement -->
        <div class="card">
            <div class="card-header">
                <h2><?= icon('trophy', 20) ?> Classement</h2>
            </div>
            <?php if (!empty($results)): ?>
                <div class="table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th style="width:60px;">Rang</th>
                                <th>Participant</th>
                                <th>Catégorie</th>
                                <th>Temps (sec.)</th>
                                <th>Dossard</th>
                                <th style="width:50px;"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($results as $i => $r): ?>
                                <tr>
                                    <td>
                                        <input type="hidden" name="result_id[]" value="<?= (int) $r['id'] ?>">
                                        <input type="number" name="result_rank[]" class="form-control" value="<?= (int) $r['rank'] ?>" min="1" style="width:60px;">
                                    </td>
                                    <td><input type="text" name="result_name[]" class="form-control" value="<?= e($r['participant_name']) ?>"></td>
                                    <td><input type="text" name="result_category[]" class="form-control" value="<?= e($r['category'] ?? '') ?>"></td>
                                    <td><input type="number" name="result_time[]" class="form-control" value="<?= (int) ($r['time_seconds'] ?? 0) ?>" min="0"></td>
                                    <td><input type="number" name="result_bib[]" class="form-control" value="<?= (int) ($r['bib_number'] ?? 0) ?>" min="0"></td>
                                    <td class="text-muted"><?= $r['time_seconds'] ? format_duration((int) $r['time_seconds']) : '-' ?></td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>

            <div class="card-body">
                <p class="text-muted">Ajouter un nouveau résultat :</p>
                <div class="form-row">
                    <div class="form-group">
                        <input type="hidden" name="result_id[]" value="">
                        <label>Rang</label>
                        <input type="number" name="result_rank[]" class="form-control" placeholder="1" min="1">
                    </div>
                    <div class="form-group">
                        <label>Participant</label>
                        <input type="text" name="result_name[]" class="form-control" placeholder="Nom du participant">
                    </div>
                    <div class="form-group">
                        <label>Catégorie</label>
                        <input type="text" name="result_category[]" class="form-control" placeholder="Senior, Vétéran...">
                    </div>
                    <div class="form-group">
                        <label>Temps (sec.)</label>
                        <input type="number" name="result_time[]" class="form-control" placeholder="3600" min="0">
                    </div>
                    <div class="form-group">
                        <label>Dossard</label>
                        <input type="number" name="result_bib[]" class="form-control" placeholder="42" min="0">
                    </div>
                </div>
            </div>
        </div>
    <?php endif; ?>

    <div style="display:flex; align-items:center; justify-content:flex-end; gap:0.5rem; margin-top:1rem;">
        <a href="/admin/hikes" class="btn btn-secondary">Annuler</a>
        <button type="submit" class="btn btn-primary">
            <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer la randonnée' ?>
        </button>
    </div>
</form>
