<!-- Header -->
<div style="background:#2C4A2E;padding:2rem 2rem 1.6rem;text-align:center">
    <div style="width:52px;height:52px;margin:0 auto 0.8rem;background:#4A6B3E;border-radius:14px;line-height:52px;text-align:center">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style="vertical-align:middle"><circle cx="12" cy="14" r="8" fill="#7A9E6B"/><ellipse cx="12" cy="13" rx="5" ry="7" fill="#A3C48E"/><path d="M12 3c-1-2 1-3 2-1" stroke="#D4C4A0" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
    </div>
    <div style="font-family:Georgia,serif;font-size:1.3rem;font-weight:900;color:#FAF5EC">Fête du Cidre</div>
    <div style="font-size:0.72rem;color:rgba(250,245,236,0.5);letter-spacing:0.1em;text-transform:uppercase;margin-top:2px">L'Hôtellerie de Flée</div>
</div>

<!-- Body -->
<div style="padding:2rem 2rem 1.5rem">
    <div style="text-align:center;margin-bottom:1.5rem">
        <div style="width:56px;height:56px;margin:0 auto 1rem;background:rgba(22,163,74,0.1);border-radius:16px;line-height:56px;text-align:center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>
        </div>
        <h1 style="font-family:Georgia,serif;font-size:1.4rem;font-weight:900;color:#2C4A2E;margin:0 0 0.4rem">Mot de passe modifié</h1>
        <p style="font-size:0.9rem;color:#6B5D4F;margin:0;line-height:1.5">Votre mot de passe a été modifié avec succès.</p>
    </div>

    <div style="background:#F0FDF4;border-radius:12px;padding:1rem 1.2rem;margin-bottom:1.5rem;border-left:4px solid #16a34a">
        <table style="width:100%;font-size:0.85rem;color:#2A2318" cellpadding="0" cellspacing="0" border="0">
            <tr><td style="padding:0.25rem 0;color:#6B5D4F;width:110px">Compte</td><td style="padding:0.25rem 0;font-weight:600"><?= e($email ?? '') ?></td></tr>
            <tr><td style="padding:0.25rem 0;color:#6B5D4F">Date</td><td style="padding:0.25rem 0;font-weight:600"><?= e($date ?? date('d/m/Y à H\hi')) ?></td></tr>
            <tr><td style="padding:0.25rem 0;color:#6B5D4F">Adresse IP</td><td style="padding:0.25rem 0;font-weight:600"><?= e($ip ?? 'inconnue') ?></td></tr>
        </table>
    </div>

    <div style="margin-top:1.5rem;padding:0.8rem 1rem;background:#FEF2F2;border-radius:10px">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
            <td style="vertical-align:top;padding-right:10px">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D94040" stroke-width="2" stroke-linecap="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/></svg>
            </td>
            <td style="font-size:0.78rem;color:#D94040;line-height:1.5"><strong>Vous n'êtes pas à l'origine de cette modification ?</strong><br>Contactez immédiatement l'administrateur du site ou utilisez la fonction «&nbsp;Mot de passe oublié&nbsp;» pour sécuriser votre compte.</td>
        </tr></table>
    </div>
</div>

<!-- Footer -->
<div style="background:#FAF5EC;padding:1.2rem 2rem;text-align:center;border-top:1px solid #F0E8D8">
    <div style="font-size:0.72rem;color:#6B5D4F;line-height:1.6">
        Association La Fête du Cidre — L'Hôtellerie de Flée, 49500<br>
        <a href="<?= e(\App\Core\Config::baseUrl()) ?>" style="color:#D4833B;text-decoration:none">fetecidre.fr</a>
    </div>
</div>
