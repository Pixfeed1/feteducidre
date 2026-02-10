<?php
/**
 * Template fiche produit — design premium.
 * Variables : $product, $image, $related, $seo
 */
$catMeta = [
    'cidre-brut' => ['icon' => 'wine',     'label' => 'Cidre brut',     'gradient' => 'linear-gradient(135deg, #2C4A2E 0%, #4A6B3E 50%, #7A9E6B 100%)'],
    'cidre-doux' => ['icon' => 'wine',     'label' => 'Cidre doux',     'gradient' => 'linear-gradient(135deg, #D4833B 0%, #E8A95B 50%, #F5D6A0 100%)'],
    'cidre-demi' => ['icon' => 'wine',     'label' => 'Cidre demi-sec', 'gradient' => 'linear-gradient(135deg, #4A6B3E 0%, #7A9E6B 50%, #E8A95B 100%)'],
    'jus'        => ['icon' => 'cup-soda', 'label' => 'Jus',            'gradient' => 'linear-gradient(135deg, #E8A95B 0%, #F5CC6A 50%, #FAE4A0 100%)'],
    'pommeau'    => ['icon' => 'grape',    'label' => 'Pommeau',        'gradient' => 'linear-gradient(135deg, #5C3D2E 0%, #8B6B4A 50%, #D4833B 100%)'],
    'coffret'    => ['icon' => 'gift',     'label' => 'Coffret',        'gradient' => 'linear-gradient(135deg, #2C4A2E 0%, #D4833B 50%, #E8A95B 100%)'],
];

$cat = $product['category'] ?? 'autres';
$meta = $catMeta[$cat] ?? ['icon' => 'package', 'label' => ucfirst($cat), 'gradient' => 'linear-gradient(135deg, var(--vert-profond), var(--vert-mousse))'];
$hasAlcohol = !empty($product['alcohol_percentage']) && (float) $product['alcohol_percentage'] > 0;
$currentPrice = $product['sale_price'] ?: $product['price'];
$inStock = $product['stock'] === null || (int) $product['stock'] > 0;
?>

<section class="product-page" style="animation:fadeInUp .8s ease both">
    <nav class="breadcrumb" aria-label="Fil d'Ariane">
        <a href="/">Accueil</a>
        <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
        <a href="/boutique">Boutique</a>
        <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
        <span aria-current="page"><?= e($product['name']) ?></span>
    </nav>

    <div class="product-layout">
        <!-- IMAGE -->
        <div class="product-gallery">
            <?php if ($image): ?>
                <?= img($image, $product['name'], 'product-gallery-img') ?>
            <?php else: ?>
                <div class="product-gallery-bg" style="background:<?= $meta['gradient'] ?>"></div>
            <?php endif; ?>
            <div class="product-gallery-badge">
                <span class="gallery-tag">
                    <?= icon($meta['icon'], 10) ?> <?= e($meta['label']) ?>
                </span>
                <?php if ($product['sale_price']): ?>
                    <span class="gallery-tag promo">Promo</span>
                <?php endif; ?>
            </div>
        </div>

        <!-- INFO -->
        <div class="product-info">
            <span class="p-cat">
                <?= icon($meta['icon'], 14) ?> <?= e($meta['label']) ?>
            </span>

            <h1><?= e($product['name']) ?></h1>

            <?php if ($product['description']): ?>
                <div class="p-desc"><?= sanitize($product['description']) ?></div>
            <?php elseif ($product['short_description']): ?>
                <p class="p-desc"><?= e($product['short_description']) ?></p>
            <?php endif; ?>

            <!-- Specs -->
            <?php if ($product['volume'] || $hasAlcohol): ?>
                <div class="specs">
                    <?php if ($product['volume']): ?>
                        <div class="spec">
                            <?= icon('wine', 18, '', 'var(--orange-cidre)') ?>
                            <span class="spec-value"><?= e($product['volume']) ?></span>
                            <span class="spec-label">Contenance</span>
                        </div>
                    <?php endif; ?>
                    <?php if ($hasAlcohol): ?>
                        <div class="spec">
                            <?= icon('gauge', 18, '', 'var(--orange-cidre)') ?>
                            <span class="spec-value"><?= number_format((float) $product['alcohol_percentage'], 1, ',', '') ?>%</span>
                            <span class="spec-label">Alcool</span>
                        </div>
                        <div class="spec">
                            <?= icon('thermometer', 18, '', 'var(--orange-cidre)') ?>
                            <span class="spec-value">8-10°C</span>
                            <span class="spec-label">Service</span>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <!-- Price -->
            <div class="price-block">
                <?php if ($product['sale_price']): ?>
                    <span class="price-old"><?= number_format((float) $product['price'], 2, ',', ' ') ?> €</span>
                <?php endif; ?>
                <span class="price-main"><?= number_format((float) $currentPrice, 2, ',', ' ') ?> €</span>
                <?php if ($product['volume']): ?>
                    <span class="price-unit">/ <?= e($product['volume']) ?></span>
                <?php endif; ?>
            </div>

            <!-- Add to cart -->
            <?php if ($inStock): ?>
                <form action="/panier/ajouter" method="post" id="addForm">
                    <?= csrf_field() ?>
                    <input type="hidden" name="product_id" value="<?= (int) $product['id'] ?>">
                    <div class="actions">
                        <div class="qty-selector">
                            <button type="button" class="qty-btn" id="qtyMinus">−</button>
                            <input type="text" class="qty-val" name="quantity" id="qtyVal" value="1" readonly>
                            <button type="button" class="qty-btn" id="qtyPlus">+</button>
                        </div>
                        <button type="submit" class="add-to-cart">
                            <?= icon('shopping-bag', 18) ?> Ajouter au panier
                        </button>
                    </div>
                </form>
            <?php else: ?>
                <div style="padding:1rem;background:var(--creme-fonce);border-radius:14px;text-align:center">
                    <p style="font-weight:600;color:var(--brun)"><?= icon('alert-triangle', 18) ?> Produit actuellement indisponible</p>
                </div>
            <?php endif; ?>

            <!-- Extra info -->
            <div class="extra-info">
                <?php if ($inStock): ?>
                    <div class="extra-item">
                        <span class="extra-dot"></span>
                        <?php if ((int) $product['stock'] > 0 && (int) $product['stock'] <= 5): ?>
                            Plus que <?= (int) $product['stock'] ?> en stock — Expédition sous 48h
                        <?php else: ?>
                            En stock — Expédition sous 48h
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
                <div class="extra-item"><span class="extra-dot"></span> Livraison soignée en emballage renforcé</div>
                <?php if ($hasAlcohol): ?>
                    <div class="extra-item"><span class="extra-dot"></span> L'abus d'alcool est dangereux pour la santé</div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</section>

<!-- Related Products -->
<?php if (!empty($related)): ?>
<section class="related-section">
    <div class="related-title">Vous aimerez aussi</div>
    <div class="related-grid">
        <?php foreach ($related as $rel):
            $relCat = $rel['category'] ?? 'autres';
            $relMeta = $catMeta[$relCat] ?? $meta;
            $relPrice = $rel['sale_price'] ?: $rel['price'];
        ?>
            <a href="/boutique/<?= e($rel['slug']) ?>" class="rel-card">
                <div class="rel-thumb" style="background:<?= $relMeta['gradient'] ?>">
                    <?php if ($rel['filename']): ?>
                        <img src="/uploads/<?= e($rel['filename']) ?>" alt="<?= e($rel['name']) ?>">
                    <?php else: ?>
                        <?= icon($relMeta['icon'], 24, '', 'rgba(255,255,255,.5)') ?>
                    <?php endif; ?>
                </div>
                <div>
                    <div class="rel-name"><?= e($rel['name']) ?></div>
                    <div class="rel-price"><?= number_format((float) $relPrice, 2, ',', ' ') ?> €</div>
                </div>
            </a>
        <?php endforeach; ?>
    </div>
</section>
<?php endif; ?>

<!-- Toast -->
<div class="toast" id="toast">
    <?= icon('check-circle', 18, '', 'var(--orange-doux)') ?> Ajouté au panier !
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var qtyVal = document.getElementById('qtyVal');
    var qtyMinus = document.getElementById('qtyMinus');
    var qtyPlus = document.getElementById('qtyPlus');
    <?php $maxStock = ((int) $product['stock'] > 0) ? (int) $product['stock'] : 99; ?>

    if (qtyMinus && qtyPlus && qtyVal) {
        qtyMinus.addEventListener('click', function() {
            var v = parseInt(qtyVal.value) || 1;
            qtyVal.value = Math.max(1, v - 1);
        });
        qtyPlus.addEventListener('click', function() {
            var v = parseInt(qtyVal.value) || 1;
            qtyVal.value = Math.min(<?= $maxStock ?>, v + 1);
        });
    }
});
</script>
