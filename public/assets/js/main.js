/**
 * Fête du Cidre — JavaScript principal (vanilla)
 */
(function () {
    'use strict';

    // ── Navbar scroll effect ──
    var navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            navbar.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // ── Mobile menu ──
    var menuToggle = document.getElementById('menuToggle');
    var navLinks = document.getElementById('navLinks');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });

        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('open');
            });
        });
    }

    // ── Scroll reveal ──
    var reveals = document.querySelectorAll('.reveal');
    if (reveals.length > 0) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry, i) {
                if (entry.isIntersecting) {
                    setTimeout(function () {
                        entry.target.classList.add('visible');
                    }, i * 80);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

        reveals.forEach(function (el) {
            observer.observe(el);
        });
    }

    // ── Smooth scroll for anchors ──
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var href = this.getAttribute('href');
            if (href === '#') return;
            var target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ── Auto-dismiss flash messages ──
    document.querySelectorAll('.flash').forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = 'opacity 0.3s, transform 0.3s';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                flash.remove();
            }, 300);
        }, 5000);
    });

    // ── Quantity buttons (cart) ──
    document.querySelectorAll('.qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var input = this.parentElement.querySelector('.qty-input');
            if (!input) return;

            var val = parseInt(input.value, 10) || 1;
            var min = parseInt(input.min, 10) || 1;
            var max = parseInt(input.max, 10) || 999;

            if (this.dataset.action === 'decrease') {
                input.value = Math.max(min, val - 1);
            } else {
                input.value = Math.min(max, val + 1);
            }

            input.dispatchEvent(new Event('change'));
        });
    });
})();
