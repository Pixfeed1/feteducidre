<?php
/**
 * Détail d'une commande — administration.
 * Variables : $order, $items, $invoice
 */

$statusMap = [
    'pending'    => ['En attente', 'badge-warning'],
    'paid'       => ['Payée', 'badge-success'],
    'processing' => ['En traitement', 'badge-info'],
    'shipped'    => ['Expédiée', 'badge-info'],
    'delivered'  => ['Livrée', 'badge-success'],
    'cancelled'  => ['Annulée', 'badge-danger'],
    'refunded'   => ['Remboursée', 'badge-secondary'],
];
$s = $statusMap[$order['status']] ?? ['Inconnu', 'badge-secondary'];
?>

<div class="page-header">
    <h1><?= icon('shopping-cart', 24) ?> Commande <?= e($order['reference']) ?></h1>
    <a href="/admin/orders" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<div style="display:grid; grid-template-columns:2fr 1fr; gap:1.5rem; align-items:start;">
    <!-- Colonne principale -->
    <div>
        <!-- Articles -->
        <div class="card">
            <div class="card-header">
                <h2>Articles commandés</h2>
            </div>
            <div class="table-responsive">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Produit</th>
                            <th>SKU</th>
                            <th>Prix unitaire</th>
                            <th>Quantité</th>
                            <th class="text-right">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($items as $item): ?>
                            <tr>
                                <td><?= e($item['product_name']) ?></td>
                                <td class="text-muted"><?= e($item['product_sku'] ?? '-') ?></td>
                                <td><?= number_format((float) $item['unit_price'], 2, ',', ' ') ?> &euro;</td>
                                <td><?= (int) $item['quantity'] ?></td>
                                <td class="text-right"><?= number_format((float) $item['total_price'], 2, ',', ' ') ?> &euro;</td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="4" class="text-right"><strong>Sous-total</strong></td>
                            <td class="text-right"><?= number_format((float) $order['subtotal'], 2, ',', ' ') ?> &euro;</td>
                        </tr>
                        <tr>
                            <td colspan="4" class="text-right">Frais de port</td>
                            <td class="text-right"><?= number_format((float) $order['shipping_cost'], 2, ',', ' ') ?> &euro;</td>
                        </tr>
                        <tr>
                            <td colspan="4" class="text-right">TVA</td>
                            <td class="text-right"><?= number_format((float) $order['tax_amount'], 2, ',', ' ') ?> &euro;</td>
                        </tr>
                        <tr>
                            <td colspan="4" class="text-right"><strong>Total TTC</strong></td>
                            <td class="text-right"><strong><?= number_format((float) $order['total'], 2, ',', ' ') ?> &euro;</strong></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>

        <!-- Informations client -->
        <div class="card">
            <div class="card-header">
                <h2>Informations client</h2>
            </div>
            <div class="card-body">
                <div class="form-row">
                    <div>
                        <strong>Client</strong><br>
                        <?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?><br>
                        <?= e($order['customer_email']) ?><br>
                        <?= e($order['customer_phone'] ?? '') ?>
                    </div>
                    <div>
                        <strong>Adresse de livraison</strong><br>
                        <?= e($order['shipping_address'] ?? '') ?><br>
                        <?= e(($order['shipping_postal_code'] ?? '') . ' ' . ($order['shipping_city'] ?? '')) ?><br>
                        <?= e($order['shipping_country'] ?? 'France') ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Colonne latérale -->
    <div>
        <!-- Statut -->
        <div class="card">
            <div class="card-header">
                <h2>Statut</h2>
                <span class="badge <?= $s[1] ?>"><?= $s[0] ?></span>
            </div>
            <div class="card-body">
                <form method="post" action="/admin/orders/<?= (int) $order['id'] ?>/status">
                    <?= csrf_field() ?>
                    <div class="form-group">
                        <label for="status">Changer le statut</label>
                        <select name="status" id="status" class="form-control">
                            <?php foreach ($statusMap as $key => [$label, $class]): ?>
                                <option value="<?= $key ?>" <?= $order['status'] === $key ? 'selected' : '' ?>>
                                    <?= $label ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="tracking_number">N° de suivi</label>
                        <input type="text" name="tracking_number" id="tracking_number" class="form-control"
                               value="<?= e($order['tracking_number'] ?? '') ?>">
                    </div>
                    <div class="form-group">
                        <label for="tracking_carrier">Transporteur</label>
                        <input type="text" name="tracking_carrier" id="tracking_carrier" class="form-control"
                               value="<?= e($order['tracking_carrier'] ?? '') ?>">
                    </div>
                    <div class="form-group">
                        <label for="admin_notes">Notes internes</label>
                        <textarea name="admin_notes" id="admin_notes" class="form-control" rows="3"><?= e($order['admin_notes'] ?? '') ?></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%;">
                        <?= icon('save', 18) ?> Mettre à jour
                    </button>
                </form>
            </div>
        </div>

        <!-- Informations -->
        <div class="card">
            <div class="card-header">
                <h2>Informations</h2>
            </div>
            <div class="card-body">
                <p><strong>Date :</strong> <?= date_fr($order['created_at'], 'datetime') ?></p>
                <p><strong>Paiement :</strong> <?= e($order['payment_method'] ?? 'N/A') ?></p>
                <?php if (!empty($order['payment_id'])): ?>
                    <p><strong>ID paiement :</strong> <?= e($order['payment_id']) ?></p>
                <?php endif; ?>
                <?php if ($invoice): ?>
                    <p>
                        <strong>Facture :</strong>
                        <a href="/admin/invoices/<?= (int) $invoice['id'] ?>"><?= e($invoice['invoice_number']) ?></a>
                    </p>
                <?php else: ?>
                    <form method="post" action="/admin/invoices/<?= (int) $order['id'] ?>/generate" class="mt-1">
                        <?= csrf_field() ?>
                        <button type="submit" class="btn btn-sm btn-secondary">
                            <?= icon('printer', 16) ?> Générer la facture
                        </button>
                    </form>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>
