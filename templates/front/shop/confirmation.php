<?php
/**
 * Template confirmation de commande.
 * Variables : $order, $orderItems, $seo
 */
?>

<section class="section section-confirmation">
    <div class="container" style="max-width:800px">

        <!-- Message de succès -->
        <div style="text-align:center;margin-bottom:3rem">
            <div style="display:inline-flex;align-items:center;justify-content:center;width:80px;height:80px;background:#e8f5e9;border-radius:50%;margin-bottom:1.5rem">
                <?= icon('check-circle', 40, '', '#2e7d32') ?>
            </div>
            <h1>Commande confirmée !</h1>
            <p style="font-size:1.1rem;color:var(--brun);margin-top:.5rem">
                Merci <?= e($order['customer_first_name']) ?>, votre commande a bien été enregistrée.
            </p>
        </div>

        <!-- Référence -->
        <div class="card" style="margin-bottom:2rem">
            <div class="card-body" style="padding:1.5rem;text-align:center">
                <p style="font-size:.9rem;color:var(--brun);margin-bottom:.25rem">Référence de commande</p>
                <p style="font-size:1.5rem;font-weight:700;color:var(--vert-profond);letter-spacing:1px"><?= e($order['reference']) ?></p>
                <p style="font-size:.85rem;color:var(--brun);margin-top:.5rem">
                    Commande passée le <?= date_fr($order['created_at'], 'datetime') ?>
                </p>
            </div>
        </div>

        <!-- Récapitulatif de commande -->
        <div class="card" style="margin-bottom:2rem">
            <div class="card-body" style="padding:1.5rem">
                <h2 style="margin-bottom:1.5rem"><?= icon('package', 22) ?> Détail de la commande</h2>

                <table style="width:100%;border-collapse:collapse">
                    <thead>
                        <tr style="border-bottom:2px solid var(--creme-fonce)">
                            <th style="text-align:left;padding:.5rem 0;font-weight:600">Produit</th>
                            <th style="text-align:center;padding:.5rem 0;font-weight:600">Qté</th>
                            <th style="text-align:right;padding:.5rem 0;font-weight:600">Prix</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($orderItems as $item): ?>
                            <tr style="border-bottom:1px solid var(--creme-fonce)">
                                <td style="padding:.75rem 0"><?= e($item['product_name']) ?></td>
                                <td style="text-align:center;padding:.75rem 0"><?= (int) $item['quantity'] ?></td>
                                <td style="text-align:right;padding:.75rem 0"><?= number_format((float) $item['total_price'], 2, ',', ' ') ?> &euro;</td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>

                <hr style="border:none;border-top:1px solid var(--creme-fonce);margin:1rem 0">

                <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                    <span>Sous-total</span>
                    <span style="font-weight:600"><?= number_format((float) $order['subtotal'], 2, ',', ' ') ?> &euro;</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                    <span><?= icon('truck', 16) ?> Livraison</span>
                    <span style="font-weight:600"><?= number_format((float) $order['shipping_cost'], 2, ',', ' ') ?> &euro;</span>
                </div>

                <hr style="border:none;border-top:2px solid var(--creme-fonce);margin:1rem 0">

                <div style="display:flex;justify-content:space-between;font-size:1.2rem">
                    <strong>Total</strong>
                    <strong style="color:var(--orange-cidre)"><?= number_format((float) $order['total'], 2, ',', ' ') ?> &euro;</strong>
                </div>
            </div>
        </div>

        <!-- Adresse de livraison -->
        <div class="card" style="margin-bottom:2rem">
            <div class="card-body" style="padding:1.5rem">
                <h3 style="margin-bottom:1rem"><?= icon('map-pin', 20) ?> Adresse de livraison</h3>
                <p>
                    <?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?><br>
                    <?= e($order['shipping_address']) ?><br>
                    <?= e($order['shipping_postal_code'] . ' ' . $order['shipping_city']) ?>
                </p>
                <?php if ($order['customer_email']): ?>
                    <p style="margin-top:.5rem">
                        <?= icon('mail', 16) ?> <?= e($order['customer_email']) ?>
                    </p>
                <?php endif; ?>
                <?php if ($order['customer_phone']): ?>
                    <p style="margin-top:.25rem">
                        <?= icon('phone', 16) ?> <?= e($order['customer_phone']) ?>
                    </p>
                <?php endif; ?>
            </div>
        </div>

        <!-- Actions -->
        <div style="text-align:center;margin-top:2rem">
            <p style="color:var(--brun);margin-bottom:1.5rem">
                Un email de confirmation sera envoyé à <strong><?= e($order['customer_email']) ?></strong>.
            </p>
            <a href="/boutique" class="btn btn-primary">
                <?= icon('arrow-left', 18) ?> Retour à la boutique
            </a>
        </div>

    </div>
</section>
