<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur de gestion des commandes.
 * Permet de consulter les commandes et de modifier leur statut.
 */
class OrderAdminController extends Controller
{
    /**
     * Liste toutes les commandes
     */
    public function index(Request $request, array $params = []): void
    {
        $status = $request->get('status');
        $sql = "SELECT * FROM orders";
        $sqlParams = [];

        if ($status) {
            $sql .= " WHERE status = ?";
            $sqlParams[] = $status;
        }

        $sql .= " ORDER BY created_at DESC";

        $orders = $this->db()->fetchAll($sql, $sqlParams);

        $this->renderAdmin('templates/admin/orders/index.php', [
            'title'         => 'Commandes',
            'orders'        => $orders,
            'currentStatus' => $status,
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
            'title'   => 'Commande ' . $order['reference'],
            'order'   => $order,
            'items'   => $items,
            'invoice' => $invoice,
        ]);
    }

    /**
     * Met à jour le statut d'une commande
     */
    public function updateStatus(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $newStatus = $request->post('status', '');

        $validStatuses = ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'];
        if (!in_array($newStatus, $validStatuses, true)) {
            set_flash('error', 'Statut invalide.');
            $this->redirect('/admin/orders/' . $id);
            return;
        }

        // Mettre à jour le numéro de suivi si fourni
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

        set_flash('success', 'Statut de la commande mis à jour.');
        $this->redirect('/admin/orders/' . $id);
    }
}
