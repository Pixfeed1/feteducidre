<?php
/**
 * Page de maintenance — template autonome (pas de layout).
 * Variables disponibles : $siteName, $estimatedReturn
 */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Maintenance — <?= htmlspecialchars($siteName ?? 'Fête du Cidre') ?></title>
    <style>
        :root {
            --vert-profond: #2C4A2E;
            --vert-clair: #5B8C3E;
            --creme: #FAF5EC;
            --creme-fonce: #F0E6D3;
            --orange-cidre: #D4833B;
            --brun-bois: #6B4226;
            --texte: #2A2318;
            --blanc: #ffffff;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                         Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
            background-color: var(--creme);
            color: var(--texte);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .maintenance {
            text-align: center;
            max-width: 540px;
            padding: 3rem 2rem;
        }

        .maintenance-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background-color: var(--vert-profond);
            margin-bottom: 2rem;
        }

        .maintenance-icon svg {
            width: 40px;
            height: 40px;
            fill: none;
            stroke: var(--creme);
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .maintenance h1 {
            font-size: 2rem;
            color: var(--vert-profond);
            margin-bottom: 1rem;
            line-height: 1.2;
        }

        .maintenance p {
            font-size: 1.1rem;
            line-height: 1.6;
            color: var(--brun-bois);
            margin-bottom: 1rem;
        }

        .maintenance-return {
            display: inline-block;
            margin-top: 1.5rem;
            padding: 0.75rem 1.5rem;
            background-color: var(--blanc);
            border: 2px solid var(--creme-fonce);
            border-radius: 8px;
            font-size: 0.95rem;
            color: var(--vert-profond);
            font-weight: 600;
        }

        .maintenance-return svg {
            display: inline-block;
            vertical-align: middle;
            width: 18px;
            height: 18px;
            margin-right: 0.4rem;
            fill: none;
            stroke: var(--orange-cidre);
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .maintenance-footer {
            margin-top: 3rem;
            font-size: 0.85rem;
            color: var(--brun-bois);
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="maintenance">
        <div class="maintenance-icon">
            <!-- Icone outil / clé -->
            <svg viewBox="0 0 24 24">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
        </div>

        <h1>Site en maintenance</h1>

        <p>
            Nous effectuons actuellement une mise à jour pour vous offrir
            une meilleure expérience. Merci de votre patience.
        </p>

        <p>
            La Fête du Cidre revient très bientôt !
        </p>

        <?php if (!empty($estimatedReturn)): ?>
        <div class="maintenance-return">
            <!-- Icone horloge -->
            <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
            </svg>
            Retour estimé : <?= htmlspecialchars($estimatedReturn) ?>
        </div>
        <?php endif; ?>

        <div class="maintenance-footer">
            <?= htmlspecialchars($siteName ?? 'Fête du Cidre') ?> &mdash; L'Hôtellerie de Flée, Maine-et-Loire
        </div>
    </div>
</body>
</html>
