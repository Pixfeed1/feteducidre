<?php

declare(strict_types=1);

namespace App\Controllers\Front;

use App\Core\Controller;
use App\Core\Request;
use App\Core\Response;

/**
 * Contrôleur des pages génériques (origines, infos, remerciements, etc.)
 */
class PageController extends Controller
{
    public function show(Request $request, array $params = []): void
    {
        $slug = ltrim($request->path(), '/');
        $db = $this->db();

        $page = $db->fetch(
            "SELECT id, title, slug, content, excerpt, meta_title, meta_description, hero_image, template
             FROM pages WHERE slug = ? AND status = ?",
            [$slug, 'published']
        );

        if (!$page) {
            Response::notFound();
            return;
        }

        $seo = [
            'title'       => $page['meta_title'] ?: $page['title'] . ' — Fête du Cidre',
            'description' => $page['meta_description'] ?: excerpt($page['content'] ?? '', 160),
            'canonical'   => \App\Core\Config::baseUrl() . '/' . $page['slug'],
        ];

        $this->render('templates/front/page.php', [
            'page' => $page,
            'seo'  => $seo,
        ]);
    }

    public function infos(Request $request, array $params = []): void
    {
        $db = $this->db();

        $page = $db->fetch(
            "SELECT id, title, slug, content, excerpt, meta_title, meta_description
             FROM pages WHERE slug = ? AND status = ?",
            ['infos-pratiques', 'published']
        );

        $settings = [];
        $rows = $db->fetchAll("SELECT `group`, `key`, value FROM settings WHERE `group` = 'general'");
        foreach ($rows as $row) {
            $settings[$row['group']][$row['key']] = $row['value'];
        }

        $seo = [
            'title'       => $page['meta_title'] ?? 'Infos Pratiques — Fête du Cidre',
            'description' => $page['meta_description'] ?? 'Toutes les informations pratiques pour la Fête du Cidre : accès, horaires, contact.',
            'canonical'   => \App\Core\Config::baseUrl() . '/infos-pratiques',
        ];

        $this->render('templates/front/infos.php', [
            'page'     => $page,
            'seo'      => $seo,
            'settings' => $settings,
        ]);
    }

    public function contact(Request $request, array $params = []): void
    {
        $db = $this->db();
        $page = $db->fetch(
            "SELECT id, title, slug, content, meta_title, meta_description FROM pages WHERE slug = ? AND status = ?",
            ['contact', 'published']
        );

        $settings = [];
        $rows = $db->fetchAll("SELECT `group`, `key`, value FROM settings WHERE `group` IN ('general', 'social')");
        foreach ($rows as $row) {
            $settings[$row['group']][$row['key']] = $row['value'];
        }

        $seo = [
            'title'       => $page['meta_title'] ?? 'Contact — Fête du Cidre',
            'description' => $page['meta_description'] ?? 'Contactez l\'association Fête du Cidre.',
            'canonical'   => \App\Core\Config::baseUrl() . '/contact',
        ];

        $this->render('templates/front/contact.php', [
            'page'     => $page,
            'seo'      => $seo,
            'settings' => $settings,
        ]);
    }

    public function contactSubmit(Request $request, array $params = []): void
    {
        // Validation CSRF
        $token = $request->post('_csrf_token');
        if (empty($token) || !hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
            set_flash('error', 'Le formulaire a expiré. Veuillez réessayer.');
            Response::redirect('/contact');
            return;
        }

        $name = $request->post('name', '');
        $email = $request->post('email', '');
        $subject = $request->post('subject', '');
        $message = $request->post('message', '');

        // Validation basique
        $errors = [];
        if (empty($name)) $errors[] = 'Le nom est requis.';
        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'Email invalide.';
        if (empty($message)) $errors[] = 'Le message est requis.';

        if (!empty($errors)) {
            $_SESSION['_old_input'] = $request->all();
            set_flash('error', implode(' ', $errors));
            Response::redirect('/contact');
            return;
        }

        // TODO: Envoyer l'email via MailService
        set_flash('success', 'Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.');
        unset($_SESSION['_old_input']);
        Response::redirect('/contact');
    }
}
