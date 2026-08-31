<?php
/**
 * Plugin Name: Réservation & Paiement Pro
 * Plugin URI:  https://exemple.test/reservation
 * Description: Prise de rendez-vous en ligne, acompte à la réservation et rappels automatiques.
 * Version:     5.1.0
 * Author:      Atelier Réservation
 * Text Domain: reservation-pro
 *
 * Même principe que `sentinelle.php` : le serveur de licences répond la
 * version, pas le paquet. Voir l'explication complète dans ce fichier-là.
 *
 * Celle-ci est là pour une raison précise : c'est l'extension qui touche aux
 * paiements. Une faille non corrigée sur ce périmètre ne coûte pas la même
 * chose qu'ailleurs, et une capture avec une seule extension bloquée laisserait
 * croire à un cas isolé. Une licence oubliée l'est rarement toute seule.
 */

if (!defined('ABSPATH')) {
    exit;
}

const RESERVATION_FICHIER = 'reservation-paiement-pro/reservation.php';
const RESERVATION_SLUG    = 'reservation-paiement-pro';
const RESERVATION_DISPO   = '5.3.1';
const RESERVATION_EXPIREE = '4 janvier 2026';

add_filter('site_transient_update_plugins', function ($transient) {
    if (!is_object($transient)) {
        $transient = new stdClass();
    }
    if (!isset($transient->response) || !is_array($transient->response)) {
        $transient->response = array();
    }

    $offre = new stdClass();
    $offre->id          = 'exemple.test/plugins/' . RESERVATION_SLUG;
    $offre->slug        = RESERVATION_SLUG;
    $offre->plugin      = RESERVATION_FICHIER;
    $offre->new_version = RESERVATION_DISPO;
    $offre->url         = 'https://exemple.test/reservation';
    $offre->package     = '';
    $offre->tested      = '7.1';
    $offre->requires_php = '8.1';

    $transient->response[RESERVATION_FICHIER] = $offre;
    return $transient;
});

add_action('in_plugin_update_message-' . RESERVATION_FICHIER, function () {
    echo ' <strong style="color:#b32d26">Licence expirée le '
        . RESERVATION_EXPIREE . '.</strong> Les versions 5.2 et '
        . RESERVATION_DISPO . ' contiennent des correctifs de sécurité sur le'
        . ' module de paiement. Aucune ne peut être installée.';
});
