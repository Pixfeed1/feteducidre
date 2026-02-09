<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur du tableau de bord admin.
 * Affiche les statistiques générales du site.
 */
class DashboardController extends Controller
{
    /**
     * Affiche le tableau de bord avec les statistiques
     */
    public function index(Request $request, array $params = []): void
    {
        $db = $this->db();

        // Nombre de commandes
        $orderCount = (int) ($db->fetch("SELECT COUNT(*) AS total FROM orders")['total'] ?? 0);

        // Chiffre d'affaires total
        $revenue = (float) ($db->fetch(
            "SELECT COALESCE(SUM(total), 0) AS total FROM orders WHERE status NOT IN ('cancelled', 'refunded')"
        )['total'] ?? 0);

        // Nombre de pages
        $pageCount = (int) ($db->fetch("SELECT COUNT(*) AS total FROM pages")['total'] ?? 0);

        // Nombre de produits
        $productCount = (int) ($db->fetch("SELECT COUNT(*) AS total FROM products")['total'] ?? 0);

        // Nombre d'utilisateurs
        $userCount = (int) ($db->fetch("SELECT COUNT(*) AS total FROM users")['total'] ?? 0);

        // Commandes récentes (5 dernières)
        $recentOrders = $db->fetchAll(
            "SELECT id, reference, customer_first_name, customer_last_name, total, status, created_at
             FROM orders ORDER BY created_at DESC LIMIT 5"
        );

        $this->renderAdmin('templates/admin/dashboard.php', [
            'title'        => 'Tableau de bord',
            'orderCount'   => $orderCount,
            'revenue'      => $revenue,
            'pageCount'    => $pageCount,
            'productCount' => $productCount,
            'userCount'    => $userCount,
            'recentOrders' => $recentOrders,
        ]);
    }
}
