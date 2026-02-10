<?php
/**
 * Template confirmation de commande — design premium.
 * Variables : $order, $orderItems, $seo
 */
$thumbGradients = [
    'linear-gradient(135deg, #2C4A2E, #4A6B3E)',
    'linear-gradient(135deg, #D4833B, #E8A95B)',
    'linear-gradient(135deg, #E8A95B, #F5CC6A)',
    'linear-gradient(135deg, #5C3D2E, #D4833B)',
    'linear-gradient(135deg, #4A6B3E, #E8A95B)',
    'linear-gradient(135deg, #2C4A2E, #E8A95B)',
];

$freeShippingThreshold = 40;
$shippingFree = (float) $order['subtotal'] >= $freeShippingThreshold;
?>

<!-- Stepper — all done -->
<div class="stepper">
    <div class="step done">
        <span class="step-num"><?= icon('check', 14) ?></span>
        <span class="step-label">Panier</span>
    </div>
    <div class="step-line done"></div>
    <div class="step done">
        <span class="step-num"><?= icon('check', 14) ?></span>
        <span class="step-label">Livraison</span>
    </div>
    <div class="step-line done"></div>
    <div class="step done">
        <span class="step-num"><?= icon('check', 14) ?></span>
        <span class="step-label">Paiement</span>
    </div>
</div>

<section class="confirm-page">

    <!-- Success Icon -->
    <div class="success-icon">
        <?= icon('check', 44, '', 'white') ?>
    </div>

    <h1>Commande confirmée !</h1>
    <p class="subtitle">
        Merci pour votre commande. Un e-mail de confirmation a été envoyé à <strong><?= e($order['customer_email']) ?></strong>.
        Votre colis sera préparé avec soin.
    </p>

    <!-- Order Number -->
    <div class="order-num">
        <?= icon('package', 18, '', 'var(--vert-mousse)') ?>
        Commande n° <strong><?= e($order['reference']) ?></strong>
    </div>

    <!-- Recap -->
    <div class="recap">
        <div class="recap-head">
            <?= icon('receipt', 18, '', 'var(--orange-cidre)') ?> Récapitulatif
        </div>
        <div class="recap-items">
            <?php foreach ($orderItems as $i => $item):
                $gradient = $thumbGradients[$i % count($thumbGradients)];
            ?>
                <div class="ri">
                    <div class="ri-thumb" style="background:<?= $gradient ?>">
                        <?= icon('wine', 16, '', 'rgba(255,255,255,.5)') ?>
                    </div>
                    <div class="ri-detail">
                        <span class="ri-name"><?= e($item['product_name']) ?></span>
                        <span class="ri-qty">× <?= (int) $item['quantity'] ?></span>
                    </div>
                    <span class="ri-price"><?= number_format((float) $item['total_price'], 2, ',', ' ') ?> €</span>
                </div>
            <?php endforeach; ?>
        </div>
        <div class="recap-divider"></div>
        <div class="recap-row">
            <span>Sous-total</span>
            <span class="v"><?= number_format((float) $order['subtotal'], 2, ',', ' ') ?> €</span>
        </div>
        <div class="recap-row">
            <span>Livraison</span>
            <?php if ($shippingFree): ?>
                <span class="v" style="color:var(--vert-clair)">Offerte</span>
            <?php else: ?>
                <span class="v"><?= number_format((float) $order['shipping_cost'], 2, ',', ' ') ?> €</span>
            <?php endif; ?>
        </div>
        <div class="recap-row total">
            <span>Total payé</span>
            <span class="v"><?= number_format((float) $order['total'], 2, ',', ' ') ?> €</span>
        </div>
    </div>

    <!-- Delivery Details -->
    <div class="delivery-info">
        <div class="dinfo">
            <div class="dinfo-label">
                <?= icon('truck', 14, '', 'var(--vert-mousse)') ?> Livraison
            </div>
            <div class="dinfo-value">
                <?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?><br>
                <?= e($order['shipping_address']) ?><br>
                <?= e($order['shipping_postal_code'] . ' ' . $order['shipping_city']) ?><br>
                France
            </div>
        </div>
        <div class="dinfo">
            <div class="dinfo-label">
                <?= icon('credit-card', 14, '', 'var(--orange-cidre)') ?> Paiement
            </div>
            <div class="dinfo-value">
                Paiement enregistré<br>
                <?= e($order['customer_email']) ?><br>
                <br>
                Expédition estimée : <strong>48h</strong>
            </div>
        </div>
    </div>

    <!-- Next Steps -->
    <div class="next-steps">
        <div class="ns">
            <span class="ns-num">1</span>
            <div class="ns-text"><strong>E-mail de confirmation</strong> envoyé à votre adresse avec le détail de la commande.</div>
        </div>
        <div class="ns">
            <span class="ns-num">2</span>
            <div class="ns-text"><strong>Préparation</strong> — votre colis est préparé et emballé avec soin sous 48h.</div>
        </div>
        <div class="ns">
            <span class="ns-num">3</span>
            <div class="ns-text"><strong>Expédition</strong> — un numéro de suivi vous sera envoyé par e-mail dès l'envoi.</div>
        </div>
    </div>

    <!-- CTAs -->
    <div class="cta-row">
        <a href="/boutique" class="cta-primary">
            <?= icon('store', 16) ?> Retour à la boutique
        </a>
        <a href="/" class="cta-secondary">
            <?= icon('home', 16) ?> Accueil
        </a>
    </div>

</section>
