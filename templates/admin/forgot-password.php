<?php
/**
 * Page mot de passe oublié — affichage autonome (sans layout sidebar).
 * Variables : $title
 * Affiche le formulaire ou l'état de succès selon le flash.
 */
$emailSent = $_SESSION['reset_email_sent'] ?? null;
$hasSuccess = !empty($_SESSION['flash']['success']);
unset($_SESSION['reset_email_sent']);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Mot de passe oublié — Administration — Fête du Cidre</title>
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
            position: fixed; inset: 0; opacity: 0.035;
            background-image:
                radial-gradient(circle at 20% 50%, var(--vert-profond, #2C4A2E) 1px, transparent 1px),
                radial-gradient(circle at 80% 20%, var(--vert-profond, #2C4A2E) 1px, transparent 1px);
            background-size: 60px 60px, 80px 80px;
            pointer-events: none;
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

        /* ===== STEPS ===== */
        .step { display: none; }
        .step.active { display: block; }

        /* ===== HEADER ===== */
        .card-header { text-align: center; margin-bottom: 2rem; }

        .logo-mark {
            width: 64px; height: 64px; margin: 0 auto 1.2rem;
            border-radius: 18px; display: flex; align-items: center; justify-content: center;
            animation: fadeInUp 0.5s 0.1s ease both; position: relative;
        }
        .logo-mark::after {
            content: ''; position: absolute; inset: -3px; border-radius: 21px; opacity: 0.2;
        }
        .logo-mark.step-email { background: var(--vert-profond, #2C4A2E); }
        .logo-mark.step-email::after { border: 2px solid var(--vert-clair, #7A9E6B); }
        .logo-mark.step-success { background: #16a34a; }
        .logo-mark.step-success::after { border: 2px solid #4ade80; }

        .card-header h1 {
            font-size: 1.5rem; font-weight: 800; color: var(--vert-profond, #2C4A2E);
            margin-bottom: 0.3rem; animation: fadeInUp 0.5s 0.15s ease both;
        }
        .card-header p {
            font-size: 0.88rem; color: var(--texte-leger, #6B5D4F); line-height: 1.5;
            animation: fadeInUp 0.5s 0.2s ease both;
        }
        .email-highlight { font-weight: 600; color: var(--texte, #2A2318); }

        /* ===== FLASH / ALERTS ===== */
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
        .form-group { margin-bottom: 1.1rem; animation: fadeInUp 0.5s 0.25s ease both; }
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
            width: 100%; padding: 0.85rem 1rem 0.85rem 2.8rem;
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

        /* ===== BUTTON ===== */
        .submit-btn {
            width: 100%; padding: 0.95rem; border: none; border-radius: 14px;
            background: var(--vert-profond, #2C4A2E); color: white;
            font-family: inherit; font-size: 0.95rem; font-weight: 600; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 0.5rem;
            transition: background 0.3s, transform 0.15s, box-shadow 0.3s;
            margin-top: 0.4rem; animation: fadeInUp 0.5s 0.35s ease both;
        }
        .submit-btn:hover {
            background: var(--vert-mousse, #4A6B3E); transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(44,74,46,0.25);
        }
        .submit-btn:active { transform: translateY(0); }

        /* ===== SUCCESS ANIMATION ===== */
        .success-checkmark { width: 56px; height: 56px; margin: 0 auto 0.5rem; }
        .checkmark-circle {
            stroke-dasharray: 166; stroke-dashoffset: 166;
            animation: circleStroke 0.6s 0.2s ease-in-out forwards;
        }
        .checkmark-check {
            stroke-dasharray: 48; stroke-dashoffset: 48;
            animation: checkStroke 0.3s 0.7s ease-in-out forwards;
        }
        @keyframes circleStroke { to { stroke-dashoffset: 0; } }
        @keyframes checkStroke { to { stroke-dashoffset: 0; } }

        /* ===== INFO ALERT (step 2) ===== */
        .info-alert {
            display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1rem;
            border-radius: 12px; font-size: 0.84rem; font-weight: 500;
            margin-bottom: 1.2rem; background: #F0FDF4; border: 1.5px solid #BBF7D0; color: #166534;
            animation: fadeInUp 0.5s 0.3s ease both;
        }

        /* ===== RESEND ===== */
        .resend-area { text-align: center; margin-top: 1rem; animation: fadeInUp 0.5s 0.35s ease both; }
        .countdown {
            display: inline-flex; align-items: center; gap: 0.35rem;
            font-size: 0.82rem; color: var(--texte-leger, #6B5D4F);
        }
        .countdown-num { font-weight: 700; color: var(--orange-cidre, #D4833B); font-variant-numeric: tabular-nums; }
        .resend-form { display: none; }
        .resend-form.show { display: block; }
        .resend-btn {
            background: none; border: none; cursor: pointer; font-family: inherit;
            font-size: 0.84rem; font-weight: 600; color: var(--orange-cidre, #D4833B);
            display: inline-flex; align-items: center; gap: 0.35rem; transition: color 0.3s;
        }
        .resend-btn:hover { color: var(--vert-profond, #2C4A2E); }

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
        }
    </style>
</head>
<body>

<div class="bg-pattern"></div>
<div class="bg-glow-1"></div>
<div class="bg-glow-2"></div>

<div class="card">

    <!-- ═══ STEP 1 : Email form ═══ -->
    <div class="step <?= ($hasSuccess && $emailSent) ? '' : 'active' ?>" id="step-email">
        <div class="card-header">
            <div class="logo-mark step-email">
                <?= icon('key-round', 30, '', '#FAF5EC') ?>
            </div>
            <h1>Mot de passe oublié</h1>
            <p>Saisissez votre adresse e-mail et nous vous enverrons un lien de réinitialisation.</p>
        </div>

        <?= flash('error') ?>

        <form method="post" action="/admin/forgot-password" novalidate>
            <?= csrf_field() ?>

            <div class="form-group">
                <label for="email">Adresse e-mail</label>
                <div class="input-wrap">
                    <span class="input-icon"><?= icon('mail', 16) ?></span>
                    <input type="email" id="email" name="email"
                           value="<?= old('email') ?>"
                           placeholder="admin@feteducidre.fr"
                           autocomplete="email" required autofocus>
                </div>
            </div>

            <button type="submit" class="submit-btn">
                <?= icon('send', 18, '', 'white') ?>
                Envoyer le lien
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

    <!-- ═══ STEP 2 : Success / Email sent ═══ -->
    <div class="step <?= ($hasSuccess && $emailSent) ? 'active' : '' ?>" id="step-success">
        <div class="card-header">
            <div class="logo-mark step-success">
                <svg class="success-checkmark" viewBox="0 0 56 56" fill="none">
                    <circle class="checkmark-circle" cx="28" cy="28" r="24" stroke="#FFFFFF" stroke-width="3" fill="none"/>
                    <path class="checkmark-check" d="M17 28l7 7 15-15" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                </svg>
            </div>
            <h1>E-mail envoyé !</h1>
            <p>Un lien de réinitialisation a été envoyé à<br>
               <span class="email-highlight"><?= htmlspecialchars($emailSent ?? '') ?></span></p>
        </div>

        <?= flash('success') ?>

        <div class="info-alert">
            <?= icon('info', 16) ?>
            <span>Vérifiez vos spams si vous ne voyez pas l'e-mail dans les prochaines minutes.</span>
        </div>

        <div class="resend-area">
            <div class="countdown" id="countdown">
                <?= icon('clock', 14) ?>
                Renvoyer dans <span class="countdown-num" id="countdownNum">60</span>s
            </div>
            <form method="post" action="/admin/forgot-password" class="resend-form" id="resendForm">
                <?= csrf_field() ?>
                <input type="hidden" name="email" value="<?= htmlspecialchars($emailSent ?? '') ?>">
                <button type="submit" class="resend-btn">
                    <?= icon('refresh-cw', 14) ?>
                    Renvoyer l'e-mail
                </button>
            </form>
        </div>

        <div class="card-footer">
            <a href="/admin/login" class="back-link">
                <?= icon('arrow-left', 14) ?>
                Retour à la connexion
            </a>
            <span class="copyright">&copy; <?= date('Y') ?> Fête du Cidre — L'Hôtellerie de Flée</span>
        </div>
    </div>

</div>

<?php if ($hasSuccess && $emailSent): ?>
<script>
(function() {
    var seconds = 60;
    var numEl = document.getElementById('countdownNum');
    var countdownEl = document.getElementById('countdown');
    var resendEl = document.getElementById('resendForm');

    var interval = setInterval(function() {
        seconds--;
        numEl.textContent = seconds;
        if (seconds <= 0) {
            clearInterval(interval);
            countdownEl.style.display = 'none';
            resendEl.classList.add('show');
        }
    }, 1000);
})();
</script>
<?php endif; ?>

</body>
</html>
