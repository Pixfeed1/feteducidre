<?php
/**
 * Formulaire de création/modification d'un utilisateur.
 * Variables : $user (null si création)
 */

$isEdit = $user !== null;
$action = $isEdit ? '/admin/users/' . (int) $user['id'] . '/update' : '/admin/users/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier l\'utilisateur' : icon('plus', 24) . ' Nouvel utilisateur' ?></h1>
    <a href="/admin/users" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-header">
            <h2>Informations du compte</h2>
        </div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">Prénom *</label>
                    <input type="text" id="first_name" name="first_name" class="form-control"
                           value="<?= e($isEdit ? $user['first_name'] : old('first_name')) ?>"
                           required>
                </div>
                <div class="form-group">
                    <label for="last_name">Nom</label>
                    <input type="text" id="last_name" name="last_name" class="form-control"
                           value="<?= e($isEdit ? ($user['last_name'] ?? '') : old('last_name')) ?>">
                </div>
            </div>

            <div class="form-group">
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" class="form-control"
                       value="<?= e($isEdit ? $user['email'] : old('email')) ?>"
                       required>
            </div>

            <?php if (!$isEdit): ?>
                <div class="form-group">
                    <label for="password">Mot de passe *</label>
                    <input type="password" id="password" name="password" class="form-control"
                           minlength="8" required>
                    <div class="form-hint">Minimum 8 caractères.</div>
                </div>
            <?php endif; ?>

            <div class="form-row">
                <div class="form-group">
                    <label for="role">Rôle</label>
                    <select id="role" name="role" class="form-control">
                        <?php $currentRole = $isEdit ? $user['role'] : old('role', 'editor'); ?>
                        <option value="editor" <?= $currentRole === 'editor' ? 'selected' : '' ?>>Éditeur</option>
                        <option value="admin" <?= $currentRole === 'admin' ? 'selected' : '' ?>>Administrateur</option>
                    </select>
                    <div class="form-hint">Les administrateurs ont accès à tous les paramètres et à la gestion des utilisateurs.</div>
                </div>
                <div class="form-group">
                    <div class="form-check" style="margin-top: 1.75rem;">
                        <input type="checkbox" id="is_active" name="is_active" value="1"
                               <?= ($isEdit ? $user['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                        <label for="is_active">Compte actif</label>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/admin/users" class="btn btn-secondary">Annuler</a>
            <button type="submit" class="btn btn-primary">
                <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer l\'utilisateur' ?>
            </button>
        </div>
    </div>
</form>

<?php if ($isEdit): ?>
    <!-- Modification du mot de passe -->
    <form method="post" action="/admin/users/<?= (int) $user['id'] ?>/password">
        <?= csrf_field() ?>

        <div class="card">
            <div class="card-header">
                <h2><?= icon('lock', 20) ?> Modifier le mot de passe</h2>
            </div>
            <div class="card-body">
                <div class="form-row">
                    <div class="form-group">
                        <label for="new_password">Nouveau mot de passe</label>
                        <input type="password" id="new_password" name="password" class="form-control"
                               minlength="8" required>
                        <div class="form-hint">Minimum 8 caractères.</div>
                    </div>
                    <div class="form-group">
                        <label for="password_confirmation">Confirmer le mot de passe</label>
                        <input type="password" id="password_confirmation" name="password_confirmation" class="form-control"
                               minlength="8" required>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-warning">
                    <?= icon('lock', 18) ?> Changer le mot de passe
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>
