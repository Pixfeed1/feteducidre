<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Injecteur de scripts personnalisés.
 * Permet d'ajouter des scripts dans le <head>, après <body> ou avant </body>
 * sans bloquer le rendu (async/defer).
 */
class ScriptInjector
{
    /**
     * Rend les scripts pour une position donnée
     *
     * @param string $position Position : 'head', 'body_start', 'body_end'
     */
    public static function render(string $position): string
    {
        $key = match ($position) {
            'head'       => 'head_scripts',
            'body_start' => 'body_start_scripts',
            'body_end'   => 'body_end_scripts',
            default      => '',
        };

        if (empty($key)) {
            return '';
        }

        try {
            $db = Database::getInstance();
            $setting = $db->fetch(
                "SELECT value FROM settings WHERE `group` = 'scripts' AND `key` = ?",
                [$key]
            );

            $scripts = $setting['value'] ?? '';
            if (empty(trim($scripts))) {
                return '';
            }

            // Ajouter async ou defer aux balises <script> qui n'en ont pas
            $scripts = preg_replace(
                '/<script(?![^>]*(async|defer))([^>]*)>/i',
                '<script defer$2>',
                $scripts
            );

            return "\n<!-- Scripts personnalisés ({$position}) -->\n" . $scripts . "\n";
        } catch (\Exception) {
            return '';
        }
    }
}
