<h2>Confirmation de votre commande</h2>

<p>Bonjour <?= htmlspecialchars($name ?? '') ?>,</p>

<p>Merci pour votre commande ! Voici le récapitulatif :</p>

<div class="info-box">
    <p style="margin:0"><strong>Commande n° <?= htmlspecialchars($order_id ?? '') ?></strong></p>
</div>

<?php if (!empty($items)): ?>
<table class="order-table">
    <thead>
        <tr>
            <th>Produit</th>
            <th>Qté</th>
            <th>Prix</th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($items as $item): ?>
        <tr>
            <td><?= htmlspecialchars($item['name'] ?? '') ?></td>
            <td><?= (int)($item['quantity'] ?? 1) ?></td>
            <td><?= number_format((float)($item['total'] ?? 0), 2, ',', ' ') ?> €</td>
        </tr>
        <?php endforeach; ?>
    </tbody>
</table>
<?php endif; ?>

<p class="order-total" style="text-align: right;">
    Total : <?= number_format((float)($total ?? 0), 2, ',', ' ') ?> €
</p>

<?php if (!empty($address)): ?>
<div class="info-box">
    <p style="margin:0"><strong>Adresse de livraison :</strong></p>
    <p style="margin:4px 0 0"><?= nl2br(htmlspecialchars($address)) ?></p>
</div>
<?php endif; ?>

<p>Nous vous informerons dès que votre commande sera expédiée.</p>
