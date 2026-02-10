<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Config;
use App\Core\Controller;
use App\Core\Request;
use App\Core\Response;
use App\Services\MailService;

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
        if (!$this->validateCsrf($request, '/admin/login')) {
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
     * Affiche le formulaire de mot de passe oublié
     */
    public function forgotPasswordForm(Request $request, array $params = []): void
    {
        if (!empty($_SESSION['admin_user'])) {
            $this->redirect('/admin/dashboard');
            return;
        }

        $this->render('templates/admin/forgot-password.php', [
            'title' => 'Mot de passe oublié',
        ], '');
    }

    /**
     * Traite la demande de réinitialisation de mot de passe
     */
    public function forgotPassword(Request $request, array $params = []): void
    {
        if (!$this->validateCsrf($request, '/admin/forgot-password')) {
            return;
        }

        $email = trim($request->post('email', ''));

        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $_SESSION['_old_input'] = ['email' => $email];
            set_flash('error', 'Veuillez saisir une adresse e-mail valide.');
            $this->redirect('/admin/forgot-password');
            return;
        }

        $user = $this->db()->fetch(
            "SELECT id, email FROM users WHERE email = ? AND is_active = 1 LIMIT 1",
            [$email]
        );

        // Toujours afficher le succès pour ne pas révéler si l'email existe
        if ($user) {
            $resetToken = bin2hex(random_bytes(32));
            $expires = date('Y-m-d H:i:s', time() + 3600);

            $this->db()->update('users', [
                'reset_token'   => hash('sha256', $resetToken),
                'reset_expires' => $expires,
            ], 'id = ?', [(int) $user['id']]);

            $resetUrl = Config::baseUrl() . '/admin/reset-password/' . $resetToken;

            try {
                $mailer = new MailService();
                $mailer->send($user['email'], 'Réinitialisation de mot de passe', 'reset-password', [
                    'email'     => $user['email'],
                    'reset_url' => $resetUrl,
                    'expiry'    => '1 heure',
                ]);
            } catch (\Exception $e) {
                error_log('Erreur envoi email reset: ' . $e->getMessage());
            }
        }

        $_SESSION['reset_email_sent'] = $email;
        set_flash('success', 'Si un compte existe avec cette adresse, un e-mail de réinitialisation a été envoyé.');
        $this->redirect('/admin/forgot-password');
    }

    /**
     * Affiche le formulaire de réinitialisation de mot de passe
     */
    public function resetPasswordForm(Request $request, array $params = []): void
    {
        $token = $params['token'] ?? '';

        if (empty($token)) {
            set_flash('error', 'Lien de réinitialisation invalide.');
            $this->redirect('/admin/login');
            return;
        }

        $hashedToken = hash('sha256', $token);
        $user = $this->db()->fetch(
            "SELECT id, email FROM users WHERE reset_token = ? AND reset_expires > NOW() AND is_active = 1 LIMIT 1",
            [$hashedToken]
        );

        if (!$user) {
            set_flash('error', 'Ce lien de réinitialisation est invalide ou a expiré.');
            $this->redirect('/admin/forgot-password');
            return;
        }

        $this->render('templates/admin/reset-password.php', [
            'title' => 'Nouveau mot de passe',
            'token' => $token,
            'email' => $user['email'],
        ], '');
    }

    /**
     * Traite la réinitialisation du mot de passe
     */
    public function resetPassword(Request $request, array $params = []): void
    {
        if (!$this->validateCsrf($request, '/admin/login')) {
            return;
        }

        $token = $params['token'] ?? '';
        $password = $request->post('password', '');
        $passwordConfirm = $request->post('password_confirm', '');

        if (empty($token)) {
            set_flash('error', 'Lien de réinitialisation invalide.');
            $this->redirect('/admin/login');
            return;
        }

        $hashedToken = hash('sha256', $token);
        $user = $this->db()->fetch(
            "SELECT id, email FROM users WHERE reset_token = ? AND reset_expires > NOW() AND is_active = 1 LIMIT 1",
            [$hashedToken]
        );

        if (!$user) {
            set_flash('error', 'Ce lien de réinitialisation est invalide ou a expiré.');
            $this->redirect('/admin/forgot-password');
            return;
        }

        // Validation du mot de passe
        if (strlen($password) < 8) {
            set_flash('error', 'Le mot de passe doit contenir au moins 8 caractères.');
            $this->redirect('/admin/reset-password/' . $token);
            return;
        }

        if ($password !== $passwordConfirm) {
            set_flash('error', 'Les mots de passe ne correspondent pas.');
            $this->redirect('/admin/reset-password/' . $token);
            return;
        }

        // Mettre à jour le mot de passe et supprimer le token
        $this->db()->update('users', [
            'password'      => password_hash($password, PASSWORD_DEFAULT),
            'reset_token'   => null,
            'reset_expires' => null,
        ], 'id = ?', [(int) $user['id']]);

        // Envoyer email de confirmation
        try {
            $mailer = new MailService();
            $mailer->send($user['email'], 'Mot de passe modifié', 'password-changed', [
                'email' => $user['email'],
                'date'  => date('d/m/Y H:i'),
                'ip'    => $request->ip(),
            ]);
        } catch (\Exception $e) {
            error_log('Erreur envoi email confirmation: ' . $e->getMessage());
        }

        set_flash('success', 'Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.');
        $this->redirect('/admin/login');
    }

    /**
     * Vérifie si l'adresse IP est bloquée par la limitation de tentatives.
     * Délègue à Security::rateLimit() (stockage fichier, indépendant de la session).
     */
    private function isRateLimited(string $ip): bool
    {
        $key = 'login_' . $ip;
        $filePath = dirname(__DIR__, 3) . '/cache/ratelimit/' . md5($key) . '.json';

        if (!file_exists($filePath)) {
            return false;
        }

        $content = file_get_contents($filePath);
        $data = $content !== false ? json_decode($content, true) : [];
        if (!is_array($data)) {
            return false;
        }

        $cutoff = time() - self::LOCKOUT_DURATION;
        $recent = array_filter($data, fn(int $ts) => $ts > $cutoff);

        return count($recent) >= self::MAX_ATTEMPTS;
    }

    /**
     * Enregistre une tentative de connexion échouée (stockage fichier).
     */
    private function recordFailedAttempt(string $ip): void
    {
        \App\Core\Security::rateLimit('login_' . $ip, self::MAX_ATTEMPTS, self::LOCKOUT_DURATION);
    }

    /**
     * Réinitialise les tentatives de connexion pour une IP.
     */
    private function clearAttempts(string $ip): void
    {
        $filePath = dirname(__DIR__, 3) . '/cache/ratelimit/' . md5('login_' . $ip) . '.json';
        if (file_exists($filePath)) {
            unlink($filePath);
        }
    }
}
