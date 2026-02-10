<?php
/**
 * Concours — administration.
 * Variables : $palmares, $documents, $categories, $cidreCount, $affichesCount, $docCount,
 *             $settings, $registrationsOpen, $currentYear
 */

$docIcons = [
    'scroll-text' => 'var(--vert-profond)',
    'file-pen'    => 'var(--bleu)',
    'mail'        => 'var(--brun)',
];
?>

<div style="max-width:1100px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:linear-gradient(135deg, var(--orange-cidre), var(--orange-doux))"><?= icon('trophy', 22, '', 'white') ?></div>
            <h1>Concours</h1>
        </div>
        <div class="page-header-actions">
            <button class="btn-primary" onclick="openModal('modalPalmares')"><?= icon('plus', 15) ?> Nouveau palmarès</button>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(212,131,59,0.12)"><?= icon('trophy', 18, '', 'var(--orange-cidre)') ?></div>
            <div><div class="stat-value"><?= $cidreCount ?></div><div class="stat-label">Palmarès cidre</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(139,92,246,0.12)"><?= icon('image', 18, '', 'var(--violet)') ?></div>
            <div><div class="stat-value"><?= $affichesCount ?></div><div class="stat-label">Palmarès affiches</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(74,107,62,0.12)"><?= icon('file-text', 18, '', 'var(--vert-mousse)') ?></div>
            <div><div class="stat-value"><?= $docCount ?></div><div class="stat-label">Documents inscrip.</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(44,74,46,0.12)"><?= icon('check-circle', 18, '', 'var(--vert-profond)') ?></div>
            <div>
                <div class="stat-value" style="color:<?= $registrationsOpen ? 'var(--vert-mousse)' : 'var(--rouge)' ?>"><?= $registrationsOpen ? 'Ouvert' : 'Fermé' ?></div>
                <div class="stat-label">Inscriptions <?= e($currentYear) ?></div>
            </div>
        </div>
    </div>

    <!-- ===== SECTION 1 : INSCRIPTIONS ===== -->
    <div class="section-block">
        <div class="section-header">
            <div class="section-icon" style="background:var(--vert-profond)"><?= icon('file-pen', 18, '', 'white') ?></div>
            <div>
                <div class="section-title">Inscriptions <?= e($currentYear) ?></div>
                <div class="section-subtitle">Règlements et formulaires par catégorie</div>
            </div>
            <div class="section-line"></div>
        </div>

        <div class="inscr-grid">
            <?php foreach ($categories as $catKey => $cat): ?>
                <div class="inscr-card">
                    <div class="inscr-card-header">
                        <div class="inscr-card-icon" style="background:<?= $cat['color'] ?>"><?= icon($cat['icon'], 18, '', 'white') ?></div>
                        <div>
                            <div class="inscr-card-title"><?= e($cat['title']) ?></div>
                            <div class="inscr-card-desc"><?= e($cat['desc']) ?></div>
                        </div>
                    </div>
                    <div class="inscr-docs">
                        <?php if (!empty($documents[$catKey])): ?>
                            <?php foreach ($documents[$catKey] as $doc): ?>
                                <div class="doc-row">
                                    <div class="doc-icon" style="background:var(--vert-profond)"><?= icon('scroll-text', 14, '', 'white') ?></div>
                                    <div class="doc-info">
                                        <div class="doc-name"><?= e($doc['name']) ?></div>
                                        <div class="doc-meta">PDF · <?= format_file_size((int) $doc['file_size']) ?></div>
                                    </div>
                                    <div class="doc-actions">
                                        <a href="/uploads/concours/<?= e($doc['filename']) ?>" class="btn-icon" style="width:26px;height:26px" title="Télécharger" download><?= icon('download', 11) ?></a>
                                        <form method="post" action="/admin/contests/documents/<?= (int) $doc['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer ce document ?')">
                                            <?= csrf_field() ?>
                                            <button type="submit" class="btn-icon danger" style="width:26px;height:26px" title="Supprimer"><?= icon('x', 11) ?></button>
                                        </form>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        <?php endif; ?>
                        <div class="doc-add" onclick="openDocModal('<?= e($catKey) ?>', '<?= e($cat['title']) ?>')"><?= icon('plus', 12) ?> Ajouter un document</div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>

    <!-- ===== SECTION 2 : PALMARÈS ===== -->
    <div class="section-block">
        <div class="section-header">
            <div class="section-icon" style="background:var(--orange-cidre)"><?= icon('award', 18, '', 'white') ?></div>
            <div>
                <div class="section-title">Palmarès</div>
                <div class="section-subtitle">Résultats des concours par année</div>
            </div>
            <div class="section-line"></div>
            <div class="section-actions">
                <button class="btn-primary btn-sm" onclick="openModal('modalPalmares')"><?= icon('plus', 13) ?> Palmarès</button>
            </div>
        </div>

        <?php if (empty($palmares)): ?>
            <div class="table-card">
                <div style="text-align:center;padding:2rem;color:var(--texte-leger)">
                    <?= icon('award', 32) ?>
                    <p style="margin-top:0.5rem">Aucun palmarès pour le moment.</p>
                </div>
            </div>
        <?php else: ?>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th style="width:30px"></th>
                            <th>Année</th>
                            <th>Type</th>
                            <th>Fichier PDF</th>
                            <th>Taille</th>
                            <th style="width:90px">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($palmares as $p): ?>
                            <tr>
                                <td><span style="color:var(--creme-fonce);cursor:grab"><?= icon('grip-vertical', 14) ?></span></td>
                                <td>
                                    <span class="td-year"><?= (int) $p['year'] ?></span>
                                    <?php if (!empty($p['label'])): ?>
                                        <span style="font-size:0.72rem;color:var(--texte-leger);margin-left:0.3rem"><?= e($p['label']) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <?php if ($p['type'] === 'cidre'): ?>
                                        <span class="td-type cidre"><?= icon('trophy', 8) ?> Cidre</span>
                                    <?php else: ?>
                                        <span class="td-type affiches"><?= icon('image', 8) ?> Affiches</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <span class="td-file"><?= icon('file-text', 12) ?> <?= e($p['original_name']) ?></span>
                                </td>
                                <td style="font-size:0.78rem;color:var(--texte-leger)"><?= format_file_size((int) $p['file_size']) ?></td>
                                <td>
                                    <div class="td-actions">
                                        <a href="/uploads/concours/<?= e($p['filename']) ?>" class="btn-icon" title="Télécharger" download><?= icon('download', 13) ?></a>
                                        <form method="post" action="/admin/contests/palmares/<?= (int) $p['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer ce palmarès ?')">
                                            <?= csrf_field() ?>
                                            <button type="submit" class="btn-icon danger" title="Supprimer"><?= icon('trash-2', 13) ?></button>
                                        </form>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
        <div class="add-row" onclick="openModal('modalPalmares')"><?= icon('plus', 14) ?> Ajouter un palmarès</div>
    </div>

    <!-- ===== SECTION 3 : PARAMÈTRES CONCOURS ===== -->
    <form method="post" action="/admin/contests/settings">
        <?= csrf_field() ?>
        <div class="settings-card">
            <div class="settings-title"><?= icon('settings', 16) ?> Paramètres du concours</div>
            <div class="settings-grid">
                <div class="field">
                    <label>Édition en cours</label>
                    <input type="text" name="contest_edition_name" value="<?= e($settings['edition_name'] ?? '') ?>" placeholder="Concours <?= $currentYear ?>">
                </div>
                <div class="field">
                    <label>Date du concours</label>
                    <input type="text" name="contest_date" value="<?= e($settings['contest_date'] ?? '') ?>" placeholder="14 juin <?= $currentYear ?>">
                </div>
                <div class="field">
                    <label>Date limite d'inscription</label>
                    <input type="date" name="contest_registration_deadline" value="<?= e($settings['registration_deadline'] ?? '') ?>">
                    <div class="field-hint"><?= icon('info', 10) ?> Après cette date, les liens d'inscription seront masqués</div>
                </div>
                <div class="field">
                    <label>E-mail de contact concours</label>
                    <input type="email" name="contest_contact_email" value="<?= e($settings['contact_email'] ?? '') ?>" placeholder="concours@fetecidre.fr">
                </div>
                <div class="field" style="grid-column:1/-1">
                    <label>Message d'information (optionnel)</label>
                    <textarea name="contest_info_message" rows="2" placeholder="Ex : Les inscriptions pour le concours <?= $currentYear ?> sont ouvertes jusqu'au 31 mai…"><?= e($settings['info_message'] ?? '') ?></textarea>
                </div>
            </div>
            <div style="margin-top:1rem;display:flex;flex-direction:column;gap:0.3rem">
                <div class="toggle-row">
                    <input type="hidden" name="contest_registrations_open" value="0">
                    <button type="button" class="toggle <?= ($settings['registrations_open'] ?? '0') === '1' ? 'active' : '' ?>" onclick="toggleSwitch(this, 'contest_registrations_open')"></button>
                    <div>
                        <div class="toggle-label">Inscriptions ouvertes</div>
                        <div class="toggle-hint">Affiche les formulaires d'inscription sur le site</div>
                    </div>
                </div>
                <div class="toggle-row">
                    <input type="hidden" name="contest_show_palmares" value="0">
                    <button type="button" class="toggle <?= ($settings['show_palmares'] ?? '0') === '1' ? 'active' : '' ?>" onclick="toggleSwitch(this, 'contest_show_palmares')"></button>
                    <div>
                        <div class="toggle-label">Afficher la page palmarès</div>
                        <div class="toggle-hint">Rend visible la page des résultats passés</div>
                    </div>
                </div>
                <div class="toggle-row">
                    <input type="hidden" name="contest_show_info_banner" value="0">
                    <button type="button" class="toggle <?= ($settings['show_info_banner'] ?? '0') === '1' ? 'active' : '' ?>" onclick="toggleSwitch(this, 'contest_show_info_banner')"></button>
                    <div>
                        <div class="toggle-label">Afficher le bandeau d'info</div>
                        <div class="toggle-hint">Message d'information en haut de la page concours</div>
                    </div>
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;margin-top:1rem">
                <button type="submit" class="btn-primary"><?= icon('check', 14) ?> Enregistrer</button>
            </div>
        </div>
    </form>

</div>

<!-- ===== MODAL: NOUVEAU PALMARÈS ===== -->
<div class="modal-overlay" id="modalPalmares">
    <div class="modal-dialog" style="max-width:520px">
        <div class="modal-head">
            <h2>Nouveau palmarès</h2>
            <button class="modal-close" onclick="closeModal('modalPalmares')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" action="/admin/contests/palmares" enctype="multipart/form-data">
            <?= csrf_field() ?>
            <div class="modal-body-content">
                <div class="field" style="margin-bottom:1rem">
                    <label>Année</label>
                    <input type="number" name="year" value="<?= $currentYear ?>" min="1989" max="2030" required>
                </div>
                <div class="field" style="margin-bottom:1rem">
                    <label>Type de concours</label>
                    <div class="type-select">
                        <label class="type-option selected" onclick="selectType(this, 'cidre')">
                            <input type="radio" name="type" value="cidre" checked style="display:none">
                            <div class="type-option-icon" style="background:var(--vert-profond)"><?= icon('trophy', 16, '', 'white') ?></div>
                            <span class="type-option-label">Cidre</span>
                        </label>
                        <label class="type-option" onclick="selectType(this, 'affiches')">
                            <input type="radio" name="type" value="affiches" style="display:none">
                            <div class="type-option-icon" style="background:var(--orange-cidre)"><?= icon('image', 16, '', 'white') ?></div>
                            <span class="type-option-label">Affiches</span>
                        </label>
                    </div>
                </div>
                <div class="field" style="margin-bottom:1rem">
                    <label>Palmarès (PDF)</label>
                    <label class="upload-zone" id="palmaresUploadZone">
                        <?= icon('award', 18) ?>
                        <span id="palmaresFileName">Glissez un PDF ou cliquez</span>
                        <small>PDF uniquement · Max 10 Mo</small>
                        <input type="file" name="pdf_file" accept=".pdf" required style="display:none" onchange="updateFileName(this, 'palmaresFileName')">
                    </label>
                </div>
                <div class="field">
                    <label>Label affiché (optionnel)</label>
                    <input type="text" name="label" placeholder="Ex : 2017 — 2016 (pour regrouper des années)">
                    <div class="field-hint"><?= icon('info', 10) ?> Laisser vide pour afficher simplement l'année</div>
                </div>
            </div>
            <div class="modal-foot">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalPalmares')">Annuler</button>
                <button type="submit" class="btn-primary"><?= icon('check', 15) ?> Enregistrer</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== MODAL: AJOUTER UN DOCUMENT ===== -->
<div class="modal-overlay" id="modalDocument">
    <div class="modal-dialog" style="max-width:520px">
        <div class="modal-head">
            <h2 id="docModalTitle">Ajouter un document</h2>
            <button class="modal-close" onclick="closeModal('modalDocument')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" action="/admin/contests/documents" enctype="multipart/form-data">
            <?= csrf_field() ?>
            <input type="hidden" name="category" id="docCategory" value="">
            <div class="modal-body-content">
                <div class="field" style="margin-bottom:1rem">
                    <label>Nom du document</label>
                    <input type="text" name="name" placeholder="Ex : Règlement concours pro <?= $currentYear ?>" required>
                </div>
                <div class="field">
                    <label>Fichier PDF</label>
                    <label class="upload-zone" id="docUploadZone">
                        <?= icon('file-text', 18) ?>
                        <span id="docFileName">Glissez un PDF ou cliquez</span>
                        <small>PDF uniquement · Max 10 Mo</small>
                        <input type="file" name="doc_file" accept=".pdf" required style="display:none" onchange="updateFileName(this, 'docFileName')">
                    </label>
                </div>
            </div>
            <div class="modal-foot">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalDocument')">Annuler</button>
                <button type="submit" class="btn-primary"><?= icon('check', 15) ?> Enregistrer</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal(id) {
    document.getElementById(id).classList.add('show');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}
document.querySelectorAll('.modal-overlay').forEach(function(m) {
    m.addEventListener('click', function(e) {
        if (e.target === m) m.classList.remove('show');
    });
});

function selectType(el, type) {
    document.querySelectorAll('.type-option').forEach(function(o) { o.classList.remove('selected'); });
    el.classList.add('selected');
    el.querySelector('input[type="radio"]').checked = true;
}

function toggleSwitch(btn, name) {
    btn.classList.toggle('active');
    var hidden = btn.previousElementSibling;
    hidden.value = btn.classList.contains('active') ? '1' : '0';
    hidden.name = name;
}

function openDocModal(category, title) {
    document.getElementById('docCategory').value = category;
    document.getElementById('docModalTitle').textContent = 'Document — ' + title;
    openModal('modalDocument');
}

function updateFileName(input, spanId) {
    var span = document.getElementById(spanId);
    if (input.files.length > 0) {
        span.textContent = input.files[0].name;
    }
}

// Drag & drop for upload zones
document.querySelectorAll('.upload-zone').forEach(function(zone) {
    var input = zone.querySelector('input[type="file"]');
    if (!input) return;

    zone.addEventListener('dragover', function(e) {
        e.preventDefault();
        zone.classList.add('dragover');
    });
    zone.addEventListener('dragleave', function() {
        zone.classList.remove('dragover');
    });
    zone.addEventListener('drop', function(e) {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            input.files = e.dataTransfer.files;
            input.dispatchEvent(new Event('change'));
        }
    });
});
</script>
