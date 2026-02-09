<?php
/**
 * Liste des pages — administration.
 * Variables : $pages
 */
?>

<div class="page-header">
    <h1><?= icon('file-text', 24) ?> Pages</h1>
    <a href="/admin/pages/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouvelle page
    </a>
</div>

<div class="card">
    <?php if (empty($pages)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('file-text', 40) ?>
                <p>Aucune page pour le moment.</p>
                <a href="/admin/pages/create" class="btn btn-primary mt-2">Créer une page</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Titre</th>
                        <th>Slug</th>
                        <th>Template</th>
                        <th>Menu</th>
                        <th>Statut</th>
                        <th>Modifié le</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($pages as $page): ?>
                        <tr>
                            <td><strong><?= e($page['title']) ?></strong></td>
                            <td class="text-muted">/<?= e($page['slug']) ?></td>
                            <td><?= e($page['template']) ?></td>
                            <td>
                                <?php if ($page['in_menu']): ?>
                                    <span class="badge badge-success"><?= icon('check', 14) ?> Oui</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary">Non</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?php if ($page['status'] === 'published'): ?>
                                    <span class="badge badge-success">Publiée</span>
                                <?php else: ?>
                                    <span class="badge badge-warning">Brouillon</span>
                                <?php endif; ?>
                            </td>
                            <td class="text-muted"><?= date_fr($page['updated_at'], 'short') ?></td>
                            <td>
                                <div class="actions">
                                    <a href="/<?= e($page['slug']) ?>" class="btn btn-sm btn-secondary" target="_blank" title="Voir">
                                        <?= icon('eye', 16) ?>
                                    </a>
                                    <a href="/admin/pages/<?= (int) $page['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/pages/<?= (int) $page['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer cette page ?')">
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
