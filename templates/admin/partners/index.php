<?php
/**
 * Liste des partenaires — administration.
 * Variables : $partners, $currentCategory
 */

$categoryMap = [
    'institutionnel' => 'Institutionnel',
    'entreprise'     => 'Entreprise',
    'media'          => 'Média',
    'associatif'     => 'Associatif',
    'autre'          => 'Autre',
];
?>

<div class="page-header">
    <h1><?= icon('heart', 24) ?> Partenaires</h1>
    <a href="/admin/partners/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouveau partenaire
    </a>
</div>

<!-- Filtres par catégorie -->
<div class="tabs mb-3">
    <a href="/admin/partners" class="tab-link <?= empty($currentCategory) ? 'active' : '' ?>">Tous</a>
    <?php foreach ($categoryMap as $key => $label): ?>
        <a href="/admin/partners?category=<?= $key ?>" class="tab-link <?= $currentCategory === $key ? 'active' : '' ?>">
            <?= $label ?>
        </a>
    <?php endforeach; ?>
</div>

<div class="card">
    <?php if (empty($partners)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('heart', 40) ?>
                <p>Aucun partenaire pour le moment.</p>
                <a href="/admin/partners/create" class="btn btn-primary mt-2">Ajouter un partenaire</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Catégorie</th>
                        <th>Site web</th>
                        <th>Ordre</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($partners as $partner): ?>
                        <tr>
                            <td><strong><?= e($partner['name']) ?></strong></td>
                            <td>
                                <span class="badge badge-info">
                                    <?= $categoryMap[$partner['category']] ?? e($partner['category']) ?>
                                </span>
                            </td>
                            <td>
                                <?php if (!empty($partner['website'])): ?>
                                    <a href="<?= e($partner['website']) ?>" target="_blank" class="text-muted">
                                        <?= icon('external-link', 14) ?> <?= e(parse_url($partner['website'], PHP_URL_HOST) ?: $partner['website']) ?>
                                    </a>
                                <?php else: ?>
                                    <span class="text-muted">-</span>
                                <?php endif; ?>
                            </td>
                            <td><?= (int) $partner['sort_order'] ?></td>
                            <td>
                                <?php if ($partner['is_active']): ?>
                                    <span class="badge badge-success">Actif</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary">Inactif</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/partners/<?= (int) $partner['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/partners/<?= (int) $partner['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer ce partenaire ?')">
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
