<?php
/**
 * Liste des albums photos — administration.
 * Variables : $albums
 */
?>

<div class="page-header">
    <h1><?= icon('images', 24) ?> Galerie</h1>
    <a href="/admin/albums/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouvel album
    </a>
</div>

<div class="card">
    <?php if (empty($albums)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('images', 40) ?>
                <p>Aucun album pour le moment.</p>
                <a href="/admin/albums/create" class="btn btn-primary mt-2">Créer un album</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Titre</th>
                        <th>Année</th>
                        <th>Photos</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($albums as $album): ?>
                        <tr>
                            <td><strong><?= e($album['title']) ?></strong></td>
                            <td><?= $album['year'] ? (int) $album['year'] : '-' ?></td>
                            <td>
                                <?= icon('image', 16) ?>
                                <?= (int) $album['photo_count'] ?>
                            </td>
                            <td>
                                <?php if ($album['is_active']): ?>
                                    <span class="badge badge-success">Actif</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary">Inactif</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/albums/<?= (int) $album['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/albums/<?= (int) $album['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer cet album et toutes ses photos ?')">
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
