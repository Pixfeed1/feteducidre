<?php
/**
 * Tableau de bord — statistiques, actions rapides, tables récentes.
 * Variables : $orderCount, $revenue, $pageCount, $productCount,
 *             $recentOrders, $recentPages, $recentProducts, $pendingOrders
 */

$adminUser = $_SESSION['admin_user'] ?? [];
$firstName = e($adminUser['first_name'] ?? 'Admin');
?>

<!-- WELCOME -->
<div class="dash-welcome">
    <div>
        <h1>Bonjour, <span><?= $firstName ?></span></h1>
        <p>Voici un aperçu de l'activité de la Fête du Cidre</p>
    </div>
    <div class="dash-welcome-actions">
        <a href="/admin/pages/create" class="btn btn-primary">
            <?= icon('plus', 16) ?> Nouvelle page
        </a>
        <a href="/admin/products/create" class="btn btn-secondary">
            <?= icon('wine', 16) ?> Ajouter un produit
        </a>
    </div>
</div>

<!-- STATS -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon" style="background:#F0FDF4">
            <?= icon('eye', 20, '', '#22c55e') ?>
        </div>
        <div class="stat-info">
            <span class="stat-label">Pages publiées</span>
            <div class="stat-value"><?= $pageCount ?></div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-icon" style="background:#FFF7ED">
            <?= icon('shopping-bag', 20, '', 'var(--orange-cidre, #D4833B)') ?>
        </div>
        <div class="stat-info">
            <span class="stat-label">Commandes</span>
            <div class="stat-value"><?= $orderCount ?></div>
            <?php if ($pendingOrders > 0): ?>
                <span class="stat-change down"><?= $pendingOrders ?> en attente</span>
            <?php endif; ?>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-icon" style="background:#EEF2FF">
            <?= icon('euro', 20, '', '#3B82F6') ?>
        </div>
        <div class="stat-info">
            <span class="stat-label">Chiffre d'affaires</span>
            <div class="stat-value"><?= number_format($revenue, 2, ',', ' ') ?> &euro;</div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-icon" style="background:var(--creme, #FAF5EC)">
            <?= icon('wine', 20, '', 'var(--vert-mousse, #4A6B3E)') ?>
        </div>
        <div class="stat-info">
            <span class="stat-label">Produits</span>
            <div class="stat-value"><?= $productCount ?></div>
        </div>
    </div>
</div>

<!-- QUICK ACTIONS -->
<div class="quick-actions">
    <a class="qa-card" href="/admin/pages/create">
        <div class="qa-icon" style="background:var(--vert-profond, #2C4A2E)">
            <?= icon('file-pen', 22, '', 'white') ?>
        </div>
        <span class="qa-label">Créer une page</span>
        <span class="qa-desc">Éditeur avec la charte graphique</span>
    </a>
    <a class="qa-card" href="/admin/albums">
        <div class="qa-icon" style="background:var(--orange-cidre, #D4833B)">
            <?= icon('image-plus', 22, '', 'white') ?>
        </div>
        <span class="qa-label">Ajouter des photos</span>
        <span class="qa-desc">Galerie, albums, affiches</span>
    </a>
    <a class="qa-card" href="/admin/products/create">
        <div class="qa-icon" style="background:var(--brun, #5C3D2E)">
            <?= icon('wine', 22, '', 'white') ?>
        </div>
        <span class="qa-label">Nouveau produit</span>
        <span class="qa-desc">Cidre, jus, coffret…</span>
    </a>
    <a class="qa-card" href="/admin/invoices">
        <div class="qa-icon" style="background:#3B82F6">
            <?= icon('receipt', 22, '', 'white') ?>
        </div>
        <span class="qa-label">Générer une facture</span>
        <span class="qa-desc">PDF auto depuis commande</span>
    </a>
</div>

<!-- TWO COL: PAGES + ORDERS -->
<div class="sections-grid">

    <!-- PAGES -->
    <div class="section-card">
        <div class="section-header">
            <div class="section-header-left">
                <div class="sh-icon" style="background:var(--vert-profond, #2C4A2E)">
                    <?= icon('file-text', 16, '', 'white') ?>
                </div>
                <span class="sh-title">Pages</span>
            </div>
            <a href="/admin/pages" class="sh-action">
                Tout voir <?= icon('chevron-right', 12) ?>
            </a>
        </div>
        <?php if (empty($recentPages)): ?>
            <div style="padding:2rem;text-align:center;color:#888">
                <?= icon('file-text', 32) ?>
                <p style="margin-top:0.5rem;font-size:0.85rem">Aucune page pour le moment.</p>
            </div>
        <?php else: ?>
            <table class="mini-table">
                <?php foreach ($recentPages as $page): ?>
                    <tr>
                        <td>
                            <div class="table-name">
                                <div class="table-icon" style="background:#F0FDF4">
                                    <?= icon('file-text', 14, '', '#22c55e') ?>
                                </div>
                                <?= e($page['title']) ?>
                            </div>
                        </td>
                        <td>
                            <?php if (($page['status'] ?? 'draft') === 'published'): ?>
                                <span class="status published">&#9679; Publié</span>
                            <?php else: ?>
                                <span class="status draft">&#9679; Brouillon</span>
                            <?php endif; ?>
                        </td>
                        <td class="table-meta"><?= time_ago($page['updated_at'] ?? $page['created_at']) ?></td>
                        <td>
                            <div class="table-actions">
                                <a class="ta-btn" href="/admin/pages/<?= (int) $page['id'] ?>/edit" title="Modifier">
                                    <?= icon('pencil', 13) ?>
                                </a>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </table>
        <?php endif; ?>
    </div>

    <!-- ORDERS -->
    <div class="section-card">
        <div class="section-header">
            <div class="section-header-left">
                <div class="sh-icon" style="background:var(--orange-cidre, #D4833B)">
                    <?= icon('shopping-bag', 16, '', 'white') ?>
                </div>
                <span class="sh-title">Dernières commandes</span>
            </div>
            <a href="/admin/orders" class="sh-action">
                Tout voir <?= icon('chevron-right', 12) ?>
            </a>
        </div>
        <?php if (empty($recentOrders)): ?>
            <div style="padding:2rem;text-align:center;color:#888">
                <?= icon('shopping-cart', 32) ?>
                <p style="margin-top:0.5rem;font-size:0.85rem">Aucune commande pour le moment.</p>
            </div>
        <?php else: ?>
            <table class="mini-table">
                <?php
                $orderStatusMap = [
                    'pending'    => ['En cours', 'pending-status'],
                    'paid'       => ['Payée', 'published'],
                    'processing' => ['En traitement', 'pending-status'],
                    'shipped'    => ['Expédié', 'published'],
                    'delivered'  => ['Livré', 'published'],
                    'cancelled'  => ['Annulée', 'draft'],
                    'refunded'   => ['Remboursée', 'draft'],
                ];
                ?>
                <?php foreach ($recentOrders as $order): ?>
                    <tr>
                        <td>
                            <a href="/admin/orders/<?= (int) $order['id'] ?>" class="table-name" style="font-weight:700;font-size:.88rem">
                                <?= e($order['reference']) ?>
                            </a>
                        </td>
                        <td><?= e($order['customer_first_name'] . ' ' . $order['customer_last_name']) ?></td>
                        <td style="font-weight:700;color:var(--vert-profond, #2C4A2E)">
                            <?= number_format((float) $order['total'], 2, ',', ' ') ?> &euro;
                        </td>
                        <td>
                            <?php $os = $orderStatusMap[$order['status']] ?? ['Inconnu', 'draft']; ?>
                            <span class="status <?= $os[1] ?>">&#9679; <?= $os[0] ?></span>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </table>
        <?php endif; ?>
    </div>
</div>

<!-- PRODUCTS TABLE -->
<?php if (!empty($recentProducts)): ?>
    <div class="full-section">
        <div class="section-header">
            <div class="section-header-left">
                <div class="sh-icon" style="background:var(--brun, #5C3D2E)">
                    <?= icon('wine', 16, '', 'white') ?>
                </div>
                <span class="sh-title">Produits</span>
            </div>
            <a href="/admin/products" class="sh-action">
                Gérer <?= icon('chevron-right', 12) ?>
            </a>
        </div>
        <table class="full-table">
            <thead>
                <tr>
                    <th>Produit</th>
                    <th>Prix</th>
                    <th>Stock</th>
                    <th>Statut</th>
                    <th style="text-align:right">Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($recentProducts as $product): ?>
                    <tr>
                        <td>
                            <div class="product-cell">
                                <div class="pc-thumb" style="background:linear-gradient(135deg, var(--vert-profond), var(--vert-mousse))">
                                    <?= icon('wine', 18, '', 'white') ?>
                                </div>
                                <div>
                                    <div class="pc-name"><?= e($product['name']) ?></div>
                                    <?php if (!empty($product['short_description'])): ?>
                                        <div class="pc-cat"><?= e(mb_strimwidth($product['short_description'], 0, 40, '…')) ?></div>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </td>
                        <td class="price-cell"><?= number_format((float) $product['price'], 2, ',', ' ') ?> &euro;</td>
                        <td>
                            <?php
                            $stock = (int) ($product['stock'] ?? 0);
                            $stockClass = $stock <= 10 ? 'low' : 'ok';
                            ?>
                            <span class="stock-cell <?= $stockClass ?>"><?= $stock ?></span>
                        </td>
                        <td>
                            <?php if ($stock <= 0): ?>
                                <span class="status draft">&#9679; Rupture</span>
                            <?php elseif ($stock <= 10): ?>
                                <span class="status pending-status">&#9679; Stock bas</span>
                            <?php else: ?>
                                <span class="status published">&#9679; En ligne</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <div class="table-actions">
                                <a class="ta-btn" href="/admin/products/<?= (int) $product['id'] ?>/edit" title="Modifier">
                                    <?= icon('pencil', 13) ?>
                                </a>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
<?php endif; ?>
