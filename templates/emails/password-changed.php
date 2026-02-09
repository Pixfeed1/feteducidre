<h2>Mot de passe modifié</h2>

<p>Bonjour,</p>

<p>Le mot de passe de votre compte <strong><?= htmlspecialchars($email ?? '') ?></strong> a été modifié avec succès.</p>

<div class="info-box">
    <p style="margin:0 0 8px"><strong>Détails :</strong></p>
    <p style="margin:0">Date : <?= htmlspecialchars($date ?? date('d/m/Y H:i')) ?></p>
    <p style="margin:0">Adresse IP : <?= htmlspecialchars($ip ?? 'inconnue') ?></p>
</div>

<p>Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.</p>
