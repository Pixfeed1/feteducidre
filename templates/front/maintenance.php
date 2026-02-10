<?php
/**
 * Page de maintenance — template autonome premium (pas de layout).
 * Variables disponibles : $siteName, $estimatedReturn
 */
$siteName = htmlspecialchars($siteName ?? 'Fête du Cidre');
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Maintenance — <?= $siteName ?></title>
    <style>
        :root {
            --vert-profond: #2C4A2E;
            --vert-mousse: #4A6B3E;
            --vert-clair: #5B8C3E;
            --creme: #FAF5EC;
            --creme-fonce: #F0E6D3;
            --orange-cidre: #D4833B;
            --orange-clair: #E8A95B;
            --brun-bois: #6B4226;
            --texte: #2A2318;
            --blanc: #ffffff;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                         Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
            background: linear-gradient(170deg, var(--creme) 0%, var(--creme-fonce) 50%, #E8DCC8 100%);
            color: var(--texte);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }

        /* ===== Decorative background apples ===== */
        .deco-apple {
            position: fixed;
            border-radius: 50%;
            opacity: 0.08;
            pointer-events: none;
            z-index: 0;
        }
        .deco-apple-1 {
            width: 300px; height: 300px;
            background: var(--vert-profond);
            top: -80px; right: -60px;
            animation: applePulse 8s ease-in-out infinite;
        }
        .deco-apple-2 {
            width: 200px; height: 200px;
            background: var(--orange-cidre);
            bottom: -40px; left: -40px;
            animation: applePulse 10s ease-in-out infinite 2s;
        }
        .deco-apple-3 {
            width: 150px; height: 150px;
            background: var(--vert-clair);
            top: 40%; left: -30px;
            animation: applePulse 12s ease-in-out infinite 4s;
        }

        @keyframes applePulse {
            0%, 100% { transform: scale(1); opacity: 0.08; }
            50% { transform: scale(1.15); opacity: 0.12; }
        }

        /* ===== Falling leaves ===== */
        .leaf {
            position: fixed;
            top: -40px;
            z-index: 0;
            pointer-events: none;
            opacity: 0;
            animation: leafFall linear forwards;
        }

        @keyframes leafFall {
            0% { transform: translateY(0) rotate(0deg); opacity: 0; }
            10% { opacity: 0.6; }
            90% { opacity: 0.4; }
            100% { transform: translateY(105vh) rotate(360deg); opacity: 0; }
        }

        /* ===== Main content ===== */
        .mnt-content {
            position: relative;
            z-index: 1;
            text-align: center;
            max-width: 580px;
            padding: 2rem 1.5rem;
            animation: fadeInUp .8s ease both;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ===== Logo / Apple icon ===== */
        .mnt-logo {
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100px;
            height: 100px;
            margin-bottom: 2rem;
        }
        .mnt-logo-circle {
            position: absolute;
            inset: 0;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--vert-profond), var(--vert-mousse));
            box-shadow: 0 8px 32px rgba(44, 74, 46, .25);
            animation: logoBounce 3s ease-in-out infinite;
        }
        .mnt-logo-ring {
            position: absolute;
            inset: -8px;
            border-radius: 50%;
            border: 2px solid var(--vert-clair);
            opacity: 0;
            animation: logoPing 3s ease-in-out infinite;
        }
        .mnt-logo .icon {
            position: relative;
            z-index: 1;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,.15));
        }

        @keyframes logoBounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.06); }
        }
        @keyframes logoPing {
            0% { transform: scale(.9); opacity: 0; }
            50% { transform: scale(1.15); opacity: .4; }
            100% { transform: scale(1.3); opacity: 0; }
        }

        /* ===== Title & subtitle ===== */
        .mnt-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--vert-profond);
            line-height: 1.2;
            margin-bottom: .75rem;
        }
        .mnt-subtitle {
            font-size: 1.1rem;
            line-height: 1.6;
            color: var(--brun-bois);
            margin-bottom: 2rem;
            max-width: 440px;
            margin-left: auto;
            margin-right: auto;
        }

        /* ===== Progress bar ===== */
        .mnt-progress {
            max-width: 320px;
            margin: 0 auto 2.5rem;
        }
        .mnt-progress-label {
            display: flex;
            justify-content: space-between;
            font-size: .8rem;
            color: var(--brun-bois);
            margin-bottom: .5rem;
            font-weight: 500;
        }
        .mnt-progress-track {
            height: 8px;
            border-radius: 4px;
            background: var(--creme-fonce);
            overflow: hidden;
            position: relative;
        }
        .mnt-progress-bar {
            height: 100%;
            width: 65%;
            border-radius: 4px;
            background: linear-gradient(90deg, var(--vert-profond), var(--vert-clair));
            position: relative;
            overflow: hidden;
        }
        .mnt-progress-bar::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,.3), transparent);
            animation: progressShimmer 2s linear infinite;
        }

        @keyframes progressShimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        /* ===== Feature cards ===== */
        .mnt-features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2.5rem;
        }
        .mnt-feat {
            background: var(--blanc);
            border-radius: 12px;
            padding: 1.25rem 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,.05);
            transition: transform .3s, box-shadow .3s;
        }
        .mnt-feat:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,.1);
        }
        .mnt-feat-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            border-radius: 10px;
            margin-bottom: .75rem;
        }
        .mnt-feat-icon.feat-trophee { background: linear-gradient(135deg, var(--orange-cidre), var(--orange-clair)); }
        .mnt-feat-icon.feat-galerie { background: linear-gradient(135deg, var(--vert-profond), var(--vert-mousse)); }
        .mnt-feat-icon.feat-rando   { background: linear-gradient(135deg, var(--brun-bois), var(--orange-cidre)); }
        .mnt-feat-name {
            display: block;
            font-size: .85rem;
            font-weight: 600;
            color: var(--vert-profond);
            margin-bottom: .25rem;
        }
        .mnt-feat-desc {
            font-size: .75rem;
            color: var(--brun-bois);
            line-height: 1.4;
        }

        /* ===== Info card ===== */
        .mnt-info {
            background: var(--blanc);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,.05);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            text-align: left;
            max-width: 420px;
            margin-left: auto;
            margin-right: auto;
        }
        .mnt-info-icon {
            flex-shrink: 0;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--vert-profond), var(--vert-mousse));
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .mnt-info-text {
            font-size: .85rem;
            color: var(--brun-bois);
            line-height: 1.5;
        }
        .mnt-info-text a {
            color: var(--vert-profond);
            font-weight: 600;
            text-decoration: none;
        }
        .mnt-info-text a:hover { text-decoration: underline; }

        /* ===== Social links ===== */
        .mnt-social {
            display: flex;
            gap: .75rem;
            justify-content: center;
            margin-bottom: 2rem;
        }
        .mnt-social a {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--blanc);
            box-shadow: 0 2px 6px rgba(0,0,0,.06);
            color: var(--vert-profond);
            transition: transform .25s, background .25s, color .25s;
        }
        .mnt-social a:hover {
            background: var(--vert-profond);
            color: var(--blanc);
            transform: scale(1.1);
        }
        .mnt-social a svg {
            width: 18px;
            height: 18px;
        }
        .mnt-social a.fb svg { fill: currentColor; stroke: none; }
        .mnt-social a.ig svg { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

        /* ===== Footer ===== */
        .mnt-footer {
            font-size: .8rem;
            color: var(--brun-bois);
            opacity: .6;
        }

        /* ===== Responsive ===== */
        @media (max-width: 640px) {
            .mnt-title { font-size: 1.5rem; }
            .mnt-subtitle { font-size: 1rem; }
            .mnt-features { grid-template-columns: 1fr; gap: .75rem; }
            .mnt-feat { display: flex; align-items: center; gap: 1rem; text-align: left; padding: 1rem; }
            .mnt-feat-icon { margin-bottom: 0; flex-shrink: 0; }
            .mnt-info { flex-direction: column; text-align: center; }
            .deco-apple-1 { width: 200px; height: 200px; }
            .deco-apple-2 { width: 140px; height: 140px; }
            .deco-apple-3 { display: none; }
        }
    </style>
</head>
<body>

<!-- Decorative pulsing circles -->
<div class="deco-apple deco-apple-1"></div>
<div class="deco-apple deco-apple-2"></div>
<div class="deco-apple deco-apple-3"></div>

<div class="mnt-content">

    <!-- Animated apple logo -->
    <div class="mnt-logo">
        <div class="mnt-logo-ring"></div>
        <div class="mnt-logo-circle"></div>
        <img src="/assets/images/logo.png" alt="Fête du Cidre" style="width:60px;height:auto;">
    </div>

    <h1 class="mnt-title">La Fête du Cidre fait peau neuve</h1>
    <p class="mnt-subtitle">
        Nous préparons de belles nouveautés pour vous. Le site sera de retour très bientôt,
        encore plus savoureux qu'avant !
    </p>

    <!-- Progress bar -->
    <div class="mnt-progress">
        <div class="mnt-progress-label">
            <span><?= icon('loader', 12) ?> Progression</span>
            <span>65%</span>
        </div>
        <div class="mnt-progress-track">
            <div class="mnt-progress-bar"></div>
        </div>
    </div>

    <!-- Feature cards -->
    <div class="mnt-features">
        <div class="mnt-feat">
            <div class="mnt-feat-icon feat-trophee">
                <?= icon('trophy', 20, '', 'white') ?>
            </div>
            <div>
                <span class="mnt-feat-name">Concours</span>
                <span class="mnt-feat-desc">Concours de cidre et animations</span>
            </div>
        </div>
        <div class="mnt-feat">
            <div class="mnt-feat-icon feat-galerie">
                <?= icon('camera', 20, '', 'white') ?>
            </div>
            <div>
                <span class="mnt-feat-name">Galerie</span>
                <span class="mnt-feat-desc">Photos et souvenirs de la fête</span>
            </div>
        </div>
        <div class="mnt-feat">
            <div class="mnt-feat-icon feat-rando">
                <?= icon('footprints', 20, '', 'white') ?>
            </div>
            <div>
                <span class="mnt-feat-name">Randonnées</span>
                <span class="mnt-feat-desc">Parcours à travers les vergers</span>
            </div>
        </div>
    </div>

    <!-- Info card -->
    <div class="mnt-info">
        <div class="mnt-info-icon">
            <?= icon('mail', 16, '', 'white') ?>
        </div>
        <div class="mnt-info-text">
            Une question ? Contactez-nous à
            <a href="mailto:contact@fetecidre.fr">contact@fetecidre.fr</a>
            <?php if (!empty($estimatedReturn)): ?>
                <br>Retour estimé : <strong><?= htmlspecialchars($estimatedReturn) ?></strong>
            <?php endif; ?>
        </div>
    </div>

    <!-- Social links -->
    <div class="mnt-social">
        <a href="https://facebook.com" class="fb" aria-label="Facebook" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
        </a>
        <a href="https://instagram.com" class="ig" aria-label="Instagram" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
        </a>
    </div>

    <!-- Footer -->
    <div class="mnt-footer">
        &copy; <?= date('Y') ?> <?= $siteName ?> — L'Hôtellerie de Flée, Maine-et-Loire
    </div>

</div>

<!-- Falling leaves animation -->
<script>
(function() {
    var colors = ['#4A6B3E', '#5B8C3E', '#D4833B', '#E8A95B', '#6B4226'];
    var leafSvg = '<svg viewBox="0 0 24 24" width="SIZE" height="SIZE"><path d="M11 20A7 7 0 0 1 9.8 6.9C15.5 4.9 17 3.5 19 2c1 2 2 4.5 1 8-1.5 5.5-4 7-9 10Z" fill="COLOR" opacity=".7"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" fill="none" stroke="COLOR" stroke-width="1.5"/></svg>';

    function createLeaf() {
        var el = document.createElement('div');
        el.className = 'leaf';
        var size = 16 + Math.random() * 16;
        var color = colors[Math.floor(Math.random() * colors.length)];
        el.innerHTML = leafSvg.replace(/SIZE/g, size).replace(/COLOR/g, color);
        el.style.left = Math.random() * 100 + 'vw';
        el.style.animationDuration = (8 + Math.random() * 8) + 's';
        el.style.animationDelay = (Math.random() * 2) + 's';
        document.body.appendChild(el);
        setTimeout(function() { el.remove(); }, 18000);
    }

    // Initial burst
    for (var i = 0; i < 4; i++) {
        setTimeout(createLeaf, i * 600);
    }
    // Continuous
    setInterval(createLeaf, 3000);
})();
</script>

</body>
</html>
