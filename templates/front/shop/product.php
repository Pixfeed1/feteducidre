<?php
/**
 * Template fiche produit.
 * Variables : $product, $image, $seo
 */
?>

<!-- Fil d'Ariane -->
<section class="breadcrumb-section">
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/boutique">Boutique</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page"><?= e($product['name']) ?></span>
        </nav>
    </div>
</section>

<!-- Détails du produit -->
<section class="section section-product-detail">
    <div class="container">
        <div class="product-detail" style="display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:start">

            <!-- Image du produit -->
            <div class="product-detail-image">
                <?php if ($image): ?>
                    <?= img($image, $product['name'], 'product-img') ?>
                <?php else: ?>
                    <div class="product-image-placeholder" style="background:var(--creme-fonce);height:400px;border-radius:14px;display:flex;align-items:center;justify-content:center">
                        <?= icon('wine', 64, '', 'var(--vert-clair)') ?>
                    </div>
                <?php endif; ?>
            </div>

            <!-- Informations produit -->
            <div class="product-detail-info">
                <?php if ($product['category']): ?>
                    <span class="product-category" style="display:inline-block;margin-bottom:.5rem"><?= e(ucfirst($product['category'])) ?></span>
                <?php endif; ?>

                <h1 style="margin-bottom:1rem"><?= e($product['name']) ?></h1>

                <!-- Prix -->
                <div class="product-detail-price" style="margin-bottom:1.5rem">
                    <?php if ($product['sale_price']): ?>
                        <span class="product-price" style="font-size:1.75rem;font-weight:700;color:var(--orange-cidre)"><?= number_format((float) $product['sale_price'], 2, ',', ' ') ?> &euro;</span>
                        <span style="text-decoration:line-through;color:var(--brun);font-size:1.1rem;margin-left:.75rem"><?= number_format((float) $product['price'], 2, ',', ' ') ?> &euro;</span>
                    <?php else: ?>
                        <span class="product-price" style="font-size:1.75rem;font-weight:700;color:var(--orange-cidre)"><?= number_format((float) $product['price'], 2, ',', ' ') ?> &euro;</span>
                    <?php endif; ?>
                </div>

                <!-- Caractéristiques -->
                <div class="product-detail-specs" style="display:flex;gap:1.5rem;margin-bottom:1.5rem;flex-wrap:wrap">
                    <?php if ($product['volume']): ?>
                        <div class="spec-item" style="display:flex;align-items:center;gap:.4rem">
                            <?= icon('package', 18, '', 'var(--vert-mousse)') ?>
                            <span>Volume : <strong><?= e($product['volume']) ?></strong></span>
                        </div>
                    <?php endif; ?>
                    <?php if ($product['alcohol_percentage'] !== null): ?>
                        <div class="spec-item" style="display:flex;align-items:center;gap:.4rem">
                            <?= icon('wine', 18, '', 'var(--vert-mousse)') ?>
                            <span>Alcool : <strong><?= number_format((float) $product['alcohol_percentage'], 1, ',', '') ?> %</strong></span>
                        </div>
                    <?php endif; ?>
                </div>

                <!-- Description -->
                <?php if ($product['description']): ?>
                    <div class="product-detail-description" style="margin-bottom:2rem;line-height:1.8">
                        <?= sanitize($product['description']) ?>
                    </div>
                <?php endif; ?>

                <!-- Formulaire d'ajout au panier -->
                <?php if ($product['stock'] === null || (int) $product['stock'] > 0): ?>
                    <form action="/panier/ajouter" method="post" class="product-add-form">
                        <?= csrf_field() ?>
                        <input type="hidden" name="product_id" value="<?= (int) $product['id'] ?>">

                        <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap">
                            <div class="quantity-selector" style="display:flex;align-items:center;gap:.5rem">
                                <label for="quantity" style="font-weight:600">Quantité :</label>
                                <input type="number" name="quantity" id="quantity" value="1" min="1"
                                       <?php if ((int) $product['stock'] > 0): ?>max="<?= (int) $product['stock'] ?>"<?php endif; ?>
                                       style="width:70px;padding:.5rem;border:2px solid var(--creme-fonce);border-radius:8px;text-align:center;font-size:1rem">
                            </div>

                            <button type="submit" class="btn btn-secondary">
                                <?= icon('shopping-cart', 18) ?> Ajouter au panier
                            </button>
                        </div>

                        <?php if ((int) $product['stock'] > 0 && (int) $product['stock'] <= 5): ?>
                            <p style="margin-top:.75rem;color:var(--orange-cidre);font-weight:500;font-size:.9rem">
                                <?= icon('alert-triangle', 16) ?> Plus que <?= (int) $product['stock'] ?> en stock
                            </p>
                        <?php endif; ?>
                    </form>
                <?php else: ?>
                    <div style="padding:1rem;background:var(--creme-fonce);border-radius:10px;text-align:center">
                        <p style="font-weight:600;color:var(--brun)"><?= icon('alert-circle', 18) ?> Produit actuellement indisponible</p>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</section>
