<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Gestionnaire de réponse HTTP.
 */
class Response
{
    /**
     * Envoie une réponse HTML
     */
    public static function html(string $content, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: text/html; charset=UTF-8');
        echo $content;
    }

    /**
     * Envoie une réponse JSON
     */
    public static function json(mixed $data, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=UTF-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }

    /**
     * Redirige vers une URL
     */
    public static function redirect(string $url, int $status = 302): void
    {
        http_response_code($status);
        header('Location: ' . $url);
        exit;
    }

    /**
     * Page 404
     */
    public static function notFound(): void
    {
        http_response_code(404);
        header('Content-Type: text/html; charset=UTF-8');

        $templateFile = dirname(__DIR__, 2) . '/templates/front/errors/404.php';
        if (file_exists($templateFile)) {
            include $templateFile;
        } else {
            echo '<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>404 — Page non trouvée</title>'
                . '<style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#FAF5EC;color:#2A2318}'
                . '.c{text-align:center}.c h1{font-size:6rem;margin:0;color:#2C4A2E}.c p{font-size:1.2rem;margin:1rem 0}'
                . '.c a{color:#D4833B;text-decoration:none;font-weight:600}.c a:hover{text-decoration:underline}</style></head>'
                . '<body><div class="c"><h1>404</h1><p>Cette page n\'existe pas.</p><p><a href="/">Retour à l\'accueil</a></p></div></body></html>';
        }
        exit;
    }

    /**
     * Erreur serveur
     */
    public static function error(string $message = '', int $status = 500): void
    {
        http_response_code($status);
        header('Content-Type: text/html; charset=UTF-8');

        $debug = Config::isDebug();

        echo '<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>Erreur serveur</title>'
            . '<style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#FAF5EC;color:#2A2318}'
            . '.c{text-align:center;max-width:600px;padding:2rem}.c h1{font-size:3rem;margin:0;color:#c00}.c p{margin:1rem 0}'
            . '.c a{color:#D4833B;text-decoration:none;font-weight:600}'
            . '.debug{text-align:left;background:#fff;padding:1rem;border-radius:8px;margin-top:1rem;font-size:0.85rem;overflow:auto}</style></head>'
            . '<body><div class="c"><h1>Erreur</h1><p>Une erreur est survenue.</p>';

        if ($debug && $message) {
            echo '<div class="debug"><pre>' . htmlspecialchars($message) . '</pre></div>';
        }

        echo '<p><a href="/">Retour à l\'accueil</a></p></div></body></html>';
        exit;
    }
}
