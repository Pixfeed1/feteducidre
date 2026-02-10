<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;
use App\Core\Database;
use Dompdf\Dompdf;
use Dompdf\Options;

/**
 * Service de génération de factures PDF via Dompdf.
 * Gère la création, le rendu, le téléchargement et le stockage des factures.
 */
class InvoicePdfService
{
    private Database $db;

    public function __construct()
    {
        $this->db = Database::getInstance();
    }

    private static function storagePath(): string
    {
        return dirname(__DIR__, 2) . '/storage/invoices';
    }

    private static function templatePath(): string
    {
        return dirname(__DIR__, 2) . '/templates/pdf/invoice.php';
    }

    // ─── MÉTHODES PUBLIQUES ───

    /**
     * Génère le PDF et retourne le contenu binaire.
     */
    public static function generatePdf(int $invoiceId): string
    {
        $data = self::getInvoiceData($invoiceId);
        if (!$data) {
            throw new \RuntimeException("Facture #{$invoiceId} introuvable.");
        }

        $html = self::renderTemplate($data);

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isPhpEnabled', false);
        $options->set('isRemoteEnabled', false);
        $options->set('defaultFont', 'Helvetica');
        $options->set('isFontSubsettingEnabled', true);
        $options->set('chroot', dirname(__DIR__, 2));

        $dompdf = new Dompdf($options);
        $dompdf->loadHtml($html);
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();

        $dompdf->addInfo('Title', "Facture {$data['invoice']['number']}");
        $dompdf->addInfo('Author', $data['association']['name']);
        $dompdf->addInfo('Creator', 'CMS Fête du Cidre');

        return $dompdf->output();
    }

    /**
     * Téléchargement navigateur (Content-Disposition: attachment).
     */
    public static function download(int $invoiceId): void
    {
        $data = self::getInvoiceData($invoiceId);
        if (!$data) {
            throw new \RuntimeException("Facture #{$invoiceId} introuvable.");
        }

        $pdf = self::generatePdf($invoiceId);
        $filename = $data['invoice']['number'] . '.pdf';

        header('Content-Type: application/pdf');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . strlen($pdf));
        header('Cache-Control: private, max-age=0, must-revalidate');
        echo $pdf;
        exit;
    }

    /**
     * Affichage inline dans le navigateur (aperçu).
     */
    public static function stream(int $invoiceId): void
    {
        $data = self::getInvoiceData($invoiceId);
        if (!$data) {
            throw new \RuntimeException("Facture #{$invoiceId} introuvable.");
        }

        $pdf = self::generatePdf($invoiceId);
        $filename = $data['invoice']['number'] . '.pdf';

        header('Content-Type: application/pdf');
        header('Content-Disposition: inline; filename="' . $filename . '"');
        header('Content-Length: ' . strlen($pdf));
        echo $pdf;
        exit;
    }

    /**
     * Sauvegarde le PDF sur le disque et met à jour la BDD.
     * @return string Chemin du fichier
     */
    public static function save(int $invoiceId): string
    {
        $data = self::getInvoiceData($invoiceId);
        if (!$data) {
            throw new \RuntimeException("Facture #{$invoiceId} introuvable.");
        }

        $dir = self::storagePath();
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }

        $filename = $data['invoice']['number'] . '.pdf';
        $filepath = $dir . '/' . $filename;
        file_put_contents($filepath, self::generatePdf($invoiceId));

        // Mettre à jour le filename en BDD
        $db = Database::getInstance();
        $db->update('invoices', ['filename' => $filename], 'id = ?', [$invoiceId]);

        return $filepath;
    }

    // ─── GÉNÉRATION DE FACTURE (instance method, used by controller) ───

    /**
     * Crée une facture pour une commande (entrée DB + fichier PDF).
     * @return array ['id', 'number', 'filename', 'path']
     */
    public function generate(int $orderId): array
    {
        $order = $this->db->fetch(
            "SELECT id, reference, customer_first_name, customer_last_name, customer_email,
                    shipping_address, shipping_city, shipping_postal_code,
                    subtotal, shipping_cost, tax_amount, total, status, created_at
             FROM orders WHERE id = ?",
            [$orderId]
        );

        if (!$order) {
            throw new \RuntimeException("Commande #{$orderId} introuvable");
        }

        $invoiceNumber = self::generateNumber();
        $invoiceStatus = in_array($order['status'], ['paid', 'delivered', 'shipped']) ? 'paid' : 'pending';

        $invoiceId = $this->db->insert('invoices', [
            'order_id'       => $orderId,
            'invoice_number' => $invoiceNumber,
            'subtotal'       => (float) $order['subtotal'],
            'tax_amount'     => (float) $order['tax_amount'],
            'total'          => (float) $order['total'],
            'status'         => $invoiceStatus,
            'issued_at'      => date('Y-m-d H:i:s'),
        ]);

        // Générer et sauvegarder le PDF
        $filepath = self::save($invoiceId);

        return [
            'id'       => $invoiceId,
            'number'   => $invoiceNumber,
            'filename' => basename($filepath),
            'path'     => $filepath,
        ];
    }

    // ─── RÉCUPÉRATION DES DONNÉES ───

    private static function getInvoiceData(int $invoiceId): ?array
    {
        $db = Database::getInstance();

        $row = $db->fetch("
            SELECT i.*, o.id AS oid, o.reference, o.status AS order_status,
                   o.customer_first_name, o.customer_last_name, o.customer_email,
                   o.shipping_address, o.shipping_city, o.shipping_postal_code,
                   o.shipping_country, o.subtotal AS order_subtotal,
                   o.shipping_cost, o.tax_amount AS order_tax,
                   o.total AS order_total, o.payment_method, o.payment_id,
                   o.tracking_number, o.tracking_carrier, o.created_at AS order_date
            FROM invoices i
            JOIN orders o ON o.id = i.order_id
            WHERE i.id = ?
        ", [$invoiceId]);

        if (!$row) {
            return null;
        }

        // Lignes de commande
        $items = $db->fetchAll("
            SELECT oi.*, p.description AS product_description
            FROM order_items oi
            LEFT JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = ?
            ORDER BY oi.id ASC
        ", [(int) $row['oid']]);

        // Date d'échéance (+30 jours)
        $invoiceDate = $row['issued_at'] ?? $row['created_at'];
        $dueDate = date('Y-m-d H:i:s', strtotime($invoiceDate . ' +30 days'));

        // Billing settings
        $settingsRows = $db->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'billing'"
        );
        $billing = [];
        foreach ($settingsRows as $s) {
            $billing[$s['key']] = $s['value'];
        }

        // General settings fallback
        $generalRows = $db->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'general'"
        );
        $general = [];
        foreach ($generalRows as $s) {
            $general[$s['key']] = $s['value'];
        }

        return [
            'invoice' => [
                'id'       => (int) $row['id'],
                'number'   => $row['invoice_number'],
                'date'     => $invoiceDate,
                'due_date' => $dueDate,
                'status'   => $row['status'],
            ],
            'order' => [
                'id'             => (int) $row['oid'],
                'reference'      => $row['reference'],
                'date'           => $row['order_date'],
                'payment_method' => $row['payment_method'] ?? '',
                'payment_id'     => $row['payment_id'] ?? '',
                'carrier'        => $row['tracking_carrier'] ?? '',
                'tracking'       => $row['tracking_number'] ?? '',
            ],
            'customer' => [
                'name'    => trim($row['customer_first_name'] . ' ' . $row['customer_last_name']),
                'email'   => $row['customer_email'],
                'address' => $row['shipping_address'] ?? '',
                'city'    => trim(($row['shipping_postal_code'] ?? '') . ' ' . ($row['shipping_city'] ?? '')),
                'country' => $row['shipping_country'] ?? 'France',
            ],
            'items'  => $items,
            'totals' => [
                'subtotal' => (float) ($row['order_subtotal'] ?? $row['subtotal']),
                'shipping' => (float) ($row['shipping_cost'] ?? 0),
                'tax'      => (float) ($row['order_tax'] ?? $row['tax_amount']),
                'total'    => (float) ($row['order_total'] ?? $row['total']),
            ],
            'association' => [
                'name'    => $billing['association_name'] ?? $general['association_name'] ?? 'La Fête du Cidre',
                'address' => $billing['address'] ?? $general['association_address'] ?? "Parc du Drugeot, L'Hôtellerie de Flée",
                'city'    => $general['association_city'] ?? '49500 Segré-en-Anjou Bleu',
                'email'   => $billing['email'] ?? $general['association_email'] ?? 'facturation@fetecidre.fr',
                'phone'   => $general['association_phone'] ?? '',
                'siret'   => $billing['siret'] ?? '',
                'rna'     => $general['association_rna'] ?? '',
                'ape'     => $general['association_ape'] ?? '9499Z',
                'site_url' => $general['site_url'] ?? Config::baseUrl(),
            ],
        ];
    }

    private static function renderTemplate(array $data): string
    {
        extract($data, EXTR_SKIP); // $invoice, $order, $customer, $items, $totals, $association
        ob_start();
        require self::templatePath();
        return ob_get_clean();
    }

    // ─── HELPERS DE FORMATAGE (appelés dans le template) ───

    public static function formatPrice(float $amount): string
    {
        return number_format($amount, 2, ',', "\u{202F}") . "\u{00A0}\u{20AC}";
    }

    public static function formatDate(string $datetime): string
    {
        $months = [
            1 => 'janvier', 2 => 'février', 3 => 'mars', 4 => 'avril',
            5 => 'mai', 6 => 'juin', 7 => 'juillet', 8 => 'août',
            9 => 'septembre', 10 => 'octobre', 11 => 'novembre', 12 => 'décembre',
        ];
        $ts = strtotime($datetime);
        return (int) date('j', $ts) . ' ' . $months[(int) date('n', $ts)] . ' ' . date('Y', $ts);
    }

    public static function formatPaymentMethod(string $method): string
    {
        return match ($method) {
            'stripe'   => 'Carte bancaire via Stripe',
            'cheque'   => 'Chèque',
            'virement' => 'Virement bancaire',
            'especes'  => 'Espèces',
            default    => ucfirst($method ?: '—'),
        };
    }

    public static function formatStatus(string $status): array
    {
        return match ($status) {
            'paid'     => ['label' => 'PAYÉE',       'class' => 'paid'],
            'pending'  => ['label' => 'EN ATTENTE',  'class' => 'pending'],
            'overdue'  => ['label' => 'EN RETARD',   'class' => 'overdue'],
            'refunded' => ['label' => 'REMBOURSÉE',  'class' => 'refunded'],
            default    => ['label' => strtoupper($status), 'class' => 'pending'],
        };
    }

    /**
     * Génère le prochain numéro de facture.
     * Format : FAC-{ANNÉE}-{COMPTEUR 4 chiffres}
     */
    public static function generateNumber(): string
    {
        $db   = Database::getInstance();
        $year = date('Y');

        $last = $db->fetch(
            "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
            ["FAC-{$year}-%"]
        );

        $counter = $last
            ? (int) substr($last['invoice_number'], strrpos($last['invoice_number'], '-') + 1) + 1
            : 1;

        return sprintf('FAC-%s-%04d', $year, $counter);
    }
}
