<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur de gestion des commandes.
 * Permet de consulter les commandes, modifier leur statut et suivre l'expédition.
 */
class OrderAdminController extends Controller
{
    /** Labels et classes de statut */
    private const STATUS_MAP = [
        'pending'    => ['En attente', 'pending'],
        'paid'       => ['Payée', 'paid'],
        'processing' => ['En préparation', 'processing'],
        'shipped'    => ['Expédiée', 'shipped'],
        'delivered'  => ['Livrée', 'delivered'],
        'cancelled'  => ['Annulée', 'cancelled'],
        'refunded'   => ['Remboursée', 'refunded'],
    ];

    /** Labels de paiement */
    private const PAYMENT_MAP = [
        'paid'     => ['Payé', 'paid'],
        'pending'  => ['En attente', 'pending'],
        'refunded' => ['Remboursé', 'refunded'],
    ];

    /**
     * Liste les commandes avec stats, filtres et pagination
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
                SUM(CASE WHEN status IN ('pending', 'paid') THEN 1 ELSE 0 END) AS new_count,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) AS processing_count,
                SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) AS shipped_count,
                COALESCE(SUM(CASE WHEN status NOT IN ('cancelled', 'refunded') AND created_at >= DATE_FORMAT(NOW(), '%Y-%m-01') THEN total ELSE 0 END), 0) AS month_revenue
             FROM orders"
        );

        // Construction de la requête filtrée
        $where = [];
        $sqlParams = [];

        if ($status) {
            if ($status === 'new') {
                $where[] = "status IN ('pending', 'paid')";
            } else {
                $where[] = "status = ?";
                $sqlParams[] = $status;
            }
        }

        if ($search) {
            $where[] = "(reference LIKE ? OR customer_first_name LIKE ? OR customer_last_name LIKE ? OR customer_email LIKE ?)";
            $searchTerm = '%' . $search . '%';
            $sqlParams = array_merge($sqlParams, [$searchTerm, $searchTerm, $searchTerm, $searchTerm]);
        }

        $whereClause = !empty($where) ? ' WHERE ' . implode(' AND ', $where) : '';

        // Compter le total filtré
        $countResult = $this->db()->fetch(
            "SELECT COUNT(*) AS total FROM orders" . $whereClause,
            $sqlParams
        );
        $totalFiltered = (int) ($countResult['total'] ?? 0);
        $totalPages = max(1, (int) ceil($totalFiltered / $perPage));

        // Récupérer les commandes paginées
        $orders = $this->db()->fetchAll(
            "SELECT * FROM orders" . $whereClause . " ORDER BY created_at DESC LIMIT {$perPage} OFFSET {$offset}",
            $sqlParams
        );

        $this->renderAdmin('templates/admin/orders/index.php', [
            'title'           => 'Commandes',
            'orders'          => $orders,
            'currentStatus'   => $status,
            'search'          => $search,
            'page'            => $page,
            'perPage'         => $perPage,
            'totalFiltered'   => $totalFiltered,
            'totalPages'      => $totalPages,
            'stats'           => $stats,
            'statusMap'       => self::STATUS_MAP,
            'paymentMap'      => self::PAYMENT_MAP,
        ]);
    }

    /**
     * Affiche le détail d'une commande
     */
    public function show(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        $order = $this->db()->fetch("SELECT * FROM orders WHERE id = ?", [$id]);
        if (!$order) {
            set_flash('error', 'Commande introuvable.');
            $this->redirect('/admin/orders');
            return;
        }

        // Récupérer les articles de la commande
        $items = $this->db()->fetchAll(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY id ASC",
            [$id]
        );

        // Récupérer la facture associée si elle existe
        $invoice = $this->db()->fetch(
            "SELECT * FROM invoices WHERE order_id = ? LIMIT 1",
            [$id]
        );

        $this->renderAdmin('templates/admin/orders/show.php', [
            'title'      => 'Commande ' . $order['reference'],
            'order'      => $order,
            'items'      => $items,
            'invoice'    => $invoice,
            'statusMap'  => self::STATUS_MAP,
            'paymentMap' => self::PAYMENT_MAP,
        ]);
    }

    /**
     * Met à jour le statut d'une commande
     */
    public function updateStatus(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $newStatus = $request->post('status', '');

        $validStatuses = array_keys(self::STATUS_MAP);
        if (!in_array($newStatus, $validStatuses, true)) {
            set_flash('error', 'Statut invalide.');
            $this->redirect('/admin/orders/' . $id);
            return;
        }

        $updates = ['status' => $newStatus];

        $trackingNumber = $request->post('tracking_number');
        if ($trackingNumber !== null) {
            $updates['tracking_number'] = $trackingNumber;
        }

        $trackingCarrier = $request->post('tracking_carrier');
        if ($trackingCarrier !== null) {
            $updates['tracking_carrier'] = $trackingCarrier;
        }

        $adminNotes = $request->post('admin_notes');
        if ($adminNotes !== null) {
            $updates['admin_notes'] = $adminNotes;
        }

        $this->db()->update('orders', $updates, 'id = ?', [$id]);

        set_flash('success', 'Commande mise à jour.');
        $this->redirect('/admin/orders/' . $id);
    }
}
