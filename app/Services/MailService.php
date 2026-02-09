<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;
use PHPMailer\PHPMailer\PHPMailer;

/**
 * Service d'envoi d'emails via PHPMailer.
 * Utilise des templates PHP pour le contenu des emails.
 */
class MailService
{
    private PHPMailer $mailer;

    public function __construct()
    {
        $this->mailer = new PHPMailer(true);

        // Configuration SMTP
        $this->mailer->isSMTP();
        $this->mailer->Host = Config::get('MAIL_HOST', 'smtp.mailtrap.io');
        $this->mailer->Port = (int) Config::get('MAIL_PORT', '587');
        $this->mailer->SMTPAuth = true;
        $this->mailer->Username = Config::get('MAIL_USER', '');
        $this->mailer->Password = Config::get('MAIL_PASS', '');
        $this->mailer->SMTPSecure = Config::get('MAIL_ENCRYPTION', 'tls');

        // Expéditeur par défaut
        $this->mailer->setFrom(
            Config::get('MAIL_FROM', 'noreply@fetecidre.fr'),
            Config::get('MAIL_FROM_NAME', 'Fête du Cidre')
        );

        $this->mailer->CharSet = 'UTF-8';
        $this->mailer->isHTML(true);
    }

    /**
     * Envoie un email avec un template
     *
     * @param string $to Adresse email du destinataire
     * @param string $subject Sujet de l'email
     * @param string $template Nom du template (sans extension)
     * @param array $data Variables à passer au template
     */
    public function send(string $to, string $subject, string $template, array $data = []): bool
    {
        try {
            $this->mailer->clearAddresses();
            $this->mailer->addAddress($to);
            $this->mailer->Subject = $subject;

            // Rendre le template
            $html = $this->renderTemplate($template, $data);
            $this->mailer->Body = $html;
            $this->mailer->AltBody = strip_tags(str_replace(['<br>', '<br/>', '<br />'], "\n", $html));

            return $this->mailer->send();
        } catch (\Exception $e) {
            error_log("Erreur envoi email : " . $e->getMessage());
            return false;
        }
    }

    /**
     * Rend un template email avec le layout
     */
    private function renderTemplate(string $template, array $data): string
    {
        extract($data);
        $basePath = dirname(__DIR__, 2) . '/templates/emails';

        // Capturer le contenu du template
        ob_start();
        $templateFile = $basePath . '/' . $template . '.php';
        if (file_exists($templateFile)) {
            include $templateFile;
        }
        $content = ob_get_clean();

        // Injecter dans le layout
        ob_start();
        $layoutFile = $basePath . '/_layout.php';
        if (file_exists($layoutFile)) {
            include $layoutFile;
        } else {
            echo $content;
        }

        return ob_get_clean();
    }
}
