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

        // Commandes en attente
        $pendingOrders = (int) ($db->fetch(
            "SELECT COUNT(*) AS total FROM orders WHERE status IN ('pending', 'processing')"
        )['total'] ?? 0);

        // Chiffre d'affaires total
        $revenue = (float) ($db->fetch(
            "SELECT COALESCE(SUM(total), 0) AS total FROM orders WHERE status NOT IN ('cancelled', 'refunded')"
        )['total'] ?? 0);

        // Nombre de pages
        $pageCount = (int) ($db->fetch("SELECT COUNT(*) AS total FROM pages")['total'] ?? 0);

        // Nombre de produits
        $productCount = (int) ($db->fetch("SELECT COUNT(*) AS total FROM products")['total'] ?? 0);

        // Commandes récentes (4 dernières)
        $recentOrders = $db->fetchAll(
            "SELECT id, reference, customer_first_name, customer_last_name, total, status, created_at
             FROM orders ORDER BY created_at DESC LIMIT 4"
        );

        // Pages récentes (4 dernières)
        $recentPages = $db->fetchAll(
            "SELECT id, title, slug, status, updated_at, created_at
             FROM pages ORDER BY updated_at DESC LIMIT 4"
        );

        // Produits récents avec stock
        $recentProducts = $db->fetchAll(
            "SELECT id, name, slug, price, stock, short_description
             FROM products ORDER BY created_at DESC LIMIT 5"
        );

        $this->renderAdmin('templates/admin/dashboard.php', [
            'title'          => 'Tableau de bord',
            'orderCount'     => $orderCount,
            'pendingOrders'  => $pendingOrders,
            'revenue'        => $revenue,
            'pageCount'      => $pageCount,
            'productCount'   => $productCount,
            'recentOrders'   => $recentOrders,
            'recentPages'    => $recentPages,
            'recentProducts' => $recentProducts,
        ]);
    }
}
