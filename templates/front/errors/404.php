<?php
/**
 * Template page d'erreur 404.
 * Affiché quand une page n'est pas trouvée.
 * Ce template est inclus directement par Response::notFound() sans passer par le layout.
 */
$baseUrl = '';
try {
    $baseUrl = \App\Core\Config::baseUrl();
} catch (\Exception) {
    // Fallback silencieux
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 — Page non trouvée — Fête du Cidre</title>
    <style>
        <?php try { echo \App\Core\Theme::cssVariables(); } catch (\Exception) { ?>
        :root {
            --vert-profond: #2C4A2E;
            --vert-mousse: #4A6B3E;
            --vert-clair: #7A9E6B;
            --orange-cidre: #D4833B;
            --creme: #FAF5EC;
            --creme-fonce: #F0E8D8;
            --brun: #5C3D2E;
            --texte: #2A2318;
            --blanc: #FFFDF8;
        }
        <?php } ?>

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Source Sans 3', system-ui, -apple-system, sans-serif;
            color: var(--texte);
            background: var(--creme);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem;
        }

        .error-page {
            text-align: center;
            max-width: 600px;
        }

        .error-code {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: clamp(6rem, 15vw, 10rem);
            font-weight: 900;
            color: var(--vert-profond);
            line-height: 1;
            opacity: .15;
        }

        .error-icon {
            margin-top: -2rem;
            margin-bottom: 1.5rem;
        }

        .error-icon svg {
            width: 64px;
            height: 64px;
            stroke: var(--vert-clair);
            fill: none;
            stroke-width: 1.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .error-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--vert-profond);
            margin-bottom: .75rem;
        }

        .error-text {
            font-size: 1.1rem;
            color: var(--brun);
            line-height: 1.6;
            margin-bottom: 2rem;
        }

        .error-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: .5rem;
            padding: .75rem 1.5rem;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: .95rem;
            cursor: pointer;
            text-decoration: none;
            transition: all .2s;
        }

        .btn-primary {
            background: var(--vert-profond);
            color: #fff;
        }

        .btn-primary:hover {
            background: var(--vert-mousse);
        }

        .btn-outline {
            background: transparent;
            border: 2px solid var(--vert-profond);
            color: var(--vert-profond);
        }

        .btn-outline:hover {
            background: var(--vert-profond);
            color: #fff;
        }

        .error-footer {
            margin-top: 3rem;
            font-size: .85rem;
            color: var(--brun);
        }

        .error-footer a {
            color: var(--orange-cidre);
            text-decoration: none;
            font-weight: 600;
        }

        .error-footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="error-page">
        <div class="error-code">404</div>

        <div class="error-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
        </div>

        <h1 class="error-title">Page introuvable</h1>
        <p class="error-text">
            La page que vous recherchez n'existe pas ou a été déplacée.
            Vérifiez l'adresse ou retournez à l'accueil.
        </p>

        <div class="error-actions">
            <a href="/" class="btn btn-primary">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                Retour à l'accueil
            </a>
            <a href="/boutique" class="btn btn-outline">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
                Voir la boutique
            </a>
        </div>

        <div class="error-footer">
            <p><a href="/">Fête du Cidre</a> — L'Hôtellerie de Flée, Maine-et-Loire</p>
        </div>
    </div>
</body>
</html>
