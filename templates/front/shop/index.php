<?php
/**
 * Template Boutique — catalogue produits avec filtres.
 * Variables : $page, $products, $categories, $seo
 */
$catMeta = [
    'cidre-brut' => ['icon' => 'wine',     'label' => 'Cidre brut',     'filter' => 'cidre'],
    'cidre-doux' => ['icon' => 'wine',     'label' => 'Cidre doux',     'filter' => 'cidre'],
    'cidre-demi' => ['icon' => 'wine',     'label' => 'Cidre demi-sec', 'filter' => 'cidre'],
    'jus'        => ['icon' => 'cup-soda', 'label' => 'Jus',            'filter' => 'jus'],
    'pommeau'    => ['icon' => 'grape',    'label' => 'Pommeau',        'filter' => 'pommeau'],
    'coffret'    => ['icon' => 'gift',     'label' => 'Coffret',        'filter' => 'coffret'],
];

$filterLabels = [
    'cidre'   => ['icon' => 'wine',     'label' => 'Cidres'],
    'jus'     => ['icon' => 'cup-soda', 'label' => 'Jus'],
    'pommeau' => ['icon' => 'grape',    'label' => 'Pommeau'],
    'coffret' => ['icon' => 'gift',     'label' => 'Coffrets'],
];

// Déterminer les filtres disponibles
$availableFilters = [];
foreach ($products as $p) {
    $cat = $p['category'] ?? '';
    $meta = $catMeta[$cat] ?? null;
    if ($meta && !isset($availableFilters[$meta['filter']])) {
        $availableFilters[$meta['filter']] = $filterLabels[$meta['filter']] ?? ['icon' => 'package', 'label' => ucfirst($meta['filter'])];
    }
}
?>

<!-- Hero -->
<section class="shop-hero">
    <div class="shop-hero-pattern"></div>
    <div class="shop-hero-deco"></div>
    <div class="shop-hero-content">
        <nav class="breadcrumb" style="justify-content:center;margin-bottom:1.5rem" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Boutique</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('store', 14) ?> Notre boutique
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">La <em>Boutique</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Cidres, jus de pomme, pommeau… retrouvez les saveurs du terroir du Haut Anjou livrées chez vous.</p>
    </div>
</section>

<?php if (!empty($page['content'])): ?>
<section class="section" style="padding-bottom:0">
    <div class="container cms-content">
        <?= sanitize($page['content']) ?>
    </div>
</section>
<?php endif; ?>

<!-- Filter Bar -->
<?php if (count($availableFilters) > 1): ?>
<div class="filter-bar">
    <div class="filter-inner">
        <button class="filter-btn active" data-filter="all">
            <?= icon('grid-3x3', 13) ?> Tout
        </button>
        <?php foreach ($availableFilters as $filterKey => $filterInfo): ?>
            <button class="filter-btn" data-filter="<?= e($filterKey) ?>">
                <?= icon($filterInfo['icon'], 13) ?> <?= e($filterInfo['label']) ?>
            </button>
        <?php endforeach; ?>
    </div>
</div>
<?php endif; ?>

<section class="shop-section">

    <!-- Info Bar -->
    <div class="info-bar">
        <div class="info-bar-inner">
            <div class="info-item">
                <div class="info-item-icon"><?= icon('truck', 18, '', 'var(--vert-mousse)') ?></div>
                <div class="info-item-text">Livraison soignée<small>Expédié sous 48h</small></div>
            </div>
            <div class="info-item">
                <div class="info-item-icon"><?= icon('shield-check', 18, '', 'var(--vert-mousse)') ?></div>
                <div class="info-item-text">Paiement sécurisé<small>CB, PayPal</small></div>
            </div>
            <div class="info-item">
                <div class="info-item-icon"><?= icon('apple', 18, '', 'var(--vert-mousse)') ?></div>
                <div class="info-item-text">Production locale<small>Haut Anjou, 49</small></div>
            </div>
        </div>
    </div>

    <!-- Products Grid -->
    <?php if (empty($products)): ?>
        <div style="text-align:center;padding:4rem 0">
            <div style="margin-bottom:1rem"><?= icon('shopping-bag', 48, '', 'var(--vert-clair)') ?></div>
            <h2 style="margin-bottom:.5rem">Aucun produit disponible</h2>
            <p style="color:var(--texte-leger)">La boutique est en cours de préparation. Revenez bientôt !</p>
        </div>
    <?php else: ?>
        <div class="products-grid" id="productsGrid">
            <?php foreach ($products as $product):
                $cat = $product['category'] ?? 'autres';
                $meta = $catMeta[$cat] ?? ['icon' => 'package', 'label' => ucfirst($cat), 'filter' => $cat];
                $filterGroup = $meta['filter'] ?? $cat;
                $hasAlcohol = !empty($product['alcohol_percentage']) && (float) $product['alcohol_percentage'] > 0;
            ?>
                <a href="/boutique/<?= e($product['slug']) ?>" class="product-card" data-cat="<?= e($cat) ?>" data-filter="<?= e($filterGroup) ?>">
                    <div class="product-img">
                        <?php if ($product['image']): ?>
                            <?= img($product['image'], $product['name'], 'product-img-bg') ?>
                        <?php else: ?>
                            <div class="product-img-bg"></div>
                        <?php endif; ?>
                        <span class="product-badge">
                            <?= icon($meta['icon'], 10) ?> <?= e($meta['label']) ?>
                        </span>
                        <?php if ($product['is_featured']): ?>
                            <span class="product-tag new">Nouveau</span>
                        <?php elseif ($product['sale_price']): ?>
                            <span class="product-tag promo">Promo</span>
                        <?php endif; ?>
                    </div>
                    <div class="product-body">
                        <span class="product-cat"><?= e($meta['label']) ?></span>
                        <span class="product-name"><?= e($product['name']) ?></span>
                        <?php if ($product['short_description']): ?>
                            <span class="product-desc"><?= e(truncate($product['short_description'], 120)) ?></span>
                        <?php endif; ?>
                        <div class="product-footer">
                            <span class="product-price">
                                <?php if ($product['sale_price']): ?>
                                    <span class="old-price"><?= number_format((float) $product['price'], 2, ',', ' ') ?> €</span>
                                    <?= number_format((float) $product['sale_price'], 2, ',', ' ') ?> €
                                <?php else: ?>
                                    <?= number_format((float) $product['price'], 2, ',', ' ') ?> €
                                <?php endif; ?>
                                <?php if ($product['volume']): ?>
                                    <small>/ <?= e($product['volume']) ?></small>
                                <?php endif; ?>
                            </span>
                            <span class="product-cta">
                                <?= icon('shopping-bag', 12) ?> Voir
                            </span>
                        </div>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</section>

<!-- Legal Notice -->
<?php
$hasAlcoholProducts = false;
foreach ($products as $p) {
    if (!empty($p['alcohol_percentage']) && (float) $p['alcohol_percentage'] > 0) {
        $hasAlcoholProducts = true;
        break;
    }
}
?>
<?php if ($hasAlcoholProducts): ?>
<section style="max-width:1200px;margin:0 auto;padding:0 2rem 3rem">
    <div class="legal-notice">
        <?= icon('alert-triangle', 16, '', 'var(--brun)') ?>
        <span>L'abus d'alcool est dangereux pour la santé, à consommer avec modération. La vente d'alcool est interdite aux mineurs.</span>
    </div>
</section>
<?php endif; ?>

<?php if (!empty($products) && count($availableFilters) > 1): ?>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var btns = document.querySelectorAll('.filter-btn');
    btns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            btns.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            var filter = btn.dataset.filter;
            document.querySelectorAll('.product-card').forEach(function(card) {
                card.style.display = (filter === 'all' || card.dataset.filter === filter) ? '' : 'none';
            });
        });
    });
});
</script>
<?php endif; ?>
