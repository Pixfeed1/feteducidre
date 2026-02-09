<?php
/**
 * Formulaire de création/modification d'une édition.
 * Variables : $edition (null si création)
 */

$isEdit = $edition !== null;
$action = $isEdit ? '/admin/editions/' . (int) $edition['id'] . '/update' : '/admin/editions/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier l\'édition' : icon('plus', 24) . ' Nouvelle édition' ?></h1>
    <a href="/admin/editions" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="year">Année *</label>
                    <input type="number" id="year" name="year" class="form-control"
                           value="<?= e($isEdit ? (string) $edition['year'] : old('year')) ?>"
                           min="1989" max="<?= date('Y') + 2 ?>" required>
                </div>
                <div class="form-group">
                    <label for="title">Titre</label>
                    <input type="text" id="title" name="title" class="form-control"
                           value="<?= e($isEdit ? ($edition['title'] ?? '') : old('title')) ?>"
                           placeholder="Ex : Édition 2025">
                </div>
            </div>

            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" class="form-control" rows="8"><?= e($isEdit ? ($edition['description'] ?? '') : old('description')) ?></textarea>
            </div>

            <div class="form-group">
                <label for="highlights">Temps forts (JSON)</label>
                <textarea id="highlights" name="highlights" class="form-control" rows="4"
                          placeholder='["Concours de cidre", "Randonnée", "Marché artisanal"]'><?= e($isEdit ? ($edition['highlights'] ?? '') : old('highlights')) ?></textarea>
                <div class="form-hint">Format JSON. Tableau de chaînes de caractères.</div>
            </div>

            <div class="form-group">
                <label for="stats">Statistiques (JSON)</label>
                <textarea id="stats" name="stats" class="form-control" rows="4"
                          placeholder='{"visiteurs": 5000, "exposants": 40}'><?= e($isEdit ? ($edition['stats'] ?? '') : old('stats')) ?></textarea>
                <div class="form-hint">Format JSON. Objet clé/valeur.</div>
            </div>

            <div class="form-group">
                <div class="form-check">
                    <input type="checkbox" id="is_active" name="is_active" value="1"
                           <?= ($isEdit ? $edition['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                    <label for="is_active">Édition active (visible sur le site)</label>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/admin/editions" class="btn btn-secondary">Annuler</a>
            <button type="submit" class="btn btn-primary">
                <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer l\'édition' ?>
            </button>
        </div>
    </div>
</form>
