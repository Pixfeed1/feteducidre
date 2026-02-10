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
        <div style="width:56px;height:56px;margin:0 auto 1rem;background:rgba(212,131,59,0.1);border-radius:16px;line-height:56px;text-align:center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#D4833B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle"><path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
        </div>
        <h1 style="font-family:Georgia,serif;font-size:1.4rem;font-weight:900;color:#2C4A2E;margin:0 0 0.4rem">Réinitialisation du mot de passe</h1>
        <p style="font-size:0.9rem;color:#6B5D4F;margin:0;line-height:1.5">Vous avez demandé la réinitialisation de votre mot de passe pour l'administration de la Fête du Cidre.</p>
    </div>

    <div style="background:#FAF5EC;border-radius:12px;padding:1rem 1.2rem;margin-bottom:1.5rem;border-left:4px solid #D4833B">
        <div style="font-size:0.72rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">Compte concerné</div>
        <div style="font-size:0.9rem;font-weight:600;color:#2A2318"><?= e($email ?? '') ?></div>
    </div>

    <!-- CTA Button -->
    <div style="text-align:center;margin:1.5rem 0">
        <a href="<?= e($reset_url ?? '#') ?>" style="display:inline-block;padding:0.85rem 2.5rem;background:#2C4A2E;color:#FAF5EC;text-decoration:none;border-radius:12px;font-size:0.92rem;font-weight:700;letter-spacing:0.02em">Réinitialiser mon mot de passe</a>
    </div>

    <p style="font-size:0.82rem;color:#6B5D4F;text-align:center;line-height:1.6;margin:0">Ce lien est valable <strong style="color:#2A2318"><?= e($expiry ?? '1 heure') ?></strong>. Passé ce délai, vous devrez refaire une demande.</p>

    <!-- Security notice -->
    <div style="margin-top:1.5rem;padding:0.8rem 1rem;background:#FEF2F2;border-radius:10px">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
            <td style="vertical-align:top;padding-right:10px">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D94040" stroke-width="2" stroke-linecap="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/></svg>
            </td>
            <td style="font-size:0.78rem;color:#D94040;line-height:1.5">Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail. Votre mot de passe restera inchangé.</td>
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
