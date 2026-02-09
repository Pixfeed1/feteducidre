<?php
/**
 * Liste des éditions — administration.
 * Variables : $editions
 */
?>

<div class="page-header">
    <h1><?= icon('calendar', 24) ?> Éditions</h1>
    <a href="/admin/editions/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouvelle édition
    </a>
</div>

<div class="card">
    <?php if (empty($editions)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('calendar', 40) ?>
                <p>Aucune édition pour le moment.</p>
                <a href="/admin/editions/create" class="btn btn-primary mt-2">Ajouter une édition</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Année</th>
                        <th>Titre</th>
                        <th>Description</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($editions as $edition): ?>
                        <tr>
                            <td><strong><?= (int) $edition['year'] ?></strong></td>
                            <td><?= e($edition['title'] ?? '') ?></td>
                            <td class="text-muted"><?= e(truncate($edition['description'] ?? '', 80)) ?></td>
                            <td>
                                <?php if ($edition['is_active']): ?>
                                    <span class="badge badge-success">Active</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary">Inactive</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/editions/<?= (int) $edition['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/editions/<?= (int) $edition['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer cette édition ?')">
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
