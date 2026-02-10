<?php
/**
 * Utilisateurs — administration (liste + modals).
 * Variables : $users, $totalUsers, $adminCount, $editorCount, $currentUserId
 */

$avatarColors = ['#D4833B', '#2C4A2E', '#3B82F6', '#7A9E6B', '#5C3D2E', '#8B5CF6', '#EC4899'];

function getInitials(string $first, string $last): string
{
    $f = mb_strtoupper(mb_substr(trim($first), 0, 1));
    $l = $last ? mb_strtoupper(mb_substr(trim($last), 0, 1)) : '';
    return $f . $l;
}

function getAvatarColor(int $id, array $colors): string
{
    return $colors[$id % count($colors)];
}
?>

<!-- ===== Page header ===== -->
<div class="page-header">
    <div class="page-header-left" style="display:flex;align-items:center;gap:1rem;">
        <div class="page-header-icon" style="background:rgba(59,130,246,0.1);">
            <?= icon('users', 22, '', '#3B82F6') ?>
        </div>
        <div>
            <h1>Utilisateurs</h1>
            <p class="page-subtitle">Gérez les accès à l'administration</p>
        </div>
    </div>
    <button type="button" class="btn btn-primary" onclick="openAddModal()">
        <?= icon('user-plus', 16) ?> Ajouter un utilisateur
    </button>
</div>

<!-- ===== Stats ===== -->
<div class="stats-row" style="grid-template-columns:repeat(3,1fr);">
    <div class="stat-card">
        <div class="stat-icon" style="background:rgba(59,130,246,0.1)"><?= icon('users', 18, '', '#3B82F6') ?></div>
        <div>
            <div class="stat-value"><?= $totalUsers ?></div>
            <div class="stat-label">Utilisateurs</div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-icon" style="background:rgba(44,74,46,0.1)"><?= icon('shield', 18, '', '#2C4A2E') ?></div>
        <div>
            <div class="stat-value"><?= $adminCount ?></div>
            <div class="stat-label">Administrateurs</div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-icon" style="background:rgba(212,131,59,0.1)"><?= icon('pencil', 18, '', '#D4833B') ?></div>
        <div>
            <div class="stat-value"><?= $editorCount ?></div>
            <div class="stat-label">Éditeurs</div>
        </div>
    </div>
</div>

<!-- ===== Users list ===== -->
<?php if (empty($users)): ?>
    <div class="card">
        <div class="card-body">
            <div class="empty-state">
                <?= icon('users', 40) ?>
                <p>Aucun utilisateur pour le moment.</p>
            </div>
        </div>
    </div>
<?php else: ?>
    <div class="users-list">
        <?php foreach ($users as $u):
            $isCurrent = (int) $u['id'] === $currentUserId;
            $initials = getInitials($u['first_name'], $u['last_name']);
            $color = getAvatarColor((int) $u['id'], $avatarColors);
            $fullName = e(trim($u['first_name'] . ' ' . $u['last_name']));
        ?>
            <div class="user-card <?= $isCurrent ? 'current' : '' ?>">
                <div class="uc-avatar" style="background:<?= $color ?>"><?= $initials ?></div>
                <div class="uc-info">
                    <div class="uc-name">
                        <?= $fullName ?>
                        <?php if ($isCurrent): ?>
                            <span class="uc-you">VOUS</span>
                        <?php endif; ?>
                    </div>
                    <div class="uc-email"><?= e($u['email']) ?></div>
                    <div class="uc-meta">
                        <span class="uc-meta-item">
                            <?= icon('calendar', 11) ?>
                            Créé le <?= date_fr($u['created_at'], 'short') ?>
                        </span>
                        <span class="uc-meta-item">
                            <?= icon('clock', 11) ?>
                            Dernière connexion : <?= $u['last_login'] ? date_fr($u['last_login'], 'datetime') : 'Jamais' ?>
                        </span>
                    </div>
                </div>
                <?php if ($u['role'] === 'admin'): ?>
                    <span class="uc-role admin"><?= icon('shield', 10) ?> Admin</span>
                <?php else: ?>
                    <span class="uc-role editor"><?= icon('pencil', 10) ?> Éditeur</span>
                <?php endif; ?>
                <div class="uc-actions">
                    <button type="button" class="uc-btn" title="Modifier"
                            onclick="openEditModal(<?= (int) $u['id'] ?>, '<?= e(addslashes($u['first_name'])) ?>', '<?= e(addslashes($u['last_name'])) ?>', '<?= e(addslashes($u['email'])) ?>', '<?= e($u['role']) ?>')">
                        <?= icon('pencil', 14) ?>
                    </button>
                    <button type="button" class="uc-btn" title="Changer le mot de passe"
                            onclick="openPwModal(<?= (int) $u['id'] ?>, '<?= e(addslashes(trim($u['first_name'] . ' ' . $u['last_name']))) ?>', '<?= e(addslashes($u['email'])) ?>', '<?= $initials ?>', '<?= $color ?>')">
                        <?= icon('key-round', 14) ?>
                    </button>
                    <?php if (!$isCurrent): ?>
                        <button type="button" class="uc-btn danger" title="Supprimer"
                                onclick="openDeleteModal(<?= (int) $u['id'] ?>, '<?= e(addslashes(trim($u['first_name'] . ' ' . $u['last_name']))) ?>')">
                            <?= icon('trash-2', 14) ?>
                        </button>
                    <?php endif; ?>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
<?php endif; ?>

<!-- ===== MODAL: AJOUTER ===== -->
<div class="modal-overlay" id="addModal" onclick="if(event.target===this)closeModal('addModal')">
    <div class="modal">
        <div class="modal-header">
            <h2>Nouvel utilisateur</h2>
            <button type="button" class="modal-close" onclick="closeModal('addModal')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" action="/admin/users/store">
            <?= csrf_field() ?>
            <div class="modal-body">
                <div class="field-row">
                    <div class="field">
                        <label for="add_first_name">Prénom</label>
                        <input type="text" id="add_first_name" name="first_name" placeholder="Prénom" required>
                    </div>
                    <div class="field">
                        <label for="add_last_name">Nom</label>
                        <input type="text" id="add_last_name" name="last_name" placeholder="Nom">
                    </div>
                </div>
                <div class="field">
                    <label for="add_email">Adresse e-mail</label>
                    <input type="email" id="add_email" name="email" placeholder="utilisateur@fetecidre.fr" required>
                </div>
                <div class="field">
                    <label for="add_password">Mot de passe</label>
                    <input type="password" id="add_password" name="password" placeholder="Minimum 8 caractères" minlength="8" required>
                    <div class="field-hint"><?= icon('info', 11) ?> L'utilisateur pourra le modifier à sa prochaine connexion.</div>
                </div>
                <div class="field">
                    <label>Rôle</label>
                    <input type="hidden" name="role" id="add_role" value="admin">
                    <div class="role-picker">
                        <div class="role-card selected" onclick="selectRole(this, 'add_role', 'admin')">
                            <div class="role-card-icon" style="background:rgba(44,74,46,0.1)"><?= icon('shield', 18, '', '#2C4A2E') ?></div>
                            <div class="role-card-name">Administrateur</div>
                            <div class="role-card-desc">Accès complet à toutes les fonctionnalités</div>
                        </div>
                        <div class="role-card" onclick="selectRole(this, 'add_role', 'editor')">
                            <div class="role-card-icon" style="background:rgba(59,130,246,0.1)"><?= icon('pencil', 18, '', '#3B82F6') ?></div>
                            <div class="role-card-name">Éditeur</div>
                            <div class="role-card-desc">Contenu, galerie, événements. Pas de boutique ni paramètres.</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeModal('addModal')">Annuler</button>
                <button type="submit" class="btn btn-primary"><?= icon('user-plus', 14) ?> Créer</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== MODAL: MODIFIER ===== -->
<div class="modal-overlay" id="editModal" onclick="if(event.target===this)closeModal('editModal')">
    <div class="modal">
        <div class="modal-header">
            <h2>Modifier l'utilisateur</h2>
            <button type="button" class="modal-close" onclick="closeModal('editModal')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" id="editForm" action="">
            <?= csrf_field() ?>
            <div class="modal-body">
                <div class="field-row">
                    <div class="field">
                        <label for="edit_first_name">Prénom</label>
                        <input type="text" id="edit_first_name" name="first_name" required>
                    </div>
                    <div class="field">
                        <label for="edit_last_name">Nom</label>
                        <input type="text" id="edit_last_name" name="last_name">
                    </div>
                </div>
                <div class="field">
                    <label for="edit_email">Adresse e-mail</label>
                    <input type="email" id="edit_email" name="email" required>
                </div>
                <div class="field">
                    <label>Rôle</label>
                    <input type="hidden" name="role" id="edit_role" value="admin">
                    <div class="role-picker" id="edit_role_picker">
                        <div class="role-card" data-role="admin" onclick="selectRole(this, 'edit_role', 'admin')">
                            <div class="role-card-icon" style="background:rgba(44,74,46,0.1)"><?= icon('shield', 18, '', '#2C4A2E') ?></div>
                            <div class="role-card-name">Administrateur</div>
                            <div class="role-card-desc">Accès complet</div>
                        </div>
                        <div class="role-card" data-role="editor" onclick="selectRole(this, 'edit_role', 'editor')">
                            <div class="role-card-icon" style="background:rgba(59,130,246,0.1)"><?= icon('pencil', 18, '', '#3B82F6') ?></div>
                            <div class="role-card-name">Éditeur</div>
                            <div class="role-card-desc">Contenu uniquement</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeModal('editModal')">Annuler</button>
                <button type="submit" class="btn btn-primary"><?= icon('check', 14) ?> Enregistrer</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== MODAL: MOT DE PASSE ===== -->
<div class="modal-overlay" id="pwModal" onclick="if(event.target===this)closeModal('pwModal')">
    <div class="modal">
        <div class="modal-header">
            <h2>Changer le mot de passe</h2>
            <button type="button" class="modal-close" onclick="closeModal('pwModal')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" id="pwForm" action="">
            <?= csrf_field() ?>
            <div class="modal-body">
                <div class="pw-user-header">
                    <div class="uc-avatar" id="pw_avatar" style="width:38px;height:38px;font-size:0.85rem;"></div>
                    <div>
                        <div class="pw-user-name" id="pw_name"></div>
                        <div class="pw-user-email" id="pw_email"></div>
                    </div>
                </div>
                <div class="field">
                    <label for="pw_password">Nouveau mot de passe</label>
                    <input type="password" id="pw_password" name="password" placeholder="Minimum 8 caractères" minlength="8" required>
                </div>
                <div class="field">
                    <label for="pw_confirm">Confirmer le mot de passe</label>
                    <input type="password" id="pw_confirm" name="password_confirmation" placeholder="Retapez le mot de passe" minlength="8" required>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeModal('pwModal')">Annuler</button>
                <button type="submit" class="btn btn-primary"><?= icon('key-round', 14) ?> Modifier</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== MODAL: SUPPRIMER ===== -->
<div class="modal-overlay" id="deleteModal" onclick="if(event.target===this)closeModal('deleteModal')">
    <div class="modal confirm-modal">
        <div class="confirm-icon" style="background:#FEF2F2"><?= icon('user-x', 24, '', '#D94040') ?></div>
        <h3>Supprimer cet utilisateur ?</h3>
        <p id="delete_text">L'utilisateur n'aura plus accès à l'administration. Cette action est irréversible.</p>
        <form method="post" id="deleteForm" action="">
            <?= csrf_field() ?>
            <div class="confirm-btns">
                <button type="button" class="btn btn-secondary" onclick="closeModal('deleteModal')">Annuler</button>
                <button type="submit" class="btn btn-danger"><?= icon('trash-2', 14) ?> Supprimer</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== JavaScript ===== -->
<script>
function openModal(id) { document.getElementById(id).classList.add('show'); }
function closeModal(id) { document.getElementById(id).classList.remove('show'); }

function selectRole(el, inputId, value) {
    el.closest('.role-picker').querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById(inputId).value = value;
}

function openAddModal() {
    document.getElementById('add_first_name').value = '';
    document.getElementById('add_last_name').value = '';
    document.getElementById('add_email').value = '';
    document.getElementById('add_password').value = '';
    document.getElementById('add_role').value = 'admin';
    var picker = document.querySelector('#addModal .role-picker');
    picker.querySelectorAll('.role-card').forEach(function(c, i) { c.classList.toggle('selected', i === 0); });
    openModal('addModal');
}

function openEditModal(id, firstName, lastName, email, role) {
    document.getElementById('editForm').action = '/admin/users/' + id + '/update';
    document.getElementById('edit_first_name').value = firstName;
    document.getElementById('edit_last_name').value = lastName;
    document.getElementById('edit_email').value = email;
    document.getElementById('edit_role').value = role;
    document.getElementById('edit_role_picker').querySelectorAll('.role-card').forEach(function(c) {
        c.classList.toggle('selected', c.dataset.role === role);
    });
    openModal('editModal');
}

function openPwModal(id, name, email, initials, color) {
    document.getElementById('pwForm').action = '/admin/users/' + id + '/password';
    document.getElementById('pw_name').textContent = name;
    document.getElementById('pw_email').textContent = email;
    var avatar = document.getElementById('pw_avatar');
    avatar.textContent = initials;
    avatar.style.background = color;
    document.getElementById('pw_password').value = '';
    document.getElementById('pw_confirm').value = '';
    openModal('pwModal');
}

function openDeleteModal(id, name) {
    document.getElementById('deleteForm').action = '/admin/users/' + id + '/delete';
    document.getElementById('delete_text').textContent = name + ' n\'aura plus accès à l\'administration. Cette action est irréversible.';
    openModal('deleteModal');
}
</script>
