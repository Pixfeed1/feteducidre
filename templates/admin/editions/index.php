<?php
/**
 * Archives — liste des éditions, section Origines, catégories.
 * Variables : $editions, $totalEditions, $totalPosters, $totalProgrammes, $totalPalmares, $origines
 */
?>

<div style="max-width:1100px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:linear-gradient(135deg, var(--brun), #8B6B4A)"><?= icon('archive', 22, '', 'white') ?></div>
            <h1>Archives</h1>
        </div>
        <div class="page-header-actions">
            <a href="/admin/editions/create" class="btn btn-primary">
                <?= icon('plus', 15) ?> Nouvelle édition
            </a>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(92,61,46,0.12)"><?= icon('calendar', 18, '', 'var(--brun)') ?></div>
            <div><div class="stat-value"><?= $totalEditions ?></div><div class="stat-label">Éditions</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(212,131,59,0.12)"><?= icon('image', 18, '', 'var(--orange-cidre)') ?></div>
            <div><div class="stat-value"><?= $totalPosters ?></div><div class="stat-label">Affiches</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(74,107,62,0.12)"><?= icon('clipboard-list', 18, '', 'var(--vert-mousse)') ?></div>
            <div><div class="stat-value"><?= $totalProgrammes ?></div><div class="stat-label">Programmes</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:rgba(139,92,246,0.12)"><?= icon('award', 18, '', 'var(--violet)') ?></div>
            <div><div class="stat-value"><?= $totalPalmares ?></div><div class="stat-label">Palmarès concours</div></div>
        </div>
    </div>

    <!-- CATÉGORIES ARCHIVES -->
    <div class="cat-grid">
        <a class="cat-card featured" href="#sectionOrigines" onclick="event.preventDefault();document.getElementById('sectionOrigines').scrollIntoView({behavior:'smooth'})">
            <div class="cat-card-icon" style="background:var(--brun)"><?= icon('book-open', 22, '', 'white') ?></div>
            <div class="cat-card-info">
                <div class="cat-card-label">Depuis les débuts</div>
                <div class="cat-card-title">Origines</div>
                <div class="cat-card-desc">L'histoire de la Fête du Cidre, texte et image d'illustration</div>
            </div>
            <div class="cat-card-actions">
                <span class="btn-icon"><?= icon('pencil', 13) ?></span>
            </div>
        </a>
        <a class="cat-card" href="#sectionEditions" onclick="event.preventDefault();document.getElementById('sectionEditions').scrollIntoView({behavior:'smooth'})">
            <div class="cat-card-arrow"><?= icon('chevron-right', 16) ?></div>
            <div class="cat-card-icon" style="background:var(--orange-cidre)"><?= icon('image', 20, '', 'white') ?></div>
            <div class="cat-card-label">Collection</div>
            <div class="cat-card-title">Affiches</div>
            <div class="cat-card-count"><?= icon('file', 10) ?> <?= $totalPosters ?> fichier<?= $totalPosters > 1 ? 's' : '' ?></div>
        </a>
        <a class="cat-card" href="#sectionEditions" onclick="event.preventDefault();document.getElementById('sectionEditions').scrollIntoView({behavior:'smooth'})">
            <div class="cat-card-arrow"><?= icon('chevron-right', 16) ?></div>
            <div class="cat-card-icon" style="background:var(--vert-mousse)"><?= icon('clipboard-list', 20, '', 'white') ?></div>
            <div class="cat-card-label">Historique</div>
            <div class="cat-card-title">Programmes</div>
            <div class="cat-card-count"><?= icon('file', 10) ?> <?= $totalProgrammes ?> fichier<?= $totalProgrammes > 1 ? 's' : '' ?></div>
        </a>
        <a class="cat-card" href="/admin/hikes">
            <div class="cat-card-arrow"><?= icon('chevron-right', 16) ?></div>
            <div class="cat-card-icon" style="background:var(--vert-clair)"><?= icon('map', 20, '', 'white') ?></div>
            <div class="cat-card-label">Parcours</div>
            <div class="cat-card-title">Randonnées</div>
            <div class="cat-card-count"><?= icon('arrow-right', 10) ?> Voir admin Randonnées</div>
        </a>
        <a class="cat-card" href="/admin/albums">
            <div class="cat-card-arrow"><?= icon('chevron-right', 16) ?></div>
            <div class="cat-card-icon" style="background:var(--bleu)"><?= icon('camera', 20, '', 'white') ?></div>
            <div class="cat-card-label">Galerie</div>
            <div class="cat-card-title">Photos</div>
            <div class="cat-card-count"><?= icon('arrow-right', 10) ?> Voir admin Galerie</div>
        </a>
        <a class="cat-card" href="#sectionEditions" onclick="event.preventDefault();document.getElementById('sectionEditions').scrollIntoView({behavior:'smooth'})">
            <div class="cat-card-arrow"><?= icon('chevron-right', 16) ?></div>
            <div class="cat-card-icon" style="background:var(--violet)"><?= icon('award', 20, '', 'white') ?></div>
            <div class="cat-card-label">Palmarès</div>
            <div class="cat-card-title">Concours</div>
            <div class="cat-card-count"><?= icon('file', 10) ?> <?= $totalPalmares ?> fichier<?= $totalPalmares > 1 ? 's' : '' ?></div>
        </a>
    </div>

    <!-- ORIGINES -->
    <form method="post" action="/admin/editions/origines" id="sectionOrigines">
        <?= csrf_field() ?>
        <div class="origines-card">
            <div class="origines-header">
                <div class="cat-card-icon" style="background:var(--brun)"><?= icon('book-open', 18, '', 'white') ?></div>
                <div class="origines-title">Page Origines</div>
                <div style="flex:1"></div>
                <div class="toggle <?= ($origines['is_published'] ?? '1') === '1' ? 'active' : '' ?>"
                     onclick="this.classList.toggle('active');this.nextElementSibling.value=this.classList.contains('active')?'1':'0'"></div>
                <input type="hidden" name="origines_published" value="<?= ($origines['is_published'] ?? '1') === '1' ? '1' : '0' ?>">
                <span style="font-size:0.72rem;color:var(--texte-leger);font-weight:600">Publié</span>
            </div>
            <div class="origines-grid">
                <div class="field">
                    <label>Titre</label>
                    <input type="text" name="origines_title" value="<?= e($origines['title'] ?? '') ?>" placeholder="Aux origines de la Fête du Cidre">
                </div>
                <div class="field">
                    <label>Sous-titre</label>
                    <input type="text" name="origines_subtitle" value="<?= e($origines['subtitle'] ?? '') ?>" placeholder="L'Hôtellerie de Flée, depuis 1989">
                </div>
                <div class="field" style="grid-column:1/-1">
                    <label>Texte de présentation</label>
                    <textarea name="origines_text" rows="4" placeholder="L'histoire de la Fête du Cidre…"><?= e($origines['text'] ?? '') ?></textarea>
                </div>
                <div class="field">
                    <label>Image d'illustration</label>
                    <?php if (!empty($origines['image'])): ?>
                        <div class="upload-zone" style="cursor:default">
                            <?= icon('image', 18) ?>
                            <span><?= e($origines['image']) ?></span>
                            <small style="color:var(--texte-leger)">Image actuelle</small>
                        </div>
                    <?php else: ?>
                        <div class="upload-zone" style="cursor:default">
                            <?= icon('image', 18) ?>
                            <span>Aucune image</span>
                        </div>
                    <?php endif; ?>
                    <div class="form-hint" style="margin-top:0.3rem;font-size:0.7rem;color:var(--texte-leger)">
                        Pour changer l'image, utilisez le formulaire ci-dessous.
                    </div>
                </div>
                <div class="field">
                    <label>Lien "En savoir plus" (optionnel)</label>
                    <input type="text" name="origines_link" value="<?= e($origines['link'] ?? '') ?>" placeholder="URL vers un article ou une page">
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;margin-top:1rem">
                <button type="submit" class="btn btn-primary"><?= icon('check', 14) ?> Enregistrer</button>
            </div>
        </div>
    </form>

    <!-- Formulaire upload image Origines séparé -->
    <form method="post" action="/admin/editions/origines/image" enctype="multipart/form-data" style="margin-top:-1.5rem;margin-bottom:2rem">
        <?= csrf_field() ?>
        <div style="display:flex;align-items:center;gap:0.8rem;padding:0.6rem 1rem;background:var(--blanc);border:1.5px solid var(--creme-fonce);border-radius:12px">
            <label style="font-size:0.78rem;font-weight:600;white-space:nowrap"><?= icon('upload', 14) ?> Image Origines :</label>
            <input type="file" name="origines_image" accept="image/jpeg,image/png,image/webp" style="font-size:0.8rem;flex:1">
            <button type="submit" class="btn btn-sm btn-primary"><?= icon('upload', 12) ?> Envoyer</button>
        </div>
    </form>

    <!-- ÉDITIONS PAR ANNÉE -->
    <div class="section-block" id="sectionEditions">
        <div class="section-header">
            <div class="section-icon" style="background:var(--vert-profond)"><?= icon('calendar', 18, '', 'white') ?></div>
            <div>
                <div class="section-title">Éditions par année</div>
                <div class="section-subtitle">Affiche, programme et palmarès concours pour chaque édition</div>
            </div>
            <div class="section-line"></div>
            <div class="section-actions">
                <a href="/admin/editions/create" class="btn btn-primary btn-sm"><?= icon('plus', 13) ?> Édition</a>
            </div>
        </div>

        <?php if (empty($editions)): ?>
            <div class="card">
                <div class="card-body">
                    <div class="empty-state" style="text-align:center;padding:3rem">
                        <?= icon('calendar', 40) ?>
                        <p style="margin-top:0.8rem;color:var(--texte-leger)">Aucune édition pour le moment.</p>
                        <a href="/admin/editions/create" class="btn btn-primary" style="margin-top:1rem"><?= icon('plus', 15) ?> Créer une édition</a>
                    </div>
                </div>
            </div>
        <?php else: ?>
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th style="width:30px"></th>
                            <th>Année</th>
                            <th>Affiche</th>
                            <th>Programme</th>
                            <th>Concours</th>
                            <th>Complétude</th>
                            <th style="width:90px">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($editions as $edition):
                            $hasPoster = !empty($edition['poster_image_id']);
                            $hasProgramme = !empty($edition['programme_image_id']);
                            $hasPalmares = !empty($edition['palmares_media_id']);
                            $score = ($hasPoster ? 1 : 0) + ($hasProgramme ? 1 : 0) + ($hasPalmares ? 1 : 0);
                            if ($score === 3) {
                                $statusClass = 'complete';
                                $statusIcon = 'check-circle';
                            } elseif ($score > 0) {
                                $statusClass = 'partial';
                                $statusIcon = 'alert-circle';
                            } else {
                                $statusClass = 'empty';
                                $statusIcon = 'circle';
                            }
                        ?>
                            <tr>
                                <td><span style="color:var(--creme-fonce)"><?= icon('grip-vertical', 14) ?></span></td>
                                <td><span class="td-year"><?= (int) $edition['year'] ?></span></td>
                                <td>
                                    <?php if ($hasPoster): ?>
                                        <span class="td-badge has"><?= icon('check', 8) ?> <?= e($edition['poster_original'] ?? 'affiche') ?></span>
                                    <?php else: ?>
                                        <span class="td-badge missing"><?= icon('minus', 8) ?> —</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <?php if ($hasProgramme): ?>
                                        <span class="td-badge has"><?= icon('check', 8) ?> <?= e($edition['programme_original'] ?? 'programme') ?></span>
                                    <?php else: ?>
                                        <span class="td-badge missing"><?= icon('minus', 8) ?> —</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <?php if ($hasPalmares): ?>
                                        <span class="td-badge has"><?= icon('check', 8) ?> <?= e($edition['palmares_original'] ?? 'palmarès') ?></span>
                                    <?php else: ?>
                                        <span class="td-badge missing"><?= icon('minus', 8) ?> —</span>
                                    <?php endif; ?>
                                </td>
                                <td><span class="td-status <?= $statusClass ?>"><?= icon($statusIcon, 8) ?> <?= $score ?>/3</span></td>
                                <td>
                                    <div class="td-actions">
                                        <a href="/admin/editions/<?= (int) $edition['id'] ?>/edit" class="btn-icon" title="Modifier"><?= icon('pencil', 13) ?></a>
                                        <form method="post" action="/admin/editions/<?= (int) $edition['id'] ?>/delete"
                                              style="display:inline" onsubmit="return confirm('Supprimer cette édition ?')">
                                            <?= csrf_field() ?>
                                            <button type="submit" class="btn-icon" title="Supprimer" style="color:var(--rouge)"><?= icon('trash-2', 13) ?></button>
                                        </form>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            <a href="/admin/editions/create" class="add-row"><?= icon('plus', 14) ?> Ajouter une édition</a>
        <?php endif; ?>
    </div>

</div>
