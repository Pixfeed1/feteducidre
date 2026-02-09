<?php
/**
 * Liste des factures — administration.
 * Variables : $invoices, $invoice (si détail), $items (si détail), $showDetail
 */

$showDetail = $showDetail ?? false;
?>

<div class="page-header">
    <h1><?= icon('printer', 24) ?> Factures</h1>
</div>

<?php if ($showDetail && !empty($invoice)): ?>
    <!-- Détail de la facture -->
    <div class="card">
        <div class="card-header">
            <h2>Facture <?= e($invoice['invoice_number']) ?></h2>
            <a href="/admin/invoices" class="btn btn-sm btn-secondary">
                <?= icon('arrow-left', 16) ?> Retour à la liste
            </a>
        </div>
        <div class="card-body">
            <div class="form-row">
                <div>
                    <p><strong>Commande :</strong> <a href="/admin/orders/<?= (int) $invoice['order_id'] ?>"><?= e($invoice['order_reference']) ?></a></p>
                    <p><strong>Date d'émission :</strong> <?= date_fr($invoice['issued_at']) ?></p>
                </div>
                <div>
                    <p><strong>Client :</strong> <?= e($invoice['customer_first_name'] . ' ' . $invoice['customer_last_name']) ?></p>
                    <p><strong>Email :</strong> <?= e($invoice['customer_email'] ?? '') ?></p>
                    <p><strong>Adresse :</strong> <?= e(($invoice['shipping_address'] ?? '') . ', ' . ($invoice['shipping_postal_code'] ?? '') . ' ' . ($invoice['shipping_city'] ?? '')) ?></p>
                </div>
            </div>
        </div>

        <?php if (!empty($items)): ?>
            <div class="table-responsive">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Désignation</th>
                            <th>Quantité</th>
                            <th>Prix unitaire</th>
                            <th class="text-right">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($items as $item): ?>
                            <tr>
                                <td><?= e($item['product_name']) ?></td>
                                <td><?= (int) $item['quantity'] ?></td>
                                <td><?= number_format((float) $item['unit_price'], 2, ',', ' ') ?> &euro;</td>
                                <td class="text-right"><?= number_format((float) $item['total_price'], 2, ',', ' ') ?> &euro;</td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="3" class="text-right"><strong>Sous-total HT</strong></td>
                            <td class="text-right"><?= number_format((float) $invoice['subtotal'], 2, ',', ' ') ?> &euro;</td>
                        </tr>
                        <tr>
                            <td colspan="3" class="text-right">TVA</td>
                            <td class="text-right"><?= number_format((float) $invoice['tax_amount'], 2, ',', ' ') ?> &euro;</td>
                        </tr>
                        <tr>
                            <td colspan="3" class="text-right"><strong>Total TTC</strong></td>
                            <td class="text-right"><strong><?= number_format((float) $invoice['total'], 2, ',', ' ') ?> &euro;</strong></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        <?php endif; ?>
    </div>

<?php else: ?>
    <!-- Liste des factures -->
    <div class="card">
        <?php if (empty($invoices)): ?>
            <div class="card-body">
                <div class="empty-state">
                    <?= icon('printer', 40) ?>
                    <p>Aucune facture pour le moment.</p>
                    <p class="text-muted">Les factures sont générées depuis les commandes.</p>
                </div>
            </div>
        <?php else: ?>
            <div class="table-responsive">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>N° Facture</th>
                            <th>Commande</th>
                            <th>Client</th>
                            <th>Total</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($invoices as $inv): ?>
                            <tr>
                                <td><strong><?= e($inv['invoice_number']) ?></strong></td>
                                <td>
                                    <a href="/admin/orders/<?= (int) $inv['order_id'] ?>"><?= e($inv['order_reference']) ?></a>
                                </td>
                                <td><?= e($inv['customer_first_name'] . ' ' . $inv['customer_last_name']) ?></td>
                                <td><?= number_format((float) $inv['total'], 2, ',', ' ') ?> &euro;</td>
                                <td class="text-muted"><?= date_fr($inv['issued_at'], 'short') ?></td>
                                <td>
                                    <a href="/admin/invoices/<?= (int) $inv['id'] ?>" class="btn btn-sm btn-secondary" title="Voir">
                                        <?= icon('eye', 16) ?>
                                    </a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
<?php endif; ?>
