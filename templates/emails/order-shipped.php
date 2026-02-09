<h2>Votre commande est en route !</h2>

<p>Bonjour <?= htmlspecialchars($name ?? '') ?>,</p>

<p>Bonne nouvelle ! Votre commande <strong>n° <?= htmlspecialchars($order_id ?? '') ?></strong> a été expédiée.</p>

<?php if (!empty($tracking)): ?>
<div class="info-box">
    <p style="margin:0"><strong>Suivi de livraison :</strong></p>
    <p style="margin:4px 0 0">Transporteur : <?= htmlspecialchars($carrier ?? '') ?></p>
    <p style="margin:4px 0 0">N° de suivi : <strong><?= htmlspecialchars($tracking) ?></strong></p>
    <?php if (!empty($eta)): ?>
    <p style="margin:4px 0 0">Livraison estimée : <?= htmlspecialchars($eta) ?></p>
    <?php endif; ?>
</div>
<?php endif; ?>

<p>Merci pour votre confiance !</p>
