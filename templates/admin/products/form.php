<?php
/**
 * Formulaire de création/modification d'un produit.
 * Variables : $product (null si création)
 */

$isEdit = $product !== null;
$action = $isEdit ? '/admin/products/' . (int) $product['id'] . '/update' : '/admin/products/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier le produit' : icon('plus', 24) . ' Nouveau produit' ?></h1>
    <a href="/admin/products" class="btn btn-secondary">
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
                    <label for="name">Nom du produit *</label>
                    <input type="text" id="name" name="name" class="form-control"
                           value="<?= e($isEdit ? $product['name'] : old('name')) ?>"
                           required>
                </div>
                <div class="form-group">
                    <label for="slug">Slug (URL)</label>
                    <input type="text" id="slug" name="slug" class="form-control"
                           value="<?= e($isEdit ? $product['slug'] : old('slug')) ?>"
                           placeholder="Généré automatiquement">
                </div>
            </div>

            <div class="form-group">
                <label for="description">Description complète</label>
                <textarea id="description" name="description" class="form-control" rows="8"><?= e($isEdit ? ($product['description'] ?? '') : old('description')) ?></textarea>
            </div>

            <div class="form-group">
                <label for="short_description">Description courte</label>
                <input type="text" id="short_description" name="short_description" class="form-control"
                       value="<?= e($isEdit ? ($product['short_description'] ?? '') : old('short_description')) ?>"
                       maxlength="500">
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h2>Prix et stock</h2>
        </div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="price">Prix (&euro;) *</label>
                    <input type="number" id="price" name="price" class="form-control"
                           value="<?= e($isEdit ? (string) $product['price'] : old('price')) ?>"
                           step="0.01" min="0" required>
                </div>
                <div class="form-group">
                    <label for="sale_price">Prix promotionnel (&euro;)</label>
                    <input type="number" id="sale_price" name="sale_price" class="form-control"
                           value="<?= e($isEdit ? (string) ($product['sale_price'] ?? '') : old('sale_price')) ?>"
                           step="0.01" min="0">
                </div>
                <div class="form-group">
                    <label for="sku">Référence (SKU)</label>
                    <input type="text" id="sku" name="sku" class="form-control"
                           value="<?= e($isEdit ? ($product['sku'] ?? '') : old('sku')) ?>">
                </div>
                <div class="form-group">
                    <label for="stock">Stock</label>
                    <input type="number" id="stock" name="stock" class="form-control"
                           value="<?= e($isEdit ? (string) $product['stock'] : old('stock', '0')) ?>"
                           min="0">
                </div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h2>Détails du produit</h2>
        </div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="weight">Poids (kg)</label>
                    <input type="number" id="weight" name="weight" class="form-control"
                           value="<?= e($isEdit ? (string) ($product['weight'] ?? '') : old('weight')) ?>"
                           step="0.01" min="0">
                </div>
                <div class="form-group">
                    <label for="volume">Volume</label>
                    <input type="text" id="volume" name="volume" class="form-control"
                           value="<?= e($isEdit ? ($product['volume'] ?? '') : old('volume')) ?>"
                           placeholder="Ex : 75cl, 1L">
                </div>
                <div class="form-group">
                    <label for="alcohol_percentage">Taux d'alcool (%)</label>
                    <input type="number" id="alcohol_percentage" name="alcohol_percentage" class="form-control"
                           value="<?= e($isEdit ? (string) ($product['alcohol_percentage'] ?? '') : old('alcohol_percentage')) ?>"
                           step="0.1" min="0">
                </div>
                <div class="form-group">
                    <label for="category">Catégorie</label>
                    <select id="category" name="category" class="form-control">
                        <option value="">-- Sélectionner --</option>
                        <?php
                        $categories = ['cidre' => 'Cidre', 'jus' => 'Jus', 'spiritueux' => 'Spiritueux', 'coffret' => 'Coffret', 'autre' => 'Autre'];
                        $currentCat = $isEdit ? ($product['category'] ?? '') : old('category');
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
                           value="<?= e($isEdit ? (string) $product['sort_order'] : old('sort_order', '0')) ?>" min="0">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <div class="form-check">
                        <input type="checkbox" id="is_featured" name="is_featured" value="1"
                               <?= ($isEdit ? $product['is_featured'] : old('is_featured')) ? 'checked' : '' ?>>
                        <label for="is_featured">Produit vedette</label>
                    </div>
                </div>
                <div class="form-group">
                    <div class="form-check">
                        <input type="checkbox" id="is_active" name="is_active" value="1"
                               <?= ($isEdit ? $product['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                        <label for="is_active">Produit actif (visible en boutique)</label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div style="display:flex; align-items:center; justify-content:flex-end; gap:0.5rem; margin-top:1rem;">
        <a href="/admin/products" class="btn btn-secondary">Annuler</a>
        <button type="submit" class="btn btn-primary">
            <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer le produit' ?>
        </button>
    </div>
</form>
