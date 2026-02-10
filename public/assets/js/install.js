/**
 * Logique JS de l'installateur — Fête du Cidre CMS
 * Gère la navigation par étapes, le test DB en AJAX, et l'installation.
 */
(function () {
  'use strict';

  var currentStep = 1;
  var dbTested = false;

  /* ── Icônes SVG réutilisables ── */
  var ICON_CHECK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"><path d="M20 6 9 17l-5-5"/></svg>';
  var ICON_ARROW_RIGHT = '<svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg>';
  var ICON_ARROW_LEFT = '<svg class="btn-icon-sm" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"/></svg>';

  /* ── Navigation entre étapes ── */
  window.goToStep = function (n) {
    /* Bloquer l'avancement si prérequis non OK */
    if (n > 1 && !window.installPrereqOk) return;
    /* Bloquer l'étape 3 sans test DB réussi */
    if (n > 2 && !dbTested) return;

    /* Mettre à jour le contenu visible */
    var contents = document.querySelectorAll('.step-content');
    for (var i = 0; i < contents.length; i++) {
      contents[i].classList.remove('active');
    }
    var target = document.getElementById('step-' + n);
    if (target) target.classList.add('active');

    /* Mettre à jour les dots du stepper */
    for (var s = 1; s <= 4; s++) {
      var dot = document.getElementById('dot-' + s);
      var label = document.getElementById('label-' + s);
      if (!dot || !label) continue;

      dot.className = 'step-dot';
      label.className = 'step-label';

      if (s < n) {
        dot.classList.add('done');
        dot.innerHTML = ICON_CHECK;
      } else if (s === n) {
        dot.classList.add('active');
        dot.textContent = s;
        label.classList.add('active');
      } else {
        dot.classList.add('upcoming');
        dot.textContent = s;
      }
    }

    /* Mettre à jour les lignes du stepper */
    for (var l = 1; l <= 3; l++) {
      var line = document.getElementById('line-' + l);
      if (!line) continue;
      line.className = 'step-line';
      if (l < n) line.classList.add('done');
    }

    /* Étape 4 : lancer l'installation */
    if (n === 4) {
      runInstall();
    }

    currentStep = n;
  };

  /* ── Test de connexion base de données (AJAX) ── */
  window.testDb = function () {
    var btn = document.getElementById('dbTestBtn');
    var result = document.getElementById('dbResult');
    var continueBtn = document.getElementById('dbContinueBtn');

    /* Récupérer les valeurs du formulaire */
    var data = {
      action: 'test-db',
      db_host: document.getElementById('db_host').value,
      db_port: document.getElementById('db_port').value,
      db_name: document.getElementById('db_name').value,
      db_user: document.getElementById('db_user').value,
      db_pass: document.getElementById('db_pass').value
    };

    /* État loading */
    btn.className = 'test-btn testing';
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/></svg> Test en cours\u2026';
    result.classList.remove('show');
    result.className = 'db-result';

    /* Requête AJAX */
    var xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.pathname, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;

      try {
        var resp = JSON.parse(xhr.responseText);
      } catch (e) {
        showDbFail(btn, result, continueBtn, 'Réponse invalide du serveur.');
        return;
      }

      if (resp.success) {
        btn.className = 'test-btn success';
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg> Connexion réussie';
        result.className = 'db-result ok show';
        result.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg> ' + resp.message;
        dbTested = true;
        if (continueBtn) continueBtn.disabled = false;
      } else {
        showDbFail(btn, result, continueBtn, resp.message || 'Connexion échouée.');
      }
    };

    var encoded = Object.keys(data).map(function (k) {
      return encodeURIComponent(k) + '=' + encodeURIComponent(data[k]);
    }).join('&');
    xhr.send(encoded);
  };

  function showDbFail(btn, result, continueBtn, message) {
    btn.className = 'test-btn fail';
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg> Connexion échouée';
    result.className = 'db-result ko show';
    result.textContent = message;
    dbTested = false;
    if (continueBtn) continueBtn.disabled = true;
  }

  /* ── Lancement de l'installation (AJAX) ── */
  function runInstall() {
    var logItems = document.querySelectorAll('#installing .log-item');
    var bar = document.getElementById('progressBar');
    var label = document.getElementById('progressLabel');
    var installingDiv = document.getElementById('installing');
    var installedDiv = document.getElementById('installed');

    /* Collecter les données des formulaires */
    var data = {
      action: 'install',
      db_host: document.getElementById('db_host').value,
      db_port: document.getElementById('db_port').value,
      db_name: document.getElementById('db_name').value,
      db_user: document.getElementById('db_user').value,
      db_pass: document.getElementById('db_pass').value,
      first_name: document.getElementById('admin_first_name').value,
      last_name: document.getElementById('admin_last_name').value,
      email: document.getElementById('admin_email').value,
      password: document.getElementById('admin_password').value,
      site_name: document.getElementById('site_name').value,
      site_url: document.getElementById('site_url').value
    };

    var percents = [10, 25, 45, 65, 80, 92, 100];
    var labels = [
      'Génération du fichier .env\u2026',
      'Connexion à la base de données\u2026',
      'Création des 15 tables\u2026',
      'Insertion des données initiales\u2026',
      'Création du compte administrateur\u2026',
      'Génération du cache initial\u2026',
      'Verrouillage de l\u2019installateur\u2026'
    ];

    /* Réinitialiser les étapes visuelles */
    for (var j = 0; j < logItems.length; j++) {
      logItems[j].className = 'log-item pending';
    }

    var step = 0;

    function advanceVisual() {
      if (step > 0 && step <= logItems.length) {
        logItems[step - 1].className = 'log-item done';
      }
      if (step < logItems.length) {
        logItems[step].className = 'log-item active';
        bar.style.width = percents[step] + '%';
        label.innerHTML = '<strong>' + labels[step] + '</strong>';
        step++;
      }
    }

    /* Avancer visuellement étape par étape */
    advanceVisual();
    var visualTimer = setInterval(function () {
      if (step < 3) advanceVisual();
    }, 700);

    /* Envoyer la requête d'installation */
    var xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.pathname, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;
      clearInterval(visualTimer);

      try {
        var resp = JSON.parse(xhr.responseText);
      } catch (e) {
        showInstallError('Réponse serveur invalide.');
        return;
      }

      if (resp.success) {
        /* Terminer toutes les étapes visuelles */
        function finishSteps() {
          if (step <= logItems.length) {
            advanceVisual();
            setTimeout(finishSteps, 400);
          } else {
            /* Marquer la dernière comme done */
            if (logItems.length > 0) {
              logItems[logItems.length - 1].className = 'log-item done';
            }
            bar.style.width = '100%';
            label.innerHTML = '<strong>Installation terminée !</strong>';

            /* Injecter les données de succès */
            var siteUrlEl = document.getElementById('success-site-url');
            var adminUrlEl = document.getElementById('success-admin-url');
            var adminEmailEl = document.getElementById('success-admin-email');
            var dbNameEl = document.getElementById('success-db-name');
            var phpVerEl = document.getElementById('success-php-version');
            var mysqlVerEl = document.getElementById('success-mysql-version');

            if (siteUrlEl) siteUrlEl.textContent = data.site_url;
            if (adminUrlEl) adminUrlEl.textContent = data.site_url + '/admin';
            if (adminEmailEl) adminEmailEl.textContent = data.email;
            if (dbNameEl) dbNameEl.textContent = resp.db_name || data.db_name;
            if (phpVerEl) phpVerEl.textContent = resp.php_version || '';
            if (mysqlVerEl) mysqlVerEl.textContent = resp.mysql_version || '';

            setTimeout(function () {
              installingDiv.style.display = 'none';
              installedDiv.style.display = 'block';
            }, 600);
          }
        }
        finishSteps();
      } else {
        showInstallError(resp.message || 'Erreur lors de l\u2019installation.');
      }
    };

    var encoded = Object.keys(data).map(function (k) {
      return encodeURIComponent(k) + '=' + encodeURIComponent(data[k]);
    }).join('&');
    xhr.send(encoded);
  }

  function showInstallError(message) {
    var label = document.getElementById('progressLabel');
    if (label) {
      label.innerHTML = '<strong style="color:var(--rouge)">' + message + '</strong>';
    }
    var activeItems = document.querySelectorAll('#installing .log-item.active');
    for (var i = 0; i < activeItems.length; i++) {
      activeItems[i].className = 'log-item';
      activeItems[i].style.color = 'var(--rouge)';
    }
  }

  /* ── Validation du formulaire admin (étape 3) ── */
  window.validateAndInstall = function () {
    var firstName = document.getElementById('admin_first_name').value.trim();
    var lastName = document.getElementById('admin_last_name').value.trim();
    var email = document.getElementById('admin_email').value.trim();
    var password = document.getElementById('admin_password').value;
    var passwordConfirm = document.getElementById('admin_password_confirm').value;
    var errors = [];

    if (!firstName) errors.push('Le prénom est requis.');
    if (!lastName) errors.push('Le nom est requis.');
    if (!email || email.indexOf('@') === -1) errors.push('Email invalide.');
    if (password.length < 8) errors.push('Le mot de passe doit faire au moins 8 caractères.');
    if (password !== passwordConfirm) errors.push('Les mots de passe ne correspondent pas.');

    var errorDiv = document.getElementById('step3-errors');
    if (errors.length > 0) {
      errorDiv.innerHTML = errors.map(function (e) {
        return '<div class="alert-error"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="flex-shrink:0"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg> ' + e + '</div>';
      }).join('');
      return;
    }
    errorDiv.innerHTML = '';
    goToStep(4);
  };

  /* ── Eye toggles (afficher/masquer mot de passe) ── */
  var SVG_EYE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>';
  var SVG_EYE_OFF = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/></svg>';

  /* Toggle password visibility — appelé via onclick comme les autres fonctions */
  window.togglePassword = function (btn, inputId) {
    var input = document.getElementById(inputId);
    if (!input) return;
    var isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    btn.innerHTML = isPassword ? SVG_EYE_OFF : SVG_EYE;
  };

  /* ── Initialisation ── */
  window.addEventListener('DOMContentLoaded', function () {
    /* Auto-focus sur le premier input visible */
    var firstInput = document.querySelector('.step-content.active input:not([disabled])');
    if (firstInput) firstInput.focus();
  });

})();
