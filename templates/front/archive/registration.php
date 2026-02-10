<?php
/**
 * Template formulaire d'inscription au concours.
 * Variables : $seo
 */
?>

<!-- Page Hero -->
<section class="page-hero">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/concours">Concours</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Inscription</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('pen-line', 16) ?> Inscription
        </span>

        <h1 class="page-hero-title">Inscription au <em>Concours</em></h1>

        <p class="page-hero-intro">Inscrivez votre cidre au concours de la Fête du Cidre</p>
    </div>
</section>

<section class="section">
    <div class="container" style="max-width:700px">
        <div class="card">
            <div class="card-body" style="padding:2rem">
                <form action="/concours/inscription" method="post">
                    <?= csrf_field() ?>

                    <h2 style="margin-bottom:1.5rem"><?= icon('user', 22) ?> Informations du producteur</h2>

                    <div class="form-group" style="margin-bottom:1rem">
                        <label for="producer_name">Nom du producteur / exploitation <span style="color:var(--orange-cidre)">*</span></label>
                        <input type="text" name="producer_name" id="producer_name"
                               value="<?= old('producer_name') ?>" required
                               class="form-control" placeholder="Nom du producteur">
                    </div>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
                        <div class="form-group">
                            <label for="email">Email <span style="color:var(--orange-cidre)">*</span></label>
                            <input type="email" name="email" id="email"
                                   value="<?= old('email') ?>" required
                                   class="form-control" placeholder="votre@email.fr">
                        </div>
                        <div class="form-group">
                            <label for="phone">Téléphone</label>
                            <input type="tel" name="phone" id="phone"
                                   value="<?= old('phone') ?>"
                                   class="form-control" placeholder="06 12 34 56 78">
                        </div>
                    </div>

                    <div class="form-group" style="margin-bottom:1rem">
                        <label for="producer_city">Ville / commune</label>
                        <input type="text" name="producer_city" id="producer_city"
                               value="<?= old('producer_city') ?>"
                               class="form-control" placeholder="Ville">
                    </div>

                    <hr style="border:none;border-top:1px solid var(--creme-fonce);margin:2rem 0">

                    <h2 style="margin-bottom:1.5rem"><?= icon('wine', 22) ?> Produit présenté</h2>

                    <div class="form-group" style="margin-bottom:1rem">
                        <label for="category">Catégorie <span style="color:var(--orange-cidre)">*</span></label>
                        <select name="category" id="category" required class="form-control">
                            <option value="">— Sélectionnez une catégorie —</option>
                            <option value="Cidre brut" <?= old('category') === 'Cidre brut' ? 'selected' : '' ?>>Cidre brut</option>
                            <option value="Cidre demi-sec" <?= old('category') === 'Cidre demi-sec' ? 'selected' : '' ?>>Cidre demi-sec</option>
                            <option value="Cidre doux" <?= old('category') === 'Cidre doux' ? 'selected' : '' ?>>Cidre doux</option>
                            <option value="Cidre rosé" <?= old('category') === 'Cidre rosé' ? 'selected' : '' ?>>Cidre rosé</option>
                            <option value="Poiré" <?= old('category') === 'Poiré' ? 'selected' : '' ?>>Poiré</option>
                            <option value="Jus de pomme" <?= old('category') === 'Jus de pomme' ? 'selected' : '' ?>>Jus de pomme</option>
                        </select>
                    </div>

                    <div class="form-group" style="margin-bottom:1rem">
                        <label for="product_name">Nom du produit <span style="color:var(--orange-cidre)">*</span></label>
                        <input type="text" name="product_name" id="product_name"
                               value="<?= old('product_name') ?>" required
                               class="form-control" placeholder="Nom de votre cidre">
                    </div>

                    <div class="form-group" style="margin-bottom:1.5rem">
                        <label for="notes">Remarques / informations complémentaires</label>
                        <textarea name="notes" id="notes" rows="4" class="form-control"
                                  placeholder="Millésime, variétés de pommes, méthode de fabrication..."><?= old('notes') ?></textarea>
                    </div>

                    <button type="submit" class="btn btn-secondary" style="width:100%;justify-content:center">
                        <?= icon('check', 18) ?> Envoyer mon inscription
                    </button>
                </form>
            </div>
        </div>

        <div style="text-align:center;margin-top:2rem">
            <a href="/concours" class="btn btn-outline">
                <?= icon('arrow-left', 18) ?> Retour au concours
            </a>
        </div>
    </div>
</section>
