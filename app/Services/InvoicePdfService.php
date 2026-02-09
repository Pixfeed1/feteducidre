<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;
use App\Core\Database;

/**
 * Service de génération de factures PDF.
 * Génère un PDF basique en HTML converti via navigateur headless ou bibliothèque.
 * En fallback : génère un HTML imprimable avec @media print optimisé.
 */
class InvoicePdfService
{
    private Database $db;

    public function __construct()
    {
        $this->db = Database::getInstance();
    }

    /**
     * Génère une facture pour une commande
     *
     * @return array Données de la facture créée
     */
    public function generate(int $orderId): array
    {
        // Récupérer la commande
        $order = $this->db->fetch(
            "SELECT id, reference, customer_first_name, customer_last_name, customer_email,
                    shipping_address, shipping_city, shipping_postal_code,
                    subtotal, shipping_cost, tax_amount, total, created_at
             FROM orders WHERE id = ?",
            [$orderId]
        );

        if (!$order) {
            throw new \RuntimeException("Commande #{$orderId} introuvable");
        }

        // Récupérer les items
        $items = $this->db->fetchAll(
            "SELECT product_name, product_sku, quantity, unit_price, total_price
             FROM order_items WHERE order_id = ?",
            [$orderId]
        );

        // Générer le numéro de facture
        $invoiceNumber = $this->generateInvoiceNumber();

        // Paramètres asso
        $settings = [];
        $rows = $this->db->fetchAll("SELECT `key`, value FROM settings WHERE `group` = 'general'");
        foreach ($rows as $row) {
            $settings[$row['key']] = $row['value'];
        }

        // Générer le HTML
        $html = $this->renderInvoiceHtml($order, $items, $invoiceNumber, $settings);

        // Sauvegarder le fichier HTML (imprimable en PDF)
        $filename = "FAC-{$invoiceNumber}.html";
        $filepath = dirname(__DIR__, 2) . '/storage/invoices/' . $filename;

        $dir = dirname($filepath);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        file_put_contents($filepath, $html);

        // Enregistrer en DB
        $invoiceId = $this->db->insert('invoices', [
            'order_id'       => $orderId,
            'invoice_number' => $invoiceNumber,
            'filename'       => $filename,
            'subtotal'       => $order['subtotal'],
            'tax_amount'     => $order['tax_amount'],
            'total'          => $order['total'],
        ]);

        return [
            'id'       => $invoiceId,
            'number'   => $invoiceNumber,
            'filename' => $filename,
            'path'     => $filepath,
        ];
    }

    /**
     * Génère un numéro de facture unique
     */
    private function generateInvoiceNumber(): string
    {
        $year = date('Y');
        $last = $this->db->fetch(
            "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
            ["{$year}-%"]
        );

        if ($last) {
            $num = (int) substr($last['invoice_number'], -3) + 1;
        } else {
            $num = 1;
        }

        return sprintf('%s-%03d', $year, $num);
    }

    /**
     * Rend le HTML de la facture (imprimable)
     */
    private function renderInvoiceHtml(array $order, array $items, string $invoiceNumber, array $settings): string
    {
        $assoName = $settings['association_name'] ?? 'Association Fête du Cidre';
        $assoAddress = $settings['association_address'] ?? 'L\'Hôtellerie de Flée, 49500';
        $assoEmail = $settings['association_email'] ?? 'contact@fetecidre.fr';
        $customerName = htmlspecialchars($order['customer_first_name'] . ' ' . $order['customer_last_name']);

        ob_start();
        ?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Facture <?= htmlspecialchars($invoiceNumber) ?></title>
<style>
    @page { margin: 2cm; }
    body { font-family: -apple-system, sans-serif; color: #2A2318; font-size: 14px; line-height: 1.5; }
    .header { display: flex; justify-content: space-between; margin-bottom: 40px; }
    .header h1 { color: #2C4A2E; font-size: 28px; margin: 0; }
    .header .badge { background: #2C4A2E; color: #fff; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; }
    .info { display: flex; justify-content: space-between; margin-bottom: 30px; }
    .info-block h3 { color: #2C4A2E; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 8px; }
    .info-block p { margin: 2px 0; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #2C4A2E; color: #fff; padding: 10px; text-align: left; font-size: 12px; text-transform: uppercase; }
    td { padding: 10px; border-bottom: 1px solid #F0E8D8; }
    .text-right { text-align: right; }
    .totals { margin-top: 20px; }
    .totals tr td { border: none; padding: 4px 10px; }
    .totals .total-row { font-size: 18px; font-weight: 700; color: #2C4A2E; }
    .footer { margin-top: 60px; text-align: center; font-size: 12px; color: #5C3D2E; border-top: 1px solid #F0E8D8; padding-top: 15px; }
</style>
</head>
<body>
<div class="header">
    <div>
        <h1><?= htmlspecialchars($assoName) ?></h1>
        <p style="color:#5C3D2E"><?= htmlspecialchars($assoAddress) ?></p>
    </div>
    <div style="text-align:right">
        <span class="badge">FACTURE</span>
        <p style="margin-top:8px;font-size:18px;font-weight:700">N° FAC-<?= htmlspecialchars($invoiceNumber) ?></p>
        <p style="color:#5C3D2E">Date : <?= date('d/m/Y', strtotime($order['created_at'])) ?></p>
    </div>
</div>

<div class="info">
    <div class="info-block">
        <h3>Émetteur</h3>
        <p><strong><?= htmlspecialchars($assoName) ?></strong></p>
        <p><?= htmlspecialchars($assoAddress) ?></p>
        <p><?= htmlspecialchars($assoEmail) ?></p>
    </div>
    <div class="info-block" style="text-align:right">
        <h3>Client</h3>
        <p><strong><?= $customerName ?></strong></p>
        <p><?= htmlspecialchars($order['shipping_address'] ?? '') ?></p>
        <p><?= htmlspecialchars(($order['shipping_postal_code'] ?? '') . ' ' . ($order['shipping_city'] ?? '')) ?></p>
        <p><?= htmlspecialchars($order['customer_email']) ?></p>
    </div>
</div>

<p>Commande : <strong><?= htmlspecialchars($order['reference']) ?></strong></p>

<table>
    <thead>
        <tr>
            <th>Produit</th>
            <th>Réf.</th>
            <th class="text-right">P.U. HT</th>
            <th class="text-right">Qté</th>
            <th class="text-right">Total HT</th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($items as $item): ?>
        <tr>
            <td><?= htmlspecialchars($item['product_name']) ?></td>
            <td><?= htmlspecialchars($item['product_sku'] ?? '—') ?></td>
            <td class="text-right"><?= number_format((float)$item['unit_price'], 2, ',', ' ') ?> €</td>
            <td class="text-right"><?= (int)$item['quantity'] ?></td>
            <td class="text-right"><?= number_format((float)$item['total_price'], 2, ',', ' ') ?> €</td>
        </tr>
        <?php endforeach; ?>
    </tbody>
</table>

<table class="totals" style="width:300px;margin-left:auto">
    <tr>
        <td>Sous-total HT</td>
        <td class="text-right"><?= number_format((float)$order['subtotal'], 2, ',', ' ') ?> €</td>
    </tr>
    <tr>
        <td>Frais de port</td>
        <td class="text-right"><?= number_format((float)$order['shipping_cost'], 2, ',', ' ') ?> €</td>
    </tr>
    <tr>
        <td>TVA (20%)</td>
        <td class="text-right"><?= number_format((float)$order['tax_amount'], 2, ',', ' ') ?> €</td>
    </tr>
    <tr class="total-row">
        <td><strong>Total TTC</strong></td>
        <td class="text-right"><strong><?= number_format((float)$order['total'], 2, ',', ' ') ?> €</strong></td>
    </tr>
</table>

<div class="footer">
    <p><?= htmlspecialchars($assoName) ?> — Association loi 1901</p>
    <p><?= htmlspecialchars($assoAddress) ?> — <?= htmlspecialchars($assoEmail) ?></p>
</div>
</body>
</html>
        <?php
        return ob_get_clean();
    }
}
