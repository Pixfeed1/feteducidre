<?php
/**
 * Détail d'une commande — administration.
 * Variables : $order, $items, $invoice, $statusMap, $paymentMap
 */

$statusIcons = [
    'pending'    => 'clock',
    'paid'       => 'check-circle',
    'processing' => 'loader',
    'shipped'    => 'truck',
    'delivered'  => 'check-circle',
    'cancelled'  => 'x-circle',
    'refunded'   => 'rotate-ccw',
];

$st = $order['status'];
$stInfo = $statusMap[$st] ?? ['Inconnu', 'pending'];
$displayStatus = in_array($st, ['pending', 'paid']) ? 'new' : $st;
$displayLabel = $displayStatus === 'new' ? 'Nouvelle' : $stInfo[0];

// Payment status
$payStatus = $order['payment_status'] ?? ($st === 'paid' || $st === 'delivered' || $st === 'shipped' ? 'paid' : ($st === 'refunded' ? 'refunded' : 'pending'));
$payInfo = $paymentMap[$payStatus] ?? ['En attente', 'pending'];

// Timeline steps
$timelineSteps = [
    'pending'    => ['Commande reçue', 'clock'],
    'paid'       => ['Paiement confirmé', 'credit-card'],
    'processing' => ['En préparation', 'loader'],
    'shipped'    => ['Expédiée', 'truck'],
    'delivered'  => ['Livrée', 'check-circle'],
];
$statusOrder = ['pending', 'paid', 'processing', 'shipped', 'delivered'];
$currentIdx = array_search($st, $statusOrder);
if ($currentIdx === false) $currentIdx = -1;

$initials = mb_strtoupper(mb_substr($order['customer_first_name'] ?? '', 0, 1) . mb_substr($order['customer_last_name'] ?? '', 0, 1));
?>

<div style="max-width:900px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <a href="/admin/orders" class="btn-icon" title="Retour" style="margin-right:0.5rem"><?= icon('arrow-left', 18) ?></a>
            <div class="page-icon" style="background:linear-gradient(135deg, var(--orange-cidre), #E8A66A)"><?= icon('shopping-bag', 22, '', 'white') ?></div>
            <div>
                <h1 style="margin:0">Commande <?= e($order['reference']) ?></h1>
                <div style="font-size:0.78rem;color:var(--texte-leger);margin-top:2px">
                    <?= date_fr($order['created_at'], 'datetime') ?> &middot;
                    <span class="status <?= $displayStatus ?>" style="font-size:0.7rem"><?= icon($statusIcons[$st] ?? 'circle', 9) ?> <?= $displayLabel ?></span>
                </div>
            </div>
        </div>
    </div>

    <form method="post" action="/admin/orders/<?= (int) $order['id'] ?>/status">
        <?= csrf_field() ?>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;align-items:start">

            <!-- LEFT COLUMN -->
            <div style="display:flex;flex-direction:column;gap:1.2rem">

                <!-- Client -->
                <div class="card" style="overflow:hidden">
                    <div class="detail-section">
                        <div class="detail-section-title"><?= icon('user', 12) ?> Client</div>
                        <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.8rem">
                            <div class="td-avatar" style="background:var(--orange-cidre);width:40px;height:40px;font-size:0.85rem"><?= $initials ?></div>
                            <div>
                                <div style="font-weight:700;font-size:0.95rem"><?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?></div>
                                <div style="font-size:0.78rem;color:var(--texte-leger)"><?= e($order['customer_email']) ?></div>
                            </div>
                        </div>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">Téléphone</span>
                                <span class="detail-value"><?= e($order['customer_phone'] ?? '—') ?></span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Méthode de paiement</span>
                                <span class="detail-value"><?= e(ucfirst($order['payment_method'] ?? '—')) ?></span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Adresse de livraison -->
                <div class="card" style="overflow:hidden">
                    <div class="detail-section">
                        <div class="detail-section-title"><?= icon('map-pin', 12) ?> Adresse de livraison</div>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">Adresse</span>
                                <span class="detail-value"><?= e($order['shipping_address'] ?? '—') ?></span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Ville</span>
                                <span class="detail-value"><?= e($order['shipping_city'] ?? '—') ?></span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Code postal</span>
                                <span class="detail-value"><?= e($order['shipping_postal_code'] ?? '—') ?></span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Pays</span>
                                <span class="detail-value"><?= e($order['shipping_country'] ?? 'France') ?></span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Articles commandés -->
                <div class="card" style="overflow:hidden">
                    <div class="detail-section">
                        <div class="detail-section-title"><?= icon('package', 12) ?> Articles commandés</div>
                        <div class="order-items">
                            <?php if (empty($items)): ?>
                                <div style="text-align:center;padding:1rem;color:var(--texte-leger);font-size:0.85rem">Aucun article</div>
                            <?php else: ?>
                                <?php foreach ($items as $item): ?>
                                    <div class="order-item">
                                        <div class="oi-img"><?= icon('package', 16, '', 'var(--texte-leger)') ?></div>
                                        <div class="oi-info">
                                            <div class="oi-name"><?= e($item['product_name']) ?></div>
                                            <div class="oi-detail"><?= e($item['product_sku'] ?? '') ?></div>
                                        </div>
                                        <div class="oi-qty">x<?= (int) $item['quantity'] ?></div>
                                        <div class="oi-price"><?= number_format((float) $item['total_price'], 2, ',', ' ') ?>&nbsp;&euro;</div>
                                    </div>
                                <?php endforeach; ?>
                            <?php endif; ?>
                        </div>

                        <!-- Summary -->
                        <div style="margin-top:1rem">
                            <div class="order-summary-row">
                                <span>Sous-total</span>
                                <span><?= number_format((float) $order['subtotal'], 2, ',', ' ') ?> &euro;</span>
                            </div>
                            <div class="order-summary-row">
                                <span>Frais de port</span>
                                <span><?= number_format((float) $order['shipping_cost'], 2, ',', ' ') ?> &euro;</span>
                            </div>
                            <div class="order-summary-row">
                                <span>TVA</span>
                                <span><?= number_format((float) $order['tax_amount'], 2, ',', ' ') ?> &euro;</span>
                            </div>
                            <div class="order-summary-row total">
                                <span>Total TTC</span>
                                <span class="os-val"><?= number_format((float) $order['total'], 2, ',', ' ') ?> &euro;</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <!-- RIGHT COLUMN -->
            <div style="display:flex;flex-direction:column;gap:1.2rem">

                <!-- Paiement -->
                <div class="card" style="overflow:hidden">
                    <div class="detail-section">
                        <div class="detail-section-title"><?= icon('credit-card', 12) ?> Paiement</div>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">Statut</span>
                                <span class="detail-value">
                                    <span class="pay-badge <?= $payInfo[1] ?>"><?= icon('credit-card', 10) ?> <?= $payInfo[0] ?></span>
                                </span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Méthode</span>
                                <span class="detail-value"><?= e(ucfirst($order['payment_method'] ?? '—')) ?></span>
                            </div>
                            <?php if (!empty($order['payment_id'])): ?>
                                <div class="detail-item" style="grid-column:1/-1">
                                    <span class="detail-label">ID Transaction</span>
                                    <span class="detail-value" style="font-size:0.78rem;font-family:monospace"><?= e($order['payment_id']) ?></span>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>

                <!-- Statut & Suivi -->
                <div class="card" style="overflow:hidden">
                    <div class="detail-section">
                        <div class="detail-section-title"><?= icon('truck', 12) ?> Statut &amp; Suivi</div>
                        <div class="status-select">
                            <?php foreach ($statusMap as $key => [$label, $class]): ?>
                                <button type="button"
                                        class="status-option s-<?= $key ?> <?= $st === $key ? 'active' : '' ?>"
                                        onclick="document.getElementById('statusInput').value='<?= $key ?>';document.querySelectorAll('.status-option').forEach(b=>b.classList.remove('active'));this.classList.add('active')">
                                    <?= $label ?>
                                </button>
                            <?php endforeach; ?>
                        </div>
                        <input type="hidden" name="status" id="statusInput" value="<?= e($st) ?>">

                        <div class="tracking-input">
                            <input type="text" name="tracking_carrier" value="<?= e($order['tracking_carrier'] ?? '') ?>" placeholder="Transporteur">
                            <input type="text" name="tracking_number" value="<?= e($order['tracking_number'] ?? '') ?>" placeholder="N° de suivi">
                        </div>
                    </div>
                </div>

                <!-- Notes -->
                <div class="card" style="overflow:hidden">
                    <div class="detail-section">
                        <div class="detail-section-title"><?= icon('message-square', 12) ?> Notes internes</div>
                        <textarea name="admin_notes" class="form-control" rows="3" placeholder="Ajouter une note interne…"><?= e($order['admin_notes'] ?? '') ?></textarea>
                    </div>
                </div>

                <!-- Timeline -->
                <?php if (!in_array($st, ['cancelled', 'refunded'])): ?>
                    <div class="card" style="overflow:hidden">
                        <div class="detail-section">
                            <div class="detail-section-title"><?= icon('clock', 12) ?> Historique</div>
                            <div class="timeline">
                                <?php foreach ($timelineSteps as $stepKey => [$stepLabel, $stepIcon]):
                                    $stepIdx = array_search($stepKey, $statusOrder);
                                    if ($stepIdx < $currentIdx) {
                                        $tlClass = 'done';
                                    } elseif ($stepIdx === $currentIdx) {
                                        $tlClass = 'current';
                                    } else {
                                        $tlClass = '';
                                    }
                                ?>
                                    <div class="tl-item <?= $tlClass ?>">
                                        <div class="tl-dot"><?= icon($stepIcon, 10, '', $tlClass ? 'white' : 'var(--texte-leger)') ?></div>
                                        <div>
                                            <div class="tl-text"><?= $stepLabel ?></div>
                                            <?php if ($tlClass === 'current'): ?>
                                                <div class="tl-date"><?= date_fr($order['updated_at'] ?? $order['created_at'], 'datetime') ?></div>
                                            <?php elseif ($tlClass === 'done'): ?>
                                                <div class="tl-date">Terminé</div>
                                            <?php endif; ?>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>
                <?php endif; ?>

            </div>

        </div>

        <!-- FOOTER ACTIONS -->
        <div class="card" style="margin-top:1.2rem;overflow:hidden">
            <div style="display:flex;align-items:center;justify-content:space-between;padding:0.8rem 1.2rem">
                <div class="modal-footer-left">
                    <?php if ($invoice): ?>
                        <a href="/admin/invoices/<?= (int) $invoice['id'] ?>" class="btn btn-secondary btn-sm">
                            <?= icon('printer', 14) ?> Facture <?= e($invoice['invoice_number'] ?? '') ?>
                        </a>
                    <?php else: ?>
                        <span style="font-size:0.78rem;color:var(--texte-leger)"><?= icon('printer', 12) ?> Pas de facture</span>
                    <?php endif; ?>
                </div>
                <div class="modal-footer-right">
                    <a href="/admin/orders" class="btn btn-secondary btn-sm"><?= icon('arrow-left', 14) ?> Retour</a>
                    <button type="submit" class="btn btn-primary btn-sm"><?= icon('save', 14) ?> Enregistrer</button>
                </div>
            </div>
        </div>

    </form>

</div>
