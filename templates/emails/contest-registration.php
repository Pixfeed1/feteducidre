<h2>Inscription au concours de cidre</h2>

<p>Une nouvelle inscription au concours a été enregistrée.</p>

<div class="info-box">
    <p style="margin:0"><strong>Producteur :</strong> <?= htmlspecialchars($producer ?? '') ?></p>
    <p style="margin:4px 0 0"><strong>Contact :</strong> <?= htmlspecialchars($contact ?? '') ?></p>
</div>

<?php if (!empty($products)): ?>
<h3 style="color:#2C4A2E;margin-top:20px">Produits inscrits</h3>
<table class="order-table">
    <thead>
        <tr>
            <th>Catégorie</th>
            <th>Produit</th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($products as $product): ?>
        <tr>
            <td><?= htmlspecialchars($product['category'] ?? '') ?></td>
            <td><?= htmlspecialchars($product['name'] ?? '') ?></td>
        </tr>
        <?php endforeach; ?>
    </tbody>
</table>
<?php endif; ?>

<?php if (!empty($stats)): ?>
<div class="info-box">
    <p style="margin:0"><strong>Statistiques inscription :</strong></p>
    <p style="margin:4px 0 0"><?= htmlspecialchars($stats) ?></p>
</div>
<?php endif; ?>
