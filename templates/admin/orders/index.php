<?php
/**
 * Liste des commandes — administration.
 * Variables : $orders, $currentStatus
 */

$statusMap = [
    'pending'    => ['En attente', 'badge-warning'],
    'paid'       => ['Payée', 'badge-success'],
    'processing' => ['En traitement', 'badge-info'],
    'shipped'    => ['Expédiée', 'badge-info'],
    'delivered'  => ['Livrée', 'badge-success'],
    'cancelled'  => ['Annulée', 'badge-danger'],
    'refunded'   => ['Remboursée', 'badge-secondary'],
];
?>

<div class="page-header">
    <h1><?= icon('shopping-cart', 24) ?> Commandes</h1>
</div>

<!-- Filtres par statut -->
<div class="tabs mb-3">
    <a href="/admin/orders" class="tab-link <?= empty($currentStatus) ? 'active' : '' ?>">Toutes</a>
    <?php foreach ($statusMap as $key => [$label, $class]): ?>
        <a href="/admin/orders?status=<?= $key ?>" class="tab-link <?= $currentStatus === $key ? 'active' : '' ?>">
            <?= $label ?>
        </a>
    <?php endforeach; ?>
</div>

<div class="card">
    <?php if (empty($orders)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('shopping-cart', 40) ?>
                <p>Aucune commande trouvée.</p>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Référence</th>
                        <th>Client</th>
                        <th>Email</th>
                        <th>Total</th>
                        <th>Statut</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($orders as $order): ?>
                        <tr>
                            <td>
                                <a href="/admin/orders/<?= (int) $order['id'] ?>">
                                    <strong><?= e($order['reference']) ?></strong>
                                </a>
                            </td>
                            <td><?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?></td>
                            <td class="text-muted"><?= e($order['customer_email']) ?></td>
                            <td><?= number_format((float) $order['total'], 2, ',', ' ') ?> &euro;</td>
                            <td>
                                <?php $s = $statusMap[$order['status']] ?? ['Inconnu', 'badge-secondary']; ?>
                                <span class="badge <?= $s[1] ?>"><?= $s[0] ?></span>
                            </td>
                            <td class="text-muted"><?= date_fr($order['created_at'], 'short') ?></td>
                            <td>
                                <a href="/admin/orders/<?= (int) $order['id'] ?>" class="btn btn-sm btn-secondary" title="Voir">
                                    <?= icon('eye', 16) ?>
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
