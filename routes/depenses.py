COULEURS = {
    'Banu':     '#5B6CFF',
    'Eoghan':   '#FF7A59',
    'Francois': '#34D399',
    'Loucia':   '#A78BFA',
    'Nassim':   '#F59E0B',
}

CATEGORIES = ['loyer', 'activite', 'courses', 'autres']

@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()

    # Total global = somme de TOUTES les dépenses
    total = sum(d.montant for d in depenses)

    # Regrouper par catégorie
    par_categorie = {}
    for cat in CATEGORIES:
        deps_cat = [d for d in depenses if d.categorie == cat]
        total_cat = sum(d.montant for d in deps_cat)

        # Barres par personne dans cette catégorie
        par_personne = {}
        for d in deps_cat:
            if d.payeur not in par_personne:
                par_personne[d.payeur] = 0
            par_personne[d.payeur] += d.montant

        barres = []
        for personne, montant in par_personne.items():
            pct = (montant / total_cat * 100) if total_cat > 0 else 0
            barres.append({
                'nom':         personne,
                'montant':     montant,
                'pourcentage': round(pct, 1),
                'couleur':     COULEURS.get(personne, '#888888')
            })

        par_categorie[cat] = {
            'depenses': deps_cat,
            'total':    total_cat,
            'barres':   barres
        }

    return render_template('depenses.html',
                           par_categorie=par_categorie,
                           total=total,
                           couleurs=COULEURS,
                           categories=CATEGORIES)

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        titre     = request.form['titre']
        montant   = float(request.form['montant'])
        categorie = request.form['categorie']

        # Plusieurs payeurs séparés par virgule
        payeurs  = request.form.getlist('payeurs')
        montants = request.form.getlist('montants_payeurs')

        for i, payeur in enumerate(payeurs):
            if payeur and montants[i]:
                nouvelle = Depense(
                    titre     = titre,
                    montant   = float(montants[i]),
                    payeur    = payeur,
                    categorie = categorie
                )
                db.session.add(nouvelle)

        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))

    return render_template('depenses.html',
                           par_categorie={},
                           total=0,
                           couleurs=COULEURS,
                           categories=CATEGORIES)

@depenses_bp.route('/depenses/supprimer/<int:id>')
def supprimer_depense(id):
    depense = Depense.query.get_or_404(id)
    db.session.delete(depense)
    db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))