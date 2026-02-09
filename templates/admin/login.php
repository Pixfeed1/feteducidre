<?php
/**
 * Page de connexion admin — affichage autonome (sans layout sidebar).
 */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Connexion — Administration Fête du Cidre</title>
    <style>
        <?= \App\Core\Theme::cssVariables() ?>

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--creme, #FAF5EC);
            color: var(--texte, #2A2318);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 1rem;
        }

        .login-container {
            width: 100%;
            max-width: 400px;
        }

        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-header .logo {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--vert-profond, #2C4A2E);
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .login-header p {
            color: #888;
            font-size: 0.875rem;
        }

        .login-card {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            padding: 2rem;
            border: 1px solid var(--creme-fonce, #F0E8D8);
        }

        .flash {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            font-weight: 500;
        }

        .flash-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .form-group {
            margin-bottom: 1.25rem;
        }

        .form-group label {
            display: block;
            font-size: 0.8125rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        .form-control {
            width: 100%;
            padding: 0.6rem 0.75rem;
            font-size: 0.9375rem;
            border: 1px solid var(--creme-fonce, #F0E8D8);
            border-radius: 6px;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--vert-clair, #7A9E6B);
            box-shadow: 0 0 0 3px rgba(122, 158, 107, 0.15);
        }

        .btn-login {
            width: 100%;
            padding: 0.65rem 1rem;
            background: var(--vert-profond, #2C4A2E);
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 0.9375rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s ease;
        }

        .btn-login:hover {
            background: var(--vert-mousse, #4A6B3E);
        }

        .login-footer {
            text-align: center;
            margin-top: 1.5rem;
        }

        .login-footer a {
            font-size: 0.8125rem;
            color: var(--vert-profond, #2C4A2E);
            text-decoration: none;
        }

        .login-footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="logo">
                <?= icon('apple', 32) ?>
                Fête du Cidre
            </div>
            <p>Espace d'administration</p>
        </div>

        <div class="login-card">
            <?= flash('success') ?>
            <?= flash('error') ?>

            <form method="post" action="/admin/login">
                <?= csrf_field() ?>

                <div class="form-group">
                    <label for="email">Adresse e-mail</label>
                    <input type="email" id="email" name="email" class="form-control"
                           value="<?= old('email') ?>"
                           placeholder="admin@fetecidre.fr"
                           required autofocus>
                </div>

                <div class="form-group">
                    <label for="password">Mot de passe</label>
                    <input type="password" id="password" name="password" class="form-control"
                           placeholder="Votre mot de passe"
                           required>
                </div>

                <button type="submit" class="btn-login">
                    <?= icon('log-in', 18) ?>
                    Se connecter
                </button>
            </form>
        </div>

        <div class="login-footer">
            <a href="/">Retour au site</a>
        </div>
    </div>
</body>
</html>
