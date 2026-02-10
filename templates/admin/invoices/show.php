<?php
/**
 * Détail d'une facture — aperçu facturation.
 * Variables : $invoice, $items, $billing, $statusMap, $statusIcons
 */

$st = $invoice['status'] ?? 'pending';
$stInfo = $statusMap[$st] ?? ['Inconnu', 'pending'];
$stIcon = $statusIcons[$st] ?? 'circle';

$assocName = $billing['association_name'] ?? 'Association la Fête du Cidre';
$assocAddress = $billing['address'] ?? '';
$assocSiret = $billing['siret'] ?? '';
$legalMentions = $billing['legal_mentions'] ?? '';
$tvaRate = $billing['tva_rate'] ?? '5,5%';
?>

<div style="max-width:800px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <a href="/admin/invoices" class="btn-icon" title="Retour" style="margin-right:0.5rem"><?= icon('arrow-left', 18) ?></a>
            <div class="page-icon" style="background:linear-gradient(135deg, var(--brun), #8B6B4A)"><?= icon('receipt', 22, '', 'white') ?></div>
            <div>
                <h1 style="margin:0">Facture <?= e($invoice['invoice_number']) ?></h1>
                <div style="font-size:0.78rem;color:var(--texte-leger);margin-top:2px">
                    Commande <a href="/admin/orders/<?= (int) $invoice['order_id'] ?>" style="color:var(--bleu)"><?= e($invoice['order_reference']) ?></a>
                    &middot; <span class="status <?= $stInfo[1] ?>" style="font-size:0.7rem"><?= icon($stIcon, 9) ?> <?= $stInfo[0] ?></span>
                </div>
            </div>
        </div>
    </div>

    <!-- INVOICE PREVIEW -->
    <div class="invoice-preview" style="margin-bottom:1.2rem">
        <!-- Header -->
        <div class="inv-header">
            <div class="inv-brand">
                <div class="inv-logo"><?= icon('receipt', 24, '', 'white') ?></div>
                <div class="inv-brand-text"><?= e($assocName) ?> <small>Association loi 1901</small></div>
            </div>
            <div class="inv-meta">
                <div class="inv-number"><?= e($invoice['invoice_number']) ?></div>
                <div class="inv-date">Émise le <?= date_fr($invoice['issued_at'], 'long') ?></div>
                <div style="margin-top:0.3rem">
                    <span class="status <?= $stInfo[1] ?>"><?= icon($stIcon, 8) ?> <?= $stInfo[0] ?></span>
                </div>
            </div>
        </div>

        <!-- Parties -->
        <div class="inv-parties">
            <div>
                <div class="inv-party-label">Émetteur</div>
                <div class="inv-party-name"><?= e($assocName) ?></div>
                <div class="inv-party-detail">
                    <?= nl2br(e($assocAddress)) ?>
                    <?php if ($assocSiret): ?><br>SIRET : <?= e($assocSiret) ?><?php endif; ?>
                </div>
            </div>
            <div>
                <div class="inv-party-label">Destinataire</div>
                <div class="inv-party-name"><?= e($invoice['customer_first_name'] . ' ' . $invoice['customer_last_name']) ?></div>
                <div class="inv-party-detail">
                    <?= e($invoice['shipping_address'] ?? '') ?><br>
                    <?= e(($invoice['shipping_postal_code'] ?? '') . ' ' . ($invoice['shipping_city'] ?? '')) ?><br>
                    <?= e($invoice['customer_email'] ?? '') ?>
                </div>
            </div>
        </div>

        <!-- Items table -->
        <table class="inv-table">
            <thead>
                <tr>
                    <th>Désignation</th>
                    <th>Qté</th>
                    <th>Prix unit.</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($items)): ?>
                    <tr><td colspan="4" style="text-align:center;color:var(--texte-leger);padding:1rem">Aucun article</td></tr>
                <?php else: ?>
                    <?php foreach ($items as $item): ?>
                        <tr>
                            <td><?= e($item['product_name']) ?></td>
                            <td><?= (int) $item['quantity'] ?></td>
                            <td><?= number_format((float) $item['unit_price'], 2, ',', ' ') ?> &euro;</td>
                            <td><?= number_format((float) $item['total_price'], 2, ',', ' ') ?> &euro;</td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>

        <!-- Totals -->
        <div class="inv-totals">
            <div class="inv-totals-inner">
                <div class="inv-total-row">
                    <span>Sous-total HT</span>
                    <span><?= number_format((float) $invoice['subtotal'], 2, ',', ' ') ?> &euro;</span>
                </div>
                <div class="inv-total-row">
                    <span>TVA (<?= e($tvaRate) ?>)</span>
                    <span><?= number_format((float) $invoice['tax_amount'], 2, ',', ' ') ?> &euro;</span>
                </div>
                <div class="inv-total-row grand">
                    <span>Total TTC</span>
                    <span><?= number_format((float) $invoice['total'], 2, ',', ' ') ?> &euro;</span>
                </div>
            </div>
        </div>

        <!-- Legal footer -->
        <?php if ($legalMentions): ?>
            <div class="inv-footer"><?= nl2br(e($legalMentions)) ?></div>
        <?php endif; ?>
    </div>

    <!-- ACTIONS FOOTER -->
    <div class="card" style="overflow:hidden">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:0.8rem 1.2rem">
            <div class="modal-footer-left">
                <button class="btn btn-secondary btn-sm"><?= icon('download', 14) ?> Télécharger PDF</button>
                <button class="btn btn-secondary btn-sm"><?= icon('send', 14) ?> Envoyer par e-mail</button>
            </div>
            <div class="modal-footer-right">
                <button class="btn btn-secondary btn-sm"><?= icon('copy', 14) ?> Dupliquer</button>
                <button class="btn btn-secondary btn-sm" onclick="window.print()"><?= icon('printer', 14) ?> Imprimer</button>
            </div>
        </div>
    </div>

</div>
