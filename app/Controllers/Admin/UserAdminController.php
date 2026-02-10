<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des utilisateurs administrateurs.
 */
class UserAdminController extends Controller
{
    /**
     * Liste tous les utilisateurs avec statistiques
     */
    public function index(Request $request, array $params = []): void
    {
        $users = $this->db()->fetchAll(
            "SELECT id, email, first_name, last_name, role, is_active, last_login, created_at
             FROM users ORDER BY role ASC, last_name ASC"
        );

        $totalUsers = count($users);
        $adminCount = 0;
        $editorCount = 0;
        foreach ($users as $u) {
            if ($u['role'] === 'admin') $adminCount++;
            else $editorCount++;
        }

        $currentUserId = (int) ($_SESSION['admin_user']['id'] ?? 0);

        $this->renderAdmin('templates/admin/users/index.php', [
            'title'         => 'Utilisateurs',
            'users'         => $users,
            'totalUsers'    => $totalUsers,
            'adminCount'    => $adminCount,
            'editorCount'   => $editorCount,
            'currentUserId' => $currentUserId,
        ]);
    }

    /**
     * Enregistre un nouvel utilisateur
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['email']) || empty($data['password']) || empty($data['first_name'])) {
            set_flash('error', 'L\'email, le prénom et le mot de passe sont obligatoires.');
            $this->redirect('/admin/users');
            return;
        }

        $existing = $this->db()->fetch("SELECT id FROM users WHERE email = ?", [$data['email']]);
        if ($existing) {
            set_flash('error', 'Un utilisateur avec cet email existe déjà.');
            $this->redirect('/admin/users');
            return;
        }

        if (strlen($data['password']) < 8) {
            set_flash('error', 'Le mot de passe doit contenir au moins 8 caractères.');
            $this->redirect('/admin/users');
            return;
        }

        $this->db()->insert('users', [
            'email'      => $data['email'],
            'password'   => password_hash($data['password'], PASSWORD_BCRYPT),
            'first_name' => $data['first_name'],
            'last_name'  => $data['last_name'] ?? '',
            'role'       => in_array($data['role'] ?? '', ['admin', 'editor'], true) ? $data['role'] : 'editor',
            'is_active'  => 1,
        ]);

        set_flash('success', 'Utilisateur créé avec succès.');
        $this->redirect('/admin/users');
    }

    /**
     * Met à jour un utilisateur existant
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['email']) || empty($data['first_name'])) {
            set_flash('error', 'L\'email et le prénom sont obligatoires.');
            $this->redirect('/admin/users');
            return;
        }

        $existing = $this->db()->fetch("SELECT id FROM users WHERE email = ? AND id != ?", [$data['email'], $id]);
        if ($existing) {
            set_flash('error', 'Un autre utilisateur utilise déjà cet email.');
            $this->redirect('/admin/users');
            return;
        }

        // Prevent removing last admin's role
        $currentUser = $this->db()->fetch("SELECT role FROM users WHERE id = ?", [$id]);
        if ($currentUser && $currentUser['role'] === 'admin' && ($data['role'] ?? '') !== 'admin') {
            $adminCount = (int) ($this->db()->fetch(
                "SELECT COUNT(*) AS total FROM users WHERE role = 'admin' AND id != ?",
                [$id]
            )['total'] ?? 0);

            if ($adminCount < 1) {
                set_flash('error', 'Impossible de modifier le rôle : il doit rester au moins un administrateur.');
                $this->redirect('/admin/users');
                return;
            }
        }

        $this->db()->update('users', [
            'email'      => $data['email'],
            'first_name' => $data['first_name'],
            'last_name'  => $data['last_name'] ?? '',
            'role'       => in_array($data['role'] ?? '', ['admin', 'editor'], true) ? $data['role'] : 'editor',
        ], 'id = ?', [$id]);

        // Update session if current user
        $currentSessionUserId = (int) ($_SESSION['admin_user']['id'] ?? 0);
        if ($currentSessionUserId === $id) {
            $_SESSION['admin_user']['email'] = $data['email'];
            $_SESSION['admin_user']['first_name'] = $data['first_name'];
            $_SESSION['admin_user']['last_name'] = $data['last_name'] ?? '';
            $_SESSION['admin_user']['role'] = in_array($data['role'] ?? '', ['admin', 'editor'], true) ? $data['role'] : 'editor';
        }

        set_flash('success', 'Utilisateur mis à jour.');
        $this->redirect('/admin/users');
    }

    /**
     * Supprime un utilisateur
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $currentUserId = (int) ($_SESSION['admin_user']['id'] ?? 0);

        if ($id === $currentUserId) {
            set_flash('error', 'Vous ne pouvez pas supprimer votre propre compte.');
            $this->redirect('/admin/users');
            return;
        }

        $user = $this->db()->fetch("SELECT role FROM users WHERE id = ?", [$id]);
        if ($user && $user['role'] === 'admin') {
            $adminCount = (int) ($this->db()->fetch(
                "SELECT COUNT(*) AS total FROM users WHERE role = 'admin' AND id != ?",
                [$id]
            )['total'] ?? 0);

            if ($adminCount < 1) {
                set_flash('error', 'Impossible de supprimer le dernier administrateur.');
                $this->redirect('/admin/users');
                return;
            }
        }

        $this->db()->delete('users', 'id = ?', [$id]);

        set_flash('success', 'Utilisateur supprimé.');
        $this->redirect('/admin/users');
    }

    /**
     * Modifie le mot de passe d'un utilisateur
     */
    public function changePassword(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        $user = $this->db()->fetch("SELECT id FROM users WHERE id = ?", [$id]);
        if (!$user) {
            set_flash('error', 'Utilisateur introuvable.');
            $this->redirect('/admin/users');
            return;
        }

        if (empty($data['password']) || strlen($data['password']) < 8) {
            set_flash('error', 'Le mot de passe doit contenir au moins 8 caractères.');
            $this->redirect('/admin/users');
            return;
        }

        if ($data['password'] !== ($data['password_confirmation'] ?? '')) {
            set_flash('error', 'Les mots de passe ne correspondent pas.');
            $this->redirect('/admin/users');
            return;
        }

        $this->db()->update('users', [
            'password' => password_hash($data['password'], PASSWORD_BCRYPT),
        ], 'id = ?', [$id]);

        set_flash('success', 'Mot de passe modifié avec succès.');
        $this->redirect('/admin/users');
    }
}
