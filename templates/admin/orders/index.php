<?php
/**
 * Liste des commandes — administration.
 * Variables : $orders, $currentStatus, $search, $page, $perPage, $totalFiltered, $totalPages,
 *             $stats, $statusMap, $paymentMap
 */

$statusIcons = [
    'pending'    => 'clock',
    'paid'       => 'check-circle',
    'processing' => 'loader',
    'shipped'    => 'truck',
    'delivered'  => 'check-circle',
    'cancelled'  => 'x-circle',
    'refunded'   => 'rotate-ccw',
];

$avatarColors = ['#D4833B', '#4A6B3E', '#3B82F6', '#8B5CF6', '#D94040', '#2C4A2E', '#7A9E6B', '#F59E0B'];

$filterChips = [
    ''           => 'Tout',
    'new'        => 'Nouvelles',
    'processing' => 'En prépa',
    'shipped'    => 'Expédiées',
    'delivered'  => 'Livrées',
    'cancelled'  => 'Annulées',
];
?>

<div style="max-width:1100px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:linear-gradient(135deg, var(--orange-cidre), #E8A66A)"><?= icon('shopping-bag', 22, '', 'white') ?></div>
            <h1>Commandes</h1>
        </div>
        <div class="page-header-actions">
            <a href="/admin/orders?export=csv" class="btn btn-secondary">
                <?= icon('download', 15) ?> Exporter CSV
            </a>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <a href="/admin/orders" class="stat-card <?= empty($currentStatus) ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(92,61,46,0.12)"><?= icon('shopping-bag', 18, '', 'var(--brun)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['total'] ?? 0) ?></div><div class="stat-label">Total commandes</div></div>
        </a>
        <a href="/admin/orders?status=new" class="stat-card <?= $currentStatus === 'new' ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(59,130,246,0.12)"><?= icon('clock', 18, '', 'var(--bleu)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['new_count'] ?? 0) ?></div><div class="stat-label">Nouvelles</div></div>
        </a>
        <a href="/admin/orders?status=processing" class="stat-card <?= $currentStatus === 'processing' ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(245,158,11,0.12)"><?= icon('loader', 18, '', 'var(--jaune)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['processing_count'] ?? 0) ?></div><div class="stat-label">En préparation</div></div>
        </a>
        <a href="/admin/orders?status=shipped" class="stat-card <?= $currentStatus === 'shipped' ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(122,158,107,0.12)"><?= icon('truck', 18, '', 'var(--vert-mousse)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['shipped_count'] ?? 0) ?></div><div class="stat-label">Expédiées</div></div>
        </a>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(212,131,59,0.12)"><?= icon('credit-card', 18, '', 'var(--orange-cidre)') ?></div>
            <div><div class="stat-value"><?= number_format((float) ($stats['month_revenue'] ?? 0), 0, ',', ' ') ?> &euro;</div><div class="stat-label">CA du mois</div></div>
        </div>
    </div>

    <!-- TOOLBAR -->
    <div class="toolbar">
        <form method="get" action="/admin/orders" class="search-box">
            <?php if ($currentStatus): ?>
                <input type="hidden" name="status" value="<?= e($currentStatus) ?>">
            <?php endif; ?>
            <span class="search-icon"><?= icon('search', 15) ?></span>
            <input type="text" name="q" value="<?= e($search ?? '') ?>" placeholder="Rechercher par référence, nom, email…">
        </form>
        <div class="filter-chips">
            <?php foreach ($filterChips as $key => $label): ?>
                <a href="/admin/orders<?= $key ? '?status=' . $key : '' ?><?= $search ? ($key ? '&' : '?') . 'q=' . urlencode($search) : '' ?>"
                   class="chip <?= ($currentStatus ?? '') === $key ? 'active' : '' ?>"><?= $label ?></a>
            <?php endforeach; ?>
        </div>
        <div class="toolbar-spacer"></div>
        <a href="/admin/orders" class="btn-icon" title="Rafraîchir"><?= icon('rotate-ccw', 15) ?></a>
    </div>

    <!-- TABLE -->
    <?php if (empty($orders)): ?>
        <div class="card">
            <div class="card-body">
                <div class="empty-state" style="text-align:center;padding:3rem">
                    <?= icon('shopping-bag', 40) ?>
                    <p style="margin-top:0.8rem;color:var(--texte-leger)">Aucune commande trouvée.</p>
                </div>
            </div>
        </div>
    <?php else: ?>
        <div class="table-card">
            <div class="table-scroll">
                <table>
                    <thead>
                        <tr>
                            <th>Commande</th>
                            <th>Client</th>
                            <th>Date</th>
                            <th>Articles</th>
                            <th>Statut</th>
                            <th>Paiement</th>
                            <th style="text-align:right">Montant</th>
                            <th style="width:50px"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($orders as $i => $order):
                            $st = $order['status'];
                            $stInfo = $statusMap[$st] ?? ['Inconnu', 'pending'];
                            $stIcon = $statusIcons[$st] ?? 'circle';

                            // Display status: group pending+paid as "new"
                            $displayStatus = in_array($st, ['pending', 'paid']) ? 'new' : $st;
                            $displayLabel = $displayStatus === 'new' ? 'Nouvelle' : $stInfo[0];
                            $displayClass = $displayStatus;

                            // Payment status
                            $payStatus = $order['payment_status'] ?? ($st === 'paid' || $st === 'delivered' || $st === 'shipped' ? 'paid' : ($st === 'refunded' ? 'refunded' : 'pending'));
                            $payInfo = $paymentMap[$payStatus] ?? ['En attente', 'pending'];

                            // Avatar color
                            $color = $avatarColors[$i % count($avatarColors)];
                            $initials = mb_strtoupper(mb_substr($order['customer_first_name'] ?? '', 0, 1) . mb_substr($order['customer_last_name'] ?? '', 0, 1));

                            // Count items
                            $itemCount = (int) ($order['items_count'] ?? 0);
                        ?>
                            <tr onclick="window.location='/admin/orders/<?= (int) $order['id'] ?>'" style="cursor:pointer">
                                <td>
                                    <div class="td-ref">
                                        <?= e($order['reference']) ?>
                                        <small><?= time_ago($order['created_at']) ?></small>
                                    </div>
                                </td>
                                <td>
                                    <div class="td-client">
                                        <div class="td-avatar" style="background:<?= $color ?>"><?= $initials ?></div>
                                        <div>
                                            <div class="td-client-name"><?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?></div>
                                            <div class="td-client-email"><?= e($order['customer_email']) ?></div>
                                        </div>
                                    </div>
                                </td>
                                <td style="font-size:0.8rem;color:var(--texte-leger)"><?= date_fr($order['created_at'], 'short') ?></td>
                                <td>
                                    <div class="td-items">
                                        <?= icon('package', 12) ?>
                                        <?php if ($itemCount > 0): ?>
                                            <?= $itemCount ?> article<?= $itemCount > 1 ? 's' : '' ?>
                                        <?php else: ?>
                                            —
                                        <?php endif; ?>
                                    </div>
                                </td>
                                <td>
                                    <span class="status <?= $displayClass ?>">
                                        <?= icon($stIcon, 10) ?> <?= $displayLabel ?>
                                    </span>
                                </td>
                                <td>
                                    <span class="pay-badge <?= $payInfo[1] ?>">
                                        <?= icon('credit-card', 10) ?> <?= $payInfo[0] ?>
                                    </span>
                                </td>
                                <td style="text-align:right">
                                    <span class="td-amount"><?= number_format((float) $order['total'], 2, ',', '&nbsp;') ?>&nbsp;&euro;</span>
                                </td>
                                <td>
                                    <a href="/admin/orders/<?= (int) $order['id'] ?>" class="btn-icon" title="Voir"><?= icon('chevron-right', 15) ?></a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <!-- PAGINATION -->
            <?php if ($totalPages > 1): ?>
                <div class="pagination">
                    <div class="pagination-info">
                        <?php
                            $start = ($page - 1) * $perPage + 1;
                            $end = min($page * $perPage, $totalFiltered);
                        ?>
                        Affichage <?= $start ?>–<?= $end ?> sur <?= $totalFiltered ?>
                    </div>
                    <div class="pagination-btns">
                        <?php
                            $baseUrl = '/admin/orders?';
                            $queryParts = [];
                            if ($currentStatus) $queryParts[] = 'status=' . urlencode($currentStatus);
                            if ($search) $queryParts[] = 'q=' . urlencode($search);
                            $baseQuery = implode('&', $queryParts);
                            if ($baseQuery) $baseQuery .= '&';
                        ?>
                        <?php if ($page > 1): ?>
                            <a href="<?= $baseUrl . $baseQuery ?>page=<?= $page - 1 ?>" class="page-btn"><?= icon('chevron-left', 13) ?></a>
                        <?php endif; ?>

                        <?php
                            $range = 2;
                            $startPage = max(1, $page - $range);
                            $endPage = min($totalPages, $page + $range);
                        ?>
                        <?php if ($startPage > 1): ?>
                            <a href="<?= $baseUrl . $baseQuery ?>page=1" class="page-btn">1</a>
                            <?php if ($startPage > 2): ?><span class="page-btn" style="border:none;cursor:default">…</span><?php endif; ?>
                        <?php endif; ?>

                        <?php for ($p = $startPage; $p <= $endPage; $p++): ?>
                            <a href="<?= $baseUrl . $baseQuery ?>page=<?= $p ?>" class="page-btn <?= $p === $page ? 'active' : '' ?>"><?= $p ?></a>
                        <?php endfor; ?>

                        <?php if ($endPage < $totalPages): ?>
                            <?php if ($endPage < $totalPages - 1): ?><span class="page-btn" style="border:none;cursor:default">…</span><?php endif; ?>
                            <a href="<?= $baseUrl . $baseQuery ?>page=<?= $totalPages ?>" class="page-btn"><?= $totalPages ?></a>
                        <?php endif; ?>

                        <?php if ($page < $totalPages): ?>
                            <a href="<?= $baseUrl . $baseQuery ?>page=<?= $page + 1 ?>" class="page-btn"><?= icon('chevron-right', 13) ?></a>
                        <?php endif; ?>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>

</div>
