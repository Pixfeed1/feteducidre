<?php
/**
 * Template page Inscription Concours — cartes documents + bannière contact.
 * Variables : $seo, $contactEmail, $contactPhone
 */
$currentYear = (int) date('Y');
?>

<!-- Page Hero -->
<section class="page-hero" style="text-align:center">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="page-hero-content" style="position:relative;z-index:2;max-width:700px;margin:0 auto;padding:5rem 2rem 4rem">
        <nav class="breadcrumb" style="justify-content:center;margin-bottom:1.5rem" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Inscription concours</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('trophy', 14) ?> Édition <?= $currentYear ?>
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Inscription au <em>concours</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Retrouvez les documents nécessaires pour participer au concours de cidre de la Fête du Cidre.</p>
    </div>
</section>

<!-- Cartes inscription -->
<section class="insc-content">

    <div class="insc-grid">
        <!-- Professionnels -->
        <div class="insc-card">
            <div class="insc-card-header">
                <div class="insc-card-icon">
                    <?= icon('trophy', 24) ?>
                </div>
                <div class="insc-card-info">
                    <h3>Professionnels</h3>
                    <p>Cidriculteurs &amp; producteurs</p>
                </div>
            </div>
            <div class="insc-card-divider"></div>
            <div class="insc-card-links">
                <a href="https://www.feteducidre.fr/wp-content/uploads/2024/06/reglement-concours-2024.pdf"
                   class="doc-link" target="_blank" rel="noopener">
                    <div class="doc-link-icon reglement">
                        <?= icon('scroll-text', 18) ?>
                    </div>
                    <div class="doc-link-info">
                        <strong>Règlement du concours</strong>
                        <span>PDF — Conditions de participation</span>
                    </div>
                    <div class="doc-link-arrow"><?= icon('download', 16) ?></div>
                </a>
                <a href="https://www.feteducidre.fr/wp-content/uploads/2024/06/formulaire-inscription-concours-2024.pdf"
                   class="doc-link" target="_blank" rel="noopener">
                    <div class="doc-link-icon inscription">
                        <?= icon('file-pen', 18) ?>
                    </div>
                    <div class="doc-link-info">
                        <strong>Formulaire d'inscription</strong>
                        <span>PDF — À remplir et retourner</span>
                    </div>
                    <div class="doc-link-arrow"><?= icon('download', 16) ?></div>
                </a>
            </div>
        </div>

        <!-- Amateurs -->
        <div class="insc-card">
            <div class="insc-card-header">
                <div class="insc-card-icon">
                    <?= icon('apple', 24) ?>
                </div>
                <div class="insc-card-info">
                    <h3>Amateurs</h3>
                    <p>Particuliers &amp; passionnés</p>
                </div>
            </div>
            <div class="insc-card-divider"></div>
            <div class="insc-card-links">
                <a href="https://www.feteducidre.fr/wp-content/uploads/2024/06/reglement-concours-2024.pdf"
                   class="doc-link" target="_blank" rel="noopener">
                    <div class="doc-link-icon reglement">
                        <?= icon('scroll-text', 18) ?>
                    </div>
                    <div class="doc-link-info">
                        <strong>Règlement du concours</strong>
                        <span>PDF — Conditions de participation</span>
                    </div>
                    <div class="doc-link-arrow"><?= icon('download', 16) ?></div>
                </a>
                <a href="https://www.feteducidre.fr/wp-content/uploads/2024/06/formulaire-inscription-concours-2024.pdf"
                   class="doc-link" target="_blank" rel="noopener">
                    <div class="doc-link-icon inscription">
                        <?= icon('file-pen', 18) ?>
                    </div>
                    <div class="doc-link-info">
                        <strong>Formulaire d'inscription</strong>
                        <span>PDF — À remplir et retourner</span>
                    </div>
                    <div class="doc-link-arrow"><?= icon('download', 16) ?></div>
                </a>
            </div>
        </div>

        <!-- Producteurs -->
        <div class="insc-card">
            <div class="insc-card-header">
                <div class="insc-card-icon">
                    <?= icon('tree-deciduous', 24) ?>
                </div>
                <div class="insc-card-info">
                    <h3>Producteurs</h3>
                    <p>Courrier &amp; informations</p>
                </div>
            </div>
            <div class="insc-card-divider"></div>
            <div class="insc-card-links">
                <a href="https://www.feteducidre.fr/wp-content/uploads/2024/06/courrier-producteurs-2024.pdf"
                   class="doc-link" target="_blank" rel="noopener">
                    <div class="doc-link-icon courrier">
                        <?= icon('send', 18) ?>
                    </div>
                    <div class="doc-link-info">
                        <strong>Courrier producteurs</strong>
                        <span>PDF — Invitation et informations</span>
                    </div>
                    <div class="doc-link-arrow"><?= icon('download', 16) ?></div>
                </a>
                <a href="https://www.feteducidre.fr/wp-content/uploads/2024/06/reglement-concours-2024.pdf"
                   class="doc-link" target="_blank" rel="noopener">
                    <div class="doc-link-icon reglement">
                        <?= icon('scroll-text', 18) ?>
                    </div>
                    <div class="doc-link-info">
                        <strong>Règlement du concours</strong>
                        <span>PDF — Conditions de participation</span>
                    </div>
                    <div class="doc-link-arrow"><?= icon('download', 16) ?></div>
                </a>
            </div>
        </div>
    </div>

    <!-- Bannière contact -->
    <div class="info-banner">
        <div class="info-banner-inner">
            <div class="info-banner-icon">
                <?= icon('help-circle', 24) ?>
            </div>
            <div class="info-banner-text">
                <h3>Besoin d'informations ?</h3>
                <p>Pour toute question sur le concours, contactez-nous par téléphone au <?= e($contactPhone ?? '02 41 61 37 26') ?> ou par email.</p>
            </div>
            <div class="info-banner-action">
                <a href="mailto:<?= e($contactEmail ?? 'contact@feteducidre.fr') ?>" class="btn btn-outline" style="color:var(--blanc);border-color:rgba(255,255,255,.4)">
                    <?= icon('mail', 16) ?> Nous écrire
                </a>
            </div>
        </div>
    </div>

</section>
