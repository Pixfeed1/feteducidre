<?php
/**
 * Template panier d'achat.
 * Variables : $items, $subtotal, $shipping, $total, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('shopping-cart', 32) ?> Panier</h1>
    </div>
</section>

<section class="section section-cart">
    <div class="container">
        <?php if (empty($items)): ?>
            <!-- Panier vide -->
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('shopping-cart', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Votre panier est vide</h2>
                <p style="margin-bottom:2rem">Parcourez notre boutique pour découvrir nos produits du terroir.</p>
                <a href="/boutique" class="btn btn-primary">
                    <?= icon('shopping-bag', 18) ?> Voir la boutique
                </a>
            </div>
        <?php else: ?>
            <div class="cart-layout" style="display:grid;grid-template-columns:1fr 350px;gap:2rem;align-items:start">

                <!-- Tableau du panier -->
                <div class="cart-items">
                    <table class="cart-table" style="width:100%;border-collapse:collapse">
                        <thead>
                            <tr style="border-bottom:2px solid var(--creme-fonce)">
                                <th style="text-align:left;padding:.75rem 0;font-weight:600">Produit</th>
                                <th style="text-align:center;padding:.75rem 0;font-weight:600">Prix unitaire</th>
                                <th style="text-align:center;padding:.75rem 0;font-weight:600">Quantité</th>
                                <th style="text-align:right;padding:.75rem 0;font-weight:600">Sous-total</th>
                                <th style="width:50px"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($items as $item): ?>
                                <tr style="border-bottom:1px solid var(--creme-fonce)">
                                    <!-- Nom du produit -->
                                    <td style="padding:1rem 0">
                                        <a href="/boutique/<?= e($item['product']['slug']) ?>" style="font-weight:600;color:var(--vert-profond)">
                                            <?= e($item['product']['name']) ?>
                                        </a>
                                        <?php if ($item['product']['volume']): ?>
                                            <br><small style="color:var(--brun)"><?= e($item['product']['volume']) ?></small>
                                        <?php endif; ?>
                                    </td>

                                    <!-- Prix unitaire -->
                                    <td style="text-align:center;padding:1rem 0">
                                        <?= number_format($item['unit_price'], 2, ',', ' ') ?> &euro;
                                    </td>

                                    <!-- Quantité avec boutons +/- -->
                                    <td style="text-align:center;padding:1rem 0">
                                        <div style="display:inline-flex;align-items:center;gap:.25rem">
                                            <form action="/panier/modifier" method="post" style="display:inline">
                                                <?= csrf_field() ?>
                                                <input type="hidden" name="product_id" value="<?= (int) $item['product']['id'] ?>">
                                                <input type="hidden" name="quantity" value="<?= $item['quantity'] - 1 ?>">
                                                <button type="submit" class="btn btn-outline btn-sm" style="padding:.25rem .5rem;min-width:auto" <?= $item['quantity'] <= 1 ? 'disabled' : '' ?>>
                                                    <?= icon('minus', 14) ?>
                                                </button>
                                            </form>

                                            <span style="display:inline-block;min-width:2rem;text-align:center;font-weight:600"><?= $item['quantity'] ?></span>

                                            <form action="/panier/modifier" method="post" style="display:inline">
                                                <?= csrf_field() ?>
                                                <input type="hidden" name="product_id" value="<?= (int) $item['product']['id'] ?>">
                                                <input type="hidden" name="quantity" value="<?= $item['quantity'] + 1 ?>">
                                                <button type="submit" class="btn btn-outline btn-sm" style="padding:.25rem .5rem;min-width:auto">
                                                    <?= icon('plus', 14) ?>
                                                </button>
                                            </form>
                                        </div>
                                    </td>

                                    <!-- Sous-total ligne -->
                                    <td style="text-align:right;padding:1rem 0;font-weight:600">
                                        <?= number_format($item['total'], 2, ',', ' ') ?> &euro;
                                    </td>

                                    <!-- Supprimer -->
                                    <td style="text-align:center;padding:1rem 0">
                                        <form action="/panier/supprimer" method="post">
                                            <?= csrf_field() ?>
                                            <input type="hidden" name="product_id" value="<?= (int) $item['product']['id'] ?>">
                                            <button type="submit" class="btn-link" style="color:var(--brun);background:none;border:none;cursor:pointer" title="Supprimer">
                                                <?= icon('trash-2', 18) ?>
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>

                    <div style="margin-top:1.5rem">
                        <a href="/boutique" class="btn btn-outline">
                            <?= icon('arrow-left', 18) ?> Continuer mes achats
                        </a>
                    </div>
                </div>

                <!-- Résumé du panier -->
                <div class="cart-summary card">
                    <div class="card-body" style="padding:1.5rem">
                        <h3 style="margin-bottom:1.5rem">Récapitulatif</h3>

                        <div style="display:flex;justify-content:space-between;margin-bottom:.75rem">
                            <span>Sous-total</span>
                            <span style="font-weight:600"><?= number_format($subtotal, 2, ',', ' ') ?> &euro;</span>
                        </div>

                        <div style="display:flex;justify-content:space-between;margin-bottom:.75rem">
                            <span><?= icon('truck', 16) ?> Livraison</span>
                            <span style="font-weight:600"><?= number_format($shipping, 2, ',', ' ') ?> &euro;</span>
                        </div>

                        <hr style="border:none;border-top:2px solid var(--creme-fonce);margin:1rem 0">

                        <div style="display:flex;justify-content:space-between;font-size:1.2rem">
                            <strong>Total</strong>
                            <strong style="color:var(--orange-cidre)"><?= number_format($total, 2, ',', ' ') ?> &euro;</strong>
                        </div>

                        <a href="/commande" class="btn btn-secondary" style="width:100%;justify-content:center;margin-top:1.5rem">
                            <?= icon('check', 18) ?> Commander
                        </a>
                    </div>
                </div>

            </div>
        <?php endif; ?>
    </div>
</section>
