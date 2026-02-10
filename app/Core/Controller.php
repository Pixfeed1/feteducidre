<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Contrôleur de base — fournit les méthodes communes à tous les contrôleurs.
 */
abstract class Controller
{
    /**
     * Rend un template avec des données
     */
    protected function render(string $template, array $data = [], string $layout = 'templates/front/layouts/base.php'): void
    {
        // Extraire les variables pour le template
        extract($data, EXTR_SKIP);

        // Capturer le contenu du template
        ob_start();
        $templatePath = dirname(__DIR__, 2) . '/' . $template;
        if (!file_exists($templatePath)) {
            ob_end_clean();
            throw new \RuntimeException("Template introuvable : {$template}");
        }
        include $templatePath;
        $content = ob_get_clean();

        // Inclure le layout (si spécifié)
        if (!empty($layout)) {
            $layoutPath = dirname(__DIR__, 2) . '/' . $layout;
            if (file_exists($layoutPath)) {
                include $layoutPath;
                return;
            }
        }

        echo $content;
    }

    /**
     * Rend un template admin
     */
    protected function renderAdmin(string $template, array $data = []): void
    {
        $this->render($template, $data, 'templates/admin/layouts/base.php');
    }

    /**
     * Redirige vers une URL
     */
    protected function redirect(string $url, int $status = 302): void
    {
        Response::redirect($url, $status);
    }

    /**
     * Réponse JSON
     */
    protected function json(mixed $data, int $status = 200): void
    {
        Response::json($data, $status);
    }

    /**
     * Valide le token CSRF d'une requête POST.
     * Redirige avec un message flash si invalide.
     *
     * @return bool true si valide, false si redirigé (le contrôleur doit return)
     */
    protected function validateCsrf(Request $request, string $redirectTo): bool
    {
        $token = $request->post('_csrf_token', '');
        if (!Security::validateCsrfToken($token)) {
            set_flash('error', 'Le formulaire a expiré. Veuillez réessayer.');
            $this->redirect($redirectTo);
            return false;
        }
        return true;
    }

    /**
     * Récupère l'instance de la base de données
     */
    protected function db(): Database
    {
        return Database::getInstance();
    }
}
