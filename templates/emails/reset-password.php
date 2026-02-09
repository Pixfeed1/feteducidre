<h2>Réinitialisation de votre mot de passe</h2>

<p>Bonjour,</p>

<p>Vous avez demandé la réinitialisation de votre mot de passe pour le compte <strong><?= htmlspecialchars($email ?? '') ?></strong>.</p>

<p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>

<p style="text-align: center;">
    <a href="<?= htmlspecialchars($reset_url ?? '#') ?>" class="email-btn">Réinitialiser mon mot de passe</a>
</p>

<div class="info-box">
    <p style="margin:0">Ce lien est valable pendant <strong><?= htmlspecialchars($expiry ?? '1 heure') ?></strong>. Si vous n'avez pas fait cette demande, ignorez simplement ce message.</p>
</div>
