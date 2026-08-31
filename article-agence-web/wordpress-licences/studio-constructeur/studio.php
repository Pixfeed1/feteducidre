<?php
/**
 * Plugin Name: Studio Constructeur de pages
 * Plugin URI:  https://exemple.test/studio
 * Description: Éditeur visuel par blocs, modèles de sections et bibliothèque de mises en page.
 * Version:     2.8.6
 * Author:      Studio
 * Text Domain: studio
 *
 * La troisième, et la plus gênante : un constructeur de pages tient TOUT le
 * site. On ne le désactive pas d'un clic pour se débarrasser du problème — la
 * mise en page part avec lui. C'est ce qui rend la licence expirée coûteuse :
 * on ne peut ni mettre à jour, ni retirer.
 *
 * Elle est en retard de deux versions majeures, avec la date d'expiration la
 * plus ancienne des trois. Sur les sites qu'on récupère, c'est toujours celle
 * qu'on trouve : l'abonnement a été pris une fois, à la livraison.
 */

if (!defined('ABSPATH')) {
    exit;
}

const STUDIO_FICHIER = 'studio-constructeur/studio.php';
const STUDIO_SLUG    = 'studio-constructeur';
const STUDIO_DISPO   = '3.0.2';
const STUDIO_EXPIREE = '28 novembre 2025';

add_filter('site_transient_update_plugins', function ($transient) {
    if (!is_object($transient)) {
        $transient = new stdClass();
    }
    if (!isset($transient->response) || !is_array($transient->response)) {
        $transient->response = array();
    }

    $offre = new stdClass();
    $offre->id          = 'exemple.test/plugins/' . STUDIO_SLUG;
    $offre->slug        = STUDIO_SLUG;
    $offre->plugin      = STUDIO_FICHIER;
    $offre->new_version = STUDIO_DISPO;
    $offre->url         = 'https://exemple.test/studio';
    $offre->package     = '';
    $offre->tested      = '7.1';
    $offre->requires_php = '8.0';

    $transient->response[STUDIO_FICHIER] = $offre;
    return $transient;
});

add_action('in_plugin_update_message-' . STUDIO_FICHIER, function () {
    echo ' <strong style="color:#b32d26">Licence expirée le '
        . STUDIO_EXPIREE . '.</strong> Deux versions majeures de retard, dont'
        . ' des correctifs de sécurité publiés. Le site reste sur la '
        . '2.8.6.';
});
