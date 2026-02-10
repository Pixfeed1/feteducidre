<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;
use App\Services\InvoicePdfService;

/**
 * Contrôleur de gestion des factures.
 * Permet de lister, consulter, générer des factures et gérer les paramètres de facturation.
 */
class InvoiceAdminController extends Controller
{
    /** Labels et classes de statut */
    private const STATUS_MAP = [
        'paid'     => ['Payée', 'paid'],
        'pending'  => ['En attente', 'pending'],
        'overdue'  => ['En retard', 'overdue'],
        'refunded' => ['Remboursée', 'refunded'],
    ];

    /** Icônes de statut */
    private const STATUS_ICONS = [
        'paid'     => 'check-circle',
        'pending'  => 'clock',
        'overdue'  => 'alert-circle',
        'refunded' => 'rotate-ccw',
    ];

    /**
     * Liste toutes les factures avec stats, filtres et pagination
     */
    public function index(Request $request, array $params = []): void
    {
        $status = $request->get('status');
        $search = $request->get('q');
        $page = max(1, (int) ($request->get('page') ?? 1));
        $perPage = 15;
        $offset = ($page - 1) * $perPage;

        // Stats globales
        $stats = $this->db()->fetch(
            "SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid_count,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN total ELSE 0 END), 0) AS total_paid
             FROM invoices"
        );

        // Construction de la requête filtrée
        $where = [];
        $sqlParams = [];

        if ($status && array_key_exists($status, self::STATUS_MAP)) {
            $where[] = "i.status = ?";
            $sqlParams[] = $status;
        }

        if ($search) {
            $where[] = "(i.invoice_number LIKE ? OR o.customer_first_name LIKE ? OR o.customer_last_name LIKE ? OR o.reference LIKE ?)";
            $searchTerm = '%' . $search . '%';
            $sqlParams = array_merge($sqlParams, [$searchTerm, $searchTerm, $searchTerm, $searchTerm]);
        }

        $whereClause = !empty($where) ? ' WHERE ' . implode(' AND ', $where) : '';

        // Compter le total filtré
        $countResult = $this->db()->fetch(
            "SELECT COUNT(*) AS total FROM invoices i JOIN orders o ON o.id = i.order_id" . $whereClause,
            $sqlParams
        );
        $totalFiltered = (int) ($countResult['total'] ?? 0);
        $totalPages = max(1, (int) ceil($totalFiltered / $perPage));

        // Récupérer les factures paginées
        $invoices = $this->db()->fetchAll(
            "SELECT i.*, o.reference AS order_reference, o.customer_first_name, o.customer_last_name,
                    o.customer_email
             FROM invoices i
             JOIN orders o ON o.id = i.order_id"
            . $whereClause
            . " ORDER BY i.issued_at DESC LIMIT {$perPage} OFFSET {$offset}",
            $sqlParams
        );

        // Billing settings
        $settingsRows = $this->db()->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'billing'"
        );
        $billing = [];
        foreach ($settingsRows as $row) {
            $billing[$row['key']] = $row['value'];
        }

        // Prochain numéro de facture
        $year = date('Y');
        $prefix = $billing['prefix'] ?? "FAC-{$year}-";
        $lastInvoice = $this->db()->fetch(
            "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
            ["FAC-{$year}-%"]
        );
        $nextNum = $lastInvoice ? (int) substr($lastInvoice['invoice_number'], -4) + 1 : 1;
        $nextInvoiceNumber = sprintf('FAC-%s-%04d', $year, $nextNum);

        $this->renderAdmin('templates/admin/invoices/index.php', [
            'title'             => 'Factures',
            'invoices'          => $invoices,
            'currentStatus'     => $status,
            'search'            => $search,
            'page'              => $page,
            'perPage'           => $perPage,
            'totalFiltered'     => $totalFiltered,
            'totalPages'        => $totalPages,
            'stats'             => $stats,
            'statusMap'         => self::STATUS_MAP,
            'statusIcons'       => self::STATUS_ICONS,
            'billing'           => $billing,
            'nextInvoiceNumber' => $nextInvoiceNumber,
        ]);
    }

    /**
     * Affiche le détail d'une facture (aperçu facture)
     */
    public function show(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        $invoice = $this->db()->fetch(
            "SELECT i.*, o.reference AS order_reference, o.customer_first_name, o.customer_last_name,
                    o.customer_email, o.customer_phone,
                    o.shipping_address, o.shipping_city, o.shipping_postal_code, o.shipping_country
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
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY id ASC",
            [(int) $invoice['order_id']]
        );

        // Billing settings pour l'en-tête de la facture
        $settingsRows = $this->db()->fetchAll(
            "SELECT `key`, value FROM settings WHERE `group` = 'billing'"
        );
        $billing = [];
        foreach ($settingsRows as $row) {
            $billing[$row['key']] = $row['value'];
        }

        $this->renderAdmin('templates/admin/invoices/show.php', [
            'title'      => 'Facture ' . $invoice['invoice_number'],
            'invoice'    => $invoice,
            'items'      => $items,
            'billing'    => $billing,
            'statusMap'  => self::STATUS_MAP,
            'statusIcons' => self::STATUS_ICONS,
        ]);
    }

    /**
     * Télécharge le PDF d'une facture
     * GET /admin/invoices/{id}/pdf
     */
    public function pdf(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        try {
            InvoicePdfService::download($id);
        } catch (\RuntimeException $e) {
            set_flash('error', $e->getMessage());
            $this->redirect('/admin/invoices');
        }
    }

    /**
     * Affiche le PDF inline (aperçu navigateur)
     * GET /admin/invoices/{id}/stream
     */
    public function stream(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        try {
            InvoicePdfService::stream($id);
        } catch (\RuntimeException $e) {
            set_flash('error', $e->getMessage());
            $this->redirect('/admin/invoices');
        }
    }

    /**
     * Génère une facture pour une commande (DB + PDF)
     * POST /admin/invoices/{id}/generate
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

        try {
            $service = new InvoicePdfService();
            $result = $service->generate($orderId);
            set_flash('success', 'Facture ' . $result['number'] . ' générée avec succès (PDF créé).');
            $this->redirect('/admin/invoices/' . $result['id']);
        } catch (\Exception $e) {
            set_flash('error', 'Erreur lors de la génération : ' . $e->getMessage());
            $this->redirect('/admin/orders/' . $orderId);
        }
    }

    /**
     * Sauvegarde les paramètres de facturation
     */
    public function saveSettings(Request $request, array $params = []): void
    {
        $data = $request->all();

        $keys = [
            'association_name' => $data['billing_association_name'] ?? '',
            'siret'            => $data['billing_siret'] ?? '',
            'address'          => $data['billing_address'] ?? '',
            'email'            => $data['billing_email'] ?? '',
            'prefix'           => $data['billing_prefix'] ?? '',
            'tva_rate'         => $data['billing_tva_rate'] ?? '',
            'legal_mentions'   => $data['billing_legal_mentions'] ?? '',
        ];

        foreach ($keys as $key => $value) {
            $existing = $this->db()->fetch(
                "SELECT id FROM settings WHERE `group` = 'billing' AND `key` = ?",
                [$key]
            );

            if ($existing) {
                $this->db()->update('settings', [
                    'value' => $value,
                ], "`group` = 'billing' AND `key` = ?", [$key]);
            } else {
                $this->db()->insert('settings', [
                    'group' => 'billing',
                    'key'   => $key,
                    'value' => $value,
                    'type'  => $key === 'legal_mentions' ? 'textarea' : ($key === 'email' ? 'text' : 'text'),
                ]);
            }
        }

        set_flash('success', 'Paramètres de facturation enregistrés.');
        $this->redirect('/admin/invoices');
    }
}
