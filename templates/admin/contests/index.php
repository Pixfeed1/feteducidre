<?php
/**
 * Liste des résultats de concours — administration.
 * Variables : $results, $years, $currentYear
 */

$medalMap = [
    'or'      => ['Or', 'badge-or'],
    'argent'  => ['Argent', 'badge-argent'],
    'bronze'  => ['Bronze', 'badge-bronze'],
    'mention' => ['Mention', 'badge-secondary'],
];
?>

<div class="page-header">
    <h1><?= icon('trophy', 24) ?> Concours</h1>
    <a href="/admin/contests/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouveau résultat
    </a>
</div>

<!-- Filtres par année -->
<?php if (!empty($years)): ?>
    <div class="tabs mb-3">
        <a href="/admin/contests" class="tab-link <?= empty($currentYear) ? 'active' : '' ?>">Toutes</a>
        <?php foreach ($years as $year): ?>
            <a href="/admin/contests?year=<?= (int) $year ?>" class="tab-link <?= $currentYear == $year ? 'active' : '' ?>">
                <?= (int) $year ?>
            </a>
        <?php endforeach; ?>
    </div>
<?php endif; ?>

<div class="card">
    <?php if (empty($results)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('trophy', 40) ?>
                <p>Aucun résultat de concours pour le moment.</p>
                <a href="/admin/contests/create" class="btn btn-primary mt-2">Ajouter un résultat</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Année</th>
                        <th>Catégorie</th>
                        <th>Rang</th>
                        <th>Producteur</th>
                        <th>Ville</th>
                        <th>Produit</th>
                        <th>Note</th>
                        <th>Médaille</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($results as $result): ?>
                        <tr>
                            <td><?= (int) $result['year'] ?></td>
                            <td><?= e($result['category']) ?></td>
                            <td><strong><?= (int) $result['rank'] ?></strong></td>
                            <td><?= e($result['producer_name']) ?></td>
                            <td class="text-muted"><?= e($result['producer_city'] ?? '-') ?></td>
                            <td><?= e($result['product_name'] ?? '-') ?></td>
                            <td><?= $result['score'] !== null ? number_format((float) $result['score'], 1) . '/20' : '-' ?></td>
                            <td>
                                <?php if (!empty($result['medal'])):
                                    $m = $medalMap[$result['medal']] ?? ['?', 'badge-secondary'];
                                ?>
                                    <span class="badge <?= $m[1] ?>"><?= $m[0] ?></span>
                                <?php else: ?>
                                    -
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/contests/<?= (int) $result['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/contests/<?= (int) $result['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer ce résultat ?')">
                                        <?= csrf_field() ?>
                                        <button type="submit" class="btn btn-sm btn-danger" title="Supprimer">
                                            <?= icon('trash-2', 16) ?>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
