<h2>Nouvelle commande reçue</h2>

<p>Une nouvelle commande vient d'être passée sur le site.</p>

<div class="info-box">
    <p style="margin:0"><strong>Commande n° <?= htmlspecialchars($order_id ?? '') ?></strong></p>
    <p style="margin:4px 0 0">Montant : <strong><?= number_format((float)($amount ?? 0), 2, ',', ' ') ?> €</strong></p>
    <p style="margin:4px 0 0">Client : <?= htmlspecialchars($customer ?? '') ?></p>
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

<p style="text-align: center;">
    <a href="<?= \App\Core\Config::baseUrl() ?>/admin/orders" class="email-btn">Voir la commande</a>
</p>
