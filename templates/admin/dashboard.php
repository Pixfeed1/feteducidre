<?php
/**
 * Tableau de bord — statistiques et activité récente.
 * Variables : $orderCount, $revenue, $pageCount, $productCount, $userCount, $recentOrders
 */
?>

<div class="page-header">
    <h1>Tableau de bord</h1>
</div>

<!-- Cartes statistiques -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon"><?= icon('shopping-cart', 22) ?></div>
        <div class="stat-value"><?= $orderCount ?></div>
        <div class="stat-label">Commandes</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon"><?= icon('tag', 22) ?></div>
        <div class="stat-value"><?= number_format($revenue, 2, ',', ' ') ?> &euro;</div>
        <div class="stat-label">Chiffre d'affaires</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon"><?= icon('file-text', 22) ?></div>
        <div class="stat-value"><?= $pageCount ?></div>
        <div class="stat-label">Pages</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon"><?= icon('package', 22) ?></div>
        <div class="stat-value"><?= $productCount ?></div>
        <div class="stat-label">Produits</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon"><?= icon('users', 22) ?></div>
        <div class="stat-value"><?= $userCount ?></div>
        <div class="stat-label">Utilisateurs</div>
    </div>
</div>

<!-- Dernières commandes -->
<div class="card">
    <div class="card-header">
        <h2>Commandes récentes</h2>
        <a href="/admin/orders" class="btn btn-sm btn-secondary">Voir tout</a>
    </div>

    <?php if (empty($recentOrders)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('shopping-cart', 40) ?>
                <p>Aucune commande pour le moment.</p>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Référence</th>
                        <th>Client</th>
                        <th>Total</th>
                        <th>Statut</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recentOrders as $order): ?>
                        <tr>
                            <td>
                                <a href="/admin/orders/<?= (int) $order['id'] ?>">
                                    <?= e($order['reference']) ?>
                                </a>
                            </td>
                            <td><?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?></td>
                            <td><?= number_format((float) $order['total'], 2, ',', ' ') ?> &euro;</td>
                            <td>
                                <?php
                                $statusMap = [
                                    'pending'    => ['En attente', 'badge-warning'],
                                    'paid'       => ['Payée', 'badge-success'],
                                    'processing' => ['En traitement', 'badge-info'],
                                    'shipped'    => ['Expédiée', 'badge-info'],
                                    'delivered'  => ['Livrée', 'badge-success'],
                                    'cancelled'  => ['Annulée', 'badge-danger'],
                                    'refunded'   => ['Remboursée', 'badge-secondary'],
                                ];
                                $s = $statusMap[$order['status']] ?? ['Inconnu', 'badge-secondary'];
                                ?>
                                <span class="badge <?= $s[1] ?>"><?= $s[0] ?></span>
                            </td>
                            <td class="text-muted"><?= date_fr($order['created_at'], 'short') ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
