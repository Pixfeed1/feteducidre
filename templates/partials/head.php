<?php
/**
 * Partial <head> — SEO, critical CSS, fonts, meta.
 * Variables attendues : $seo, $page
 */
$siteName = 'Fête du Cidre';
$baseUrl = \App\Core\Config::baseUrl();
?>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title><?= e($seo['title'] ?? $siteName) ?></title>
<meta name="description" content="<?= e($seo['description'] ?? '') ?>">

<?php if (!empty($seo['canonical'])): ?>
<link rel="canonical" href="<?= e($seo['canonical']) ?>">
<?php endif; ?>

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:title" content="<?= e($seo['title'] ?? $siteName) ?>">
<meta property="og:description" content="<?= e($seo['description'] ?? '') ?>">
<meta property="og:url" content="<?= e($seo['canonical'] ?? $baseUrl) ?>">
<meta property="og:site_name" content="<?= e($siteName) ?>">
<meta property="og:locale" content="fr_FR">

<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="<?= $baseUrl ?>/assets/images/favicon.svg">
<meta name="theme-color" content="#2C4A2E">

<!-- Preload fonts -->
<link rel="preload" href="<?= $baseUrl ?>/assets/fonts/playfair-display-v37-latin-900.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="<?= $baseUrl ?>/assets/fonts/source-sans-3-v15-latin-regular.woff2" as="font" type="font/woff2" crossorigin>

<!-- Cormorant Garamond (Google Fonts) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">

<!-- 1. Variables couleurs dynamiques -->
<style><?= \App\Core\Theme::cssVariables() ?></style>

<!-- 2. Critical CSS inliné -->
<style>
/* Reset minimal */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;font-size:16px}
body{font-family:'Source Sans 3',system-ui,-apple-system,sans-serif;color:var(--texte);background:var(--blanc);line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{max-width:100%;height:auto;display:block}
a{color:var(--orange-cidre);text-decoration:none;transition:color .2s}
a:hover{color:var(--vert-mousse)}
h1,h2,h3,h4,h5,h6{font-family:'Playfair Display',Georgia,serif;color:var(--vert-profond);line-height:1.2;font-weight:700}
h1{font-size:clamp(2rem,5vw,3.5rem)}
h2{font-size:clamp(1.5rem,4vw,2.5rem)}
h3{font-size:clamp(1.2rem,3vw,1.75rem)}
button,input,select,textarea{font-family:inherit;font-size:inherit}
ul,ol{list-style:none}

/* Layout */
.container{width:100%;max-width:1200px;margin:0 auto;padding:0 1.5rem}

/* Boutons */
.btn{display:inline-flex;align-items:center;gap:.6rem;padding:1rem 2rem;border:none;border-radius:100px;font-family:'Source Sans 3',sans-serif;font-weight:600;font-size:.9rem;cursor:pointer;transition:all .4s cubic-bezier(.23,1,.32,1);text-decoration:none;letter-spacing:.03em;position:relative;overflow:hidden}
.btn-primary{background:var(--orange-cidre);color:#fff;box-shadow:0 4px 20px rgba(212,131,59,.3)}
.btn-primary:hover{background:#C0742F;color:#fff;box-shadow:0 8px 32px rgba(212,131,59,.4);transform:translateY(-2px)}
.btn-secondary{background:var(--vert-profond);color:#fff}
.btn-secondary:hover{background:var(--vert-mousse);color:#fff}
.btn-outline{background:transparent;border:2px solid var(--vert-profond);color:var(--vert-profond)}
.btn-outline:hover{background:var(--vert-profond);color:var(--creme);transform:translateY(-2px)}

/* Grilles */
.grid{display:grid;gap:1.5rem}
.grid-2{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}

/* Cards */
.card{background:var(--blanc);border-radius:14px;overflow:hidden;box-shadow:0 2px 8px rgba(42,35,24,.06);transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(42,35,24,.1)}
.card-body{padding:1.25rem}

/* Flash messages */
.flash{display:flex;align-items:center;gap:.75rem;padding:1rem 1.5rem;border-radius:10px;margin:1rem 2rem;font-weight:500}
.flash-success{background:#e8f5e9;color:#2e7d32;border:1px solid #c8e6c9}
.flash-error{background:#fce4ec;color:#c62828;border:1px solid #f8bbd0}
.flash-warning{background:#fff3e0;color:#e65100;border:1px solid #ffe0b2}
.flash-info{background:#e3f2fd;color:#1565c0;border:1px solid #bbdefb}

/* Icons */
.icon{flex-shrink:0;vertical-align:middle}

/* Fonts */
@font-face{font-family:'Playfair Display';src:url('<?= $baseUrl ?>/assets/fonts/playfair-display-v37-latin-900.woff2') format('woff2');font-weight:900;font-style:normal;font-display:swap}
@font-face{font-family:'Playfair Display';src:url('<?= $baseUrl ?>/assets/fonts/playfair-display-v37-latin-700.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:'Playfair Display';src:url('<?= $baseUrl ?>/assets/fonts/playfair-display-v37-latin-regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'Playfair Display';src:url('<?= $baseUrl ?>/assets/fonts/playfair-display-v37-latin-italic.woff2') format('woff2');font-weight:400;font-style:italic;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('<?= $baseUrl ?>/assets/fonts/source-sans-3-v15-latin-300.woff2') format('woff2');font-weight:300;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('<?= $baseUrl ?>/assets/fonts/source-sans-3-v15-latin-regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('<?= $baseUrl ?>/assets/fonts/source-sans-3-v15-latin-500.woff2') format('woff2');font-weight:500;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('<?= $baseUrl ?>/assets/fonts/source-sans-3-v15-latin-600.woff2') format('woff2');font-weight:600;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url('<?= $baseUrl ?>/assets/fonts/source-sans-3-v15-latin-700.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap}
</style>

<!-- CSS principal (non-bloquant) -->
<link rel="stylesheet" href="<?= asset('assets/css/main.css') ?>" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="<?= asset('assets/css/main.css') ?>"></noscript>
