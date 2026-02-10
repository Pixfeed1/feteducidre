<?php
/**
 * Randonnées — administration.
 * Variables : $editions, $responses, $categories, $editionCount, $classementCount,
 *             $responseCount, $fileCount, $settings
 */
?>

<div style="max-width:1100px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:linear-gradient(135deg, var(--vert-profond), var(--vert-mousse))"><?= icon('map', 22, '', 'white') ?></div>
            <h1>Randonnées</h1>
        </div>
        <div class="page-header-actions">
            <button class="btn-primary" onclick="openModal('modalEdition')"><?= icon('plus', 15) ?> Nouvelle édition</button>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(44,74,46,0.12)"><?= icon('calendar', 18, '', 'var(--vert-profond)') ?></div>
            <div><div class="stat-value"><?= $editionCount ?></div><div class="stat-label">Éditions</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(212,131,59,0.12)"><?= icon('trophy', 18, '', 'var(--orange-cidre)') ?></div>
            <div><div class="stat-value"><?= $classementCount ?></div><div class="stat-label">Classements</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(59,130,246,0.12)"><?= icon('file-text', 18, '', 'var(--bleu)') ?></div>
            <div><div class="stat-value"><?= $responseCount ?></div><div class="stat-label">Réponses</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(122,158,107,0.12)"><?= icon('file-check', 18, '', 'var(--vert-mousse)') ?></div>
            <div><div class="stat-value"><?= $fileCount ?></div><div class="stat-label">Fichiers PDF</div></div>
        </div>
    </div>

    <!-- ===== SECTION 1 : RÉSULTATS ET CLASSEMENTS ===== -->
    <div class="section-block">
        <div class="section-header">
            <div class="section-icon" style="background:var(--vert-profond)"><?= icon('trophy', 18, '', 'white') ?></div>
            <div>
                <div class="section-title">Résultats et classements</div>
                <div class="section-subtitle">PDF de classement par catégorie et par édition</div>
            </div>
            <div class="section-line"></div>
        </div>

        <?php if (empty($editions)): ?>
            <div class="table-card">
                <div style="text-align:center;padding:2rem;color:var(--texte-leger)">
                    <?= icon('calendar', 32) ?>
                    <p style="margin-top:0.5rem">Aucune édition pour le moment.</p>
                </div>
            </div>
        <?php else: ?>
            <?php foreach ($editions as $ed): ?>
                <div class="edition-card" id="edition-<?= (int) $ed['id'] ?>">
                    <div class="edition-row" onclick="toggleEdition(<?= (int) $ed['id'] ?>)">
                        <div class="edition-grip" onclick="event.stopPropagation()"><?= icon('grip-vertical', 14) ?></div>
                        <div class="edition-year"><?= (int) $ed['year'] ?></div>
                        <div class="edition-badges">
                            <?php foreach ($ed['cats'] as $catKey): ?>
                                <?php if (isset($categories[$catKey])): ?>
                                    <?php $cat = $categories[$catKey]; ?>
                                    <span class="cat-badge <?= e($catKey) ?>">
                                        <?= icon($cat['icon'], 10) ?> <?= e($cat['title']) ?>
                                        <?php if (isset($ed['files'][$catKey])): ?>
                                            <span class="badge-file"><?= icon('file-check', 9) ?></span>
                                        <?php endif; ?>
                                    </span>
                                <?php endif; ?>
                            <?php endforeach; ?>
                            <?php if ($ed['include_responses'] ?? false): ?>
                                <span class="cat-badge reponse"><?= icon('file-text', 10) ?> Réponses</span>
                            <?php endif; ?>
                        </div>
                        <?php if ($ed['complete']): ?>
                            <span class="edition-status complete"><?= icon('check-circle', 11) ?> Complet</span>
                        <?php else: ?>
                            <span class="edition-status partial"><?= icon('alert-circle', 11) ?> <?= (int) $ed['filled'] ?>/<?= (int) $ed['total'] ?></span>
                        <?php endif; ?>
                        <div class="edition-actions" onclick="event.stopPropagation()">
                            <form method="post" action="/admin/hikes/<?= (int) $ed['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer cette édition et tous ses fichiers ?')">
                                <?= csrf_field() ?>
                                <button type="submit" class="btn-icon danger" title="Supprimer"><?= icon('trash-2', 13) ?></button>
                            </form>
                        </div>
                        <button class="edition-toggle"><?= icon('chevron-down', 14) ?></button>
                    </div>

                    <div class="edition-detail">
                        <div class="detail-grid">
                            <?php foreach ($ed['cats'] as $catKey): ?>
                                <?php if (!isset($categories[$catKey])) continue; ?>
                                <?php $cat = $categories[$catKey]; ?>
                                <div class="file-slot">
                                    <div class="file-slot-header">
                                        <div class="file-slot-icon" style="background:<?= $cat['bg'] ?>;color:<?= $cat['color'] ?>"><?= icon($cat['icon'], 14) ?></div>
                                        <div>
                                            <div class="file-slot-label"><?= e($cat['title']) ?></div>
                                            <div class="file-slot-sub">Classement PDF</div>
                                        </div>
                                    </div>

                                    <?php if (isset($ed['files'][$catKey])): ?>
                                        <?php $f = $ed['files'][$catKey]; ?>
                                        <div class="file-attached">
                                            <?= icon('file-text', 14, '', 'var(--vert-profond)') ?>
                                            <span class="file-attached-name"><?= e($f['original_name']) ?></span>
                                            <span class="file-attached-size"><?= format_file_size((int) $f['file_size']) ?></span>
                                            <form method="post" action="/admin/hikes/file/<?= (int) $f['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer ce fichier ?')">
                                                <?= csrf_field() ?>
                                                <button type="submit" class="file-attached-remove" title="Supprimer"><?= icon('x', 11) ?></button>
                                            </form>
                                        </div>
                                    <?php else: ?>
                                        <label class="file-empty upload-zone" data-edition="<?= (int) $ed['id'] ?>" data-category="<?= e($catKey) ?>">
                                            <?= icon('upload', 16) ?>
                                            <span>Glissez un PDF ou cliquez</span>
                                            <small>PDF · Max 10 Mo</small>
                                            <input type="file" accept=".pdf" style="display:none" onchange="uploadSlotFile(this, <?= (int) $ed['id'] ?>, '<?= e($catKey) ?>')">
                                        </label>
                                    <?php endif; ?>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>

    <!-- ===== SECTION 2 : RÉPONSES AUX QUESTIONNAIRES ===== -->
    <div class="section-block">
        <div class="section-header">
            <div class="section-icon" style="background:var(--bleu)"><?= icon('file-text', 18, '', 'white') ?></div>
            <div>
                <div class="section-title">Réponses aux questionnaires</div>
                <div class="section-subtitle">PDF des réponses par année</div>
            </div>
            <div class="section-line"></div>
            <div class="section-actions">
                <button class="btn-primary btn-sm" onclick="openModal('modalResponse')"><?= icon('plus', 13) ?> Réponse</button>
            </div>
        </div>

        <?php if (empty($responses)): ?>
            <div class="table-card">
                <div style="text-align:center;padding:2rem;color:var(--texte-leger)">
                    <?= icon('file-text', 32) ?>
                    <p style="margin-top:0.5rem">Aucune réponse pour le moment.</p>
                </div>
            </div>
        <?php else: ?>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th style="width:30px"></th>
                            <th>Année</th>
                            <th>Fichier PDF</th>
                            <th>Taille</th>
                            <th style="width:90px">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($responses as $resp): ?>
                            <tr>
                                <td><span style="color:var(--creme-fonce);cursor:grab"><?= icon('grip-vertical', 14) ?></span></td>
                                <td><span class="td-year"><?= (int) $resp['year'] ?></span></td>
                                <td><span class="td-file"><?= icon('file-text', 12) ?> <?= e($resp['original_name']) ?></span></td>
                                <td style="font-size:0.78rem;color:var(--texte-leger)"><?= format_file_size((int) $resp['file_size']) ?></td>
                                <td>
                                    <div class="td-actions">
                                        <a href="/uploads/randonnees/<?= e($resp['filename']) ?>" class="btn-icon" title="Télécharger" download><?= icon('download', 13) ?></a>
                                        <form method="post" action="/admin/hikes/responses/<?= (int) $resp['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer cette réponse ?')">
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
        <div class="add-row" onclick="openModal('modalResponse')"><?= icon('plus', 14) ?> Ajouter une réponse</div>
    </div>

    <!-- ===== SECTION 3 : PAGE STATISTIQUES ===== -->
    <form method="post" action="/admin/hikes/settings">
        <?= csrf_field() ?>
        <div class="section-block">
            <div class="section-header">
                <div class="section-icon" style="background:var(--vert-mousse)"><?= icon('bar-chart-3', 18, '', 'white') ?></div>
                <div>
                    <div class="section-title">Page statistiques</div>
                    <div class="section-subtitle">Lien externe vers les statistiques de la randonnée</div>
                </div>
                <div class="section-line"></div>
            </div>

            <div class="stats-link-card">
                <div style="flex:1">
                    <div class="field" style="margin-bottom:0.8rem">
                        <label>URL de la page statistiques</label>
                        <input type="url" name="hike_stats_url" value="<?= e($settings['stats_url'] ?? '') ?>" placeholder="https://example.com/stats-randonnee">
                        <div class="field-hint"><?= icon('info', 10) ?> Lien vers la page externe de statistiques</div>
                    </div>
                    <div class="toggle-row">
                        <input type="hidden" name="hike_stats_visible" value="0">
                        <button type="button" class="toggle <?= ($settings['stats_visible'] ?? '0') === '1' ? 'active' : '' ?>" onclick="toggleSwitch(this, 'hike_stats_visible')"></button>
                        <div>
                            <div class="toggle-label">Afficher sur le site</div>
                            <div class="toggle-hint">Rend le lien statistiques visible sur la page randonnée</div>
                        </div>
                    </div>
                </div>
                <div>
                    <button type="submit" class="btn-primary"><?= icon('check', 14) ?> Enregistrer</button>
                </div>
            </div>
        </div>
    </form>

</div>

<!-- ===== MODAL: NOUVELLE ÉDITION ===== -->
<div class="modal-overlay" id="modalEdition">
    <div class="modal-dialog" style="max-width:520px">
        <div class="modal-head">
            <h2>Nouvelle édition</h2>
            <button class="modal-close" onclick="closeModal('modalEdition')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" action="/admin/hikes">
            <?= csrf_field() ?>
            <div class="modal-body-content">
                <div class="field" style="margin-bottom:1rem">
                    <label>Année</label>
                    <input type="number" name="year" value="<?= date('Y') ?>" min="1989" max="2030" required>
                </div>
                <div class="field" style="margin-bottom:1rem">
                    <label>Catégories de classement</label>
                    <div class="check-group">
                        <?php foreach ($categories as $catKey => $cat): ?>
                            <div class="check-item checked" onclick="toggleCheck(this)">
                                <input type="hidden" name="cat_<?= e($catKey) ?>" value="1">
                                <div class="check-box"><?= icon('check', 10, '', 'white') ?></div>
                                <span class="check-label"><?= icon($cat['icon'], 12) ?> <?= e($cat['title']) ?></span>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
                <div class="toggle-row" style="margin-bottom:0.8rem">
                    <input type="hidden" name="include_responses" value="1">
                    <button type="button" class="toggle active" onclick="toggleSwitch(this, 'include_responses')"></button>
                    <div class="toggle-row-left">
                        <div class="toggle-row-label">Inclure les réponses</div>
                        <div class="toggle-row-desc">Associer les réponses au questionnaire à cette édition</div>
                    </div>
                </div>
                <div class="toggle-row">
                    <input type="hidden" name="is_active" value="1">
                    <button type="button" class="toggle active" onclick="toggleSwitch(this, 'is_active')"></button>
                    <div class="toggle-row-left">
                        <div class="toggle-row-label">Publié</div>
                        <div class="toggle-row-desc">Visible sur le site public</div>
                    </div>
                </div>
            </div>
            <div class="modal-foot">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalEdition')">Annuler</button>
                <button type="submit" class="btn-primary"><?= icon('check', 15) ?> Créer l'édition</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== MODAL: NOUVELLE RÉPONSE ===== -->
<div class="modal-overlay" id="modalResponse">
    <div class="modal-dialog" style="max-width:520px">
        <div class="modal-head">
            <h2>Nouvelle réponse</h2>
            <button class="modal-close" onclick="closeModal('modalResponse')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" action="/admin/hikes/responses" enctype="multipart/form-data">
            <?= csrf_field() ?>
            <div class="modal-body-content">
                <div class="field" style="margin-bottom:1rem">
                    <label>Année</label>
                    <input type="number" name="year" value="<?= date('Y') ?>" min="1989" max="2030" required>
                </div>
                <div class="field">
                    <label>Réponse (PDF)</label>
                    <label class="upload-zone" id="responseUploadZone">
                        <?= icon('file-text', 18) ?>
                        <span id="responseFileName">Glissez un PDF ou cliquez</span>
                        <small>PDF uniquement · Max 10 Mo</small>
                        <input type="file" name="pdf_file" accept=".pdf" required style="display:none" onchange="updateFileName(this, 'responseFileName')">
                    </label>
                </div>
            </div>
            <div class="modal-foot">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalResponse')">Annuler</button>
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

function toggleSwitch(btn, name) {
    btn.classList.toggle('active');
    var hidden = btn.previousElementSibling;
    hidden.value = btn.classList.contains('active') ? '1' : '0';
    hidden.name = name;
}

function toggleEdition(id) {
    var card = document.getElementById('edition-' + id);
    if (card) card.classList.toggle('expanded');
}

function toggleCheck(el) {
    el.classList.toggle('checked');
    var input = el.querySelector('input[type="hidden"]');
    input.value = el.classList.contains('checked') ? '1' : '0';
}

function updateFileName(input, spanId) {
    var span = document.getElementById(spanId);
    if (input.files.length > 0) {
        span.textContent = input.files[0].name;
    }
}

/* Upload a PDF from file-slot directly */
function uploadSlotFile(input, editionId, category) {
    if (!input.files.length) return;
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/admin/hikes/' + editionId + '/file';
    form.enctype = 'multipart/form-data';
    form.style.display = 'none';

    // CSRF token
    var csrfInput = document.querySelector('input[name="_csrf_token"]');
    if (csrfInput) {
        var csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = '_csrf_token';
        csrf.value = csrfInput.value;
        form.appendChild(csrf);
    }

    // Category
    var catInput = document.createElement('input');
    catInput.type = 'hidden';
    catInput.name = 'category';
    catInput.value = category;
    form.appendChild(catInput);

    // File — use DataTransfer to copy file
    var fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.name = 'pdf_file';
    var dt = new DataTransfer();
    dt.items.add(input.files[0]);
    fileInput.files = dt.files;
    form.appendChild(fileInput);

    document.body.appendChild(form);
    form.submit();
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
