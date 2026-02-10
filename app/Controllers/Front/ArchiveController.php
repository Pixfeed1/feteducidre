<?php

declare(strict_types=1);

namespace App\Controllers\Front;

use App\Core\Controller;
use App\Core\Config;
use App\Core\Request;
use App\Core\Response;

/**
 * Contrôleur des archives, concours et randonnée.
 * Gère les éditions passées, les résultats de concours et les classements de randonnée.
 */
class ArchiveController extends Controller
{
    /**
     * Page d'accueil des archives — navigation vers les sections.
     */
    public function index(Request $request, array $params = []): void
    {
        $db = $this->db();

        $page = $db->fetch(
            "SELECT id, title, slug, content, meta_title, meta_description FROM pages WHERE slug = ? AND status = ?",
            ['archives', 'published']
        );

        $seo = [
            'title'       => 'Revivez les années — Archives — Fête du Cidre',
            'description' => 'Plongez dans les archives de la Fête du Cidre : origines, affiches, randonnées, programmes, photos et concours.',
            'canonical'   => Config::baseUrl() . '/archives',
        ];

        $this->render('templates/front/archive/index.php', [
            'page' => $page,
            'seo'  => $seo,
        ]);
    }

    /**
     * Liste les programmes / flyers de toutes les éditions.
     */
    public function programmes(Request $request, array $params = []): void
    {
        $db = $this->db();

        $editions = $db->fetchAll(
            "SELECT id, year, title, programme_image_id
             FROM editions WHERE is_active = 1 ORDER BY year DESC"
        );

        $seo = [
            'title'       => 'Programmes & Flyers — Archives Fête du Cidre',
            'description' => 'Retrouvez les programmes et flyers de toutes les éditions de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/archives/programmes',
        ];

        $this->render('templates/front/archive/programmes.php', [
            'editions' => $editions,
            'seo'      => $seo,
        ]);
    }

    /**
     * Affiche une édition par année.
     */
    public function show(Request $request, array $params = []): void
    {
        $year = (int) ($params['year'] ?? 0);
        $db = $this->db();

        $edition = $db->fetch(
            "SELECT id, year, title, description, poster_image_id, programme_image_id, highlights, stats
             FROM editions WHERE year = ? AND is_active = 1",
            [$year]
        );

        if (!$edition) {
            Response::notFound();
            return;
        }

        // Décoder les données JSON
        $edition['highlights'] = !empty($edition['highlights'])
            ? json_decode($edition['highlights'], true) : [];
        $edition['stats'] = !empty($edition['stats'])
            ? json_decode($edition['stats'], true) : [];

        // Récupérer l'affiche si définie
        $poster = null;
        if ($edition['poster_image_id']) {
            $poster = $db->fetch(
                "SELECT id, filename, alt_text, width, height, dominant_color, has_webp, has_avif, sizes
                 FROM media WHERE id = ?",
                [(int) $edition['poster_image_id']]
            );
        }

        // Récupérer les résultats de concours pour cette année
        $contestResults = $db->fetchAll(
            "SELECT id, category, `rank`, producer_name, producer_city, product_name, medal
             FROM contest_results WHERE year = ? ORDER BY category ASC, `rank` ASC",
            [$year]
        );

        // SEO
        $seo = [
            'title'       => 'Édition ' . $year . ' — Archives Fête du Cidre',
            'description' => $edition['description']
                ? excerpt($edition['description'], 160)
                : 'Découvrez l\'édition ' . $year . ' de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/archives/' . $year,
        ];

        $this->render('templates/front/archive/show.php', [
            'edition'        => $edition,
            'poster'         => $poster,
            'contestResults' => $contestResults,
            'seo'            => $seo,
        ]);
    }

    /**
     * Page du concours — grille des années par type (cidre / affiches).
     */
    public function contests(Request $request, array $params = []): void
    {
        $db = $this->db();

        $page = $db->fetch(
            "SELECT id, title, slug, content, meta_title, meta_description FROM pages WHERE slug = ? AND status = ?",
            ['concours', 'published']
        );

        // Récupérer les années et catégories disponibles
        $rows = $db->fetchAll(
            "SELECT DISTINCT year, category FROM contest_results ORDER BY year DESC"
        );

        // Séparer cidre et affiches
        $cidreYears = [];
        $affichesYears = [];
        foreach ($rows as $row) {
            $year = (int) $row['year'];
            $cat  = mb_strtolower($row['category']);
            if (str_contains($cat, 'affiche')) {
                if (!in_array($year, $affichesYears, true)) {
                    $affichesYears[] = $year;
                }
            } else {
                if (!in_array($year, $cidreYears, true)) {
                    $cidreYears[] = $year;
                }
            }
        }

        // SEO
        $seo = [
            'title'       => 'Les Concours — Fête du Cidre',
            'description' => 'Retrouvez les palmarès des concours de cidre et d\'affiches de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/concours',
        ];

        $this->render('templates/front/archive/contests.php', [
            'page'          => $page,
            'cidreYears'    => $cidreYears,
            'affichesYears' => $affichesYears,
            'seo'           => $seo,
        ]);
    }

    /**
     * Palmarès complet des concours par année et catégorie.
     */
    public function palmares(Request $request, array $params = []): void
    {
        $db = $this->db();

        // Année demandée (par défaut : la plus récente)
        $selectedYear = $request->get('year') ? (int) $request->get('year') : null;

        $years = $db->fetchAll(
            "SELECT DISTINCT year FROM contest_results ORDER BY year DESC"
        );

        if (!$selectedYear && !empty($years)) {
            $selectedYear = (int) $years[0]['year'];
        }

        // Résultats pour l'année sélectionnée
        $results = [];
        if ($selectedYear) {
            $results = $db->fetchAll(
                "SELECT id, category, `rank`, producer_name, producer_city, product_name, score, medal
                 FROM contest_results WHERE year = ? ORDER BY category ASC, `rank` ASC",
                [$selectedYear]
            );
        }

        // Grouper par catégorie
        $grouped = [];
        foreach ($results as $row) {
            $grouped[$row['category']][] = $row;
        }

        // SEO
        $seo = [
            'title'       => 'Palmarès du Concours — Fête du Cidre',
            'description' => 'Tous les résultats et classements du concours de cidre par année et catégorie.',
            'canonical'   => Config::baseUrl() . '/concours/palmares',
        ];

        $this->render('templates/front/archive/palmares.php', [
            'years'        => $years,
            'selectedYear' => $selectedYear,
            'grouped'      => $grouped,
            'seo'          => $seo,
        ]);
    }

    /**
     * Page d'inscription au concours — documents et contact.
     */
    public function registration(Request $request, array $params = []): void
    {
        $db = $this->db();

        // Récupérer les coordonnées depuis les settings
        $rows = $db->fetchAll("SELECT `key`, value FROM settings WHERE `group` = 'general'");
        $general = [];
        foreach ($rows as $row) {
            $general[$row['key']] = $row['value'];
        }

        // SEO
        $seo = [
            'title'       => 'Inscription au Concours — Fête du Cidre',
            'description' => 'Retrouvez les documents pour participer au concours de cidre de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/concours/inscription',
        ];

        $this->render('templates/front/archive/registration.php', [
            'seo'          => $seo,
            'contactEmail' => $general['email'] ?? null,
            'contactPhone' => $general['phone'] ?? null,
        ]);
    }

    /**
     * Traitement du formulaire d'inscription au concours (POST).
     */
    public function registerContest(Request $request, array $params = []): void
    {
        // Validation CSRF
        $token = $request->post('_csrf_token');
        if (empty($token) || !hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
            set_flash('error', 'Le formulaire a expiré. Veuillez réessayer.');
            Response::redirect('/concours/inscription');
            return;
        }

        // Récupérer les données du formulaire
        $producerName = $request->post('producer_name', '');
        $producerCity = $request->post('producer_city', '');
        $email        = $request->post('email', '');
        $phone        = $request->post('phone', '');
        $category     = $request->post('category', '');
        $productName  = $request->post('product_name', '');
        $notes        = $request->post('notes', '');

        // Validation
        $errors = [];
        if (empty($producerName)) {
            $errors[] = 'Le nom du producteur est requis.';
        }
        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $errors[] = 'Une adresse email valide est requise.';
        }
        if (empty($category)) {
            $errors[] = 'La catégorie est requise.';
        }
        if (empty($productName)) {
            $errors[] = 'Le nom du produit est requis.';
        }

        if (!empty($errors)) {
            $_SESSION['_old_input'] = $request->all();
            set_flash('error', implode(' ', $errors));
            Response::redirect('/concours/inscription');
            return;
        }

        // TODO: Enregistrer l'inscription en base ou envoyer par email
        unset($_SESSION['_old_input']);
        set_flash('success', 'Votre inscription au concours a bien été enregistrée. Nous vous recontacterons prochainement.');
        Response::redirect('/concours/inscription');
    }

    /**
     * Page archives des randonnées — classements par année/catégorie, réponses.
     */
    public function hike(Request $request, array $params = []): void
    {
        $db = $this->db();

        $page = $db->fetch(
            "SELECT id, title, slug, content, meta_title, meta_description FROM pages WHERE slug = ? AND status = ?",
            ['randonnee', 'published']
        );

        // Années avec résultats, groupés par catégorie
        $rows = $db->fetchAll(
            "SELECT DISTINCT he.year, hr.category
             FROM hike_editions he
             JOIN hike_results hr ON he.id = hr.hike_edition_id
             WHERE he.is_active = 1
             ORDER BY he.year DESC, hr.category ASC"
        );

        $classementYears = [];
        foreach ($rows as $row) {
            $year = (int) $row['year'];
            $classementYears[$year][] = $row['category'];
        }

        // Années avec éditions pour les réponses du rallye
        $editionYears = $db->fetchAll(
            "SELECT year FROM hike_editions WHERE is_active = 1 ORDER BY year DESC"
        );
        $reponseYears = array_column($editionYears, 'year');

        // SEO
        $seo = [
            'title'       => 'Randonnées — Archives — Fête du Cidre',
            'description' => 'Résultats, classements et réponses du rallye pédestre de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/randonnee',
        ];

        $this->render('templates/front/archive/hike.php', [
            'page'            => $page,
            'classementYears' => $classementYears,
            'reponseYears'    => $reponseYears,
            'seo'             => $seo,
        ]);
    }

    /**
     * Classements de la randonnée.
     */
    public function hikeRanking(Request $request, array $params = []): void
    {
        $db = $this->db();

        // Année demandée (par défaut : la plus récente)
        $selectedYear = $request->get('year') ? (int) $request->get('year') : null;

        $years = $db->fetchAll(
            "SELECT DISTINCT he.year
             FROM hike_editions he
             JOIN hike_results hr ON he.id = hr.hike_edition_id
             WHERE he.is_active = 1
             ORDER BY he.year DESC"
        );

        if (!$selectedYear && !empty($years)) {
            $selectedYear = (int) $years[0]['year'];
        }

        // Résultats pour l'année sélectionnée
        $results = [];
        if ($selectedYear) {
            $results = $db->fetchAll(
                "SELECT hr.id, hr.`rank`, hr.participant_name, hr.category, hr.time_seconds, hr.bib_number
                 FROM hike_results hr
                 JOIN hike_editions he ON hr.hike_edition_id = he.id
                 WHERE he.year = ? AND he.is_active = 1
                 ORDER BY hr.`rank` ASC",
                [$selectedYear]
            );
        }

        // SEO
        $seo = [
            'title'       => 'Classement Randonnée — Fête du Cidre',
            'description' => 'Consultez les classements de la randonnée de la Fête du Cidre.',
            'canonical'   => Config::baseUrl() . '/randonnee/classement',
        ];

        $this->render('templates/front/archive/ranking.php', [
            'years'        => $years,
            'selectedYear' => $selectedYear,
            'results'      => $results,
            'seo'          => $seo,
        ]);
    }
}
