<?php
/**
 * Formulaire de création/modification d'une édition.
 * Variables : $edition (null si création)
 */

$isEdit = $edition !== null;
$action = $isEdit ? '/admin/editions/' . (int) $edition['id'] . '/update' : '/admin/editions/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier l\'édition ' . (int) $edition['year'] : icon('plus', 24) . ' Nouvelle édition' ?></h1>
    <a href="/admin/editions" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>" enctype="multipart/form-data">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-header">
            <h2>Informations de base</h2>
        </div>
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
                <textarea id="description" name="description" class="form-control" rows="4"><?= e($isEdit ? ($edition['description'] ?? '') : old('description')) ?></textarea>
            </div>

            <div class="form-group">
                <label for="notes">Notes (optionnel)</label>
                <textarea id="notes" name="notes" class="form-control" rows="2" placeholder="Remarques sur cette édition…"><?= e($isEdit ? ($edition['notes'] ?? '') : old('notes')) ?></textarea>
            </div>

            <div class="form-group">
                <div class="form-check">
                    <input type="checkbox" id="is_active" name="is_active" value="1"
                           <?= ($isEdit ? $edition['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                    <label for="is_active">Édition active (visible sur le site)</label>
                </div>
            </div>
        </div>
    </div>

    <!-- Fichiers -->
    <div class="card">
        <div class="card-header">
            <h2><?= icon('upload', 18) ?> Fichiers de l'édition</h2>
        </div>
        <div class="card-body">
            <!-- Affiche -->
            <div class="form-group">
                <label for="poster"><?= icon('image', 16) ?> Affiche (image)</label>
                <?php if ($isEdit && !empty($edition['poster_filename'])): ?>
                    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;padding:0.5rem 0.8rem;background:var(--creme);border-radius:8px">
                        <span class="td-badge has"><?= icon('check', 8) ?> <?= e($edition['poster_original'] ?? $edition['poster_filename']) ?></span>
                        <label style="font-size:0.78rem;cursor:pointer;color:var(--rouge)">
                            <input type="checkbox" name="remove_poster" value="1" style="margin-right:0.3rem"> Supprimer
                        </label>
                    </div>
                <?php endif; ?>
                <input type="file" id="poster" name="poster" class="form-control" accept="image/jpeg,image/png,image/webp">
                <div class="form-hint">JPG, PNG, WebP — Max 5 Mo</div>
            </div>

            <!-- Programme -->
            <div class="form-group">
                <label for="programme"><?= icon('clipboard-list', 16) ?> Programme (PDF)</label>
                <?php if ($isEdit && !empty($edition['programme_filename'])): ?>
                    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;padding:0.5rem 0.8rem;background:var(--creme);border-radius:8px">
                        <span class="td-badge has"><?= icon('check', 8) ?> <?= e($edition['programme_original'] ?? $edition['programme_filename']) ?></span>
                        <label style="font-size:0.78rem;cursor:pointer;color:var(--rouge)">
                            <input type="checkbox" name="remove_programme" value="1" style="margin-right:0.3rem"> Supprimer
                        </label>
                    </div>
                <?php endif; ?>
                <input type="file" id="programme" name="programme" class="form-control" accept="application/pdf">
                <div class="form-hint">PDF uniquement — Max 10 Mo</div>
            </div>

            <!-- Palmarès -->
            <div class="form-group">
                <label for="palmares"><?= icon('award', 16) ?> Palmarès concours (PDF)</label>
                <?php if ($isEdit && !empty($edition['palmares_filename'])): ?>
                    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;padding:0.5rem 0.8rem;background:var(--creme);border-radius:8px">
                        <span class="td-badge has"><?= icon('check', 8) ?> <?= e($edition['palmares_original'] ?? $edition['palmares_filename']) ?></span>
                        <label style="font-size:0.78rem;cursor:pointer;color:var(--rouge)">
                            <input type="checkbox" name="remove_palmares" value="1" style="margin-right:0.3rem"> Supprimer
                        </label>
                    </div>
                <?php endif; ?>
                <input type="file" id="palmares" name="palmares" class="form-control" accept="application/pdf">
                <div class="form-hint">PDF uniquement — Max 10 Mo</div>
            </div>
        </div>
    </div>

    <!-- Avancé -->
    <div class="card">
        <div class="card-header">
            <h2>Données avancées</h2>
        </div>
        <div class="card-body">
            <div class="form-group">
                <label for="highlights">Temps forts (JSON)</label>
                <textarea id="highlights" name="highlights" class="form-control" rows="3"
                          placeholder='["Concours de cidre", "Randonnée", "Marché artisanal"]'><?= e($isEdit ? ($edition['highlights'] ?? '') : old('highlights')) ?></textarea>
                <div class="form-hint">Format JSON. Tableau de chaînes de caractères.</div>
            </div>

            <div class="form-group">
                <label for="stats">Statistiques (JSON)</label>
                <textarea id="stats" name="stats" class="form-control" rows="3"
                          placeholder='{"visiteurs": 5000, "exposants": 40}'><?= e($isEdit ? ($edition['stats'] ?? '') : old('stats')) ?></textarea>
                <div class="form-hint">Format JSON. Objet clé/valeur.</div>
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
