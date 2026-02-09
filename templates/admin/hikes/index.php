<?php
/**
 * Liste des éditions de randonnée — administration.
 * Variables : $hikes
 */
?>

<div class="page-header">
    <h1><?= icon('mountain', 24) ?> Randonnées</h1>
    <a href="/admin/hikes/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouvelle randonnée
    </a>
</div>

<div class="card">
    <?php if (empty($hikes)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('mountain', 40) ?>
                <p>Aucune randonnée pour le moment.</p>
                <a href="/admin/hikes/create" class="btn btn-primary mt-2">Ajouter une randonnée</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Année</th>
                        <th>Titre</th>
                        <th>Date</th>
                        <th>Distance</th>
                        <th>Participants</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($hikes as $hike): ?>
                        <tr>
                            <td><strong><?= (int) $hike['year'] ?></strong></td>
                            <td><?= e($hike['title'] ?? '') ?></td>
                            <td class="text-muted"><?= $hike['date'] ? date_fr($hike['date']) : '-' ?></td>
                            <td><?= $hike['distance_km'] ? number_format((float) $hike['distance_km'], 1) . ' km' : '-' ?></td>
                            <td><?= $hike['participant_count'] ? (int) $hike['participant_count'] : '-' ?></td>
                            <td>
                                <?php if ($hike['is_active']): ?>
                                    <span class="badge badge-success">Active</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary">Inactive</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/hikes/<?= (int) $hike['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <form method="post" action="/admin/hikes/<?= (int) $hike['id'] ?>/delete"
                                          class="confirm-delete"
                                          onsubmit="return confirm('Supprimer cette randonnée et tous ses résultats ?')">
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
