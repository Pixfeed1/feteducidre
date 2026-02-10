<?php

/**
 * Installateur web — Fête du Cidre CMS.
 *
 * Architecture en 3 parties :
 *   1. Logique PHP (prérequis, AJAX test-db, AJAX install)
 *   2. Template HTML (stepper 4 étapes, design fidèle à la maquette)
 *   3. CSS séparé (assets/css/install.css) + JS séparé (assets/js/install.js)
 *
 * Se verrouille après installation via storage/.installed
 */

declare(strict_types=1);

$basePath = dirname(__DIR__);
$lockFile = $basePath . '/storage/.installed';

/** Assainit un nom de base de données (garde uniquement [a-zA-Z0-9_]) */
function sanitizeDbName(string $name): string
{
    return preg_replace('/[^a-zA-Z0-9_]/', '', $name);
}

/* ── Rediriger si déjà installé ── */
if (file_exists($lockFile)) {
    header('Location: /admin');
    exit;
}

/* ═══════════════════════════════════════════════════════════════
 *  SECTION 1 : LOGIQUE PHP — PRÉREQUIS
 * ═══════════════════════════════════════════════════════════════ */

/**
 * Vérifie tous les prérequis serveur.
 * Chaque check contient : name, detail, status (pass|fail|warn), value, badge (ok|ko|opt), required.
 */
function checkPrerequisites(): array
{
    $basePath = dirname(__DIR__);
    $checks = [];

    /* PHP version */
    $phpOk = version_compare(PHP_VERSION, '8.0.0', '>=');
    $checks[] = [
        'name'     => 'PHP',
        'detail'   => 'Version 8.0+ requise',
        'status'   => $phpOk ? 'pass' : 'fail',
        'value'    => PHP_VERSION,
        'badge'    => $phpOk ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Extension PDO MySQL */
    $pdoOk = extension_loaded('pdo_mysql');
    $checks[] = [
        'name'     => 'Extension PDO MySQL',
        'detail'   => 'Connexion base de données',
        'status'   => $pdoOk ? 'pass' : 'fail',
        'value'    => $pdoOk ? 'Installée' : 'Manquante',
        'badge'    => $pdoOk ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Extension GD */
    $gdOk = extension_loaded('gd');
    $checks[] = [
        'name'     => 'Extension GD',
        'detail'   => 'Traitement d\'images (redimensionnement, WebP, AVIF)',
        'status'   => $gdOk ? 'pass' : 'fail',
        'value'    => $gdOk ? 'Installée' : 'Manquante',
        'badge'    => $gdOk ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Extension mbstring */
    $mbOk = extension_loaded('mbstring');
    $checks[] = [
        'name'     => 'Extension mbstring',
        'detail'   => 'Gestion des caractères UTF-8',
        'status'   => $mbOk ? 'pass' : 'fail',
        'value'    => $mbOk ? 'Installée' : 'Manquante',
        'badge'    => $mbOk ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Extension intl (optionnelle) */
    $intlOk = extension_loaded('intl');
    $checks[] = [
        'name'     => 'Extension intl',
        'detail'   => 'Formatage dates/nombres en français (optionnel)',
        'status'   => $intlOk ? 'pass' : 'warn',
        'value'    => $intlOk ? 'Installée' : 'Optionnelle',
        'badge'    => $intlOk ? 'ok' : 'opt',
        'required' => false,
    ];

    /* mod_rewrite (détection heuristique) */
    $rewriteOk = function_exists('apache_get_modules')
        ? in_array('mod_rewrite', apache_get_modules(), true)
        : true; /* Assume OK si pas Apache (nginx, PHP built-in) */
    $checks[] = [
        'name'     => 'Apache mod_rewrite',
        'detail'   => 'Réécriture d\'URL (URLs propres)',
        'status'   => $rewriteOk ? 'pass' : 'fail',
        'value'    => $rewriteOk ? 'Activé' : 'Désactivé',
        'badge'    => $rewriteOk ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Composer vendor */
    $composerOk = file_exists($basePath . '/vendor/autoload.php');
    $checks[] = [
        'name'     => 'Dépendances Composer',
        'detail'   => 'vendor/autoload.php présent',
        'status'   => $composerOk ? 'pass' : 'fail',
        'value'    => $composerOk ? 'OK' : 'Manquant',
        'badge'    => $composerOk ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Permissions d'écriture */
    $dirs = ['cache', 'storage', 'storage/uploads', 'storage/logs'];
    $allWritable = true;
    foreach ($dirs as $dir) {
        $fullPath = $basePath . '/' . $dir;
        if (!is_dir($fullPath) || !is_writable($fullPath)) {
            $allWritable = false;
            break;
        }
    }
    $checks[] = [
        'name'     => 'Permissions d\'écriture',
        'detail'   => 'cache/, storage/, storage/uploads/',
        'status'   => $allWritable ? 'pass' : 'fail',
        'value'    => $allWritable ? 'OK' : 'Non accessible',
        'badge'    => $allWritable ? 'ok' : 'ko',
        'required' => true,
    ];

    /* Espace disque */
    $freeSpace = @disk_free_space($basePath);
    $freeSpaceMb = $freeSpace ? round($freeSpace / 1024 / 1024) : 0;
    $spaceOk = $freeSpaceMb >= 100;
    if ($freeSpaceMb >= 1024) {
        $spaceLabel = number_format($freeSpaceMb / 1024, 1, ',', ' ') . ' Go';
    } else {
        $spaceLabel = $freeSpaceMb . ' Mo';
    }
    $checks[] = [
        'name'     => 'Espace disque',
        'detail'   => 'Minimum 100 Mo requis',
        'status'   => $spaceOk ? 'pass' : 'fail',
        'value'    => $spaceLabel,
        'badge'    => $spaceOk ? 'ok' : 'ko',
        'required' => true,
    ];

    return $checks;
}

/* ═══════════════════════════════════════════════════════════════
 *  SECTION 2 : HANDLERS AJAX
 * ═══════════════════════════════════════════════════════════════ */

$isAjax = !empty($_SERVER['HTTP_X_REQUESTED_WITH'])
    && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $isAjax) {
    header('Content-Type: application/json; charset=UTF-8');
    $action = $_POST['action'] ?? '';

    /* ── Test de connexion DB ── */
    if ($action === 'test-db') {
        $host = trim($_POST['db_host'] ?? 'localhost');
        $port = trim($_POST['db_port'] ?? '3306');
        $name = trim($_POST['db_name'] ?? '');
        $user = trim($_POST['db_user'] ?? '');
        $pass = $_POST['db_pass'] ?? '';

        try {
            $dsn = "mysql:host={$host};port={$port};charset=utf8mb4";
            $pdo = new PDO($dsn, $user, $pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_TIMEOUT => 5,
            ]);

            $mysqlVersion = $pdo->query('SELECT VERSION()')->fetchColumn();

            /* Vérifier/créer la base */
            $safeName = sanitizeDbName($name);
            $pdo->exec("CREATE DATABASE IF NOT EXISTS `{$safeName}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            $pdo->exec("USE `{$safeName}`");

            /* Compter les tables existantes */
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = ?");
            $stmt->execute([$safeName]);
            $tableCount = (int) $stmt->fetchColumn();
            $dbState = $tableCount === 0
                ? '(vide, prête à l\'installation)'
                : "({$tableCount} tables existantes)";

            echo json_encode([
                'success'       => true,
                'message'       => "Connecté — MySQL {$mysqlVersion} — Base \"{$safeName}\" accessible {$dbState}",
                'mysql_version' => $mysqlVersion,
            ]);
        } catch (PDOException $e) {
            echo json_encode([
                'success' => false,
                'message' => 'Connexion échouée : ' . $e->getMessage(),
            ]);
        }
        exit;
    }

    /* ── Installation complète ── */
    if ($action === 'install') {
        $host     = trim($_POST['db_host'] ?? 'localhost');
        $port     = trim($_POST['db_port'] ?? '3306');
        $dbName   = sanitizeDbName(trim($_POST['db_name'] ?? ''));
        $dbUser   = trim($_POST['db_user'] ?? '');
        $dbPass   = $_POST['db_pass'] ?? '';

        $firstName = trim($_POST['first_name'] ?? '');
        $lastName  = trim($_POST['last_name'] ?? '');
        $email     = trim($_POST['email'] ?? '');
        $password  = $_POST['password'] ?? '';
        $siteName  = trim($_POST['site_name'] ?? 'Fête du Cidre');
        $siteUrl   = rtrim(trim($_POST['site_url'] ?? 'http://localhost:8080'), '/');

        /* Validation */
        if (empty($firstName) || empty($email) || strlen($password) < 8) {
            echo json_encode(['success' => false, 'message' => 'Données du formulaire invalides.']);
            exit;
        }
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            echo json_encode(['success' => false, 'message' => 'Adresse email invalide.']);
            exit;
        }

        try {
            /* 1. Connexion DB */
            $dsn = "mysql:host={$host};port={$port};charset=utf8mb4";
            $pdo = new PDO($dsn, $dbUser, $dbPass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            ]);
            $pdo->exec("CREATE DATABASE IF NOT EXISTS `{$dbName}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            $pdo->exec("USE `{$dbName}`");

            $mysqlVersion = $pdo->query('SELECT VERSION()')->fetchColumn();

            /* 2. Générer le .env */
            $appKey = bin2hex(random_bytes(32));
            $envContent = <<<ENV
APP_NAME="{$siteName}"
APP_URL={$siteUrl}
APP_ENV=production
APP_DEBUG=false
APP_KEY={$appKey}

DB_HOST={$host}
DB_PORT={$port}
DB_NAME={$dbName}
DB_USER={$dbUser}
DB_PASS={$dbPass}
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

            /* 3. Exécuter les migrations */
            $migrationsDir = $basePath . '/migrations';
            $files = glob($migrationsDir . '/*.sql');
            sort($files);
            foreach ($files as $file) {
                $sql = file_get_contents($file);
                if (!empty(trim($sql))) {
                    $pdo->exec($sql);
                }
            }

            /* 4. Insérer les pages par défaut */
            $defaultPages = [
                ['Accueil', 'accueil', 'home', 1, 1, 'Fête du Cidre — L\'Hôtellerie de Flée', 'Découvrez la Fête du Cidre, événement incontournable depuis 1989.'],
                ['Nos Origines', 'origines', 'page', 1, 2, 'Nos Origines — Fête du Cidre', 'L\'histoire de la Fête du Cidre depuis 1989.'],
                ['Infos Pratiques', 'infos-pratiques', 'page', 1, 3, 'Infos Pratiques — Fête du Cidre', 'Horaires, tarifs, accès et informations pratiques.'],
                ['Programme 2025', 'programme-2025', 'page', 1, 4, 'Programme 2025 — Fête du Cidre', 'Le programme complet de l\'édition 2025.'],
                ['Boutique', 'boutique', 'shop', 1, 5, 'Boutique — Fête du Cidre', 'Produits du terroir et articles de la Fête du Cidre.'],
                ['Galerie Photos', 'galerie', 'gallery', 1, 6, 'Galerie Photos — Fête du Cidre', 'Toutes les photos des éditions de la Fête du Cidre.'],
                ['Archives', 'archives', 'archive', 1, 7, 'Archives — Fête du Cidre', 'Retrouvez toutes les éditions passées.'],
                ['Concours', 'concours', 'contest', 1, 8, 'Concours — Fête du Cidre', 'Le concours de cidre et ses palmarès.'],
                ['Randonnée', 'randonnee', 'hike', 0, 0, 'Randonnée — Fête du Cidre', 'La randonnée de la Fête du Cidre.'],
                ['Remerciements', 'remerciements', 'page', 0, 0, 'Remerciements — Fête du Cidre', 'Merci à tous nos bénévoles et partenaires.'],
                ['Mentions Légales', 'mentions-legales', 'legal', 0, 0, 'Mentions Légales', 'Mentions légales et politique de confidentialité.'],
                ['Contact', 'contact', 'contact', 0, 0, 'Contact — Fête du Cidre', 'Contactez l\'association Fête du Cidre.'],
            ];
            $stmtPage = $pdo->prepare(
                "INSERT INTO pages (title, slug, template, in_menu, menu_order, meta_title, meta_description, status, content, created_by)
                 VALUES (?, ?, ?, ?, ?, ?, ?, 'published', '<p>Contenu à rédiger.</p>', 1)"
            );
            foreach ($defaultPages as $p) {
                $stmtPage->execute($p);
            }

            /* 5. Créer le compte admin */
            $hashedPassword = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
            $stmtUser = $pdo->prepare(
                "INSERT INTO users (email, password, first_name, last_name, role, is_active) VALUES (?, ?, ?, ?, 'admin', 1)"
            );
            $stmtUser->execute([$email, $hashedPassword, $firstName, $lastName]);

            /* 6. Insérer les settings par défaut */
            $stmtSetting = $pdo->prepare(
                "INSERT INTO settings (`group`, `key`, value, type, label) VALUES (?, ?, ?, ?, ?)"
            );
            $defaultSettings = [
                ['general', 'site_name', $siteName, 'text', 'Nom du site'],
                ['general', 'association_name', $siteName, 'text', 'Nom de l\'association'],
                ['general', 'association_email', $email, 'text', 'Email de contact'],
                ['general', 'association_address', 'L\'Hôtellerie de Flée, 49500', 'text', 'Adresse'],
                ['general', 'association_phone', '', 'text', 'Téléphone'],
                ['social', 'facebook_url', '', 'text', 'Page Facebook'],
                ['social', 'instagram_url', '', 'text', 'Compte Instagram'],
                ['shop', 'shipping_cost', '5.90', 'text', 'Frais de port (€)'],
                ['shop', 'free_shipping_threshold', '50', 'text', 'Franco de port (€)'],
                ['seo', 'default_meta_title', $siteName, 'text', 'Meta title par défaut'],
                ['seo', 'default_meta_description', 'La Fête du Cidre de L\'Hôtellerie de Flée — depuis 1989.', 'text', 'Meta description par défaut'],
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

            /* 7. Verrouiller l'installateur */
            file_put_contents($lockFile, date('Y-m-d H:i:s') . ' — Installé par ' . $email);

            /* Nombre de tables créées */
            $stmtCount = $pdo->prepare("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = ?");
            $stmtCount->execute([$dbName]);
            $tableCount = (int) $stmtCount->fetchColumn();

            echo json_encode([
                'success'       => true,
                'message'       => 'Installation terminée avec succès.',
                'db_name'       => $dbName . ' (' . $tableCount . ' tables)',
                'php_version'   => PHP_VERSION,
                'mysql_version' => $mysqlVersion,
            ]);
        } catch (\Exception $e) {
            echo json_encode([
                'success' => false,
                'message' => 'Erreur : ' . $e->getMessage(),
            ]);
        }
        exit;
    }

    /* Action inconnue */
    echo json_encode(['success' => false, 'message' => 'Action inconnue.']);
    exit;
}

/* ═══════════════════════════════════════════════════════════════
 *  SECTION 3 : DONNÉES POUR LE TEMPLATE
 * ═══════════════════════════════════════════════════════════════ */

$checks = checkPrerequisites();
$allRequiredPass = true;
foreach ($checks as $c) {
    if ($c['required'] && $c['status'] !== 'pass') {
        $allRequiredPass = false;
        break;
    }
}

/* Icônes SVG réutilisables dans le template */
$svgCheck = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
$svgFail = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>';
$svgWarn = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/></svg>';

/* ═══════════════════════════════════════════════════════════════
 *  SECTION 4 : TEMPLATE HTML
 * ═══════════════════════════════════════════════════════════════ */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Installation — Fête du Cidre CMS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/install.css">
</head>
<body>

<div class="bg-pattern"></div>
<div class="bg-glow-1"></div>
<div class="bg-glow-2"></div>

<div class="installer">

  <!-- Header -->
  <div class="installer-header">
    <div class="header-logo">
      <img src="/assets/images/logo.png" alt="Fête du Cidre">
    </div>
    <h1>Installation</h1>
    <p>Configuration du CMS Fête du Cidre</p>
  </div>

  <!-- Stepper -->
  <div style="margin-bottom:2rem;animation:fadeInUp 0.6s 0.1s ease both">
    <div class="stepper">
      <div class="step-dot active" id="dot-1">1</div>
      <div class="step-line" id="line-1"></div>
      <div class="step-dot upcoming" id="dot-2">2</div>
      <div class="step-line" id="line-2"></div>
      <div class="step-dot upcoming" id="dot-3">3</div>
      <div class="step-line" id="line-3"></div>
      <div class="step-dot upcoming" id="dot-4">4</div>
    </div>
    <div class="step-labels">
      <div class="step-label active" id="label-1">Pré-requis</div>
      <div class="step-label" id="label-2">Base de données</div>
      <div class="step-label" id="label-3">Admin</div>
      <div class="step-label" id="label-4">Finalisation</div>
    </div>
  </div>

  <!-- Card -->
  <div class="card">

    <!-- ═══ ÉTAPE 1 : Pré-requis ═══ -->
    <div class="step-content active" id="step-1">
      <div class="card-body">
        <div class="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--vert-profond)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>
          Vérification des pré-requis
        </div>
        <div class="section-desc">Le système vérifie automatiquement que votre serveur est compatible.</div>

        <div class="checks-list">
          <?php foreach ($checks as $check): ?>
          <div class="check-item">
            <div class="check-icon <?= $check['status'] ?>">
              <?php if ($check['status'] === 'pass'): ?>
                <?= $svgCheck ?>
              <?php elseif ($check['status'] === 'warn'): ?>
                <?= $svgWarn ?>
              <?php else: ?>
                <?= $svgFail ?>
              <?php endif; ?>
            </div>
            <div class="check-info">
              <div class="check-name"><?= htmlspecialchars($check['name']) ?></div>
              <div class="check-detail"><?= htmlspecialchars($check['detail']) ?></div>
            </div>
            <span class="check-status <?= $check['badge'] ?>"><?= htmlspecialchars($check['value']) ?></span>
          </div>
          <?php endforeach; ?>
        </div>

        <?php if ($allRequiredPass): ?>
        <div class="checks-summary all-pass">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>
          Tous les pré-requis obligatoires sont remplis. Vous pouvez continuer.
        </div>
        <?php else: ?>
        <div class="checks-summary has-fail">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>
          Des pré-requis obligatoires ne sont pas remplis. Corrigez-les avant de continuer.
        </div>
        <?php endif; ?>
      </div>
      <div class="card-footer">
        <div></div>
        <button class="btn-primary" onclick="goToStep(2)" <?= $allRequiredPass ? '' : 'disabled' ?>>
          Continuer
          <svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>
    </div>

    <!-- ═══ ÉTAPE 2 : Base de données ═══ -->
    <div class="step-content" id="step-2">
      <div class="card-body">
        <div class="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--vert-profond)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
          Base de données MySQL
        </div>
        <div class="section-desc">Saisissez les identifiants de connexion à votre base de données. Ces informations se trouvent dans le panel de votre hébergeur (OVH, o2switch, etc.).</div>

        <div class="field-row-3">
          <div class="field">
            <label for="db_host">Hôte</label>
            <input type="text" id="db_host" value="localhost" placeholder="localhost ou adresse MySQL">
          </div>
          <div class="field">
            <label for="db_port">Port</label>
            <input type="text" id="db_port" value="3306" placeholder="3306">
          </div>
          <div class="field">
            <label>Charset</label>
            <input type="text" value="utf8mb4" disabled>
          </div>
        </div>

        <div class="field">
          <label for="db_name">Nom de la base de données</label>
          <input type="text" id="db_name" placeholder="fete_cidre" value="fete_cidre">
          <div class="field-hint">La base sera créée automatiquement si elle n'existe pas.</div>
        </div>

        <div class="field-row">
          <div class="field">
            <label for="db_user">Utilisateur MySQL</label>
            <input type="text" id="db_user" placeholder="fete_cidre_user" value="root">
          </div>
          <div class="field">
            <label for="db_pass">Mot de passe MySQL</label>
            <div class="field-password">
              <input type="password" id="db_pass" placeholder="••••••••">
              <button type="button" class="eye-toggle" onclick="togglePassword(this, 'db_pass')" aria-label="Afficher le mot de passe">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
          </div>
        </div>

        <button class="test-btn" id="dbTestBtn" onclick="testDb()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/></svg>
          Tester la connexion
        </button>

        <div class="db-result" id="dbResult"></div>
      </div>
      <div class="card-footer">
        <button class="btn-secondary" onclick="goToStep(1)">
          <svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"/></svg>
          Retour
        </button>
        <button class="btn-primary" id="dbContinueBtn" onclick="goToStep(3)" disabled>
          Continuer
          <svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>
    </div>

    <!-- ═══ ÉTAPE 3 : Compte admin ═══ -->
    <div class="step-content" id="step-3">
      <div class="card-body">
        <div class="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--vert-profond)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>
          Compte administrateur
        </div>
        <div class="section-desc">Créez le premier compte administrateur. D'autres comptes pourront être ajoutés ultérieurement depuis l'admin.</div>

        <div id="step3-errors"></div>

        <div class="field-row">
          <div class="field">
            <label for="admin_first_name">Prénom</label>
            <input type="text" id="admin_first_name" placeholder="Jean">
          </div>
          <div class="field">
            <label for="admin_last_name">Nom</label>
            <input type="text" id="admin_last_name" placeholder="Dupont">
          </div>
        </div>

        <div class="field">
          <label for="admin_email">Adresse e-mail</label>
          <div class="input-with-icon">
            <span class="input-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg></span>
            <input type="email" id="admin_email" placeholder="admin@fetecidre.fr">
          </div>
          <div class="field-hint">Cet e-mail servira aussi pour la connexion et les notifications.</div>
        </div>

        <div class="field">
          <label for="admin_password">Mot de passe</label>
          <div class="field-password">
            <input type="password" id="admin_password" placeholder="Minimum 8 caractères">
            <button type="button" class="eye-toggle" onclick="togglePassword(this, 'admin_password')" aria-label="Afficher le mot de passe">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>

        <div class="field">
          <label for="admin_password_confirm">Confirmer le mot de passe</label>
          <div class="field-password">
            <input type="password" id="admin_password_confirm" placeholder="Retapez le mot de passe">
            <button type="button" class="eye-toggle" onclick="togglePassword(this, 'admin_password_confirm')" aria-label="Afficher le mot de passe">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>

        <div class="site-info-section">
          <div class="site-info-title">Informations du site</div>
          <div class="field">
            <label for="site_name">Nom de l'association / site</label>
            <input type="text" id="site_name" value="La Fête du Cidre" placeholder="La Fête du Cidre">
          </div>
          <div class="field">
            <label for="site_url">URL du site</label>
            <div class="input-with-icon">
              <span class="input-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></span>
              <input type="url" id="site_url" placeholder="https://fetecidre.fr" value="http://localhost:8080">
            </div>
          </div>
        </div>
      </div>
      <div class="card-footer">
        <button class="btn-secondary" onclick="goToStep(2)">
          <svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"/></svg>
          Retour
        </button>
        <button class="btn-primary" onclick="validateAndInstall()">
          Installer
          <svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg>
        </button>
      </div>
    </div>

    <!-- ═══ ÉTAPE 4 : Installation ═══ -->
    <div class="step-content" id="step-4">
      <div class="card-body">

        <!-- Phase A : Installation en cours -->
        <div id="installing">
          <div class="section-title">
            <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--orange-cidre)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
            Installation en cours…
          </div>
          <div class="section-desc">Le CMS est en cours d'installation. Ne fermez pas cette page.</div>

          <div class="install-progress">
            <div class="progress-bar-wrap"><div class="progress-bar" id="progressBar"></div></div>
            <div class="progress-label" id="progressLabel"><strong>Démarrage…</strong></div>

            <div class="install-steps-log">
              <div class="log-item pending"><span class="log-dot"></span> Génération du fichier .env</div>
              <div class="log-item pending"><span class="log-dot"></span> Connexion à la base de données</div>
              <div class="log-item pending"><span class="log-dot"></span> Création des 15 tables</div>
              <div class="log-item pending"><span class="log-dot"></span> Insertion des données initiales</div>
              <div class="log-item pending"><span class="log-dot"></span> Création du compte administrateur</div>
              <div class="log-item pending"><span class="log-dot"></span> Génération du cache initial</div>
              <div class="log-item pending"><span class="log-dot"></span> Verrouillage de l'installateur</div>
            </div>
          </div>
        </div>

        <!-- Phase B : Succès (masqué par défaut) -->
        <div id="installed" style="display:none">
          <div class="success-screen">
            <div class="success-icon">
              <svg class="success-checkmark" viewBox="0 0 40 40" fill="none">
                <circle class="circle" cx="20" cy="20" r="17" stroke="#16a34a" stroke-width="2.5" fill="none"/>
                <path class="check" d="M12 20l5 5 11-11" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              </svg>
            </div>
            <h2>Installation terminée !</h2>
            <p>Le CMS Fête du Cidre est prêt à l'emploi.</p>

            <div class="success-info">
              <div class="success-info-row"><span>URL du site</span> <span id="success-site-url"></span></div>
              <div class="success-info-row"><span>URL admin</span> <span id="success-admin-url"></span></div>
              <div class="success-info-row"><span>E-mail admin</span> <span id="success-admin-email"></span></div>
              <div class="success-info-row"><span>Base de données</span> <span id="success-db-name"></span></div>
              <div class="success-info-row"><span>Version PHP</span> <span id="success-php-version"></span></div>
              <div class="success-info-row"><span>Version MySQL</span> <span id="success-mysql-version"></span></div>
            </div>

            <div class="security-warn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="flex-shrink:0;margin-top:1px"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/></svg>
              <div><strong>Sécurité :</strong> L'installateur est désormais verrouillé. Pour le relancer, supprimez le fichier <code style="background:rgba(217,64,64,0.1);padding:0.1rem 0.3rem;border-radius:4px">storage/.installed</code></div>
            </div>

            <a href="/admin/login" class="btn-primary" style="font-size:0.92rem;padding:0.8rem 2rem;display:inline-flex">
              <svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>
              Accéder à l'administration
            </a>
          </div>
        </div>

      </div>
    </div>

  </div>

  <div class="installer-footer">
    Fête du Cidre CMS v1.0 — &copy; <?= date('Y') ?> Association La Fête du Cidre
  </div>
</div>

<script>
/* Transmettre le résultat des prérequis au JS */
window.installPrereqOk = <?= $allRequiredPass ? 'true' : 'false' ?>;
</script>
<script src="/assets/js/install.js"></script>
</body>
</html>
