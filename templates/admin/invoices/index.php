<?php
/**
 * Liste des factures — administration.
 * Variables : $invoices, $currentStatus, $search, $page, $perPage, $totalFiltered, $totalPages,
 *             $stats, $statusMap, $statusIcons, $billing, $nextInvoiceNumber
 */

$filterChips = [
    ''         => ['Tout', null],
    'paid'     => ['Payées', 'var(--vert-profond)'],
    'pending'  => ['En attente', 'var(--jaune)'],
    'overdue'  => ['En retard', 'var(--rouge)'],
    'refunded' => ['Remboursées', 'var(--texte-leger)'],
];
?>

<div style="max-width:1100px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:linear-gradient(135deg, var(--brun), #8B6B4A)"><?= icon('receipt', 22, '', 'white') ?></div>
            <h1>Factures</h1>
        </div>
        <div class="page-header-actions">
            <a href="/admin/invoices?export=csv" class="btn btn-secondary">
                <?= icon('download', 15) ?> Exporter CSV
            </a>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <a href="/admin/invoices" class="stat-card <?= empty($currentStatus) ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(92,61,46,0.12)"><?= icon('receipt', 18, '', 'var(--brun)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['total'] ?? 0) ?></div><div class="stat-label">Factures émises</div></div>
        </a>
        <a href="/admin/invoices?status=paid" class="stat-card <?= $currentStatus === 'paid' ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(74,107,62,0.12)"><?= icon('check-circle', 18, '', 'var(--vert-mousse)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['paid_count'] ?? 0) ?></div><div class="stat-label">Payées</div></div>
        </a>
        <a href="/admin/invoices?status=pending" class="stat-card <?= $currentStatus === 'pending' ? 'active-filter' : '' ?>" style="text-decoration:none;color:inherit">
            <div class="stat-icon" style="background:rgba(245,158,11,0.12)"><?= icon('clock', 18, '', 'var(--jaune)') ?></div>
            <div><div class="stat-value"><?= (int) ($stats['pending_count'] ?? 0) ?></div><div class="stat-label">En attente</div></div>
        </a>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(44,74,46,0.12)"><?= icon('euro', 18, '', 'var(--vert-profond)') ?></div>
            <div><div class="stat-value"><?= number_format((float) ($stats['total_paid'] ?? 0), 0, ',', ' ') ?> &euro;</div><div class="stat-label">Total encaissé</div></div>
        </div>
    </div>

    <!-- TOOLBAR -->
    <div class="toolbar">
        <form method="get" action="/admin/invoices" class="search-box">
            <?php if ($currentStatus): ?>
                <input type="hidden" name="status" value="<?= e($currentStatus) ?>">
            <?php endif; ?>
            <span class="search-icon"><?= icon('search', 15) ?></span>
            <input type="text" name="q" value="<?= e($search ?? '') ?>" placeholder="Rechercher une facture, un client…">
        </form>
        <div class="filter-chips">
            <?php foreach ($filterChips as $key => [$label, $dotColor]): ?>
                <a href="/admin/invoices<?= $key ? '?status=' . $key : '' ?><?= $search ? ($key ? '&' : '?') . 'q=' . urlencode($search) : '' ?>"
                   class="chip <?= ($currentStatus ?? '') === $key ? 'active' : '' ?>">
                    <?php if ($dotColor): ?><span class="cd" style="background:<?= $dotColor ?>"></span><?php endif; ?>
                    <?= $label ?>
                </a>
            <?php endforeach; ?>
        </div>
        <div class="toolbar-spacer"></div>
        <a href="/admin/invoices" class="btn-icon" title="Rafraîchir"><?= icon('rotate-ccw', 15) ?></a>
    </div>

    <!-- TABLE -->
    <?php if (empty($invoices)): ?>
        <div class="card">
            <div class="card-body">
                <div class="empty-state" style="text-align:center;padding:3rem">
                    <?= icon('receipt', 40) ?>
                    <p style="margin-top:0.8rem;color:var(--texte-leger)">Aucune facture pour le moment.</p>
                    <p style="font-size:0.82rem;color:var(--texte-leger)">Les factures sont générées depuis les commandes.</p>
                </div>
            </div>
        </div>
    <?php else: ?>
        <div class="table-card">
            <div class="table-scroll">
                <table>
                    <thead>
                        <tr>
                            <th>N° Facture</th>
                            <th>Commande</th>
                            <th>Client</th>
                            <th>Date</th>
                            <th>Statut</th>
                            <th style="text-align:right">Montant</th>
                            <th style="width:100px">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($invoices as $inv):
                            $st = $inv['status'] ?? 'pending';
                            $stInfo = $statusMap[$st] ?? ['Inconnu', 'pending'];
                            $stIcon = $statusIcons[$st] ?? 'circle';
                        ?>
                            <tr onclick="window.location='/admin/invoices/<?= (int) $inv['id'] ?>'" style="cursor:pointer">
                                <td><span class="td-ref"><?= e($inv['invoice_number']) ?></span></td>
                                <td>
                                    <a href="/admin/orders/<?= (int) $inv['order_id'] ?>" class="td-order" onclick="event.stopPropagation()">
                                        <?= icon('link', 10) ?> <?= e($inv['order_reference']) ?>
                                    </a>
                                </td>
                                <td>
                                    <div>
                                        <div class="td-client"><?= e($inv['customer_first_name'] . ' ' . $inv['customer_last_name']) ?></div>
                                        <div class="td-client-sub"><?= e($inv['customer_email']) ?></div>
                                    </div>
                                </td>
                                <td style="font-size:0.82rem;white-space:nowrap"><?= date_fr($inv['issued_at'], 'short') ?></td>
                                <td>
                                    <span class="status <?= $stInfo[1] ?>">
                                        <?= icon($stIcon, 8) ?> <?= $stInfo[0] ?>
                                    </span>
                                </td>
                                <td style="text-align:right">
                                    <?php if ($st === 'refunded'): ?>
                                        <span class="td-amount" style="text-decoration:line-through;opacity:0.5"><?= number_format((float) $inv['total'], 2, ',', '&nbsp;') ?>&nbsp;&euro;</span>
                                    <?php elseif ($st === 'overdue'): ?>
                                        <span class="td-amount" style="color:var(--rouge)"><?= number_format((float) $inv['total'], 2, ',', '&nbsp;') ?>&nbsp;&euro;</span>
                                    <?php else: ?>
                                        <span class="td-amount"><?= number_format((float) $inv['total'], 2, ',', '&nbsp;') ?>&nbsp;&euro;</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <div class="td-actions">
                                        <a href="/admin/invoices/<?= (int) $inv['id'] ?>" class="btn-icon" title="Voir" onclick="event.stopPropagation()"><?= icon('eye', 13) ?></a>
                                        <button class="btn-icon" title="Télécharger PDF" onclick="event.stopPropagation()"><?= icon('download', 13) ?></button>
                                        <button class="btn-icon" title="Envoyer par e-mail" onclick="event.stopPropagation()"><?= icon('send', 13) ?></button>
                                    </div>
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
                        Affichage <?= $start ?> – <?= $end ?> sur <?= $totalFiltered ?> factures
                    </div>
                    <div class="pagination-btns">
                        <?php
                            $baseUrl = '/admin/invoices?';
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

    <!-- PARAMÈTRES DE FACTURATION -->
    <form method="post" action="/admin/invoices/settings">
        <?= csrf_field() ?>
        <div class="settings-block">
            <div class="settings-title"><?= icon('settings', 16) ?> Paramètres de facturation</div>
            <div class="settings-grid">
                <div class="field">
                    <label>Nom de l'association</label>
                    <input type="text" name="billing_association_name" value="<?= e($billing['association_name'] ?? '') ?>" placeholder="Association la Fête du Cidre">
                </div>
                <div class="field">
                    <label>N° SIRET</label>
                    <input type="text" name="billing_siret" value="<?= e($billing['siret'] ?? '') ?>" placeholder="123 456 789 00012">
                </div>
                <div class="field">
                    <label>Adresse</label>
                    <input type="text" name="billing_address" value="<?= e($billing['address'] ?? '') ?>" placeholder="Parc du Drugeot, L'Hôtellerie de Flée, 49500">
                </div>
                <div class="field">
                    <label>E-mail facturation</label>
                    <input type="email" name="billing_email" value="<?= e($billing['email'] ?? '') ?>" placeholder="facturation@fetecidre.fr">
                </div>
                <div class="field">
                    <label>Préfixe numérotation</label>
                    <input type="text" name="billing_prefix" value="<?= e($billing['prefix'] ?? 'FAC-' . date('Y') . '-') ?>" placeholder="FAC-<?= date('Y') ?>-">
                    <div class="field-hint"><?= icon('info', 10) ?> Prochain numéro : <?= e($nextInvoiceNumber) ?></div>
                </div>
                <div class="field">
                    <label>Taux TVA par défaut</label>
                    <input type="text" name="billing_tva_rate" value="<?= e($billing['tva_rate'] ?? '5,5%') ?>" placeholder="5,5%">
                    <div class="field-hint"><?= icon('info', 10) ?> Produits alimentaires</div>
                </div>
                <div class="field" style="grid-column:1/-1">
                    <label>Mentions légales (pied de facture)</label>
                    <textarea name="billing_legal_mentions" rows="2" placeholder="Association loi 1901 — N° RNA…"><?= e($billing['legal_mentions'] ?? '') ?></textarea>
                </div>
            </div>
            <div class="settings-footer">
                <button type="submit" class="btn btn-primary"><?= icon('check', 14) ?> Enregistrer</button>
            </div>
        </div>
    </form>

</div>
