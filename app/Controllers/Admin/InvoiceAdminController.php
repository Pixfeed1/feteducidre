<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur de gestion des factures.
 * Permet de lister, consulter et générer des factures.
 */
class InvoiceAdminController extends Controller
{
    /**
     * Liste toutes les factures
     */
    public function index(Request $request, array $params = []): void
    {
        $invoices = $this->db()->fetchAll(
            "SELECT i.*, o.reference AS order_reference, o.customer_first_name, o.customer_last_name
             FROM invoices i
             JOIN orders o ON o.id = i.order_id
             ORDER BY i.issued_at DESC"
        );

        $this->renderAdmin('templates/admin/invoices/index.php', [
            'title'    => 'Factures',
            'invoices' => $invoices,
        ]);
    }

    /**
     * Affiche le détail d'une facture
     */
    public function show(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        $invoice = $this->db()->fetch(
            "SELECT i.*, o.reference AS order_reference, o.customer_first_name, o.customer_last_name,
                    o.customer_email, o.shipping_address, o.shipping_city, o.shipping_postal_code
             FROM invoices i
             JOIN orders o ON o.id = i.order_id
             WHERE i.id = ?",
            [$id]
        );

        if (!$invoice) {
            set_flash('error', 'Facture introuvable.');
            $this->redirect('/admin/invoices');
            return;
        }

        // Récupérer les articles de la commande liée
        $items = $this->db()->fetchAll(
            "SELECT * FROM order_items WHERE order_id = ?",
            [(int) $invoice['order_id']]
        );

        $this->renderAdmin('templates/admin/invoices/index.php', [
            'title'       => 'Facture ' . $invoice['invoice_number'],
            'invoices'    => [],
            'invoice'     => $invoice,
            'items'       => $items,
            'showDetail'  => true,
        ]);
    }

    /**
     * Génère une facture pour une commande
     */
    public function generate(Request $request, array $params = []): void
    {
        $orderId = (int) ($params['id'] ?? 0);

        // Vérifier que la commande existe
        $order = $this->db()->fetch("SELECT * FROM orders WHERE id = ?", [$orderId]);
        if (!$order) {
            set_flash('error', 'Commande introuvable.');
            $this->redirect('/admin/orders');
            return;
        }

        // Vérifier qu'une facture n'existe pas déjà
        $existing = $this->db()->fetch("SELECT id FROM invoices WHERE order_id = ?", [$orderId]);
        if ($existing) {
            set_flash('warning', 'Une facture existe déjà pour cette commande.');
            $this->redirect('/admin/invoices/' . (int) $existing['id']);
            return;
        }

        // Générer le numéro de facture
        $year = date('Y');
        $lastInvoice = $this->db()->fetch(
            "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
            ["FAC-{$year}-%"]
        );

        if ($lastInvoice) {
            $lastNum = (int) substr($lastInvoice['invoice_number'], -4);
            $nextNum = $lastNum + 1;
        } else {
            $nextNum = 1;
        }

        $invoiceNumber = sprintf('FAC-%s-%04d', $year, $nextNum);

        // Créer la facture
        $invoiceId = $this->db()->insert('invoices', [
            'order_id'       => $orderId,
            'invoice_number' => $invoiceNumber,
            'subtotal'       => (float) $order['subtotal'],
            'tax_amount'     => (float) $order['tax_amount'],
            'total'          => (float) $order['total'],
            'issued_at'      => date('Y-m-d H:i:s'),
        ]);

        set_flash('success', 'Facture ' . $invoiceNumber . ' générée avec succès.');
        $this->redirect('/admin/orders/' . $orderId);
    }
}
