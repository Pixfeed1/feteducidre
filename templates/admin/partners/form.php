<?php
/**
 * Formulaire de création/modification d'un partenaire.
 * Variables : $partner (null si création)
 */

$isEdit = $partner !== null;
$action = $isEdit ? '/admin/partners/' . (int) $partner['id'] . '/update' : '/admin/partners/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier le partenaire' : icon('plus', 24) . ' Nouveau partenaire' ?></h1>
    <a href="/admin/partners" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="name">Nom *</label>
                    <input type="text" id="name" name="name" class="form-control"
                           value="<?= e($isEdit ? $partner['name'] : old('name')) ?>"
                           required>
                </div>
                <div class="form-group">
                    <label for="slug">Slug</label>
                    <input type="text" id="slug" name="slug" class="form-control"
                           value="<?= e($isEdit ? $partner['slug'] : old('slug')) ?>"
                           placeholder="Généré automatiquement">
                </div>
            </div>

            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" class="form-control" rows="4"><?= e($isEdit ? ($partner['description'] ?? '') : old('description')) ?></textarea>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="website">Site web</label>
                    <input type="url" id="website" name="website" class="form-control"
                           value="<?= e($isEdit ? ($partner['website'] ?? '') : old('website')) ?>"
                           placeholder="https://exemple.fr">
                </div>
                <div class="form-group">
                    <label for="category">Catégorie</label>
                    <select id="category" name="category" class="form-control">
                        <?php
                        $categories = ['institutionnel' => 'Institutionnel', 'entreprise' => 'Entreprise', 'media' => 'Média', 'associatif' => 'Associatif', 'autre' => 'Autre'];
                        $currentCat = $isEdit ? $partner['category'] : old('category', 'autre');
                        foreach ($categories as $val => $label):
                        ?>
                            <option value="<?= $val ?>" <?= $currentCat === $val ? 'selected' : '' ?>><?= e($label) ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="sort_order">Ordre d'affichage</label>
                    <input type="number" id="sort_order" name="sort_order" class="form-control"
                           value="<?= e($isEdit ? (string) $partner['sort_order'] : old('sort_order', '0')) ?>" min="0">
                </div>
                <div class="form-group">
                    <div class="form-check" style="margin-top: 1.75rem;">
                        <input type="checkbox" id="is_active" name="is_active" value="1"
                               <?= ($isEdit ? $partner['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                        <label for="is_active">Partenaire actif (visible sur le site)</label>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/admin/partners" class="btn btn-secondary">Annuler</a>
            <button type="submit" class="btn btn-primary">
                <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer le partenaire' ?>
            </button>
        </div>
    </div>
</form>
