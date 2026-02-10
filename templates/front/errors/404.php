<?php
/**
 * Template page d'erreur 404 — Pomme perdue dans le verger.
 * Inclus par Response::notFound() sans layout.
 * CSS : /assets/css/404.css — JS : /assets/js/404.js
 */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page introuvable — Fête du Cidre</title>
<meta name="robots" content="noindex, nofollow">

<!-- Fonts -->
<link rel="preload" href="/assets/fonts/playfair-display-v37-latin-900.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/source-sans-3-v15-latin-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">

<!-- Variables couleurs -->
<style>
<?php try { echo \App\Core\Theme::cssVariables(); } catch (\Exception) { ?>
:root {
  --vert-profond: #2C4A2E;
  --vert-mousse: #4A6B3E;
  --vert-clair: #7A9E6B;
  --orange-cidre: #D4833B;
  --orange-doux: #E8A95B;
  --creme: #FAF5EC;
  --creme-fonce: #F0E8D8;
  --brun: #5C3D2E;
  --texte: #2A2318;
  --texte-leger: #6B5D4F;
  --blanc: #FFFDF8;
}
<?php } ?>

/* Fonts locales */
@font-face{font-family:'Playfair Display';src:url('/assets/fonts/playfair-display-v37-latin-900.woff2') format('woff2');font-weight:900;font-style:normal;font-display:swap}
@font-face{font-family:'Playfair Display';src:url('/assets/fonts/playfair-display-v37-latin-700.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('/assets/fonts/source-sans-3-v15-latin-regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('/assets/fonts/source-sans-3-v15-latin-600.woff2') format('woff2');font-weight:600;font-style:normal;font-display:swap}

/* Reset minimal */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
</style>

<!-- CSS 404 -->
<link rel="stylesheet" href="/assets/css/404.css">
</head>
<body class="page-404">

<!-- Formes décoratives -->
<div class="deco-shapes">
  <div class="deco-shape"></div>
  <div class="deco-shape"></div>
  <div class="deco-shape"></div>
  <div class="deco-shape"></div>
</div>

<!-- Feuilles flottantes -->
<div class="leaves" id="leaves"></div>

<!-- Contenu -->
<div class="error-container">

  <!-- Pomme perdue -->
  <div class="apple-scene">
    <svg class="apple-svg" width="150" height="150" viewBox="0 0 150 150" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="75" cy="138" rx="35" ry="6" fill="#2C4A2E" opacity="0.07"/>
      <g class="apple-body">
        <ellipse cx="75" cy="88" rx="40" ry="42" fill="#7A9E6B"/>
        <ellipse cx="60" cy="80" rx="18" ry="28" fill="#8DB87E" opacity="0.6"/>
        <ellipse cx="55" cy="74" rx="8" ry="14" fill="#A3C48E" opacity="0.4"/>
        <ellipse cx="90" cy="95" rx="15" ry="22" fill="#5C8A52" opacity="0.3"/>
        <ellipse cx="75" cy="48" rx="12" ry="4" fill="#5C8A52" opacity="0.3"/>
        <path d="M75 48 C73 38, 78 28, 82 24" stroke="#8B6B4A" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        <path d="M80 30 C86 24, 96 26, 98 32 C100 38, 92 40, 84 34Z" fill="#4A6B3E"/>
        <path d="M80 30 C88 30, 94 32, 98 32" stroke="#5C8A52" stroke-width="0.8" fill="none"/>
        <g>
          <circle cx="62" cy="82" r="6" fill="white"/>
          <circle cx="60" cy="82" r="3.5" fill="#2A2318">
            <animate attributeName="cx" values="60;64;60;58;60" dur="3s" repeatCount="indefinite"/>
          </circle>
          <circle cx="59" cy="80.5" r="1.2" fill="white"/>
          <circle cx="88" cy="82" r="6" fill="white"/>
          <circle cx="86" cy="82" r="3.5" fill="#2A2318">
            <animate attributeName="cx" values="86;90;86;84;86" dur="3s" repeatCount="indefinite"/>
          </circle>
          <circle cx="85" cy="80.5" r="1.2" fill="white"/>
        </g>
        <path d="M69 96 Q75 92, 81 96" stroke="#2A2318" stroke-width="1.8" fill="none" stroke-linecap="round"/>
      </g>
      <g class="question-mark">
        <text x="105" y="52" font-family="Playfair Display, serif" font-size="28" font-weight="900" fill="#D4833B" opacity="0.7">?</text>
      </g>
    </svg>
  </div>

  <!-- Code erreur -->
  <div class="error-code">
    <span>4</span><span class="zero-1">0</span><span class="zero-2">4</span>
  </div>

  <h1 class="error-title">Cette page s'est perdue dans le verger</h1>

  <p class="error-subtitle">
    La page que vous cherchez n'existe pas ou a été déplacée.<br>
    Pas de panique, le cidre coule toujours !
  </p>

  <div class="separator">
    <div class="line"></div>
    <div class="dot"></div>
    <div class="line"></div>
  </div>

  <div class="error-actions">
    <a href="/" class="btn btn-primary">
      <?= function_exists('icon') ? icon('home', 16) : '' ?>
      Retour à l'accueil
    </a>
    <button class="btn btn-secondary" onclick="history.back()">
      <?= function_exists('icon') ? icon('arrow-left', 16) : '' ?>
      Page précédente
    </button>
  </div>

  <div class="suggestions">
    <div class="suggestions-title">Peut-être cherchez-vous</div>
    <div class="suggestions-links">
      <a href="/programme">Programme</a>
      <a href="/boutique">Boutique</a>
      <a href="/concours">Concours</a>
      <a href="/galerie">Galerie</a>
      <a href="/infos-pratiques">Infos pratiques</a>
    </div>
  </div>

</div>

<!-- Footer -->
<div class="footer-note">
  <a href="/">Fête du Cidre — L'Hôtellerie de Flée</a>
</div>

<script src="/assets/js/404.js"></script>
</body>
</html>
