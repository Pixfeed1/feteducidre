<?php

/**
 * Installateur web — Fête du Cidre CMS.
 * Vérifie les prérequis, configure la BDD, crée l'admin, exécute les migrations.
 * Se verrouille après installation via storage/.installed
 */

declare(strict_types=1);

$basePath = dirname(__DIR__);
$lockFile = $basePath . '/storage/.installed';

// Vérifier si déjà installé
if (file_exists($lockFile)) {
    header('Location: /admin');
    exit;
}

$step = $_GET['step'] ?? '1';
$errors = [];
$success = false;

// ── Étape 1 : Prérequis ──
function checkPrerequisites(): array
{
    $checks = [];

    // PHP version
    $checks['php_version'] = [
        'label'  => 'PHP >= 8.2',
        'status' => version_compare(PHP_VERSION, '8.2.0', '>='),
        'value'  => PHP_VERSION,
    ];

    // Extensions
    $extensions = ['pdo', 'pdo_mysql', 'mbstring', 'gd', 'json', 'fileinfo', 'intl'];
    foreach ($extensions as $ext) {
        $checks["ext_{$ext}"] = [
            'label'  => "Extension {$ext}",
            'status' => extension_loaded($ext),
            'value'  => extension_loaded($ext) ? 'OK' : 'Manquante',
        ];
    }

    // Composer
    $checks['composer'] = [
        'label'  => 'Dépendances Composer',
        'status' => file_exists(dirname(__DIR__) . '/vendor/autoload.php'),
        'value'  => file_exists(dirname(__DIR__) . '/vendor/autoload.php') ? 'Installées' : 'Manquantes',
    ];

    // Permissions d'écriture
    $writableDirs = ['cache', 'storage', 'storage/uploads', 'storage/logs'];
    foreach ($writableDirs as $dir) {
        $fullPath = dirname(__DIR__) . '/' . $dir;
        $writable = is_dir($fullPath) && is_writable($fullPath);
        $checks["writable_{$dir}"] = [
            'label'  => "Écriture {$dir}/",
            'status' => $writable,
            'value'  => $writable ? 'OK' : 'Non accessible',
        ];
    }

    return $checks;
}

// ── Traitement du formulaire ──
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $step = $_POST['step'] ?? '2';

    if ($step === '2') {
        // Test connexion BDD
        $dbHost = trim($_POST['db_host'] ?? 'localhost');
        $dbPort = trim($_POST['db_port'] ?? '3306');
        $dbName = trim($_POST['db_name'] ?? '');
        $dbUser = trim($_POST['db_user'] ?? '');
        $dbPass = $_POST['db_pass'] ?? '';

        try {
            $dsn = "mysql:host={$dbHost};port={$dbPort};charset=utf8mb4";
            $pdo = new PDO($dsn, $dbUser, $dbPass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            ]);

            // Créer la base si elle n'existe pas
            $pdo->exec("CREATE DATABASE IF NOT EXISTS `{$dbName}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            $pdo->exec("USE `{$dbName}`");

            // Stocker en session pour l'étape suivante
            session_start();
            $_SESSION['install_db'] = compact('dbHost', 'dbPort', 'dbName', 'dbUser', 'dbPass');
            $step = '3';
        } catch (\PDOException $e) {
            $errors[] = 'Connexion échouée : ' . $e->getMessage();
            $step = '2';
        }
    } elseif ($step === '3') {
        session_start();

        $firstName = trim($_POST['first_name'] ?? '');
        $lastName = trim($_POST['last_name'] ?? '');
        $email = trim($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';
        $siteName = trim($_POST['site_name'] ?? 'Fête du Cidre');
        $siteUrl = trim($_POST['site_url'] ?? 'http://localhost:8080');

        // Validation
        if (empty($firstName)) $errors[] = 'Le prénom est requis.';
        if (empty($lastName)) $errors[] = 'Le nom est requis.';
        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'Email invalide.';
        if (strlen($password) < 8) $errors[] = 'Le mot de passe doit faire au moins 8 caractères.';

        if (empty($errors) && !empty($_SESSION['install_db'])) {
            $db = $_SESSION['install_db'];

            try {
                // Générer le .env
                $appKey = bin2hex(random_bytes(32));
                $envContent = <<<ENV
APP_NAME="{$siteName}"
APP_URL={$siteUrl}
APP_ENV=production
APP_DEBUG=false
APP_KEY={$appKey}

DB_HOST={$db['dbHost']}
DB_PORT={$db['dbPort']}
DB_NAME={$db['dbName']}
DB_USER={$db['dbUser']}
DB_PASS={$db['dbPass']}
DB_CHARSET=utf8mb4

CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_PAGES_TTL=86400

MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=587
MAIL_USER=
MAIL_PASS=
MAIL_FROM=noreply@fetecidre.fr
MAIL_FROM_NAME="{$siteName}"
MAIL_ENCRYPTION=tls

IMAGE_MAX_WIDTH=1920
IMAGE_QUALITY_WEBP=82
IMAGE_QUALITY_AVIF=68
IMAGE_SIZES=800,400,200

STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

ADMIN_PATH=/admin
ADMIN_SESSION_LIFETIME=7200

MAINTENANCE_ENABLED=false
MAINTENANCE_SECRET=dev-bypass-token
ENV;
                file_put_contents($basePath . '/.env', $envContent);

                // Connexion à la BDD
                $dsn = "mysql:host={$db['dbHost']};port={$db['dbPort']};dbname={$db['dbName']};charset=utf8mb4";
                $pdo = new PDO($dsn, $db['dbUser'], $db['dbPass'], [
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                ]);

                // Exécuter les migrations
                $migrationsDir = $basePath . '/migrations';
                $files = glob($migrationsDir . '/*.sql');
                sort($files);
                foreach ($files as $file) {
                    $sql = file_get_contents($file);
                    if (!empty(trim($sql))) {
                        $pdo->exec($sql);
                    }
                }

                // Créer l'admin
                $hashedPassword = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
                $stmt = $pdo->prepare(
                    "INSERT INTO users (email, password, first_name, last_name, role, is_active)
                     VALUES (?, ?, ?, ?, 'admin', 1)"
                );
                $stmt->execute([$email, $hashedPassword, $firstName, $lastName]);

                // Insérer les pages par défaut
                $defaultPages = [
                    ['Accueil', 'accueil', 'home', 1, 1],
                    ['Nos Origines', 'origines', 'page', 1, 2],
                    ['Infos Pratiques', 'infos-pratiques', 'page', 1, 3],
                    ['Programme 2025', 'programme-2025', 'page', 1, 4],
                    ['Boutique', 'boutique', 'shop', 1, 5],
                    ['Galerie Photos', 'galerie', 'gallery', 1, 6],
                    ['Archives', 'archives', 'archive', 1, 7],
                    ['Concours', 'concours', 'contest', 1, 8],
                    ['Randonnée', 'randonnee', 'hike', 0, 0],
                    ['Remerciements', 'remerciements', 'page', 0, 0],
                    ['Mentions Légales', 'mentions-legales', 'legal', 0, 0],
                    ['Contact', 'contact', 'contact', 0, 0],
                ];
                $stmtPage = $pdo->prepare(
                    "INSERT INTO pages (title, slug, template, in_menu, menu_order, status, content, created_by)
                     VALUES (?, ?, ?, ?, ?, 'published', '<p>Contenu à rédiger.</p>', 1)"
                );
                foreach ($defaultPages as $p) {
                    $stmtPage->execute($p);
                }

                // Insérer les settings par défaut
                $stmtSetting = $pdo->prepare(
                    "INSERT INTO settings (`group`, `key`, value, type, label) VALUES (?, ?, ?, ?, ?)"
                );
                $defaultSettings = [
                    ['general', 'site_name', $siteName, 'text', 'Nom du site'],
                    ['general', 'association_name', $siteName, 'text', 'Nom de l\'association'],
                    ['general', 'association_email', $email, 'text', 'Email de contact'],
                    ['colors', 'vert-profond', '#2C4A2E', 'color', 'Vert profond'],
                    ['colors', 'vert-mousse', '#4A6B3E', 'color', 'Vert mousse'],
                    ['colors', 'vert-clair', '#7A9E6B', 'color', 'Vert clair'],
                    ['colors', 'orange-cidre', '#D4833B', 'color', 'Orange cidre'],
                    ['colors', 'orange-doux', '#E8A95B', 'color', 'Orange doux'],
                    ['colors', 'creme', '#FAF5EC', 'color', 'Crème'],
                    ['colors', 'creme-fonce', '#F0E8D8', 'color', 'Crème foncé'],
                    ['colors', 'brun', '#5C3D2E', 'color', 'Brun'],
                    ['colors', 'texte', '#2A2318', 'color', 'Texte'],
                    ['colors', 'blanc', '#FFFDF8', 'color', 'Blanc'],
                ];
                foreach ($defaultSettings as $s) {
                    $stmtSetting->execute($s);
                }

                // Créer le fichier de verrouillage
                file_put_contents($lockFile, date('Y-m-d H:i:s'));

                $success = true;
                $step = '4';

                // Nettoyer la session
                unset($_SESSION['install_db']);
            } catch (\Exception $e) {
                $errors[] = 'Erreur d\'installation : ' . $e->getMessage();
            }
        }
    }
}

$prerequisites = ($step === '1') ? checkPrerequisites() : [];
$allOk = empty(array_filter($prerequisites, fn($c) => !$c['status']));
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Installation — Fête du Cidre CMS</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #FAF5EC; color: #2A2318; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
        .installer { max-width: 600px; width: 100%; background: #FFFDF8; border-radius: 16px; box-shadow: 0 4px 24px rgba(42,35,24,.08); overflow: hidden; }
        .installer-header { background: #2C4A2E; padding: 2rem; text-align: center; color: #fff; }
        .installer-header h1 { font-family: Georgia, serif; font-size: 1.75rem; margin-bottom: .25rem; }
        .installer-header p { opacity: .8; font-size: .9rem; }
        .installer-body { padding: 2rem; }
        .steps { display: flex; gap: .5rem; margin-bottom: 2rem; }
        .step { flex: 1; height: 4px; border-radius: 2px; background: #F0E8D8; }
        .step.active { background: #D4833B; }
        .step.done { background: #2C4A2E; }
        .check-list { list-style: none; }
        .check-list li { display: flex; align-items: center; gap: .75rem; padding: .5rem 0; border-bottom: 1px solid #F0E8D8; }
        .check-ok { color: #2C4A2E; font-weight: 700; }
        .check-fail { color: #c00; font-weight: 700; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; font-weight: 600; margin-bottom: .25rem; font-size: .9rem; }
        .form-group input { width: 100%; padding: .6rem .8rem; border: 2px solid #F0E8D8; border-radius: 8px; font-size: .95rem; }
        .form-group input:focus { outline: none; border-color: #4A6B3E; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .btn { display: inline-block; padding: .75rem 1.5rem; border: none; border-radius: 10px; font-weight: 600; font-size: .95rem; cursor: pointer; text-decoration: none; }
        .btn-primary { background: #2C4A2E; color: #fff; }
        .btn-primary:hover { background: #4A6B3E; }
        .btn-secondary { background: #D4833B; color: #fff; }
        .alert { padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .alert-error { background: #fce4ec; color: #c00; border: 1px solid #f8bbd0; }
        .alert-success { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    </style>
</head>
<body>
<div class="installer">
    <div class="installer-header">
        <h1>Fête du Cidre CMS</h1>
        <p>Assistant d'installation</p>
    </div>
    <div class="installer-body">
        <div class="steps">
            <div class="step <?= $step >= 1 ? ($step > 1 ? 'done' : 'active') : '' ?>"></div>
            <div class="step <?= $step >= 2 ? ($step > 2 ? 'done' : 'active') : '' ?>"></div>
            <div class="step <?= $step >= 3 ? ($step > 3 ? 'done' : 'active') : '' ?>"></div>
            <div class="step <?= $step >= 4 ? 'active' : '' ?>"></div>
        </div>

        <?php foreach ($errors as $err): ?>
            <div class="alert alert-error"><?= htmlspecialchars($err) ?></div>
        <?php endforeach; ?>

        <?php if ($step === '1'): ?>
            <!-- Étape 1 : Prérequis -->
            <h2 style="margin-bottom:1rem">Vérification des prérequis</h2>
            <ul class="check-list">
                <?php foreach ($prerequisites as $check): ?>
                <li>
                    <span class="<?= $check['status'] ? 'check-ok' : 'check-fail' ?>">
                        <?= $check['status'] ? '✓' : '✗' ?>
                    </span>
                    <span><?= htmlspecialchars($check['label']) ?></span>
                    <span style="margin-left:auto;color:#5C3D2E;font-size:.85rem"><?= htmlspecialchars($check['value']) ?></span>
                </li>
                <?php endforeach; ?>
            </ul>
            <?php if ($allOk): ?>
                <a href="?step=2" class="btn btn-primary" style="margin-top:1.5rem;display:block;text-align:center">Continuer</a>
            <?php else: ?>
                <p style="margin-top:1rem;color:#c00">Corrigez les problèmes ci-dessus avant de continuer.</p>
            <?php endif; ?>

        <?php elseif ($step === '2'): ?>
            <!-- Étape 2 : Base de données -->
            <h2 style="margin-bottom:1rem">Connexion à la base de données</h2>
            <form method="post">
                <input type="hidden" name="step" value="2">
                <div class="form-row">
                    <div class="form-group">
                        <label>Hôte</label>
                        <input type="text" name="db_host" value="localhost" required>
                    </div>
                    <div class="form-group">
                        <label>Port</label>
                        <input type="text" name="db_port" value="3306" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Nom de la base</label>
                    <input type="text" name="db_name" value="fete_cidre" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Utilisateur</label>
                        <input type="text" name="db_user" value="root" required>
                    </div>
                    <div class="form-group">
                        <label>Mot de passe</label>
                        <input type="password" name="db_pass">
                    </div>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Tester et continuer</button>
            </form>

        <?php elseif ($step === '3'): ?>
            <!-- Étape 3 : Compte admin + config -->
            <h2 style="margin-bottom:1rem">Configuration du site</h2>
            <form method="post">
                <input type="hidden" name="step" value="3">
                <div class="form-row">
                    <div class="form-group">
                        <label>Prénom</label>
                        <input type="text" name="first_name" required>
                    </div>
                    <div class="form-group">
                        <label>Nom</label>
                        <input type="text" name="last_name" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Email admin</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Mot de passe (min. 8 caractères)</label>
                    <input type="password" name="password" minlength="8" required>
                </div>
                <hr style="border:none;border-top:1px solid #F0E8D8;margin:1.5rem 0">
                <div class="form-group">
                    <label>Nom du site</label>
                    <input type="text" name="site_name" value="Fête du Cidre" required>
                </div>
                <div class="form-group">
                    <label>URL du site</label>
                    <input type="url" name="site_url" value="http://localhost:8080" required>
                </div>
                <button type="submit" class="btn btn-secondary" style="width:100%">Installer</button>
            </form>

        <?php elseif ($step === '4'): ?>
            <!-- Étape 4 : Succès -->
            <div class="alert alert-success">
                <strong>Installation terminée !</strong><br>
                Le CMS a été installé avec succès.
            </div>
            <p style="margin-bottom:1rem">Vous pouvez maintenant accéder à l'administration :</p>
            <a href="/admin/login" class="btn btn-primary" style="display:block;text-align:center">Accéder à l'admin</a>
        <?php endif; ?>
    </div>
</div>
</body>
</html>
