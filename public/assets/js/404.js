/**
 * Page 404 — Feuilles flottantes.
 */
(function () {
    var container = document.getElementById('leaves');
    if (!container) return;

    var colors = ['#7A9E6B', '#4A6B3E', '#D4833B', '#E8A95B', '#8DB87E'];

    function createLeaf() {
        var leaf = document.createElement('div');
        leaf.className = 'leaf';

        var color = colors[Math.floor(Math.random() * colors.length)];
        var size = 10 + Math.random() * 14;
        var x = Math.random() * 100;
        var duration = 12 + Math.random() * 18;
        var spinDuration = 4 + Math.random() * 6;
        var delay = Math.random() * 20;

        leaf.style.left = x + '%';
        leaf.style.animationDuration = duration + 's';
        leaf.style.animationDelay = delay + 's';

        leaf.innerHTML = '<svg width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="' + color + '" style="animation-duration:' + spinDuration + 's; opacity:0.5">'
            + '<path d="M12 2C6.5 6 2 12 2 17c0 3 2.5 5 5.5 5 2 0 3.5-1 4.5-3 1 2 2.5 3 4.5 3 3 0 5.5-2 5.5-5 0-5-4.5-11-10-15z"/>'
            + '</svg>';

        container.appendChild(leaf);

        setTimeout(function () {
            if (leaf.parentNode) leaf.remove();
        }, (duration + delay) * 1000);
    }

    // Quelques feuilles au départ
    for (var i = 0; i < 5; i++) {
        setTimeout(createLeaf, i * 800);
    }

    // En ajouter régulièrement
    setInterval(createLeaf, 4000);
})();
