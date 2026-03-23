

/* 
 global
 */

/* 
 fichier depense

 */


//tâches

function ouvrirModal() {
      const overlay = document.getElementById('modal-overlay');
      if (overlay) overlay.style.display = 'flex';
    }

    function fermerModal() {
      const overlay = document.getElementById('modal-overlay');
      if (overlay) overlay.style.display = 'none';
    }

    function fermerModalOverlay(e) {
      if (e.target === document.getElementById('modal-overlay')) fermerModal();
    }

    function filtrer(statut, btn) {
      document.querySelectorAll('.filtre-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.tache-card').forEach(card => {
        card.style.display = (statut === 'tous' || card.dataset.statut === statut) ? 'flex' : 'none';
      });
    }

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') fermerModal();
    });

    // function ouvrirModal() {
    //   const overlay = document.getElementById('modal-overlay');
    //   if (overlay) overlay.style.display = 'flex';
    // }

    // function fermerModal() {
    //   const overlay = document.getElementById('modal-overlay');
    //   if (overlay) overlay.style.display = 'none';
    // }

    // function fermerModalOverlay(e) {
    //   if (e.target === document.getElementById('modal-overlay')) fermerModal();
    // }

    //     // Filtres
    // function filtrer(statut, btn) {
    //   document.querySelectorAll('.filtre-btn').forEach(b => b.classList.remove('active'));
    //   btn.classList.add('active');
    //   document.querySelectorAll('.tache-card').forEach(card => {
    //     if (statut === 'tous' || card.dataset.statut === statut) {
    //       card.style.display = 'flex';
    //     } else {
    //       card.style.display = 'none';
    //     }
    //   });
    // }