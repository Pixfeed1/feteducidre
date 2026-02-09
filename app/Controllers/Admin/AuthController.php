<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;
use App\Core\Response;

/**
 * Contrôleur d'authentification admin.
 * Gère le login, le logout et la limitation des tentatives de connexion.
 */
class AuthController extends Controller
{
    /** Nombre maximal de tentatives de connexion */
    private const MAX_ATTEMPTS = 5;

    /** Durée du blocage en secondes (15 minutes) */
    private const LOCKOUT_DURATION = 900;

    /**
     * Affiche le formulaire de connexion
     */
    public function loginForm(Request $request, array $params = []): void
    {
        // Si déjà connecté, rediriger vers le dashboard
        if (!empty($_SESSION['admin_user'])) {
            $this->redirect('/admin/dashboard');
            return;
        }

        $this->render('templates/admin/login.php', [
            'title' => 'Connexion',
        ], '');
    }

    /**
     * Traite la soumission du formulaire de connexion.
     * Vérifie le token CSRF, la limitation de tentatives, et les identifiants.
     */
    public function login(Request $request, array $params = []): void
    {
        // Vérifier le token CSRF
        $token = $request->post('_csrf_token', '');
        $sessionToken = $_SESSION['csrf_token'] ?? '';
        if (empty($token) || !hash_equals($sessionToken, $token)) {
            set_flash('error', 'Le formulaire a expiré. Veuillez réessayer.');
            $this->redirect('/admin/login');
            return;
        }

        $email = $request->post('email', '');
        $password = $request->post('password', '');
        $ip = $request->ip();

        // Vérifier la limitation de tentatives
        if ($this->isRateLimited($ip)) {
            set_flash('error', 'Trop de tentatives de connexion. Veuillez réessayer dans 15 minutes.');
            $this->redirect('/admin/login');
            return;
        }

        // Valider les champs requis
        if (empty($email) || empty($password)) {
            $_SESSION['_old_input'] = ['email' => $email];
            set_flash('error', 'Veuillez remplir tous les champs.');
            $this->redirect('/admin/login');
            return;
        }

        // Rechercher l'utilisateur en base
        $user = $this->db()->fetch(
            "SELECT * FROM users WHERE email = ? AND is_active = 1 LIMIT 1",
            [$email]
        );

        // Vérifier le mot de passe
        if (!$user || !password_verify($password, $user['password'])) {
            $this->recordFailedAttempt($ip);
            $_SESSION['_old_input'] = ['email' => $email];
            set_flash('error', 'Identifiants incorrects.');
            $this->redirect('/admin/login');
            return;
        }

        // Réinitialiser les tentatives
        $this->clearAttempts($ip);

        // Régénérer l'identifiant de session pour prévenir la fixation de session
        session_regenerate_id(true);

        // Stocker les informations de l'utilisateur en session
        $_SESSION['admin_user'] = [
            'id'         => $user['id'],
            'email'      => $user['email'],
            'first_name' => $user['first_name'],
            'last_name'  => $user['last_name'],
            'role'       => $user['role'],
        ];
        $_SESSION['admin_last_activity'] = time();

        // Mettre à jour la date de dernière connexion
        $this->db()->update('users', ['last_login' => date('Y-m-d H:i:s')], 'id = ?', [(int) $user['id']]);

        set_flash('success', 'Bienvenue, ' . e($user['first_name']) . ' !');
        $this->redirect('/admin/dashboard');
    }

    /**
     * Déconnecte l'utilisateur et détruit la session
     */
    public function logout(Request $request, array $params = []): void
    {
        $_SESSION = [];

        if (ini_get('session.use_cookies')) {
            $params = session_get_cookie_params();
            setcookie(
                session_name(),
                '',
                time() - 42000,
                $params['path'],
                $params['domain'],
                $params['secure'],
                $params['httponly']
            );
        }

        session_destroy();

        // Redémarrer une session pour le message flash
        session_start();
        set_flash('success', 'Vous avez été déconnecté.');
        $this->redirect('/admin/login');
    }

    /**
     * Vérifie si l'adresse IP est bloquée par la limitation de tentatives
     */
    private function isRateLimited(string $ip): bool
    {
        $key = 'login_attempts_' . md5($ip);
        $attempts = $_SESSION[$key] ?? [];

        // Nettoyer les tentatives expirées
        $cutoff = time() - self::LOCKOUT_DURATION;
        $attempts = array_filter($attempts, fn(int $ts) => $ts > $cutoff);
        $_SESSION[$key] = $attempts;

        return count($attempts) >= self::MAX_ATTEMPTS;
    }

    /**
     * Enregistre une tentative de connexion échouée
     */
    private function recordFailedAttempt(string $ip): void
    {
        $key = 'login_attempts_' . md5($ip);
        $attempts = $_SESSION[$key] ?? [];
        $attempts[] = time();
        $_SESSION[$key] = $attempts;
    }

    /**
     * Réinitialise les tentatives de connexion pour une IP
     */
    private function clearAttempts(string $ip): void
    {
        $key = 'login_attempts_' . md5($ip);
        unset($_SESSION[$key]);
    }
}
