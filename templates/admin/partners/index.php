<?php
/**
 * Partenaires — administration.
 * Variables : $categories, $grouped, $totalPartners, $totalCategories,
 *             $activeCount, $withLogo, $withLink, $availableIcons, $availableColors
 */
?>

<div style="max-width:1100px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:linear-gradient(135deg, var(--orange-cidre), var(--orange-doux))"><?= icon('heart', 22, '', 'white') ?></div>
            <h1>Partenaires</h1>
        </div>
        <div class="page-header-actions">
            <button class="btn-secondary" onclick="openModal('modalCategory')"><?= icon('folder-plus', 15) ?> Catégorie</button>
            <button class="btn-primary" onclick="openModal('modalPartner')"><?= icon('plus', 15) ?> Nouveau partenaire</button>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(212,131,59,0.12)"><?= icon('heart', 18, '', 'var(--orange-cidre)') ?></div>
            <div><div class="stat-value"><?= $totalPartners ?></div><div class="stat-label">Partenaires</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(74,107,62,0.12)"><?= icon('folder', 18, '', 'var(--vert-mousse)') ?></div>
            <div><div class="stat-value"><?= $totalCategories ?></div><div class="stat-label">Catégories</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(59,130,246,0.12)"><?= icon('check-circle', 18, '', 'var(--bleu)') ?></div>
            <div><div class="stat-value"><?= $activeCount ?></div><div class="stat-label">Actifs</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(107,93,79,0.12)"><?= icon('image', 18, '', 'var(--texte-leger)') ?></div>
            <div><div class="stat-value"><?= $withLogo ?></div><div class="stat-label">Avec logo</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(92,61,46,0.12)"><?= icon('link', 18, '', 'var(--brun)') ?></div>
            <div><div class="stat-value"><?= $withLink ?></div><div class="stat-label">Avec lien</div></div>
        </div>
    </div>

    <!-- TOOLBAR -->
    <div class="toolbar">
        <div class="search-box">
            <span class="search-icon"><?= icon('search', 15) ?></span>
            <input type="text" placeholder="Rechercher un partenaire…" oninput="filterPartners(this.value)">
        </div>
        <div class="filter-chips">
            <button class="chip active" onclick="filterCat('all', this)">Tout</button>
            <?php foreach ($categories as $cat): ?>
                <button class="chip" onclick="filterCat('<?= e($cat['slug']) ?>', this)">
                    <span class="cat-dot" style="background:<?= e($cat['color']) ?>"></span>
                    <?= e($cat['name']) ?>
                </button>
            <?php endforeach; ?>
        </div>
    </div>

    <!-- CATEGORY GROUPS -->
    <?php foreach ($categories as $cat): ?>
        <?php $catPartners = $grouped[(int) $cat['id']] ?? []; ?>
        <div class="cat-group" data-cat="<?= e($cat['slug']) ?>">
            <div class="cat-header">
                <div class="cat-icon" style="background:<?= e($cat['color']) ?>"><?= icon($cat['icon'], 18, '', 'white') ?></div>
                <span class="cat-title"><?= e($cat['name']) ?></span>
                <span class="cat-count"><?= count($catPartners) ?></span>
                <div class="cat-line"></div>
                <div class="cat-actions">
                    <button class="btn-icon" title="Modifier la catégorie" onclick="openEditCatModal(<?= (int) $cat['id'] ?>, '<?= e($cat['name'], ENT_QUOTES) ?>', '<?= e($cat['icon']) ?>', '<?= e($cat['color']) ?>', <?= (int) $cat['sort_order'] ?>)"><?= icon('pencil', 13) ?></button>
                    <button class="btn-icon" title="Ajouter un partenaire" onclick="openModalForCat(<?= (int) $cat['id'] ?>)"><?= icon('plus', 14) ?></button>
                </div>
            </div>

            <?php if (empty($catPartners)): ?>
                <div class="partner-table">
                    <div style="text-align:center;padding:1.5rem;color:var(--texte-leger);font-size:0.85rem">
                        Aucun partenaire dans cette catégorie.
                    </div>
                </div>
            <?php else: ?>
                <div class="partner-table">
                    <table>
                        <thead><tr>
                            <th style="width:30px"></th>
                            <th>Partenaire</th>
                            <th>Site web</th>
                            <th>Statut</th>
                            <th style="width:90px">Actions</th>
                        </tr></thead>
                        <tbody>
                            <?php foreach ($catPartners as $p): ?>
                                <tr data-name="<?= e(mb_strtolower($p['name'])) ?>">
                                    <td><span class="td-grip"><?= icon('grip-vertical', 14) ?></span></td>
                                    <td>
                                        <div class="td-partner">
                                            <div class="td-logo <?= !empty($p['logo_filename']) ? 'has-logo' : '' ?>">
                                                <?php if (!empty($p['logo_filename'])): ?>
                                                    <img src="/uploads/partenaires/<?= e($p['logo_filename']) ?>" alt="<?= e($p['name']) ?>">
                                                <?php else: ?>
                                                    <?= icon($cat['icon'], 16, '', 'var(--texte-leger)') ?>
                                                <?php endif; ?>
                                            </div>
                                            <div>
                                                <div class="td-name"><?= e($p['name']) ?></div>
                                                <?php if (!empty($p['description'])): ?>
                                                    <div class="td-detail"><?= e($p['description']) ?></div>
                                                <?php endif; ?>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <?php if (!empty($p['website'])): ?>
                                            <a href="<?= e($p['website']) ?>" class="td-url" target="_blank" rel="noopener">
                                                <?= icon('external-link', 11) ?>
                                                <?= e(parse_url($p['website'], PHP_URL_HOST) ?: $p['website']) ?>
                                            </a>
                                        <?php else: ?>
                                            <span style="font-size:0.78rem;color:var(--texte-leger)">—</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($p['is_active']): ?>
                                            <span class="td-status-partner active"><?= icon('circle', 6) ?> Actif</span>
                                        <?php else: ?>
                                            <span class="td-status-partner inactive"><?= icon('circle', 6) ?> Inactif</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <div class="td-actions">
                                            <button class="btn-icon" title="Modifier" onclick="openEditPartnerModal(<?= (int) $p['id'] ?>, <?= e(json_encode($p['name']), ENT_QUOTES) ?>, <?= e(json_encode($p['description'] ?? ''), ENT_QUOTES) ?>, <?= (int) ($p['category_id'] ?? 0) ?>, <?= e(json_encode($p['website'] ?? ''), ENT_QUOTES) ?>, <?= $p['is_active'] ? 'true' : 'false' ?>, <?= e(json_encode($p['logo_filename'] ?? ''), ENT_QUOTES) ?>)"><?= icon('pencil', 13) ?></button>
                                            <form method="post" action="/admin/partners/<?= (int) $p['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer ce partenaire ?')">
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
            <div class="add-row" onclick="openModalForCat(<?= (int) $cat['id'] ?>)"><?= icon('plus', 14) ?> Ajouter un partenaire</div>
        </div>
    <?php endforeach; ?>

    <!-- Uncategorized partners -->
    <?php if (!empty($grouped[0])): ?>
        <div class="cat-group" data-cat="sans-categorie">
            <div class="cat-header">
                <div class="cat-icon" style="background:var(--texte-leger)"><?= icon('heart', 18, '', 'white') ?></div>
                <span class="cat-title">Sans catégorie</span>
                <span class="cat-count"><?= count($grouped[0]) ?></span>
                <div class="cat-line"></div>
            </div>
            <div class="partner-table">
                <table>
                    <thead><tr>
                        <th style="width:30px"></th>
                        <th>Partenaire</th>
                        <th>Site web</th>
                        <th>Statut</th>
                        <th style="width:90px">Actions</th>
                    </tr></thead>
                    <tbody>
                        <?php foreach ($grouped[0] as $p): ?>
                            <tr data-name="<?= e(mb_strtolower($p['name'])) ?>">
                                <td><span class="td-grip"><?= icon('grip-vertical', 14) ?></span></td>
                                <td>
                                    <div class="td-partner">
                                        <div class="td-logo">
                                            <?php if (!empty($p['logo_filename'])): ?>
                                                <img src="/uploads/partenaires/<?= e($p['logo_filename']) ?>" alt="<?= e($p['name']) ?>">
                                            <?php else: ?>
                                                <?= icon('heart', 16, '', 'var(--texte-leger)') ?>
                                            <?php endif; ?>
                                        </div>
                                        <div>
                                            <div class="td-name"><?= e($p['name']) ?></div>
                                            <?php if (!empty($p['description'])): ?>
                                                <div class="td-detail"><?= e($p['description']) ?></div>
                                            <?php endif; ?>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <?php if (!empty($p['website'])): ?>
                                        <a href="<?= e($p['website']) ?>" class="td-url" target="_blank" rel="noopener">
                                            <?= icon('external-link', 11) ?>
                                            <?= e(parse_url($p['website'], PHP_URL_HOST) ?: $p['website']) ?>
                                        </a>
                                    <?php else: ?>
                                        <span style="font-size:0.78rem;color:var(--texte-leger)">—</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <?php if ($p['is_active']): ?>
                                        <span class="td-status-partner active"><?= icon('circle', 6) ?> Actif</span>
                                    <?php else: ?>
                                        <span class="td-status-partner inactive"><?= icon('circle', 6) ?> Inactif</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <div class="td-actions">
                                        <button class="btn-icon" title="Modifier" onclick="openEditPartnerModal(<?= (int) $p['id'] ?>, <?= e(json_encode($p['name']), ENT_QUOTES) ?>, <?= e(json_encode($p['description'] ?? ''), ENT_QUOTES) ?>, 0, <?= e(json_encode($p['website'] ?? ''), ENT_QUOTES) ?>, <?= $p['is_active'] ? 'true' : 'false' ?>, <?= e(json_encode($p['logo_filename'] ?? ''), ENT_QUOTES) ?>)"><?= icon('pencil', 13) ?></button>
                                        <form method="post" action="/admin/partners/<?= (int) $p['id'] ?>/delete" style="display:inline" onsubmit="return confirm('Supprimer ce partenaire ?')">
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
        </div>
    <?php endif; ?>

</div>

<!-- ===== MODAL: PARTENAIRE ===== -->
<div class="modal-overlay" id="modalPartner">
    <div class="modal-dialog" style="max-width:560px">
        <div class="modal-head">
            <h2 id="partnerModalTitle">Nouveau partenaire</h2>
            <button class="modal-close" onclick="closeModal('modalPartner')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" id="partnerForm" action="/admin/partners" enctype="multipart/form-data">
            <?= csrf_field() ?>
            <input type="hidden" name="remove_logo" id="partnerRemoveLogo" value="0">
            <div class="modal-body-content">
                <div class="field">
                    <label>Nom du partenaire</label>
                    <input type="text" name="name" id="partnerName" placeholder="ex : Ouest France" required>
                </div>
                <div class="field">
                    <label>Description / détail</label>
                    <input type="text" name="description" id="partnerDetail" placeholder="ex : Quotidien, Z.I. Segré…">
                    <div class="field-hint"><?= icon('info', 11) ?> Texte affiché sous le nom sur la page Remerciements</div>
                </div>
                <div class="field">
                    <label>Catégorie</label>
                    <div class="cat-select-grid">
                        <?php foreach ($categories as $cat): ?>
                            <div class="cat-select-item" data-catval="<?= (int) $cat['id'] ?>" onclick="selectCat(this)">
                                <div class="csi-icon" style="background:<?= e($cat['color']) ?>"><?= icon($cat['icon'], 14, '', 'white') ?></div>
                                <span class="csi-label"><?= e($cat['name']) ?></span>
                            </div>
                        <?php endforeach; ?>
                    </div>
                    <input type="hidden" name="category_id" id="partnerCategoryId" value="">
                </div>
                <div class="field">
                    <label>Logo (optionnel)</label>
                    <div class="logo-upload">
                        <div class="logo-preview" id="logoPreview" onclick="document.getElementById('logoInput').click()">
                            <?= icon('image', 22, '', 'var(--creme-fonce)') ?>
                        </div>
                        <div class="logo-upload-info">
                            <span id="logoLabel">Aucun logo</span>
                            <small>PNG, JPG ou SVG · 200×200px recommandé</small>
                            <div class="logo-upload-btns">
                                <button type="button" class="upload-btn" onclick="document.getElementById('logoInput').click()">Parcourir…</button>
                                <button type="button" class="upload-btn danger" onclick="removeLogo()">Retirer</button>
                            </div>
                        </div>
                    </div>
                    <input type="file" name="logo_file" id="logoInput" accept="image/*" style="display:none" onchange="previewLogo(this)">
                </div>
                <div class="field">
                    <label>Site web (optionnel)</label>
                    <input type="url" name="website" id="partnerUrl" placeholder="https://…">
                    <div class="field-hint"><?= icon('info', 11) ?> Le logo sera cliquable vers cette URL</div>
                </div>
                <div class="field" style="margin-top:0.5rem">
                    <div class="toggle-row">
                        <div class="toggle-row-left">
                            <span class="toggle-row-label">Actif</span>
                            <span class="toggle-row-desc">Affiché sur la page Remerciements</span>
                        </div>
                        <input type="hidden" name="is_active" id="partnerActiveHidden" value="1">
                        <button type="button" class="toggle active" id="partnerActiveToggle" onclick="toggleSwitch(this, 'is_active')"></button>
                    </div>
                </div>
            </div>
            <div class="modal-foot">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalPartner')">Annuler</button>
                <button type="submit" class="btn-primary" id="partnerSubmitBtn"><?= icon('check', 15) ?> Enregistrer</button>
            </div>
        </form>
    </div>
</div>

<!-- ===== MODAL: CATÉGORIE ===== -->
<div class="modal-overlay" id="modalCategory">
    <div class="modal-dialog" style="max-width:480px">
        <div class="modal-head">
            <h2 id="catModalTitle">Nouvelle catégorie</h2>
            <button class="modal-close" onclick="closeModal('modalCategory')"><?= icon('x', 16) ?></button>
        </div>
        <form method="post" id="catForm" action="/admin/partners/categories">
            <?= csrf_field() ?>
            <div class="modal-body-content">
                <div class="field">
                    <label>Nom de la catégorie</label>
                    <input type="text" name="name" id="catName" placeholder="ex : Partenaires techniques" required>
                </div>
                <div class="field-row">
                    <div class="field">
                        <label>Icône</label>
                        <select name="icon" id="catIcon">
                            <?php foreach ($availableIcons as $iconName => $iconLabel): ?>
                                <option value="<?= e($iconName) ?>"><?= e($iconLabel) ?> (<?= e($iconName) ?>)</option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div class="field">
                        <label>Couleur</label>
                        <div class="color-picker" id="colorPicker">
                            <?php foreach ($availableColors as $i => $color): ?>
                                <div class="color-swatch <?= $i === 0 ? 'active' : '' ?>" style="background:<?= e($color) ?>" data-color="<?= e($color) ?>" onclick="selectColor(this)"></div>
                            <?php endforeach; ?>
                        </div>
                        <input type="hidden" name="color" id="catColor" value="<?= e($availableColors[0]) ?>">
                    </div>
                </div>
                <div class="field">
                    <label>Ordre d'affichage</label>
                    <input type="number" name="sort_order" id="catSortOrder" value="<?= count($categories) + 1 ?>" min="1">
                </div>
            </div>
            <div class="modal-foot">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modalCategory')">Annuler</button>
                <button type="submit" class="btn-primary"><?= icon('check', 15) ?> Enregistrer</button>
            </div>
        </form>
    </div>
</div>

<script>
/* ── Modal helpers ── */
function openModal(id) { document.getElementById(id).classList.add('show'); }
function closeModal(id) { document.getElementById(id).classList.remove('show'); }
document.querySelectorAll('.modal-overlay').forEach(function(m) {
    m.addEventListener('click', function(e) { if (e.target === m) m.classList.remove('show'); });
});

function toggleSwitch(btn, name) {
    btn.classList.toggle('active');
    var hidden = btn.previousElementSibling;
    hidden.value = btn.classList.contains('active') ? '1' : '0';
    hidden.name = name;
}

/* ── Category selector in partner modal ── */
function selectCat(el) {
    document.querySelectorAll('.cat-select-item').forEach(function(i) { i.classList.remove('active'); });
    el.classList.add('active');
    document.getElementById('partnerCategoryId').value = el.dataset.catval;
}

function openModalForCat(catId) {
    resetPartnerModal();
    document.querySelectorAll('.cat-select-item').forEach(function(i) {
        i.classList.toggle('active', parseInt(i.dataset.catval) === catId);
    });
    document.getElementById('partnerCategoryId').value = catId;
    openModal('modalPartner');
}

/* ── Partner modal: create / edit ── */
function resetPartnerModal() {
    document.getElementById('partnerModalTitle').textContent = 'Nouveau partenaire';
    document.getElementById('partnerForm').action = '/admin/partners';
    document.getElementById('partnerName').value = '';
    document.getElementById('partnerDetail').value = '';
    document.getElementById('partnerUrl').value = '';
    document.getElementById('partnerCategoryId').value = '';
    document.getElementById('partnerRemoveLogo').value = '0';
    document.getElementById('partnerActiveHidden').value = '1';
    var toggle = document.getElementById('partnerActiveToggle');
    toggle.classList.add('active');
    document.querySelectorAll('.cat-select-item').forEach(function(i) { i.classList.remove('active'); });
    resetLogoPreview();
}

function openEditPartnerModal(id, name, desc, catId, url, active, logo) {
    document.getElementById('partnerModalTitle').textContent = 'Modifier le partenaire';
    document.getElementById('partnerForm').action = '/admin/partners/' + id + '/update';
    document.getElementById('partnerName').value = name;
    document.getElementById('partnerDetail').value = desc || '';
    document.getElementById('partnerUrl').value = url || '';
    document.getElementById('partnerCategoryId').value = catId || '';
    document.getElementById('partnerRemoveLogo').value = '0';
    document.getElementById('partnerActiveHidden').value = active ? '1' : '0';
    var toggle = document.getElementById('partnerActiveToggle');
    toggle.classList.toggle('active', active);

    document.querySelectorAll('.cat-select-item').forEach(function(i) {
        i.classList.toggle('active', parseInt(i.dataset.catval) === catId);
    });

    if (logo) {
        document.getElementById('logoPreview').innerHTML = '<img src="/uploads/partenaires/' + logo + '">';
        document.getElementById('logoLabel').textContent = logo;
    } else {
        resetLogoPreview();
    }

    openModal('modalPartner');
}

/* ── Logo preview ── */
function previewLogo(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('logoPreview').innerHTML = '<img src="' + e.target.result + '">';
            document.getElementById('logoLabel').textContent = input.files[0].name;
        };
        reader.readAsDataURL(input.files[0]);
        document.getElementById('partnerRemoveLogo').value = '0';
    }
}

function removeLogo() {
    resetLogoPreview();
    document.getElementById('logoInput').value = '';
    document.getElementById('partnerRemoveLogo').value = '1';
}

function resetLogoPreview() {
    document.getElementById('logoPreview').innerHTML = '<?= icon('image', 22, '', 'var(--creme-fonce)') ?>';
    document.getElementById('logoLabel').textContent = 'Aucun logo';
}

/* ── Category modal: create / edit ── */
function openEditCatModal(id, name, iconVal, color, order) {
    document.getElementById('catModalTitle').textContent = 'Modifier la catégorie';
    document.getElementById('catForm').action = '/admin/partners/categories/' + id + '/update';
    document.getElementById('catName').value = name;
    document.getElementById('catIcon').value = iconVal;
    document.getElementById('catSortOrder').value = order;
    document.getElementById('catColor').value = color;
    document.querySelectorAll('.color-swatch').forEach(function(s) {
        s.classList.toggle('active', s.dataset.color === color);
    });
    openModal('modalCategory');
}

function selectColor(el) {
    document.querySelectorAll('.color-swatch').forEach(function(s) { s.classList.remove('active'); });
    el.classList.add('active');
    document.getElementById('catColor').value = el.dataset.color;
}

/* ── Filter by category ── */
function filterCat(cat, btn) {
    document.querySelectorAll('.chip').forEach(function(c) { c.classList.remove('active'); });
    btn.classList.add('active');
    document.querySelectorAll('.cat-group').forEach(function(g) {
        g.style.display = (cat === 'all' || g.dataset.cat === cat) ? '' : 'none';
    });
}

/* ── Search ── */
function filterPartners(q) {
    var query = q.toLowerCase().trim();
    document.querySelectorAll('.cat-group').forEach(function(group) {
        var hasVisible = false;
        group.querySelectorAll('tbody tr').forEach(function(row) {
            var name = row.dataset.name || '';
            var match = !query || name.includes(query);
            row.style.display = match ? '' : 'none';
            if (match) hasVisible = true;
        });
        group.style.display = hasVisible || !query ? '' : 'none';
    });
}
</script>
