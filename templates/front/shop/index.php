<?php
/**
 * Template liste des produits de la boutique.
 * Variables : $products, $grouped, $categories, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('shopping-bag', 32) ?> Boutique</h1>
        <p>Cidres artisanaux, jus de pomme et produits du terroir</p>
    </div>
</section>

<!-- Filtres par catégorie -->
<?php if (!empty($categories)): ?>
<section class="section" style="padding-bottom:0">
    <div class="container">
        <div class="filter-bar">
            <button class="btn btn-primary btn-sm filter-btn active" data-filter="all">
                <?= icon('filter', 16) ?> Tout afficher
            </button>
            <?php foreach ($categories as $cat): ?>
                <button class="btn btn-outline btn-sm filter-btn" data-filter="<?= e(slugify($cat)) ?>">
                    <?= e(ucfirst($cat)) ?>
                </button>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- Grille des produits -->
<section class="section section-products">
    <div class="container">
        <?php if (empty($products)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('shopping-bag', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucun produit disponible</h2>
                <p>La boutique est en cours de préparation. Revenez bientôt !</p>
            </div>
        <?php else: ?>
            <?php foreach ($grouped as $category => $categoryProducts): ?>
                <div class="product-group" data-category="<?= e(slugify($category)) ?>">
                    <h2 class="product-group-title" style="margin-bottom:1.5rem">
                        <?= e(ucfirst($category)) ?>
                    </h2>
                    <div class="grid grid-3" style="margin-bottom:3rem">
                        <?php foreach ($categoryProducts as $product): ?>
                            <div class="card product-card">
                                <div class="product-image" style="background:var(--creme-fonce);height:200px;display:flex;align-items:center;justify-content:center">
                                    <?= icon('wine', 48, '', 'var(--vert-clair)') ?>
                                </div>
                                <div class="card-body">
                                    <?php if ($product['category']): ?>
                                        <span class="product-category"><?= e(ucfirst($product['category'])) ?></span>
                                    <?php endif; ?>
                                    <h3 class="product-name"><?= e($product['name']) ?></h3>
                                    <p class="product-desc"><?= e(truncate($product['short_description'] ?? '', 100)) ?></p>
                                    <div class="product-footer">
                                        <?php if ($product['sale_price']): ?>
                                            <span class="product-price product-price--sale"><?= number_format((float) $product['sale_price'], 2, ',', ' ') ?> &euro;</span>
                                            <span class="product-price product-price--original" style="text-decoration:line-through;color:var(--brun);font-size:.85rem;margin-left:.5rem"><?= number_format((float) $product['price'], 2, ',', ' ') ?> &euro;</span>
                                        <?php else: ?>
                                            <span class="product-price"><?= number_format((float) $product['price'], 2, ',', ' ') ?> &euro;</span>
                                        <?php endif; ?>
                                        <?php if ($product['volume']): ?>
                                            <span class="product-volume"><?= e($product['volume']) ?></span>
                                        <?php endif; ?>
                                    </div>
                                    <a href="/boutique/<?= e($product['slug']) ?>" class="btn btn-primary btn-sm" style="margin-top:.75rem;width:100%;justify-content:center">
                                        <?= icon('eye', 16) ?> Voir le produit
                                    </a>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</section>
