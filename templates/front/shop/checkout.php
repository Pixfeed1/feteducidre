<?php
/**
 * Template page commande — design premium.
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
$finalTotal = $freeShipping ? $subtotal : $total;
?>

<!-- Stepper -->
<div class="stepper">
    <div class="step done">
        <span class="step-num"><?= icon('check', 14) ?></span>
        <span class="step-label">Panier</span>
    </div>
    <div class="step-line done"></div>
    <div class="step active">
        <span class="step-num">2</span>
        <span class="step-label">Livraison</span>
    </div>
    <div class="step-line"></div>
    <div class="step">
        <span class="step-num">3</span>
        <span class="step-label">Paiement</span>
    </div>
</div>

<form action="/commande" method="post" id="checkoutForm">
    <?= csrf_field() ?>

    <div class="checkout-page" style="animation:fadeInUp .8s ease both">

        <!-- Left Column: Form Sections -->
        <div class="form-section">

            <!-- Delivery Address -->
            <div>
                <div class="section-head">
                    <div class="section-icon">
                        <?= icon('truck', 18) ?>
                    </div>
                    <div>
                        <h2>Adresse de livraison</h2>
                        <p>Où souhaitez-vous être livré ?</p>
                    </div>
                </div>
                <div class="form-card">
                    <div class="form-row">
                        <div class="field">
                            <label for="first_name">Prénom <span class="req">*</span></label>
                            <input type="text" name="first_name" id="first_name" value="<?= old('first_name') ?>" required placeholder="Votre prénom">
                        </div>
                        <div class="field">
                            <label for="last_name">Nom <span class="req">*</span></label>
                            <input type="text" name="last_name" id="last_name" value="<?= old('last_name') ?>" required placeholder="Votre nom">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="field">
                            <label for="email">Email <span class="req">*</span></label>
                            <input type="email" name="email" id="email" value="<?= old('email') ?>" required placeholder="votre@email.fr">
                        </div>
                        <div class="field">
                            <label for="phone">Téléphone</label>
                            <input type="tel" name="phone" id="phone" value="<?= old('phone') ?>" placeholder="06 12 34 56 78">
                        </div>
                    </div>
                    <div class="form-row full">
                        <div class="field">
                            <label for="address">Adresse <span class="req">*</span></label>
                            <input type="text" name="address" id="address" value="<?= old('address') ?>" required placeholder="Numéro et nom de rue">
                        </div>
                    </div>
                    <div class="form-row triple">
                        <div class="field">
                            <label for="postal_code">Code postal <span class="req">*</span></label>
                            <input type="text" name="postal_code" id="postal_code" value="<?= old('postal_code') ?>" required placeholder="49000" maxlength="5" pattern="[0-9]{5}">
                        </div>
                        <div class="field">
                            <label for="city">Ville <span class="req">*</span></label>
                            <input type="text" name="city" id="city" value="<?= old('city') ?>" required placeholder="Ville">
                        </div>
                        <div class="field">
                            <label for="country">Pays</label>
                            <select name="country" id="country">
                                <option value="FR" selected>France</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row full" style="margin-bottom:0">
                        <div class="field">
                            <label for="notes">Notes de commande</label>
                            <textarea name="notes" id="notes" rows="2" placeholder="Instructions particulières pour la livraison..."><?= old('notes') ?></textarea>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Payment -->
            <div>
                <div class="section-head">
                    <div class="section-icon">
                        <?= icon('lock', 18) ?>
                    </div>
                    <div>
                        <h2>Paiement</h2>
                        <p>Choisissez votre mode de paiement</p>
                    </div>
                </div>
                <div class="form-card">
                    <div class="payment-methods">
                        <label class="pm selected" id="pmCb">
                            <input type="radio" name="payment_method" value="card" checked>
                            <span class="pm-dot"></span>
                            <span class="pm-icon cb"><?= icon('credit-card', 18) ?></span>
                            <span class="pm-label">
                                Carte bancaire
                                <small>Visa, Mastercard</small>
                            </span>
                        </label>
                        <label class="pm" id="pmVir">
                            <input type="radio" name="payment_method" value="transfer">
                            <span class="pm-dot"></span>
                            <span class="pm-icon vir"><?= icon('building', 18) ?></span>
                            <span class="pm-label">
                                Virement
                                <small>Virement bancaire</small>
                            </span>
                        </label>
                    </div>

                    <div class="card-fields" id="cardFields">
                        <div class="form-row full">
                            <div class="field">
                                <label for="card_number">Numéro de carte <span class="req">*</span></label>
                                <input type="text" id="card_number" placeholder="1234 5678 9012 3456" maxlength="19">
                            </div>
                        </div>
                        <div class="form-row" style="margin-bottom:0">
                            <div class="field">
                                <label for="card_expiry">Date d'expiration <span class="req">*</span></label>
                                <input type="text" id="card_expiry" placeholder="MM/AA" maxlength="5">
                            </div>
                            <div class="field">
                                <label for="card_cvc">CVC <span class="req">*</span></label>
                                <input type="text" id="card_cvc" placeholder="123" maxlength="4">
                            </div>
                        </div>
                    </div>

                    <div class="cgv-check">
                        <input type="checkbox" name="cgv" id="cgv" required>
                        <label for="cgv">J'accepte les <a href="/mentions-legales">conditions générales de vente</a> et la <a href="/mentions-legales">politique de confidentialité</a>.</label>
                    </div>
                </div>
            </div>

        </div>

        <!-- Right Column: Order Summary -->
        <div class="order-summary">
            <div class="os-title">
                <?= icon('shopping-bag', 18) ?> Votre commande
            </div>

            <div class="os-items">
                <?php foreach ($items as $item):
                    $product = $item['product'];
                    $cat = $product['category'] ?? 'autres';
                    $meta = $catMeta[$cat] ?? ['icon' => 'package', 'label' => ucfirst($cat), 'gradient' => 'linear-gradient(135deg, var(--vert-profond), var(--vert-mousse))'];
                ?>
                    <div class="os-item">
                        <div class="os-thumb" style="background:<?= $meta['gradient'] ?>">
                            <?= icon($meta['icon'], 18, '', 'rgba(255,255,255,.5)') ?>
                        </div>
                        <div class="os-detail">
                            <span class="os-name"><?= e($product['name']) ?></span>
                            <span class="os-qty">Qté : <?= $item['quantity'] ?><?php if ($product['volume']): ?> × <?= e($product['volume']) ?><?php endif; ?></span>
                        </div>
                        <span class="os-price"><?= number_format($item['total'], 2, ',', ' ') ?> €</span>
                    </div>
                <?php endforeach; ?>
            </div>

            <div class="os-divider"></div>

            <div class="os-row">
                <span>Sous-total (<?= $totalQty ?> article<?= $totalQty > 1 ? 's' : '' ?>)</span>
                <span class="val"><?= number_format($subtotal, 2, ',', ' ') ?> €</span>
            </div>
            <div class="os-row">
                <span>Livraison</span>
                <?php if ($freeShipping): ?>
                    <span class="val" style="color:var(--vert-clair)">Offerte</span>
                <?php else: ?>
                    <span class="val"><?= number_format($shipping, 2, ',', ' ') ?> €</span>
                <?php endif; ?>
            </div>
            <div class="os-row total">
                <span>Total</span>
                <span class="val"><?= number_format($finalTotal, 2, ',', ' ') ?> €</span>
            </div>

            <button type="submit" class="pay-btn">
                <?= icon('lock', 16) ?> Payer <?= number_format($finalTotal, 2, ',', ' ') ?> €
            </button>

            <div class="os-secure">
                <?= icon('shield-check', 14, '', 'var(--vert-clair)') ?> Paiement 100% sécurisé
            </div>
        </div>

    </div>
</form>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var pms = document.querySelectorAll('.pm');
    var cardFields = document.getElementById('cardFields');

    pms.forEach(function(pm) {
        pm.addEventListener('click', function() {
            pms.forEach(function(p) { p.classList.remove('selected'); });
            pm.classList.add('selected');
            var radio = pm.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
            if (cardFields) {
                cardFields.style.display = (radio && radio.value === 'card') ? '' : 'none';
            }
        });
    });
});
</script>
