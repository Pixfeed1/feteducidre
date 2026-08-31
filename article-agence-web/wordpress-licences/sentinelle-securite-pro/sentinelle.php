<?php
/**
 * Plugin Name: Sentinelle Sécurité Pro
 * Plugin URI:  https://exemple.test/sentinelle
 * Description: Pare-feu applicatif, journal des connexions et blocage des tentatives répétées.
 * Version:     3.4.2
 * Author:      Sentinelle
 * Text Domain: sentinelle
 *
 * ---------------------------------------------------------------------------
 * POURQUOI CETTE EXTENSION EXISTE DANS CE DÉPÔT
 * ---------------------------------------------------------------------------
 * Elle sert à produire une capture RÉELLE de l'écran des extensions dans l'état
 * « licence expirée ». Elle ne truque rien : elle utilise le mécanisme normal
 * de WordPress.
 *
 * Une extension payante interroge le serveur de son éditeur, qui répond deux
 * choses : la dernière version publiée, et — si la licence est valide — l'URL
 * du paquet à télécharger. Licence expirée, le serveur répond toujours la
 * version, mais SANS paquet.
 *
 * C'est exactement ce que fait le filtre ci-dessous : il déclare une version
 * disponible et laisse `package` vide. WordPress fait alors le reste tout seul
 * et affiche « Automatic update is unavailable for this plugin » — la mention
 * qu'on voit sur la capture n'est pas écrite par moi, elle vient du coeur.
 *
 * Les noms d'éditeurs sont inventés, les domaines sont en `.test` (RFC 2606) :
 * aucune extension réelle n'est mise en cause.
 */

if (!defined('ABSPATH')) {
    exit;
}

const SENTINELLE_FICHIER = 'sentinelle-securite-pro/sentinelle.php';
const SENTINELLE_SLUG    = 'sentinelle-securite-pro';
const SENTINELLE_DISPO   = '3.6.0';
const SENTINELLE_EXPIREE = '12 mars 2026';

/**
 * La réponse du serveur de licences, telle que WordPress l'attend.
 *
 * `package` vide = licence expirée. C'est la seule différence avec une
 * extension à jour de son abonnement.
 */
add_filter('site_transient_update_plugins', function ($transient) {
    if (!is_object($transient)) {
        $transient = new stdClass();
    }
    if (!isset($transient->response) || !is_array($transient->response)) {
        $transient->response = array();
    }

    $offre = new stdClass();
    $offre->id          = 'exemple.test/plugins/' . SENTINELLE_SLUG;
    $offre->slug        = SENTINELLE_SLUG;
    $offre->plugin      = SENTINELLE_FICHIER;
    $offre->new_version = SENTINELLE_DISPO;
    $offre->url         = 'https://exemple.test/sentinelle';
    $offre->package     = '';   // licence expirée : rien à télécharger
    $offre->tested      = '7.1';
    $offre->requires_php = '8.0';

    $transient->response[SENTINELLE_FICHIER] = $offre;
    return $transient;
});

/**
 * Le message de l'éditeur, ajouté sous la ligne de mise à jour.
 *
 * WordPress prévoit ce point d'accroche précisément pour ça : c'est là que les
 * extensions payantes expliquent pourquoi la mise à jour ne partira pas.
 */
add_action('in_plugin_update_message-' . SENTINELLE_FICHIER, function () {
    echo ' <strong style="color:#b32d26">Licence expirée le '
        . SENTINELLE_EXPIREE . '.</strong> La version ' . SENTINELLE_DISPO
        . ' corrige une faille de sécurité déjà publiée. Elle ne sera pas'
        . ' installée tant que la licence n’est pas renouvelée.';
});
