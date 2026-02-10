<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Bootstrap de l'application.
 * Point d'entrée principal qui initialise la config, le routeur et dispatch la requête.
 */
class App
{
    private Router $router;
    private Request $request;

    public function __construct()
    {
        // Démarrer la session
        if (session_status() === PHP_SESSION_NONE) {
            session_start([
                'cookie_httponly' => true,
                'cookie_samesite' => 'Lax',
                'use_strict_mode' => true,
            ]);
        }

        // Charger la configuration
        Config::getInstance();

        // Initialiser le routeur et la requête
        $this->router = new Router();
        $this->request = new Request();

        // Déclarer les routes
        $this->registerRoutes();
    }

    /**
     * Lance l'application
     */
    public function run(): void
    {
        try {
            // Vérifier le mode maintenance avant le routage
            $maintenance = new \App\Middleware\MaintenanceMiddleware();
            $maintenance->handle($this->request, function () {
                $this->router->dispatch($this->request);
            });
        } catch (\Exception $e) {
            if (Config::isDebug()) {
                Response::error($e->getMessage() . "\n\n" . $e->getTraceAsString());
            } else {
                Response::error();
            }
        }
    }

    /**
     * Déclare toutes les routes de l'application
     */
    private function registerRoutes(): void
    {
        $r = $this->router;

        // ── Routes front publiques ──
        $r->get('/', [\App\Controllers\Front\HomeController::class, 'index']);

        // Pages génériques par slug
        $r->get('/origines', [\App\Controllers\Front\PageController::class, 'show']);
        $r->get('/infos-pratiques', [\App\Controllers\Front\PageController::class, 'infos']);
        $r->get('/remerciements', [\App\Controllers\Front\PageController::class, 'remerciements']);
        $r->get('/mentions-legales', [\App\Controllers\Front\PageController::class, 'show']);
        $r->get('/programme-2025', [\App\Controllers\Front\PageController::class, 'show']);

        // Contact
        $r->get('/contact', [\App\Controllers\Front\PageController::class, 'contact']);
        $r->post('/contact', [\App\Controllers\Front\PageController::class, 'contactSubmit']);

        // Boutique
        $r->get('/boutique', [\App\Controllers\Front\ShopController::class, 'index']);
        $r->get('/boutique/{slug}', [\App\Controllers\Front\ShopController::class, 'show']);
        $r->get('/panier', [\App\Controllers\Front\ShopController::class, 'cart']);
        $r->post('/panier/ajouter', [\App\Controllers\Front\ShopController::class, 'addToCart']);
        $r->post('/panier/modifier', [\App\Controllers\Front\ShopController::class, 'updateCart']);
        $r->post('/panier/supprimer', [\App\Controllers\Front\ShopController::class, 'removeFromCart']);
        $r->get('/commande', [\App\Controllers\Front\ShopController::class, 'checkout']);
        $r->post('/commande', [\App\Controllers\Front\ShopController::class, 'processCheckout']);
        $r->get('/commande/confirmation/{reference}', [\App\Controllers\Front\ShopController::class, 'confirmation']);

        // Galerie
        $r->get('/galerie', [\App\Controllers\Front\GalleryController::class, 'index']);
        $r->get('/galerie/{slug}', [\App\Controllers\Front\GalleryController::class, 'album']);

        // Archives
        $r->get('/archives', [\App\Controllers\Front\ArchiveController::class, 'index']);
        $r->get('/archives/programmes', [\App\Controllers\Front\ArchiveController::class, 'programmes']);
        $r->get('/archives/{year}', [\App\Controllers\Front\ArchiveController::class, 'show']);

        // Concours
        $r->get('/concours', [\App\Controllers\Front\ArchiveController::class, 'contests']);
        $r->get('/concours/palmares', [\App\Controllers\Front\ArchiveController::class, 'palmares']);
        $r->get('/concours/inscription', [\App\Controllers\Front\ArchiveController::class, 'registration']);
        $r->post('/concours/inscription', [\App\Controllers\Front\ArchiveController::class, 'registerContest']);

        // Randonnée
        $r->get('/randonnee', [\App\Controllers\Front\ArchiveController::class, 'hike']);
        $r->get('/randonnee/classement', [\App\Controllers\Front\ArchiveController::class, 'hikeRanking']);

        // Webhooks (paiement)
        $r->post('/webhook/stripe', [\App\Controllers\Front\WebhookController::class, 'stripe']);

        // ── Routes admin ──
        $r->get('/admin/login', [\App\Controllers\Admin\AuthController::class, 'loginForm']);
        $r->post('/admin/login', [\App\Controllers\Admin\AuthController::class, 'login']);
        $r->get('/admin/logout', [\App\Controllers\Admin\AuthController::class, 'logout']);
        $r->get('/admin/forgot-password', [\App\Controllers\Admin\AuthController::class, 'forgotPasswordForm']);
        $r->post('/admin/forgot-password', [\App\Controllers\Admin\AuthController::class, 'forgotPassword']);
        $r->get('/admin/reset-password/{token}', [\App\Controllers\Admin\AuthController::class, 'resetPasswordForm']);
        $r->post('/admin/reset-password/{token}', [\App\Controllers\Admin\AuthController::class, 'resetPassword']);

        // Routes admin protégées par middleware
        $r->group('/admin', \App\Middleware\AuthMiddleware::class, function (Router $r) {
            $r->get('', [\App\Controllers\Admin\DashboardController::class, 'index']);
            $r->get('/dashboard', [\App\Controllers\Admin\DashboardController::class, 'index']);

            // Pages
            $r->resource('/pages', \App\Controllers\Admin\PageAdminController::class);

            // Produits
            $r->resource('/products', \App\Controllers\Admin\ProductAdminController::class);

            // Commandes
            $r->get('/orders', [\App\Controllers\Admin\OrderAdminController::class, 'index']);
            $r->get('/orders/{id}', [\App\Controllers\Admin\OrderAdminController::class, 'show']);
            $r->post('/orders/{id}/status', [\App\Controllers\Admin\OrderAdminController::class, 'updateStatus']);

            // Factures
            $r->get('/invoices', [\App\Controllers\Admin\InvoiceAdminController::class, 'index']);
            $r->get('/invoices/{id}/pdf', [\App\Controllers\Admin\InvoiceAdminController::class, 'pdf']);
            $r->get('/invoices/{id}/stream', [\App\Controllers\Admin\InvoiceAdminController::class, 'stream']);
            $r->get('/invoices/{id}', [\App\Controllers\Admin\InvoiceAdminController::class, 'show']);
            $r->post('/invoices/{id}/generate', [\App\Controllers\Admin\InvoiceAdminController::class, 'generate']);
            $r->post('/invoices/settings', [\App\Controllers\Admin\InvoiceAdminController::class, 'saveSettings']);

            // Actualités (redirection externe)
            $r->get('/news', [\App\Controllers\Admin\NewsAdminController::class, 'index']);
            $r->post('/news', [\App\Controllers\Admin\NewsAdminController::class, 'update']);

            // Galerie
            $r->resource('/albums', \App\Controllers\Admin\AlbumAdminController::class);
            $r->post('/albums/{id}/photos', [\App\Controllers\Admin\AlbumAdminController::class, 'uploadPhotos']);
            $r->post('/photos/{id}/delete', [\App\Controllers\Admin\AlbumAdminController::class, 'deletePhoto']);

            // Éditions / Archives
            $r->post('/editions/origines', [\App\Controllers\Admin\EditionAdminController::class, 'saveOrigines']);
            $r->post('/editions/origines/image', [\App\Controllers\Admin\EditionAdminController::class, 'uploadOriginesImage']);
            $r->resource('/editions', \App\Controllers\Admin\EditionAdminController::class);

            // Concours
            $r->get('/contests', [\App\Controllers\Admin\ContestAdminController::class, 'index']);
            $r->post('/contests/palmares', [\App\Controllers\Admin\ContestAdminController::class, 'storePalmares']);
            $r->post('/contests/palmares/{id}/delete', [\App\Controllers\Admin\ContestAdminController::class, 'deletePalmares']);
            $r->post('/contests/documents', [\App\Controllers\Admin\ContestAdminController::class, 'storeDocument']);
            $r->post('/contests/documents/{id}/delete', [\App\Controllers\Admin\ContestAdminController::class, 'deleteDocument']);
            $r->post('/contests/settings', [\App\Controllers\Admin\ContestAdminController::class, 'saveSettings']);

            // Partenaires
            $r->get('/partners', [\App\Controllers\Admin\PartnerAdminController::class, 'index']);
            $r->post('/partners', [\App\Controllers\Admin\PartnerAdminController::class, 'store']);
            $r->post('/partners/{id}/update', [\App\Controllers\Admin\PartnerAdminController::class, 'update']);
            $r->post('/partners/{id}/delete', [\App\Controllers\Admin\PartnerAdminController::class, 'destroy']);
            $r->post('/partners/categories', [\App\Controllers\Admin\PartnerAdminController::class, 'storeCategory']);
            $r->post('/partners/categories/{id}/update', [\App\Controllers\Admin\PartnerAdminController::class, 'updateCategory']);
            $r->post('/partners/categories/{id}/delete', [\App\Controllers\Admin\PartnerAdminController::class, 'destroyCategory']);

            // Randonnées
            $r->get('/hikes', [\App\Controllers\Admin\HikeAdminController::class, 'index']);
            $r->post('/hikes', [\App\Controllers\Admin\HikeAdminController::class, 'store']);
            $r->post('/hikes/{id}/delete', [\App\Controllers\Admin\HikeAdminController::class, 'destroy']);
            $r->post('/hikes/{id}/file', [\App\Controllers\Admin\HikeAdminController::class, 'uploadFile']);
            $r->post('/hikes/file/{id}/delete', [\App\Controllers\Admin\HikeAdminController::class, 'deleteFile']);
            $r->post('/hikes/responses', [\App\Controllers\Admin\HikeAdminController::class, 'storeResponse']);
            $r->post('/hikes/responses/{id}/delete', [\App\Controllers\Admin\HikeAdminController::class, 'deleteResponse']);
            $r->post('/hikes/settings', [\App\Controllers\Admin\HikeAdminController::class, 'saveSettings']);

            // Paramètres
            $r->get('/settings', [\App\Controllers\Admin\SettingsAdminController::class, 'index']);
            $r->post('/settings', [\App\Controllers\Admin\SettingsAdminController::class, 'update']);
            $r->post('/settings/colors/reset', [\App\Controllers\Admin\SettingsAdminController::class, 'resetColors']);
            $r->post('/settings/upload/{type}', [\App\Controllers\Admin\SettingsAdminController::class, 'uploadLogo']);
            $r->post('/settings/remove/{type}', [\App\Controllers\Admin\SettingsAdminController::class, 'removeLogo']);
            $r->post('/settings/export-db', [\App\Controllers\Admin\SettingsAdminController::class, 'exportDb']);

            // Utilisateurs
            $r->resource('/users', \App\Controllers\Admin\UserAdminController::class);
            $r->post('/users/{id}/password', [\App\Controllers\Admin\UserAdminController::class, 'changePassword']);

            // Média upload (AJAX)
            $r->post('/media/upload', [\App\Controllers\Admin\MediaAdminController::class, 'upload']);
            $r->post('/media/{id}/delete', [\App\Controllers\Admin\MediaAdminController::class, 'delete']);

            // Cache
            $r->post('/cache/clear', [\App\Controllers\Admin\SettingsAdminController::class, 'clearCache']);
        });
    }
}
