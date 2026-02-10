<?php
/**
 * Page réinitialisation mot de passe — affichage autonome (sans layout sidebar).
 * Variables : $title, $token, $email
 */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Nouveau mot de passe — Administration — Fête du Cidre</title>
    <style>
        <?= \App\Core\Theme::cssVariables() ?>

        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { font-size: 16px; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
            background: var(--creme, #FAF5EC);
            position: relative; overflow: hidden;
        }

        /* ===== BACKGROUND ===== */
        .bg-pattern {
            position: fixed; inset: 0; opacity: 0.035;
            background-image:
                radial-gradient(circle at 20% 50%, var(--vert-profond, #2C4A2E) 1px, transparent 1px),
                radial-gradient(circle at 80% 20%, var(--vert-profond, #2C4A2E) 1px, transparent 1px);
            background-size: 60px 60px, 80px 80px; pointer-events: none;
        }
        .bg-glow-1 {
            position: fixed; width: 600px; height: 600px; border-radius: 50%;
            background: radial-gradient(circle, var(--vert-profond, #2C4A2E) 0%, transparent 70%);
            opacity: 0.04; top: -15%; right: -10%; pointer-events: none;
        }
        .bg-glow-2 {
            position: fixed; width: 500px; height: 500px; border-radius: 50%;
            background: radial-gradient(circle, var(--orange-cidre, #D4833B) 0%, transparent 70%);
            opacity: 0.04; bottom: -15%; left: -10%; pointer-events: none;
        }

        /* ===== CARD ===== */
        .card {
            position: relative; z-index: 2; width: 100%; max-width: 420px; margin: 2rem;
            background: var(--blanc, #FFFDF8); border-radius: 28px;
            border: 1.5px solid var(--creme-fonce, #F0E8D8);
            box-shadow: 0 4px 6px rgba(44,74,46,.02), 0 12px 40px rgba(44,74,46,.06), 0 40px 80px rgba(44,74,46,.04);
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
            width: 64px; height: 64px; margin: 0 auto 1.2rem;
            border-radius: 18px; display: flex; align-items: center; justify-content: center;
            background: var(--orange-cidre, #D4833B);
            animation: fadeInUp 0.5s 0.1s ease both; position: relative;
        }
        .logo-mark::after {
            content: ''; position: absolute; inset: -3px; border-radius: 21px;
            border: 2px solid var(--orange-doux, #E8A95B); opacity: 0.2;
        }
        .card-header h1 {
            font-size: 1.5rem; font-weight: 800; color: var(--vert-profond, #2C4A2E);
            margin-bottom: 0.3rem; animation: fadeInUp 0.5s 0.15s ease both;
        }
        .card-header p {
            font-size: 0.88rem; color: var(--texte-leger, #6B5D4F); line-height: 1.5;
            animation: fadeInUp 0.5s 0.2s ease both;
        }

        /* ===== FLASH ===== */
        .flash {
            display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1rem;
            border-radius: 12px; font-size: 0.84rem; font-weight: 500;
            margin-bottom: 1.2rem; animation: shakeIn 0.4s ease both;
        }
        .flash-error { background: #FEF2F2; border: 1.5px solid #FECACA; color: #D94040; }
        .flash-success { background: #F0FDF4; border: 1.5px solid #BBF7D0; color: #166534; }
        @keyframes shakeIn {
            0% { transform: translateX(-8px); opacity: 0; }
            30% { transform: translateX(5px); }
            60% { transform: translateX(-3px); }
            100% { transform: translateX(0); opacity: 1; }
        }

        /* ===== FORM ===== */
        .form-group { margin-bottom: 1.1rem; animation: fadeInUp 0.5s ease both; }
        .form-group:nth-child(1) { animation-delay: 0.25s; }
        .form-group:nth-child(2) { animation-delay: 0.3s; }
        .form-group label {
            display: block; font-size: 0.76rem; font-weight: 600; letter-spacing: 0.06em;
            text-transform: uppercase; color: var(--texte-leger, #6B5D4F); margin-bottom: 0.45rem;
        }
        .input-wrap { position: relative; display: flex; align-items: center; }
        .input-icon {
            position: absolute; left: 1rem; color: var(--texte-leger, #6B5D4F);
            opacity: 0.5; display: flex; pointer-events: none; transition: opacity 0.3s;
        }
        .input-wrap input {
            width: 100%; padding: 0.85rem 2.8rem;
            border: 2px solid var(--creme-fonce, #F0E8D8); border-radius: 14px;
            font-family: inherit; font-size: 0.92rem; color: var(--texte, #2A2318);
            background: white; outline: none; transition: border-color 0.3s, box-shadow 0.3s;
        }
        .input-wrap input::placeholder { color: var(--texte-leger, #6B5D4F); opacity: 0.45; }
        .input-wrap input:focus {
            border-color: var(--vert-clair, #7A9E6B);
            box-shadow: 0 0 0 4px rgba(122,158,107,0.1);
        }
        .input-wrap input:focus ~ .input-icon { opacity: 1; }

        .eye-toggle {
            position: absolute; right: 0.8rem; background: none; border: none;
            color: var(--texte-leger, #6B5D4F); opacity: 0.5; cursor: pointer;
            padding: 0.3rem; display: flex; transition: opacity 0.3s;
        }
        .eye-toggle:hover { opacity: 1; }

        /* ===== PASSWORD STRENGTH ===== */
        .pw-strength { display: flex; gap: 4px; margin-top: 0.5rem; height: 4px; }
        .pw-bar {
            flex: 1; height: 100%; border-radius: 100px;
            background: var(--creme-fonce, #F0E8D8); transition: background 0.3s;
        }
        .pw-strength[data-level="1"] .pw-bar:nth-child(1) { background: #D94040; }
        .pw-strength[data-level="2"] .pw-bar:nth-child(-n+2) { background: #D4833B; }
        .pw-strength[data-level="3"] .pw-bar:nth-child(-n+3) { background: #E8A95B; }
        .pw-strength[data-level="4"] .pw-bar { background: #16a34a; }

        .pw-label {
            font-size: 0.7rem; font-weight: 600; margin-top: 0.3rem;
            color: var(--texte-leger, #6B5D4F); text-align: right; transition: color 0.3s;
        }

        /* ===== REQUIREMENTS ===== */
        .pw-requirements {
            margin-top: 0.6rem; padding: 0.7rem 0.8rem;
            background: var(--creme, #FAF5EC); border-radius: 10px;
            display: flex; flex-wrap: wrap; gap: 0.15rem 1rem;
        }
        .pw-req {
            font-size: 0.72rem; color: var(--texte-leger, #6B5D4F);
            display: flex; align-items: center; gap: 0.3rem; transition: color 0.3s;
        }
        .pw-req.met { color: #16a34a; }
        .pw-req .req-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: var(--creme-fonce, #F0E8D8); flex-shrink: 0; transition: background 0.3s;
        }
        .pw-req.met .req-dot { background: #16a34a; }

        /* ===== BUTTON ===== */
        .submit-btn {
            width: 100%; padding: 0.95rem; border: none; border-radius: 14px;
            background: var(--vert-profond, #2C4A2E); color: white;
            font-family: inherit; font-size: 0.95rem; font-weight: 600; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 0.5rem;
            transition: background 0.3s, transform 0.15s, box-shadow 0.3s;
            margin-top: 0.4rem; animation: fadeInUp 0.5s 0.4s ease both;
        }
        .submit-btn:hover {
            background: var(--vert-mousse, #4A6B3E); transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(44,74,46,0.25);
        }
        .submit-btn:active { transform: translateY(0); }

        /* ===== FOOTER ===== */
        .card-footer {
            text-align: center; margin-top: 1.8rem; padding-top: 1.4rem;
            border-top: 1.5px solid var(--creme-fonce, #F0E8D8);
            animation: fadeInUp 0.5s 0.45s ease both;
        }
        .back-link {
            display: inline-flex; align-items: center; gap: 0.4rem;
            font-size: 0.84rem; color: var(--texte-leger, #6B5D4F);
            text-decoration: none; transition: color 0.3s;
        }
        .back-link:hover { color: var(--orange-cidre, #D4833B); }
        .copyright {
            display: block; margin-top: 1rem; font-size: 0.72rem;
            color: var(--texte-leger, #6B5D4F); opacity: 0.4;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 480px) {
            .card { padding: 2rem 1.5rem 1.8rem; margin: 1rem; border-radius: 22px; }
            .card-header h1 { font-size: 1.3rem; }
            .pw-requirements { flex-direction: column; gap: 0.2rem; }
        }
    </style>
</head>
<body>

<div class="bg-pattern"></div>
<div class="bg-glow-1"></div>
<div class="bg-glow-2"></div>

<div class="card">
    <div class="card-header">
        <div class="logo-mark">
            <?= icon('lock-keyhole', 30, '', '#FAF5EC') ?>
        </div>
        <h1>Nouveau mot de passe</h1>
        <p>Choisissez un mot de passe sécurisé pour votre compte.</p>
    </div>

    <?= flash('error') ?>

    <form method="post" action="/admin/reset-password/<?= htmlspecialchars($token ?? '') ?>" novalidate>
        <?= csrf_field() ?>

        <div class="form-group">
            <label for="password">Nouveau mot de passe</label>
            <div class="input-wrap">
                <span class="input-icon"><?= icon('key-round', 16) ?></span>
                <input type="password" id="password" name="password"
                       placeholder="••••••••" autocomplete="new-password" required autofocus>
                <button type="button" class="eye-toggle" id="eyeToggle1" aria-label="Afficher le mot de passe">
                    <?= icon('eye', 16) ?>
                </button>
            </div>
            <div class="pw-strength" id="pwStrength" data-level="0">
                <div class="pw-bar"></div>
                <div class="pw-bar"></div>
                <div class="pw-bar"></div>
                <div class="pw-bar"></div>
            </div>
            <div class="pw-label" id="pwLabel"></div>
            <div class="pw-requirements">
                <span class="pw-req" id="req-length"><span class="req-dot"></span> 8 caractères min.</span>
                <span class="pw-req" id="req-upper"><span class="req-dot"></span> 1 majuscule</span>
                <span class="pw-req" id="req-lower"><span class="req-dot"></span> 1 minuscule</span>
                <span class="pw-req" id="req-number"><span class="req-dot"></span> 1 chiffre</span>
            </div>
        </div>

        <div class="form-group">
            <label for="password_confirm">Confirmer le mot de passe</label>
            <div class="input-wrap">
                <span class="input-icon"><?= icon('shield-check', 16) ?></span>
                <input type="password" id="password_confirm" name="password_confirm"
                       placeholder="••••••••" autocomplete="new-password" required>
                <button type="button" class="eye-toggle" id="eyeToggle2" aria-label="Afficher le mot de passe">
                    <?= icon('eye', 16) ?>
                </button>
            </div>
        </div>

        <button type="submit" class="submit-btn">
            <?= icon('check', 18, '', 'white') ?>
            Réinitialiser
        </button>
    </form>

    <div class="card-footer">
        <a href="/admin/login" class="back-link">
            <?= icon('arrow-left', 14) ?>
            Retour à la connexion
        </a>
        <span class="copyright">&copy; <?= date('Y') ?> Fête du Cidre — L'Hôtellerie de Flée</span>
    </div>
</div>

<script>
(function() {
    var pwInput = document.getElementById('password');
    var confirmInput = document.getElementById('password_confirm');

    // Password strength
    pwInput.addEventListener('input', function() {
        var val = this.value;
        var level = 0;
        var checks = {
            length: val.length >= 8,
            upper: /[A-Z]/.test(val),
            lower: /[a-z]/.test(val),
            number: /[0-9]/.test(val)
        };

        for (var key in checks) {
            var el = document.getElementById('req-' + key);
            if (el) {
                if (checks[key]) { el.classList.add('met'); level++; }
                else { el.classList.remove('met'); }
            }
        }

        document.getElementById('pwStrength').dataset.level = level;
        var labels = ['', 'Faible', 'Moyen', 'Correct', 'Fort'];
        var colors = ['', '#D94040', '#D4833B', '#E8A95B', '#16a34a'];
        var labelEl = document.getElementById('pwLabel');
        labelEl.textContent = val.length > 0 ? labels[level] : '';
        labelEl.style.color = colors[level];
    });

    // Eye toggles
    function setupToggle(btnId, inputId) {
        var btn = document.getElementById(btnId);
        var input = document.getElementById(inputId);
        var visible = false;
        btn.addEventListener('click', function() {
            visible = !visible;
            input.type = visible ? 'text' : 'password';
            btn.innerHTML = visible
                ? '<?= icon("eye-off", 16) ?>'
                : '<?= icon("eye", 16) ?>';
        });
    }

    setupToggle('eyeToggle1', 'password');
    setupToggle('eyeToggle2', 'password_confirm');
})();
</script>

</body>
</html>
