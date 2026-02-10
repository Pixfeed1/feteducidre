<?php
/**
 * Template panier d'achat — design premium.
 * Variables : $items, $subtotal, $shipping, $total, $seo
 */
$catMeta = [
    'cidre-brut' => ['icon' => 'wine',     'label' => 'Cidre brut',     'gradient' => 'linear-gradient(135deg, #2C4A2E, #4A6B3E)'],
    'cidre-doux' => ['icon' => 'wine',     'label' => 'Cidre doux',     'gradient' => 'linear-gradient(135deg, #D4833B, #E8A95B)'],
    'cidre-demi' => ['icon' => 'wine',     'label' => 'Cidre demi-sec', 'gradient' => 'linear-gradient(135deg, #4A6B3E, #E8A95B)'],
    'jus'        => ['icon' => 'cup-soda', 'label' => 'Jus',            'gradient' => 'linear-gradient(135deg, #E8A95B, #F5CC6A)'],
    'pommeau'    => ['icon' => 'grape',    'label' => 'Pommeau',        'gradient' => 'linear-gradient(135deg, #5C3D2E, #D4833B)'],
    'coffret'    => ['icon' => 'gift',     'label' => 'Coffret',        'gradient' => 'linear-gradient(135deg, #2C4A2E, #E8A95B)'],
];

$totalQty = 0;
foreach ($items as $item) {
    $totalQty += $item['quantity'];
}

$freeShippingThreshold = 40;
$freeShipping = $subtotal >= $freeShippingThreshold;
?>

<!-- Stepper -->
<div class="stepper">
    <div class="step active">
        <span class="step-num">1</span>
        <span class="step-label">Panier</span>
    </div>
    <div class="step-line"></div>
    <div class="step">
        <span class="step-num">2</span>
        <span class="step-label">Livraison</span>
    </div>
    <div class="step-line"></div>
    <div class="step">
        <span class="step-num">3</span>
        <span class="step-label">Paiement</span>
    </div>
</div>

<section class="cart-page" style="animation:fadeInUp .8s ease both">

    <h1>
        <?= icon('shopping-bag', 28) ?> Votre panier
        <?php if (!empty($items)): ?>
            <span class="cart-count"><?= $totalQty ?> article<?= $totalQty > 1 ? 's' : '' ?></span>
        <?php endif; ?>
    </h1>

    <?php if (empty($items)): ?>
        <!-- Empty cart -->
        <div class="cart-empty">
            <div style="margin-bottom:1rem"><?= icon('shopping-bag', 48, '', 'var(--vert-clair)') ?></div>
            <h2 style="margin-bottom:.5rem">Votre panier est vide</h2>
            <p style="color:var(--texte-leger);margin-bottom:2rem">Parcourez notre boutique pour découvrir nos produits du terroir.</p>
            <a href="/boutique" class="checkout-btn" style="display:inline-flex;max-width:280px;margin:0 auto">
                <?= icon('shopping-bag', 18) ?> Voir la boutique
            </a>
        </div>
    <?php else: ?>
        <!-- Cart items -->
        <div class="cart-items">
            <?php foreach ($items as $item):
                $product = $item['product'];
                $cat = $product['category'] ?? 'autres';
                $meta = $catMeta[$cat] ?? ['icon' => 'package', 'label' => ucfirst($cat), 'gradient' => 'linear-gradient(135deg, var(--vert-profond), var(--vert-mousse))'];
            ?>
                <div class="cart-item">
                    <div class="item-thumb" style="background:<?= $meta['gradient'] ?>">
                        <?php if (!empty($product['image_id'])): ?>
                            <?php /* Image would go here if loaded */ ?>
                        <?php endif; ?>
                        <?= icon($meta['icon'], 24, '', 'rgba(255,255,255,.5)') ?>
                    </div>
                    <div class="item-info">
                        <span class="item-cat"><?= e($meta['label']) ?></span>
                        <a href="/boutique/<?= e($product['slug']) ?>" class="item-name"><?= e($product['name']) ?></a>
                        <span class="item-unit"><?= number_format($item['unit_price'], 2, ',', ' ') ?> €<?php if ($product['volume']): ?> × <?= e($product['volume']) ?><?php endif; ?></span>
                    </div>
                    <div class="item-actions">
                        <span class="item-price"><?= number_format($item['total'], 2, ',', ' ') ?> €</span>
                        <div class="item-qty">
                            <form action="/panier/modifier" method="post" style="display:contents">
                                <?= csrf_field() ?>
                                <input type="hidden" name="product_id" value="<?= (int) $product['id'] ?>">
                                <input type="hidden" name="quantity" value="<?= $item['quantity'] - 1 ?>">
                                <button type="submit" class="iq-btn" <?= $item['quantity'] <= 1 ? 'disabled' : '' ?>>−</button>
                            </form>
                            <span class="iq-val"><?= $item['quantity'] ?></span>
                            <form action="/panier/modifier" method="post" style="display:contents">
                                <?= csrf_field() ?>
                                <input type="hidden" name="product_id" value="<?= (int) $product['id'] ?>">
                                <input type="hidden" name="quantity" value="<?= $item['quantity'] + 1 ?>">
                                <button type="submit" class="iq-btn">+</button>
                            </form>
                        </div>
                        <form action="/panier/supprimer" method="post">
                            <?= csrf_field() ?>
                            <input type="hidden" name="product_id" value="<?= (int) $product['id'] ?>">
                            <button type="submit" class="item-remove">
                                <?= icon('trash-2', 12) ?> Retirer
                            </button>
                        </form>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <!-- Summary -->
        <div class="cart-summary">
            <div class="summary-title">Récapitulatif</div>
            <div class="summary-row">
                <span>Sous-total (<?= $totalQty ?> article<?= $totalQty > 1 ? 's' : '' ?>)</span>
                <span class="val"><?= number_format($subtotal, 2, ',', ' ') ?> €</span>
            </div>
            <div class="summary-row">
                <span>Livraison estimée</span>
                <span class="val" style="color:var(--texte-leger);font-size:.9rem">
                    <?php if ($freeShipping): ?>
                        <span style="color:var(--vert-clair);font-weight:600">Offerte</span>
                    <?php else: ?>
                        <?= number_format($shipping, 2, ',', ' ') ?> €
                    <?php endif; ?>
                </span>
            </div>
            <?php if (!$freeShipping): ?>
                <div class="summary-row" style="font-size:.8rem;color:var(--vert-clair)">
                    <span><?= icon('apple', 14) ?> Livraison offerte dès <?= $freeShippingThreshold ?> € d'achat</span>
                </div>
            <?php endif; ?>
            <div class="summary-row total">
                <span>Total</span>
                <span class="val"><?= number_format($freeShipping ? $subtotal : $total, 2, ',', ' ') ?> €</span>
            </div>
            <a href="/commande" class="checkout-btn">
                <?= icon('lock', 16) ?> Commander
            </a>
            <a href="/boutique" class="continue-link">
                <?= icon('arrow-left', 14) ?> Continuer mes achats
            </a>
            <div class="secure-note">
                <?= icon('shield-check', 14, '', 'var(--vert-clair)') ?> Paiement 100% sécurisé
            </div>
        </div>
    <?php endif; ?>
</section>
