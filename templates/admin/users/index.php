<?php
/**
 * Liste des utilisateurs — administration.
 * Variables : $users
 */

$currentUserId = (int) ($_SESSION['admin_user']['id'] ?? 0);
?>

<div class="page-header">
    <h1><?= icon('users', 24) ?> Utilisateurs</h1>
    <a href="/admin/users/create" class="btn btn-primary">
        <?= icon('plus', 18) ?> Nouvel utilisateur
    </a>
</div>

<div class="card">
    <?php if (empty($users)): ?>
        <div class="card-body">
            <div class="empty-state">
                <?= icon('users', 40) ?>
                <p>Aucun utilisateur pour le moment.</p>
                <a href="/admin/users/create" class="btn btn-primary mt-2">Créer un utilisateur</a>
            </div>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Email</th>
                        <th>Rôle</th>
                        <th>Statut</th>
                        <th>Dernière connexion</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                        <tr>
                            <td>
                                <strong><?= e($user['first_name'] . ' ' . $user['last_name']) ?></strong>
                                <?php if ((int) $user['id'] === $currentUserId): ?>
                                    <span class="badge badge-info">Vous</span>
                                <?php endif; ?>
                            </td>
                            <td class="text-muted"><?= e($user['email']) ?></td>
                            <td>
                                <?php if ($user['role'] === 'admin'): ?>
                                    <span class="badge badge-warning"><?= icon('shield', 12) ?> Admin</span>
                                <?php else: ?>
                                    <span class="badge badge-secondary"><?= icon('edit', 12) ?> Éditeur</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?php if ($user['is_active']): ?>
                                    <span class="badge badge-success">Actif</span>
                                <?php else: ?>
                                    <span class="badge badge-danger">Inactif</span>
                                <?php endif; ?>
                            </td>
                            <td class="text-muted">
                                <?= $user['last_login'] ? date_fr($user['last_login'], 'datetime') : 'Jamais' ?>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="/admin/users/<?= (int) $user['id'] ?>/edit" class="btn btn-sm btn-secondary" title="Modifier">
                                        <?= icon('edit', 16) ?>
                                    </a>
                                    <?php if ((int) $user['id'] !== $currentUserId): ?>
                                        <form method="post" action="/admin/users/<?= (int) $user['id'] ?>/delete"
                                              class="confirm-delete"
                                              onsubmit="return confirm('Supprimer cet utilisateur ?')">
                                            <?= csrf_field() ?>
                                            <button type="submit" class="btn btn-sm btn-danger" title="Supprimer">
                                                <?= icon('trash-2', 16) ?>
                                            </button>
                                        </form>
                                    <?php endif; ?>
                                </div>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
