<?php
/**
 * Page de connexion admin — affichage autonome (sans layout sidebar).
 * Variables disponibles : $title
 */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Connexion — Administration — Fête du Cidre</title>
    <style>
        <?= \App\Core\Theme::cssVariables() ?>

        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { font-size: 16px; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--creme, #FAF5EC);
            position: relative;
            overflow: hidden;
        }

        /* ===== BACKGROUND ===== */
        .bg-pattern {
            position: fixed;
            inset: 0;
            opacity: 0.035;
            background-image:
                radial-gradient(circle at 20% 50%, var(--vert-profond, #2C4A2E) 1px, transparent 1px),
                radial-gradient(circle at 80% 20%, var(--vert-profond, #2C4A2E) 1px, transparent 1px);
            background-size: 60px 60px, 80px 80px;
            pointer-events: none;
        }

        .bg-glow-1 {
            position: fixed;
            width: 600px; height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, var(--vert-profond, #2C4A2E) 0%, transparent 70%);
            opacity: 0.04;
            top: -15%; right: -10%;
            pointer-events: none;
        }

        .bg-glow-2 {
            position: fixed;
            width: 500px; height: 500px;
            border-radius: 50%;
            background: radial-gradient(circle, var(--orange-cidre, #D4833B) 0%, transparent 70%);
            opacity: 0.04;
            bottom: -15%; left: -10%;
            pointer-events: none;
        }

        /* ===== CARD ===== */
        .login-card {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 420px;
            margin: 2rem;
            background: var(--blanc, #FFFDF8);
            border-radius: 28px;
            border: 1.5px solid var(--creme-fonce, #F0E8D8);
            box-shadow:
                0 4px 6px rgba(44, 74, 46, 0.02),
                0 12px 40px rgba(44, 74, 46, 0.06),
                0 40px 80px rgba(44, 74, 46, 0.04);
            padding: 2.8rem 2.5rem 2.2rem;
            animation: cardIn 0.7s cubic-bezier(0.23, 1, 0.32, 1) both;
        }

        @keyframes cardIn {
            from { opacity: 0; transform: translateY(24px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* ===== HEADER ===== */
        .card-header { text-align: center; margin-bottom: 2rem; }

        .logo-mark {
            width: 64px; height: 64px;
            margin: 0 auto 1.2rem;
            border-radius: 18px;
            background: var(--vert-profond, #2C4A2E);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeInUp 0.5s 0.1s ease both;
            position: relative;
        }

        .logo-mark::after {
            content: '';
            position: absolute;
            inset: -3px;
            border-radius: 21px;
            border: 2px solid var(--vert-clair, #7A9E6B);
            opacity: 0.2;
        }

        .card-header h1 {
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--vert-profond, #2C4A2E);
            margin-bottom: 0.3rem;
            animation: fadeInUp 0.5s 0.15s ease both;
        }

        .card-header p {
            font-size: 0.9rem;
            color: var(--texte-leger, #6B5D4F);
            animation: fadeInUp 0.5s 0.2s ease both;
        }

        /* ===== FLASH MESSAGES ===== */
        .flash {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            font-size: 0.84rem;
            font-weight: 500;
            margin-bottom: 1.2rem;
            animation: shakeIn 0.4s ease both;
        }

        .flash-error {
            background: #FEF2F2;
            border: 1.5px solid #FECACA;
            color: #D94040;
        }

        .flash-success {
            background: #F0FDF4;
            border: 1.5px solid #BBF7D0;
            color: #166534;
        }

        @keyframes shakeIn {
            0% { transform: translateX(-8px); opacity: 0; }
            30% { transform: translateX(5px); }
            60% { transform: translateX(-3px); }
            100% { transform: translateX(0); opacity: 1; }
        }

        /* ===== FORM ===== */
        .form-group {
            margin-bottom: 1.1rem;
            animation: fadeInUp 0.5s ease both;
        }

        .form-group:nth-child(1) { animation-delay: 0.25s; }
        .form-group:nth-child(2) { animation-delay: 0.3s; }

        .form-group label {
            display: block;
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--texte-leger, #6B5D4F);
            margin-bottom: 0.35rem;
        }

        .input-wrap {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-icon {
            position: absolute;
            left: 0.9rem;
            pointer-events: none;
            display: flex;
            color: var(--texte-leger, #6B5D4F);
            transition: color 0.3s;
        }

        .input-wrap input {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 2.7rem;
            border: 2px solid var(--creme-fonce, #F0E8D8);
            border-radius: 12px;
            font-family: inherit;
            font-size: 0.92rem;
            color: var(--texte, #2A2318);
            background: white;
            outline: none;
            transition: all 0.3s;
        }

        .input-wrap input::placeholder {
            color: var(--texte-leger, #6B5D4F);
            opacity: 0.45;
        }

        .input-wrap input:focus {
            border-color: var(--vert-clair, #7A9E6B);
            box-shadow: 0 0 0 4px rgba(122, 158, 107, 0.1);
        }

        .input-wrap input:focus ~ .input-icon { color: var(--vert-profond, #2C4A2E); }

        .eye-toggle {
            position: absolute;
            right: 0.8rem;
            background: none;
            border: none;
            cursor: pointer;
            color: var(--texte-leger, #6B5D4F);
            display: flex;
            align-items: center;
            padding: 4px;
            border-radius: 6px;
            transition: all 0.2s;
        }

        .eye-toggle:hover {
            color: var(--vert-profond, #2C4A2E);
            background: var(--creme, #FAF5EC);
        }

        /* Options */
        .form-options {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.6rem;
            animation: fadeInUp 0.5s 0.35s ease both;
        }

        .forgot-link {
            font-size: 0.82rem;
            color: var(--orange-cidre, #D4833B);
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }
        .forgot-link:hover { color: var(--vert-profond, #2C4A2E); }

        .remember {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            cursor: pointer;
        }

        .remember input[type=checkbox] {
            width: 16px; height: 16px;
            accent-color: var(--vert-profond, #2C4A2E);
            cursor: pointer;
        }

        .remember span {
            font-size: 0.84rem;
            color: var(--texte-leger, #6B5D4F);
            user-select: none;
        }

        /* Submit */
        .submit-btn {
            width: 100%;
            padding: 0.9rem;
            border: none;
            border-radius: 12px;
            background: var(--vert-profond, #2C4A2E);
            color: white;
            font-family: inherit;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
            animation: fadeInUp 0.5s 0.4s ease both;
        }

        .submit-btn:hover {
            background: var(--vert-mousse, #4A6B3E);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(44, 74, 46, 0.25);
        }

        .submit-btn:active { transform: translateY(0); }

        /* ===== FOOTER ===== */
        .card-footer {
            margin-top: 2rem;
            text-align: center;
            padding-top: 1.5rem;
            border-top: 1px solid var(--creme-fonce, #F0E8D8);
            animation: fadeInUp 0.5s 0.45s ease both;
        }

        .card-footer .back-link {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.84rem;
            color: var(--texte-leger, #6B5D4F);
            text-decoration: none;
            transition: color 0.3s;
        }

        .card-footer .back-link:hover { color: var(--orange-cidre, #D4833B); }

        .card-footer .copyright {
            display: block;
            margin-top: 1rem;
            font-size: 0.72rem;
            color: var(--texte-leger, #6B5D4F);
            opacity: 0.4;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 480px) {
            .login-card {
                padding: 2rem 1.5rem 1.8rem;
                margin: 1rem;
                border-radius: 22px;
            }
            .card-header h1 { font-size: 1.4rem; }
            .form-options { flex-direction: column; gap: 0.6rem; align-items: flex-start; }
        }
    </style>
</head>
<body>

<div class="bg-pattern"></div>
<div class="bg-glow-1"></div>
<div class="bg-glow-2"></div>

<div class="login-card">

    <div class="card-header">
        <div class="logo-mark">
            <?= icon('apple', 36, '', '#A3C48E') ?>
        </div>
        <h1>Fête du Cidre</h1>
        <p>Connectez-vous à l'espace d'administration</p>
    </div>

    <?= flash('success') ?>
    <?= flash('error') ?>

    <form method="post" action="/admin/login" novalidate>
        <?= csrf_field() ?>

        <div class="form-group">
            <label for="email">E-mail</label>
            <div class="input-wrap">
                <span class="input-icon"><?= icon('mail', 16) ?></span>
                <input type="email" id="email" name="email"
                       value="<?= old('email') ?>"
                       placeholder="admin@feteducidre.fr"
                       autocomplete="email" required autofocus>
            </div>
        </div>

        <div class="form-group">
            <label for="password">Mot de passe</label>
            <div class="input-wrap">
                <span class="input-icon"><?= icon('key-round', 16) ?></span>
                <input type="password" id="password" name="password"
                       placeholder="••••••••"
                       autocomplete="current-password" required>
                <button type="button" class="eye-toggle" id="eyeToggle" aria-label="Afficher le mot de passe">
                    <?= icon('eye', 16) ?>
                </button>
            </div>
        </div>

        <div class="form-options">
            <label class="remember">
                <input type="checkbox" id="remember" name="remember">
                <span>Se souvenir de moi</span>
            </label>
            <a href="/admin/forgot-password" class="forgot-link">Mot de passe oublié ?</a>
        </div>

        <button type="submit" class="submit-btn">
            <?= icon('log-in', 18, '', 'white') ?>
            Se connecter
        </button>
    </form>

    <div class="card-footer">
        <a href="/" class="back-link">
            <?= icon('arrow-left', 14) ?>
            Retour au site
        </a>
        <span class="copyright">&copy; <?= date('Y') ?> Fête du Cidre — L'Hôtellerie de Flée</span>
    </div>

</div>

<script>
(function() {
    var toggle = document.getElementById('eyeToggle');
    var pwd = document.getElementById('password');
    var visible = false;

    toggle.addEventListener('click', function() {
        visible = !visible;
        pwd.type = visible ? 'text' : 'password';
        toggle.innerHTML = visible
            ? '<?= icon("eye-off", 16) ?>'
            : '<?= icon("eye", 16) ?>';
    });
})();
</script>

</body>
</html>
