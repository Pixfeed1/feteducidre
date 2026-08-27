<?php
/**
 * Bascule progressive — module de démonstration pour l'article.
 *
 * Il n'ajoute qu'une page de configuration : le sélecteur à trois positions
 * Désactivé / Par IP / Complet, plus la liste d'adresses autorisées. C'est
 * exactement l'écran que l'article décrit, et il est produit par PrestaShop
 * lui-même — pas redessiné.
 */
if (!defined('_PS_VERSION_')) { exit; }

class PixfeedBascule extends Module
{
    public function __construct()
    {
        $this->name = 'pixfeedbascule';
        $this->tab = 'front_office_features';
        $this->version = '1.0.0';
        $this->author = 'Pixfeed';
        $this->need_instance = 0;
        $this->bootstrap = true;
        parent::__construct();
        $this->displayName = 'Bascule progressive';
        $this->description = 'Choisit qui voit la nouvelle vitrine : personne, '
            . 'quelques adresses de test, ou tout le monde.';
        $this->ps_versions_compliancy = ['min' => '1.7', 'max' => _PS_VERSION_];
    }

    public function install()
    {
        return parent::install()
            && Configuration::updateValue('PIXFEED_MODE', 'ip')
            && Configuration::updateValue('PIXFEED_IPS', '203.0.113.24, 203.0.113.57');
    }

    public function uninstall()
    {
        return parent::uninstall()
            && Configuration::deleteByName('PIXFEED_MODE')
            && Configuration::deleteByName('PIXFEED_IPS');
    }

    public function getContent()
    {
        $sortie = '';
        if (Tools::isSubmit('submitPixfeedBascule')) {
            Configuration::updateValue('PIXFEED_MODE', Tools::getValue('PIXFEED_MODE'));
            Configuration::updateValue('PIXFEED_IPS', Tools::getValue('PIXFEED_IPS'));
            $sortie .= $this->displayConfirmation('Réglage enregistré.');
        }
        return $sortie . $this->renderForm();
    }

    protected function renderForm()
    {
        $champs = [
            'form' => [
                'legend' => [
                    'title' => 'Mode de diffusion',
                    'icon' => 'icon-random',
                ],
                'description' => 'Ce réglage décide qui reçoit les pages '
                    . 'fabriquées par la nouvelle vitrine. Vous pouvez revenir '
                    . 'en arrière à tout moment : rien n\'est irréversible.',
                'input' => [
                    [
                        'type' => 'radio',
                        'label' => 'Qui voit la nouvelle vitrine',
                        'name' => 'PIXFEED_MODE',
                        'required' => true,
                        'class' => 't',
                        'values' => [
                            ['id' => 'mode_off', 'value' => 'off',
                             'label' => 'Désactivé — tout est servi par PrestaShop'],
                            ['id' => 'mode_ip', 'value' => 'ip',
                             'label' => 'Par IP — seules les adresses listées ci-dessous'],
                            ['id' => 'mode_full', 'value' => 'full',
                             'label' => 'Complet — tous les visiteurs'],
                        ],
                    ],
                    [
                        'type' => 'text',
                        'label' => 'Adresses autorisées',
                        'name' => 'PIXFEED_IPS',
                        'desc' => 'Séparées par des virgules. Vos bureaux, '
                            . 'votre téléphone — personne d\'autre ne verra la '
                            . 'nouvelle vitrine.',
                        'size' => 60,
                    ],
                ],
                'submit' => ['title' => 'Enregistrer'],
            ],
        ];

        $aide = new HelperForm();
        $aide->module = $this;
        $aide->name_controller = $this->name;
        $aide->token = Tools::getAdminTokenLite('AdminModules');
        $aide->currentIndex = AdminController::$currentIndex
            . '&configure=' . $this->name;
        $aide->submit_action = 'submitPixfeedBascule';
        $aide->default_form_language = (int) Configuration::get('PS_LANG_DEFAULT');
        $aide->fields_value = [
            'PIXFEED_MODE' => Configuration::get('PIXFEED_MODE'),
            'PIXFEED_IPS' => Configuration::get('PIXFEED_IPS'),
        ];
        return $aide->generateForm([$champs]);
    }
}
