<?php
/**
 * Template facture PDF — Fête du Cidre
 * Rendu par InvoicePdfService::renderTemplate() via Dompdf.
 *
 * Variables :
 *   $invoice      — ['id', 'number', 'date', 'due_date', 'status']
 *   $order        — ['id', 'reference', 'date', 'payment_method', 'payment_id', 'carrier', 'tracking']
 *   $customer     — ['name', 'email', 'address', 'city', 'country']
 *   $items        — [['product_name', 'product_description', 'quantity', 'unit_price', 'total_price'], ...]
 *   $totals       — ['subtotal', 'shipping', 'tax', 'total']
 *   $association  — ['name', 'address', 'city', 'email', 'phone', 'siret', 'rna', 'ape', 'site_url']
 */

use App\Services\InvoicePdfService as Fmt;

$status = Fmt::formatStatus($invoice['status']);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
@page {
    size: A4 portrait;
    margin: 0;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9pt;
    color: #2A2318;
    line-height: 1.4;
}

.page {
    width: 210mm;
    min-height: 297mm;
    position: relative;
}

/* ───── TOP LINES ───── */
.top-line {
    height: 3px;
    background-color: #2C4A2E;
    width: 100%;
}
.top-line-orange {
    height: 1.5px;
    background-color: #D4833B;
    width: 100%;
}

/* ───── HEADER ───── */
.header {
    padding: 14mm 22mm 0 22mm;
}
.header-table { width: 100%; }
.header-table td { vertical-align: top; }

.logo-box {
    width: 12mm;
    height: 12mm;
    background-color: #2C4A2E;
    border-radius: 3mm;
    text-align: center;
    display: inline-block;
    vertical-align: middle;
}

.org-name {
    font-size: 15pt;
    font-weight: bold;
    color: #2C4A2E;
    vertical-align: middle;
    padding-left: 4mm;
}
.org-subtitle {
    font-size: 7.5pt;
    color: #6B5D4F;
    padding-left: 4mm;
}

.invoice-label {
    font-size: 7pt;
    color: #6B5D4F;
    text-align: right;
    letter-spacing: 1px;
}
.invoice-number {
    font-size: 18pt;
    font-weight: bold;
    color: #2C4A2E;
    text-align: right;
}

/* ───── SEPARATOR ───── */
.separator {
    border: none;
    border-top: 0.8px solid #F0E8D8;
    margin: 4mm 22mm;
}

/* ───── INFO ROW ───── */
.info-row {
    padding: 0 22mm;
    margin-bottom: 5mm;
}
.info-row table { width: 100%; }
.info-row td { vertical-align: top; }

.info-label {
    font-size: 6.5pt;
    color: #6B5D4F;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1mm;
}
.info-value {
    font-size: 9pt;
    font-weight: bold;
    color: #2A2318;
}

/* Badges statut */
.badge-paid {
    display: inline-block;
    background-color: #2C4A2E;
    color: white;
    font-size: 7.5pt;
    font-weight: bold;
    padding: 2px 12px;
    border-radius: 10px;
    letter-spacing: 0.5px;
}
.badge-pending {
    display: inline-block;
    background-color: #D4833B;
    color: white;
    font-size: 7.5pt;
    font-weight: bold;
    padding: 2px 12px;
    border-radius: 10px;
    letter-spacing: 0.5px;
}
.badge-overdue {
    display: inline-block;
    background-color: #DC2626;
    color: white;
    font-size: 7.5pt;
    font-weight: bold;
    padding: 2px 12px;
    border-radius: 10px;
}
.badge-refunded {
    display: inline-block;
    background-color: #6B5D4F;
    color: white;
    font-size: 7.5pt;
    font-weight: bold;
    padding: 2px 12px;
    border-radius: 10px;
}

/* ───── PARTIES (ÉMETTEUR / DESTINATAIRE) ───── */
.parties {
    padding: 0 22mm;
    margin-bottom: 8mm;
}
.parties table { width: 100%; }
.parties td { vertical-align: top; width: 50%; }

.party-label {
    font-size: 6.5pt;
    font-weight: bold;
    color: #2C4A2E;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.party-underline {
    display: inline-block;
    width: 8mm;
    height: 2px;
    background-color: #D4833B;
    margin-top: 1mm;
    margin-bottom: 3mm;
}
.party-underline-short {
    display: inline-block;
    width: 6mm;
    height: 2px;
    background-color: #D4833B;
    margin-top: 1mm;
    margin-bottom: 3mm;
}
.party-name {
    font-size: 9pt;
    font-weight: bold;
    color: #2A2318;
    margin-bottom: 1mm;
}
.party-detail {
    font-size: 8pt;
    color: #6B5D4F;
    line-height: 1.6;
}
.party-email {
    font-size: 8pt;
    color: #4A6B3E;
}

/* ───── TABLEAU DES ARTICLES ───── */
.items-section {
    padding: 0 22mm;
}

.items-table {
    width: 100%;
    border-collapse: collapse;
    border: 0.8px solid #F0E8D8;
}

.items-table thead th {
    background-color: #2C4A2E;
    color: white;
    font-size: 6.5pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 3mm 4mm;
    text-align: left;
}
.items-table thead th.c { text-align: center; }
.items-table thead th.r { text-align: right; }

.items-table tbody td {
    padding: 3.5mm 4mm;
    font-size: 8.5pt;
    vertical-align: middle;
}
.items-table tbody tr:nth-child(odd) td { background-color: #FAF5EC; }
.items-table tbody tr:nth-child(even) td { background-color: #FFFDF8; }

.item-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 2mm;
    vertical-align: middle;
}
.dot-green { background-color: #7A9E6B; }
.dot-orange { background-color: #E8A95B; }

.item-name {
    font-weight: bold;
    color: #2A2318;
    font-size: 8.5pt;
}
.item-desc {
    font-size: 7pt;
    color: #6B5D4F;
    margin-top: 0.5mm;
}
.td-c { text-align: center; }
.td-r { text-align: right; }
.td-r-b { text-align: right; font-weight: bold; }

/* ───── BOTTOM SECTION (PAIEMENT + TOTAUX) ───── */
.bottom-section {
    padding: 4mm 22mm 0 22mm;
}
.bottom-table { width: 100%; }
.bottom-table > tbody > tr > td { vertical-align: top; }

.pay-label {
    font-size: 6.5pt;
    font-weight: bold;
    color: #2C4A2E;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.pay-underline {
    display: inline-block;
    width: 16mm;
    height: 2px;
    background-color: #D4833B;
    margin-top: 1mm;
    margin-bottom: 3mm;
}
.pay-row-label {
    font-size: 7pt;
    color: #6B5D4F;
    width: 20mm;
    padding: 1mm 0;
}
.pay-row-value {
    font-size: 7.5pt;
    font-weight: bold;
    color: #2A2318;
    padding: 1mm 0;
}

.totals-table {
    width: 68mm;
    margin-left: auto;
}
.totals-table td {
    padding: 1.5mm 0;
    font-size: 8pt;
}
.totals-label { color: #6B5D4F; }
.totals-value { text-align: right; }
.totals-value-bold { text-align: right; font-weight: bold; }

.totals-sep td {
    border-bottom: 1px solid #F0E8D8;
    padding-bottom: 3mm;
}

.total-grand-box {
    background-color: #2C4A2E;
    border-radius: 3px;
    padding: 3mm 4mm;
    margin-top: 2mm;
}
.total-grand-box table { width: 100%; }
.total-grand-label {
    color: white;
    font-size: 9pt;
    font-weight: bold;
}
.total-grand-value {
    color: white;
    font-size: 13pt;
    font-weight: bold;
    text-align: right;
}

/* ───── MENTIONS LÉGALES ───── */
.legal {
    padding: 0 22mm;
    margin-top: 5mm;
    border-top: 0.5px solid #F0E8D8;
    padding-top: 3mm;
}
.legal p {
    font-size: 6.5pt;
    color: #6B5D4F;
    line-height: 1.5;
}

/* ───── FOOTER ───── */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
}
.footer-orange-line {
    height: 1px;
    background-color: #D4833B;
}
.footer-band {
    background-color: #2C4A2E;
    padding: 3mm 22mm;
    text-align: center;
}
.footer-text {
    font-size: 6pt;
    color: #C8D8C0;
}
.footer-thanks {
    font-size: 5.5pt;
    font-weight: bold;
    color: #E8A95B;
    margin-top: 1mm;
}
</style>
</head>
<body>

<div class="page">

    <!-- TOP LINES -->
    <div class="top-line"></div>
    <div class="top-line-orange"></div>

    <!-- HEADER -->
    <div class="header">
        <table class="header-table">
            <tr>
                <td style="width:65%">
                    <table><tr>
                        <td style="width:14mm; vertical-align:middle">
                            <div class="logo-box">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-top:2mm">
                                    <circle cx="12" cy="13" r="7" fill="#7A9E6B"/>
                                    <circle cx="12" cy="12.5" r="4.5" fill="#A3C48E"/>
                                    <path d="M12 6c-.5-2 .5-3 1.5-1.5" stroke="#D4C4A0" stroke-width="1" fill="none" stroke-linecap="round"/>
                                </svg>
                            </div>
                        </td>
                        <td style="vertical-align:middle">
                            <div class="org-name"><?= htmlspecialchars($association['name']) ?></div>
                            <div class="org-subtitle"><?= htmlspecialchars($association['address']) ?> · Association loi 1901</div>
                        </td>
                    </tr></table>
                </td>
                <td style="width:35%">
                    <div class="invoice-label">FACTURE</div>
                    <div class="invoice-number"><?= htmlspecialchars($invoice['number']) ?></div>
                </td>
            </tr>
        </table>
    </div>

    <hr class="separator">

    <!-- INFO ROW -->
    <div class="info-row">
        <table>
            <tr>
                <td style="width:25%">
                    <div class="info-label">Date d'émission</div>
                    <div class="info-value"><?= Fmt::formatDate($invoice['date']) ?></div>
                </td>
                <td style="width:25%">
                    <div class="info-label">Échéance</div>
                    <div class="info-value"><?= isset($invoice['due_date']) ? Fmt::formatDate($invoice['due_date']) : '—' ?></div>
                </td>
                <td style="width:25%">
                    <div class="info-label">Commande</div>
                    <div class="info-value"><?= htmlspecialchars($order['reference']) ?></div>
                </td>
                <td style="width:25%; text-align:right">
                    <span class="badge-<?= $status['class'] ?>"><?= $status['label'] ?></span>
                </td>
            </tr>
        </table>
    </div>

    <!-- ÉMETTEUR / DESTINATAIRE -->
    <div class="parties">
        <table>
            <tr>
                <td>
                    <div class="party-label">DE</div>
                    <div class="party-underline"></div><br>
                    <div class="party-name"><?= htmlspecialchars($association['name']) ?></div>
                    <div class="party-detail">
                        <?= htmlspecialchars($association['address']) ?><br>
                        <?= htmlspecialchars($association['city']) ?><br>
                        <?php if (!empty($association['siret'])): ?>SIRET : <?= htmlspecialchars($association['siret']) ?><br><?php endif ?>
                        <?= htmlspecialchars($association['email']) ?>
                    </div>
                </td>
                <td>
                    <div class="party-label">À</div>
                    <div class="party-underline-short"></div><br>
                    <div class="party-name"><?= htmlspecialchars($customer['name']) ?></div>
                    <div class="party-detail">
                        <?= nl2br(htmlspecialchars($customer['address'])) ?><br>
                        <?= htmlspecialchars($customer['city']) ?><br>
                        <?= htmlspecialchars($customer['country'] ?? 'France') ?>
                    </div>
                    <div class="party-email"><?= htmlspecialchars($customer['email']) ?></div>
                </td>
            </tr>
        </table>
    </div>

    <!-- TABLEAU DES ARTICLES -->
    <div class="items-section">
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width:48%">Désignation</th>
                    <th class="c" style="width:12%">Qté</th>
                    <th class="c" style="width:18%">Prix unit.</th>
                    <th class="r" style="width:22%">Total</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($items as $i => $item): ?>
                <tr>
                    <td>
                        <span class="item-dot <?= $i % 2 === 0 ? 'dot-green' : 'dot-orange' ?>"></span>
                        <span class="item-name"><?= htmlspecialchars($item['product_name']) ?></span>
                        <?php if (!empty($item['product_description'])): ?>
                            <div class="item-desc" style="padding-left:5mm"><?= htmlspecialchars(mb_strimwidth($item['product_description'], 0, 60, '…')) ?></div>
                        <?php endif ?>
                    </td>
                    <td class="td-c"><?= (int) $item['quantity'] ?></td>
                    <td class="td-c"><?= Fmt::formatPrice((float) $item['unit_price']) ?></td>
                    <td class="td-r-b"><?= Fmt::formatPrice((float) $item['total_price']) ?></td>
                </tr>
                <?php endforeach ?>
            </tbody>
        </table>
    </div>

    <!-- PAIEMENT + TOTAUX -->
    <div class="bottom-section">
        <table class="bottom-table">
            <tr>
                <!-- Paiement (gauche) -->
                <td style="width:50%">
                    <div class="pay-label">Paiement</div>
                    <div class="pay-underline"></div>
                    <table>
                        <tr>
                            <td class="pay-row-label">Méthode</td>
                            <td class="pay-row-value"><?= Fmt::formatPaymentMethod($order['payment_method']) ?></td>
                        </tr>
                        <tr>
                            <td class="pay-row-label">Statut</td>
                            <td class="pay-row-value">
                                <?php if ($invoice['status'] === 'paid'): ?>
                                    Payé le <?= Fmt::formatDate($order['date']) ?>
                                <?php else: ?>
                                    <?= $status['label'] ?>
                                <?php endif ?>
                            </td>
                        </tr>
                        <?php if (!empty($order['payment_id'])): ?>
                        <tr>
                            <td class="pay-row-label">Transaction</td>
                            <td class="pay-row-value"><?= htmlspecialchars(mb_strimwidth($order['payment_id'], 0, 24, '…')) ?></td>
                        </tr>
                        <?php endif ?>
                    </table>
                </td>

                <!-- Totaux (droite) -->
                <td style="width:50%">
                    <table class="totals-table">
                        <tr>
                            <td class="totals-label">Sous-total HT</td>
                            <td class="totals-value-bold"><?= Fmt::formatPrice($totals['subtotal']) ?></td>
                        </tr>
                        <tr class="totals-sep">
                            <td class="totals-label">Livraison<?php if (!empty($order['carrier'])): ?> (<?= htmlspecialchars($order['carrier']) ?>)<?php endif ?></td>
                            <td class="totals-value-bold"><?= $totals['shipping'] > 0 ? Fmt::formatPrice($totals['shipping']) : 'Offerts' ?></td>
                        </tr>
                        <tr>
                            <td class="totals-label">TVA</td>
                            <td class="totals-value" style="font-style:italic"><?= $totals['tax'] > 0 ? Fmt::formatPrice($totals['tax']) : 'Non applicable (art. 293B)' ?></td>
                        </tr>
                    </table>

                    <div class="total-grand-box">
                        <table>
                            <tr>
                                <td class="total-grand-label">TOTAL TTC</td>
                                <td class="total-grand-value"><?= Fmt::formatPrice($totals['total']) ?></td>
                            </tr>
                        </table>
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <!-- MENTIONS LÉGALES -->
    <div class="legal">
        <p>
            Association loi 1901<?php if (!empty($association['rna'])): ?> — N° RNA <?= htmlspecialchars($association['rna']) ?><?php endif ?> — Non assujetti à la TVA (article 293B du Code Général des Impôts).<br>
            En cas de retard de paiement, pénalité de 3× le taux d'intérêt légal + indemnité forfaitaire de 40 € pour frais de recouvrement.<br>
            Pas d'escompte pour paiement anticipé. Délai de paiement : 30 jours à compter de la date d'émission de la facture.
        </p>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <div class="footer-orange-line"></div>
        <div class="footer-band">
            <div class="footer-text">
                <?= htmlspecialchars($association['name']) ?> · <?= htmlspecialchars($association['address']) ?>, <?= htmlspecialchars($association['city']) ?> · <?= htmlspecialchars($association['site_url'] ?? '') ?>
            </div>
            <div class="footer-thanks">Merci pour votre commande !</div>
        </div>
    </div>

</div>

</body>
</html>
