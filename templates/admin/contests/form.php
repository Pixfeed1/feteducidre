<?php
/**
 * Formulaire de création/modification d'un résultat de concours.
 * Variables : $result (null si création), $editions
 */

$isEdit = $result !== null;
$action = $isEdit ? '/admin/contests/' . (int) $result['id'] . '/update' : '/admin/contests/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier le résultat' : icon('plus', 24) . ' Nouveau résultat' ?></h1>
    <a href="/admin/contests" class="btn btn-secondary">
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
                           value="<?= e($isEdit ? (string) $result['year'] : old('year')) ?>"
                           min="1989" max="<?= date('Y') + 1 ?>" required>
                </div>
                <div class="form-group">
                    <label for="edition_id">Édition liée</label>
                    <select id="edition_id" name="edition_id" class="form-control">
                        <option value="">-- Aucune --</option>
                        <?php foreach ($editions as $ed): ?>
                            <option value="<?= (int) $ed['id'] ?>"
                                    <?= ($isEdit ? ($result['edition_id'] ?? '') : old('edition_id')) == $ed['id'] ? 'selected' : '' ?>>
                                <?= (int) $ed['year'] ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="form-group">
                    <label for="category">Catégorie *</label>
                    <input type="text" id="category" name="category" class="form-control"
                           value="<?= e($isEdit ? $result['category'] : old('category')) ?>"
                           placeholder="Ex : Cidre Brut, Cidre Doux, Jus de Pomme"
                           required>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="rank">Classement *</label>
                    <input type="number" id="rank" name="rank" class="form-control"
                           value="<?= e($isEdit ? (string) $result['rank'] : old('rank', '1')) ?>"
                           min="1" required>
                </div>
                <div class="form-group">
                    <label for="medal">Médaille</label>
                    <select id="medal" name="medal" class="form-control">
                        <option value="">-- Aucune --</option>
                        <?php
                        $medals = ['or' => 'Or', 'argent' => 'Argent', 'bronze' => 'Bronze', 'mention' => 'Mention'];
                        $currentMedal = $isEdit ? ($result['medal'] ?? '') : old('medal');
                        foreach ($medals as $val => $label):
                        ?>
                            <option value="<?= $val ?>" <?= $currentMedal === $val ? 'selected' : '' ?>><?= e($label) ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="form-group">
                    <label for="score">Note (/20)</label>
                    <input type="number" id="score" name="score" class="form-control"
                           value="<?= e($isEdit ? (string) ($result['score'] ?? '') : old('score')) ?>"
                           step="0.1" min="0" max="20">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="producer_name">Nom du producteur *</label>
                    <input type="text" id="producer_name" name="producer_name" class="form-control"
                           value="<?= e($isEdit ? $result['producer_name'] : old('producer_name')) ?>"
                           required>
                </div>
                <div class="form-group">
                    <label for="producer_city">Ville du producteur</label>
                    <input type="text" id="producer_city" name="producer_city" class="form-control"
                           value="<?= e($isEdit ? ($result['producer_city'] ?? '') : old('producer_city')) ?>">
                </div>
            </div>

            <div class="form-group">
                <label for="product_name">Nom du produit</label>
                <input type="text" id="product_name" name="product_name" class="form-control"
                       value="<?= e($isEdit ? ($result['product_name'] ?? '') : old('product_name')) ?>">
            </div>

            <div class="form-group">
                <label for="notes">Notes / Commentaires</label>
                <textarea id="notes" name="notes" class="form-control" rows="3"><?= e($isEdit ? ($result['notes'] ?? '') : old('notes')) ?></textarea>
            </div>
        </div>
        <div class="card-footer">
            <a href="/admin/contests" class="btn btn-secondary">Annuler</a>
            <button type="submit" class="btn btn-primary">
                <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Ajouter le résultat' ?>
            </button>
        </div>
    </div>
</form>
