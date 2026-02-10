<?php

declare(strict_types=1);

namespace App\Controllers\Front;

use App\Core\Controller;
use App\Core\Request;
use App\Core\Response;
use App\Services\PaymentService;

/**
 * Contrôleur des webhooks de paiement.
 * Reçoit les notifications Stripe pour confirmer les paiements.
 */
class WebhookController extends Controller
{
    /**
     * Endpoint Stripe webhook (POST /webhook/stripe).
     * Reçoit les événements Stripe et met à jour le statut des commandes.
     */
    public function stripe(Request $request, array $params = []): void
    {
        // Le payload brut est nécessaire pour la vérification de signature
        $payload = file_get_contents('php://input');
        $signature = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';

        if (empty($payload) || empty($signature)) {
            http_response_code(400);
            echo json_encode(['error' => 'Missing payload or signature']);
            exit;
        }

        try {
            $paid = PaymentService::handleWebhook($payload, $signature);
            http_response_code(200);
            echo json_encode(['received' => true, 'paid' => $paid]);
        } catch (\Stripe\Exception\SignatureVerificationException $e) {
            http_response_code(400);
            echo json_encode(['error' => 'Invalid signature']);
        } catch (\Exception $e) {
            http_response_code(500);
            echo json_encode(['error' => 'Webhook error']);
        }
        exit;
    }
}
