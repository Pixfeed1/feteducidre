<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($subject ?? 'Fête du Cidre') ?></title>
    <style>
        body { margin: 0; padding: 0; background: #FAF5EC; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #2A2318; }
        .email-wrapper { max-width: 600px; margin: 0 auto; padding: 20px; }
        .email-header { background: #2C4A2E; padding: 30px 24px; text-align: center; border-radius: 14px 14px 0 0; }
        .email-header h1 { color: #fff; font-size: 24px; margin: 0; font-family: Georgia, serif; }
        .email-body { background: #FFFDF8; padding: 32px 24px; }
        .email-body h2 { color: #2C4A2E; font-size: 20px; margin: 0 0 16px; font-family: Georgia, serif; }
        .email-body p { margin: 0 0 16px; line-height: 1.6; font-size: 15px; }
        .email-body a { color: #D4833B; }
        .email-btn { display: inline-block; background: #D4833B; color: #fff !important; padding: 12px 28px; border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 15px; margin: 8px 0; }
        .email-footer { background: #F0E8D8; padding: 20px 24px; text-align: center; border-radius: 0 0 14px 14px; font-size: 13px; color: #5C3D2E; }
        .email-footer a { color: #5C3D2E; }
        .info-box { background: #FAF5EC; border-left: 4px solid #2C4A2E; padding: 16px; margin: 16px 0; border-radius: 0 8px 8px 0; }
        .order-table { width: 100%; border-collapse: collapse; margin: 16px 0; }
        .order-table th { text-align: left; padding: 8px; border-bottom: 2px solid #F0E8D8; font-size: 13px; color: #5C3D2E; text-transform: uppercase; }
        .order-table td { padding: 8px; border-bottom: 1px solid #F0E8D8; font-size: 14px; }
        .order-total { font-weight: 700; font-size: 16px; color: #2C4A2E; }
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-header">
            <h1>Fête du Cidre</h1>
        </div>
        <div class="email-body">
            <?= $content ?>
        </div>
        <div class="email-footer">
            <p>Association Fête du Cidre — L'Hôtellerie de Flée, 49500</p>
            <p><a href="<?= \App\Core\Config::baseUrl() ?>">www.fetecidre.fr</a></p>
        </div>
    </div>
</body>
</html>
