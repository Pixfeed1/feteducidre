<?php
/**
 * Liste des produits — administration.
 * Variables : $products
 */
?>

<div class="page-header">
    <h1><?= icon('package', 24) ?> Produits</h1>
    <a href="/admin/products/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouveau produit
    </a>
</div>

<div class="card">
    <?php if (empty($products)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('package', 40) ?>
                <p>Aucun produit pour le moment.</p>
                <a href="/admin/products/create" class="btn btn-primary mt-2">Ajouter un produit</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>SKU</th>
                        <th>Prix</th>
                        <th>Stock</th>
                        <th>Catégorie</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($products as $product): ?>
                        <tr>
                            <td>
                                <strong><?= e($product['name']) ?></strong>
                                <?php if ($product['is_featured']): ?>
                                    <span class="badge badge-warning" title="Produit vedette"><?= icon('star', 12) ?></span>
                                <?php endif; ?>
                            </td>
                            <td class="text-muted"><?= e($product['sku'] ?? '-') ?></td>
                            <td>
                                <?= number_format((float) $product['price'], 2, ',', ' ') ?> &euro;
                                <?php if (!empty($product['sale_price'])): ?>
                                    <br><small class="text-danger"><?= number_format((float) $product['sale_price'], 2, ',', ' ') ?> &euro;</small>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?php if ((int) $product['stock'] <= 0): ?>
                                    <span class="badge badge-danger">Épuisé</span>
                                <?php elseif ((int) $product['stock'] <= 5): ?>
                                    <span class="badge badge-warning"><?= (int) $product['stock'] ?></span>
                                <?php else: ?>
                                    <?= (int) $product['stock'] ?>
                                <?php endif; ?>
                            </td>
                            <td><?= e($product['category'] ?? '-') ?></td>
                            <td>
                                <?php if ($product['is_active']): ?>
                                    <span class="badge badge-success">Actif</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary">Inactif</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/products/<?= (int) $product['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/products/<?= (int) $product['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer ce produit ?')">
                                        <?= csrf_field() ?>
                                        <button type="submit" class="btn btn-sm btn-danger" title="Supprimer">
                                            <?= icon('trash-2', 16) ?>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
