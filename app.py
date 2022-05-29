import datetime, os, time, re
from werkzeug.utils import secure_filename

from config import app, db, ALLOWED_EXTENSIONS, DIR_ROOT, desc
from flask import render_template, redirect, url_for, request, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_required, login_user, \
                        logout_user, current_user

from forms import UserForm, LoginForm, EditUserForm, MaterielForm, SousensembleForm, ArticleForm, OutilForm,\
    MaterieladdoutilForm, SiteForm, MaterielinsiteForm, GammeForm, InterventionForm, Ordre_maintenanceForm,\
    OperateurForm, Ordre_updateForm, Ordre_maintenance_createForm, Document_materieltypeForm, Document_interForm,\
    Document_omForm, Delete_composantForm, Add_composantForm, Import_dataForm, FilterForm

from models import User, Materieltype, Sousensemble, Outils, Article, Site, Materiel, Gamme, Intervention,\
    Ordre_maintenance, Operateur, Document_materieltype, Document_inter, Document_om, Role



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def ctrl_autorisation(role):
    roles = [(role.role) for role in current_user.roles]
    if role not in roles:
        return False
    else:
        return True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def user_load(user_id):
    return User.query.get(user_id)


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash(message='Vous êtes déjà conecté')
        return redirect(url_for('index'))
    loginform = LoginForm(request.form)
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user and user.check_password(loginform.password.data):
            login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', loginform=loginform)

@app.route('/profil')
@login_required
def profil():
    return render_template('profil.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user', methods=['POST', 'GET'])
def user():
    """if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))"""

    userform = UserForm(request.form)
    if userform.validate_on_submit():
        toto = User()
        userform.roles.data = Role.query.filter(Role.id.in_(userform.roles.data)).all()
        userform.populate_obj(toto)
        toto.hash_password(userform.password.data)
        db.session.add(toto)
        db.session.commit()
        return redirect(url_for('users'))
    else:
        print(userform.errors)
    return render_template('user.html', userform=userform)


@app.route('/user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    userform = EditUserForm(obj=user, data=request.form)

    if userform.validate_on_submit():
        userform.roles.data = Role.query.filter(Role.id.in_(userform.roles.data)).all()
        userform.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))
    userform.roles.data = [(data.id) for data in user.roles]
    return render_template('edit_user.html', userform=userform)

@app.route('/users')
@login_required
def users():
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    users_list = User.query.all()
    return render_template('users.html', users=users_list)

@app.route('/user/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_delete(user_id):
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

# Materiel type
@app.route('/materiel', methods=['get','post'])
@login_required
def materiel():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materieltype()
    materielform = MaterielForm(request.form)
    if materielform.validate_on_submit():
        #materielform.populate_obj(materiel)
        materiel.marque = materielform.marque.data
        materiel.modele = materielform.modele.data
        materiel.categorie = materielform.categorie.data
        materiel.info = materielform.info.data
        materiel.author = current_user.id
        liste = (materielform.sousensembles.data)
        materiel.gammes = Gamme.query.filter(Gamme.id.in_(materielform.gammes.data)).all()

        composants = [(data) for data in Sousensemble.query.filter(Sousensemble.id.in_(liste)).all()]
        for composant in composants:
            materiel.sousensembles.append(composant)
        db.session.add(materiel)
        db.session.commit()
        return  redirect(url_for('materiels'))
    else:
        print(materielform.errors)
    return  render_template('materiel/materiel.html', materielform=materielform)

@app.route('/materiel/detail/<int:materiel_id>')
@login_required
def materiel_detail(materiel_id):
    materiel = Materieltype.query.get(materiel_id)
    form = Delete_composantForm()
    return render_template('materiel/materiel_detail.html', materiel=materiel, form=form)

@app.route('/materiel/delete/<int:materiel_id>')
@login_required
def materiel_delete(materiel_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materieltype.query.get(materiel_id)
    if materiel.user == current_user:
        db.session.delete(materiel)
        db.session.commit()
        return redirect(url_for('materiels'))
    else:
        return redirect(url_for('index'))

@app.route('/materiel/update/<int:materiel_id>',methods=['post','get'])
def materiel_update(materiel_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materieltype.query.get(materiel_id)
    materieltypeform = MaterielForm(obj=materiel, data=request.form )
    materieltypeform.sousensembles.data = [(data.id) for data in materiel.sousensembles]
    if materieltypeform.validate_on_submit():
        materiel.marque = materieltypeform.marque.data
        materiel.modele = materieltypeform.modele.data
        materiel.categorie = materieltypeform.categorie.data
        materiel.info = materieltypeform.info.data

        materiel.gammes = Gamme.query.filter(Gamme.id.in_(materieltypeform.gammes.data)).all()

        liste = (materieltypeform.sousensembles.raw_data)

        materiel.sousensembles = []
        composants = [(data) for data in Sousensemble.query.filter(Sousensemble.id.in_(liste)).all()]
        for composant in composants:
            materiel.sousensembles.append(composant)
        db.session.add(materiel)
        db.session.commit()
        return redirect(url_for('materiel_detail', materiel_id=materiel_id))
    else:
        print(materieltypeform.errors)
    materieltypeform.gammes.data = [(data.id) for data in materiel.gammes]
    print(materiel.gammes)
    return render_template('materiel/materiel_update.html', materieltypeform=materieltypeform)

@app.route('/materiels/<int:page>')
@app.route('/materiels')
@login_required
def materiels(page=None):
    materiels = Materieltype.query.all()
    toto = Materieltype.query.paginate(page=page, per_page=15)
    return render_template('materiel/materiels.html', materiels=materiels, toto=toto)

@app.route('/materiel/composant/delete', methods=['post','get'])
@login_required
def materiel_composant_remove():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    removeform = Delete_composantForm(request.form)
    if removeform.validate_on_submit():
        materiel = Materieltype.query.get(removeform.materiel_id.data)
        composant = Sousensemble.query.get(removeform.composant_id.data)
        materiel.sousensembles.remove(composant)
        db.session.add(materiel)
        db.session.commit()
    return redirect(url_for('materiel_detail', materiel_id=materiel.id))

@app.route('/materiel/outil/delete', methods=['post','get'])
@login_required
def materiel_outil_remove():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    removeform = Delete_composantForm(request.form)
    if removeform.validate_on_submit():
        materiel = Materieltype.query.get(removeform.materiel_id.data)
        outil = Outils.query.get(removeform.composant_id.data)
        materiel.listeoutils.remove(outil)
        db.session.add(outil)
        db.session.commit()
    return redirect(url_for('materiel_detail', materiel_id=materiel.id))

# sous-ensemble
@app.route('/sous_ensemble', methods=['post','get'])
@login_required
def sous_ensemble():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    sousensemble = Sousensemble()
    sousensembleform = SousensembleForm(request.form)
    if sousensembleform.validate_on_submit():
        sousensembleform.populate_obj(sousensemble)
        db.session.add(sousensemble)
        db.session.commit()
        return redirect(url_for('sous_ensembles'))
    return render_template('sous_ensemble/sous_ensemble.html', sousensembleform=sousensembleform)

@app.route('/sous_ensemble/<int:sous_ensemble_id>')
@login_required
def sous_ensemble_detail(sous_ensemble_id):
    sous_ensemble = Sousensemble.query.get(sous_ensemble_id)
    return render_template('sous_ensemble/sous_ensemble_detail.html', sous_ensemble=sous_ensemble)

@app.route('/sous_ensemble/update/<int:sous_ensemble_id>', methods=['get','post'])
@login_required
def sous_ensemble_update(sous_ensemble_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    sous_ensemble = Sousensemble.query.get(sous_ensemble_id)
    sous_ensembleform = SousensembleForm(obj=sous_ensemble, data=request.form)
    if sous_ensembleform.validate_on_submit():
        sous_ensembleform.populate_obj(sous_ensemble)
        db.session.add(sous_ensemble)
        db.session.commit()
        return redirect(url_for('sous_ensemble_detail', sous_ensemble_id=sous_ensemble.id))
    return render_template('sous_ensemble/sous_ensemble_update.html', sous_ensembleform=sous_ensembleform)

@app.route('/sous_ensemble/delete/<int:sous_ensemble_id>')
@login_required
def sous_ensemble_delete(sous_ensemble_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    sous_ensemble = Sousensemble.query.get(sous_ensemble_id)
    db.session.delete(sous_ensemble)
    db.session.commit()
    return redirect(url_for('sous_ensembles'))

@app.route('/sous_ensembles')
@login_required
def sous_ensembles():
    sousensembles = Sousensemble.query.all()
    return render_template('sous_ensemble/sous_ensembles.html', sousensembles=sousensembles)

# Article
@app.route('/article', methods=['post','get'])
@login_required
def article():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    article = Article()
    articleform = ArticleForm(request.form)
    if articleform.validate_on_submit():
        articleform.populate_obj(article)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('articles'))
    return render_template('article/article.html', articleform=articleform)

@app.route('/article/delete/<int:article_id>')
@login_required
def article_delete(article_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    article = Article.query.get(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('articles'))

@app.route('/article/update/<int:article_id>',methods=['post','get'])
def article_update(article_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    article = Article.query.get(article_id)
    articleform = ArticleForm(data=request.form, obj=article)
    if articleform.validate_on_submit():
        articleform.populate_obj(article)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('articles'))
    return render_template('article/article_update.html', article=article, articleform=articleform )

@app.route('/articles/<int:page>')
@login_required
def articles(page):
    articles_list = Article.query.all()
    toto = Article.query.paginate(page=page, per_page=10)
    return render_template('article/articles.html',articles_list=articles_list, toto=toto)

# outils
@app.route('/outil', methods=['get','post'])
@login_required
def outil():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    outil = Outils()
    outilform = OutilForm(request.form)
    if outilform.validate_on_submit():
        outilform.populate_obj(outil)
        db.session.add(outil)
        db.session.commit()
        return redirect(url_for('outils'))
    return render_template('outil/outil.html', outilform=outilform)

@app.route('/outils')
@login_required
def outils():
    outils_list = Outils.query.all()
    return render_template('outil/outils.html', outils_list=outils_list)

@app.route('/outil/delete/<int:outil_id>')
@login_required
def outil_delete(outil_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    outil = Outils.query.get(outil_id)
    db.session.delete(outil)
    db.session.commit()
    flash('outil effacé')
    return redirect(url_for('outils'))

@app.route('/outil/update/<int:outil_id>', methods=['post','get'])
@login_required
def outil_update(outil_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    outil = Outils.query.get(outil_id)
    outilform = OutilForm(data=request.form, obj=outil)
    if outilform.validate_on_submit():
        outilform.populate_obj(outil)
        db.session.add(outil)
        db.session.commit()
        flash('Mise à jour faite')
        return redirect(url_for('outil_detail',outil_id=outil.id))
    return render_template('outil/outil_update.html', outilform=outilform, outil=outil)


@app.route('/outils/detail/<int:outil_id>')
@login_required
def outil_detail(outil_id):
    outil = Outils.query.get(outil_id)
    return render_template('outil/outil_detail.html',outil=outil)

@app.route('/materiel_add_outils/<int:materiel_id>', methods=['get','post'])
@login_required
def materiel_add_outil(materiel_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    composantform = Delete_composantForm(request.form)
    materiel = Materieltype.query.get(materiel_id)
    materiel_add_outilform = MaterieladdoutilForm(request.form)
    if materiel_add_outilform.validate_on_submit():
        liste = (materiel_add_outilform.outils.data)
        composants = [(data) for data in Outils.query.filter(Outils.id.in_(liste)).all()]
        for composant in composants:
            materiel.listeoutils.append(composant)
        db.session.add(materiel)
        db.session.commit()
        return redirect(url_for('materiel_detail', materiel_id=materiel_id))
    materiel_add_outilform.outils.data = [(data.id) for data in materiel.listeoutils]
    return render_template('materiel/materiel_add_outils.html', materiel_add_outilform=materiel_add_outilform, materiel=materiel, composantform=composantform)

@app.route('/materiel/add/gamme/<int:materiel_id>', methods=['post','get'])
@login_required
def materiel_add_gamme(materiel_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materieltype.query.get(materiel_id)
    materielform = MaterielForm(data=request.form, obj=materiel)

    if materielform.validate_on_submit():
        materiel.gammes = Gamme.query.filter(Gamme.id.in_(materielform.gammes.data)).all()
        #materielform.gammes.data = [1]
        #materielform.populate_obj(materiel)

        db.session.add(materiel)
        db.session.commit()
        return redirect(url_for('materiel_detail', materiel_id=materiel.id))
    else:
        print(materielform.errors)
    materielform.gammes.data = [(data.id) for data in materiel.gammes]
    return render_template('materiel/materiel_add_gamme.html', materiel=materiel, form=materielform)


@app.route('/materiel/composant/add/<int:materiel_id>',methods=['post','get'])
@login_required
def materiel_composant_add(materiel_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materieltype.query.get(materiel_id)
    materielform = Add_composantForm(data=request.form)
    liste = [(data.id) for data in materiel.sousensembles]

    materielform.sousensembles.choices = [(data.id, data.designation+' - '+data.info[:25]) for data in Sousensemble.query.filter(Sousensemble.id.notin_(liste)).all()]
    if materielform.validate_on_submit():
        composant = Sousensemble.query.get(int(materielform.sousensembles.data))
        materiel.sousensembles.append(composant)
        db.session.add(materiel)
        db.session.commit()
        return redirect(url_for('materiel_detail', materiel_id=materiel.id))
    else:
        print(materielform.errors)
    return  render_template('materiel/materiel_add_composant.html', materiel=materiel, materielform=materielform)

# gestion parc
@app.route('/materielinsite', methods=['post','get'])
@login_required
def materielinsite():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materiel()
    materielform = MaterielinsiteForm(request.form)
    if materielform.validate_on_submit():
        materielform.populate_obj(materiel)

        db.session.add(materiel)
        db.session.commit()
        return redirect(url_for('parcs'))
    return render_template('parc/materiel_insite.html', materielform=materielform)

@app.route('/materielinsite/update/<int:materielinsite_id>',methods=['post','get'])
@login_required
def materiel_insite_update(materielinsite_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel_insite = Materiel.query.get(materielinsite_id)
    materiel_insiteform = MaterielinsiteForm(data=request.form, obj=materiel_insite)
    if materiel_insiteform.validate_on_submit():
        materiel_insiteform.populate_obj(materiel_insite)
        db.session.add(materiel_insite)
        db.session.commit()
        return redirect(url_for('materiel_insite_detail',materielinsite_id=materiel_insite.id))
    return render_template('parc/materiel_insite_update.html', materiel_insiteform=materiel_insiteform, materiel_insite=materiel_insite)

@app.route('/materielinsite/detail/<int:materielinsite_id>')
@login_required
def materiel_insite_detail(materielinsite_id):
    materiel_insite = Materiel.query.get(materielinsite_id)
    return  render_template('parc/materiel_insite_detail.html', materiel_insite=materiel_insite)

@app.route('/materielinsite/delete/<int:materiel_id>')
@login_required
def materielinisite_delete(materiel_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    try:
        materiel = Materiel.query.get(materiel_id)
        db.session.delete(materiel)
        db.session.commit()
    except:
        flash('Le matérie ne peut être effacé, des écritures existent sur son compte')
    return redirect(url_for('parcs'))



# site
@app.route('/site', methods=['post','get'])
@login_required
def site():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    site= Site()
    siteform = SiteForm(request.form)
    if siteform.validate_on_submit():
        siteform.populate_obj(site)
        db.session.add(site)
        db.session.commit()
        return redirect(url_for('sites'))
    return render_template('site/site.html', siteform=siteform)

@app.route('/site/update/<int:site_id>', methods=['post','get'])
def site_update(site_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    site  = Site.query.get(site_id)
    siteform = SiteForm(data=request.form, obj=site)
    if siteform.validate_on_submit():
        siteform.populate_obj(site)
        db.session.add(site)
        db.session.commit()
        return redirect(url_for('sites'))
    return render_template('site/site_update.html', siteform=siteform, site=site)

@app.route('/sites')
@login_required
def sites():
    liste_sites = Site.query.all()
    return render_template('site/sites.html', liste_sites=liste_sites)

@app.route('/site/detail/<int:site_id>')
@login_required
def site_detail(site_id):
    site = Site.query.get(site_id)
    return render_template('site/site_detail.html', site=site)

@app.route('/parcs')
@app.route('/parcs/<int:page>')
@login_required
def parcs(page=1):
    parcs= Materiel.query.paginate(page=page,per_page=10)
    return render_template('parc/parcs.html', parcs=parcs)

# Gamme préventive
@app.route('/gamme', methods=['get','post'])
@login_required
def gamme():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    gamme= Gamme()
    gammeform = GammeForm(request.form)
    if gammeform.validate_on_submit():
        gammeform.populate_obj(gamme)
        liste = gammeform.materieltype.data
        materieltypes = [(data) for data in Materieltype.query.filter(Materieltype.id.in_(liste)).all()]
        for materieltype in materieltypes:
            materieltype.gammes.append(gamme)

        gamme.materieltype_gammes.append = materieltype
        db.session.add(gamme)
        db.session.commit()
        return redirect(url_for('gammes'))
    else:
        print(gammeform.errors)
    return render_template('gamme/gamme.html', gammeform=gammeform)

@app.route('/gammes')
@login_required
def gammes():
    gammes = Gamme.query.all()
    return render_template('gamme/gammes.html', gammes=gammes)

@app.route('/gamme/detail/<int:gamme_id>')
@login_required
def gamme_detail(gamme_id):
    gamme = Gamme.query.get(gamme_id)
    return render_template('gamme/gamme_detail.html', gamme=gamme)

@app.route('/gamme/update/<int:gamme_id>', methods=['post','get'])
@login_required
def gamme_update(gamme_id):
    gamme = Gamme.query.get(gamme_id)
    gammeform = GammeForm(data=request.form, obj=gamme)
    if gammeform.validate_on_submit():
        gammeform.populate_obj(gamme)
        # effacement des enregistrements précédents
        gamme.materieltype_gammes = []
        db.session.commit()


        liste = gammeform.materieltype.data
        materieltypes = [(data) for data in Materieltype.query.filter(Materieltype.id.in_(liste)).all()]
        for materieltype in materieltypes:
            materieltype.gammes.append(gamme)

        db.session.add(gamme)
        db.session.commit()
        return redirect(url_for('gamme_detail',gamme_id=gamme.id))

    gammeform.materieltype.data = [(data.id) for data in gamme.materieltype_gammes]
    return render_template('gamme/gamme_update.html', gammeform=gammeform, gamme=gamme)

@app.route('/gamme/delete/<int:gamme_id>')
@login_required
def gamme_delete(gamme_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    gamme = Gamme.query.get(gamme_id)
    db.session.delete(gamme)
    db.session.commit()
    return redirect(url_for('gammes'))

# maintenance
@app.route('/intervention', methods=['get','post'])
@login_required
def intervention():
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    intervention = Intervention()
    interventionform = InterventionForm(request.form)
    if interventionform.validate_on_submit():
        interventionform.populate_obj(intervention)
        intervention.close_date = datetime.datetime.utcnow()
        intervention.created_date = datetime.datetime.utcnow()
        intervention.date_intervention = datetime.datetime.utcnow()

        list_prim = [(interventionform.materiel.data)]
        list = Materiel.query.filter(Materiel.id.in_(list_prim)).all()

        materiels = [(data) for data in list]

        for materiel in materiels:
            materiel.interventions.append(intervention)

        db.session.add(intervention)
        db.session.commit()
        return redirect(url_for('interventions'))
    return render_template('intervention/intervention.html', interventionform=interventionform)

@app.route('/interventions/<int:page>')
@app.route('/interventions')
@login_required
def interventions(page=None):
    if ctrl_autorisation('operateur'):
        interventions = Intervention.query.filter(Intervention.operateur_intervention==current_user).paginate(page=page, per_page=10)
    else:
        interventions = Intervention.query.paginate(page=page, per_page=10)
    return render_template('intervention/interventions.html', interventions=interventions)

@app.route('/intervention/detail/<int:intervention_id>')
@login_required
def intervention_detail(intervention_id):
    intervention = Intervention.query.get(intervention_id)
    return render_template('intervention/intervention_detail.html',intervention=intervention)

@app.route('/intervention/update/<int:intervention_id>', methods=['get','post'])
@login_required
def intervention_update(intervention_id):
    intervention = Intervention.query.get(intervention_id)
    print(intervention.operateur_intervention.user,current_user)
    if (ctrl_autorisation('operateur') and  intervention.operateur_intervention.user == current_user) or ctrl_autorisation('agent'):

        interventionform = InterventionForm(data=request.form, obj=intervention)
        if interventionform.validate_on_submit():
            interventionform.populate_obj(intervention)

            db.session.add(intervention)
            db.session.commit()
            return redirect(url_for('intervention_detail', intervention_id=intervention_id))
        else:
            print(interventionform.errors)
        return render_template('intervention/intervention_update.html', intervention=intervention, interventionform=interventionform)

    else:
        return redirect(url_for('index'))

@app.route('/intervention/delete/<int:intervention_id>')
@login_required
def intervention_delete(intervention_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    intervention = Intervention.query.get(intervention_id)
    if intervention.status != None:
        flash(message='Suppression impossible: le bon d\'intervention a été déjà saisi')
    else:
        flash(message='Suppression faite')
        db.session.delete(intervention)
        db.session.commit()
    return redirect(url_for('interventions'))

@app.route('/intervention_demande/<int:ordre_id>', methods=['get','post'])
@login_required
def intervention_demande(ordre_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    ordre = Ordre_maintenance.query.get(ordre_id)

    intervention= Intervention()
    interventionform = InterventionForm(data=request.form)
    docuform = Document_materieltypeForm(request.form)
    if interventionform.validate_on_submit():
        intervention.om_id =ordre.id
        intervention.operateur_id = interventionform.operateur_id.data
        intervention.date_intervention = interventionform.date_intervention.data
        intervention.materiel.append(ordre.materiel_om)
        db.session.add(intervention)
        db.session.commit()
        if 'path' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['path']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename != '':
            if file and allowed_file(file.filename):
                document = Document_inter()
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                document.path = filename
                document.descriptif = docuform.description.data
                document.nom = docuform.nom.data
                document.intervention_id = intervention.id
                db.session.add(document)

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.commit()
        return redirect(url_for('ordres_maintenance',page=1))
    else:
        print(interventionform.errors)
    return render_template('intervention/intervention_create.html',interventionform=interventionform, docuform=docuform, ordre=ordre)

# ordre de maintenance
@app.route('/ordre_maintenance/<int:materiel_id>', methods=['post','get'])
@app.route('/ordre_maintenance', methods=['post','get'])
@login_required
def ordre_maintenance(materiel_id=None):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    ordre_maintenance_inst = Ordre_maintenance()
    ordre_maintenance_inst.origine_om = 'curatif'
    materiel = None
    if materiel_id:
        ordre_maintenance_inst.materiel_id = materiel_id
        materiel = Materiel.query.get(materiel_id)

    ordre_maintenanceform = Ordre_maintenanceForm(data=request.form, obj=ordre_maintenance_inst)


    docuform = Document_omForm(data=request.form)
    if ordre_maintenanceform.validate_on_submit():
        ordre_maintenanceform.om_status = 'declenche'
        ordre_maintenanceform.populate_obj(ordre_maintenance_inst)

        db.session.add(ordre_maintenance_inst)
        db.session.commit()

        if 'path' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['path']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename != '':
            if file and allowed_file(file.filename):
                document = Document_om()
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                document.path = filename
                document.descriptif = docuform.description.data
                document.nom = docuform.nom.data
                document.om_id = ordre_maintenance_inst.id
                db.session.add(document)
                db.session.commit()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        if ordre_maintenance_inst.origine_om=='preventif':
            return redirect(url_for('ordre_maintenance_complete_form',ordre_id=ordre_maintenance_inst.id))
        return redirect(url_for('intervention_demande', ordre_id=ordre_maintenance_inst.id))
    else:
        print(ordre_maintenanceform.errors)

    return render_template('ordre_maintenance/ordre_maintenance.html',materiel=materiel, docuform=docuform, ordre_maintenanceform=ordre_maintenanceform)

@app.route('/ordre_maintenance_complete_form/<int:ordre_id>', methods=['post','get'])
@login_required
def ordre_maintenance_complete_form(ordre_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    ordre = Ordre_maintenance.query.get(ordre_id)
    ordre_form = Ordre_updateForm(data=request.form, obj=ordre)
    ordre_form.gamme_id.choices = [(data.id, data.nom+'_'+data.categorie) for data in ordre.materiel_om.materiel_type_materiels.gammes]
    if ordre_form.validate_on_submit():
        ordre_form.populate_obj(ordre)
        db.session.add(ordre)
        db.session.commit()
        return redirect(url_for('ordres_maintenance',page=1))
    return  render_template('ordre_maintenance/ordre_maintenance_complete_form.html', ordreform=ordre_form)

@app.route('/ordres_maintenance/<int:page>')
@login_required
def ordres_maintenance(page):
    filterform = FilterForm()
    # gestion filtre
    if request.args.get('om_status'):
        filterform.om_status.data = request.args.get('om_status')
    if request.args.get('om_origine'):
        filterform.om_origine.data = request.args.get('om_origine')
    if request.args.get('om_si'):
        filterform.om_si.data = request.args.get('om_si')

    if request.args.get('date_depart'):
        filterform.date_depart.data = datetime.datetime.strptime(request.args.get('date_depart'),'%d-%m-%Y')
    if request.args.get('date_fin'):
        filterform.date_fin.data = datetime.datetime.strptime(request.args.get('date_fin'),'%d-%m-%Y')

    data = list()

    if filterform.om_status.data=='true':
        data.append(Ordre_maintenance.om_status == 'clos')
    elif filterform.om_status.data=='false':
        data.append(Ordre_maintenance.om_status != 'clos')

    if filterform.om_origine.data=='true':
        data.append(Ordre_maintenance.origine_om=='preventif')
    elif filterform.om_origine.data=='false':
        data.append(Ordre_maintenance.origine_om!='preventif')

    if filterform.om_si.data=='true':
        data.append(Ordre_maintenance.interventions==None)
    elif filterform.om_si.data=='false':
        data.append(Ordre_maintenance.interventions!=None)

    if filterform.date_depart.data:
        try:
            data.append(Ordre_maintenance.date_debut>=filterform.date_depart.data)
        except:
            pass

    if filterform.date_fin.data:
        try:
            data.append(Ordre_maintenance.date_fin<=filterform.date_fin.data)
        except:
            pass

    if len(data)>0:
        toto = Ordre_maintenance.query.filter(*data).order_by((Ordre_maintenance.date_debut).desc()).paginate(page=page,per_page=25)
    else:
        toto = Ordre_maintenance.query.order_by((Ordre_maintenance.date_debut).desc()).paginate(page=page,per_page=25)
    return render_template('ordre_maintenance/ordres_maintenance.html', toto=toto, ordres=toto, filterform=filterform )

@app.route('/ordre_maintenance/update/<int:ordre_id>', methods=['post','get'])
@login_required
def ordre_maintenance_update(ordre_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    ordre = Ordre_maintenance.query.get(ordre_id)
    ordreform = Ordre_maintenanceForm(data=request.form, obj=ordre)
    if ordreform.validate_on_submit():
        ordreform.populate_obj(ordre)
        if ordre.origine_om != 'preventif':
            ordre.gamme_id = ''
        db.session.add(ordre)
        db.session.commit()
        if ordre.origine_om=='preventif':
            return redirect(url_for('ordre_maintenance_complete_form',ordre_id=ordre_id))
        return redirect(url_for('ordre_maintenance_detail', ordre_id=ordre_id))
    else:
        print(ordreform.errors)
    return render_template('ordre_maintenance/ordre_maintenance_update.html', ordre_maintenanceform=ordreform, ordre=ordre)

@app.route('/ordre_maintenance/detail/<int:ordre_id>', methods=['get','post'])
@login_required
def ordre_maintenance_detail(ordre_id):
    ordre = Ordre_maintenance.query.get(ordre_id)
    return render_template('ordre_maintenance/ordre_maintenance_detail.html', ordre=ordre)

@app.route('/ordre_maintenance/delete/<int:ordre_id>')
@login_required
def ordre_maintenance_delete(ordre_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    try:
        ordre = Ordre_maintenance.query.get(ordre_id)
        db.session.delete(ordre)
        db.session.commit()
    except:
        flash(message='Suppression impossible: des interventions sont rattachées à l\'ordre de maintenance')
    return redirect(url_for('ordres_maintenance',page=1))

@app.route('/ordre_maintenance/close/<int:ordre_id>', methods=['get','post'])
@login_required
def ordre_maintenance_close(ordre_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    ordre = Ordre_maintenance.query.get(ordre_id)
    if not ordre.date_cloture:
        ordre.date_cloture = datetime.datetime.utcnow()

    ordreform = Ordre_maintenanceForm(data=request.form, obj=ordre)

    if ordreform.validate_on_submit():
        ordreform.populate_obj(ordre)
        db.session.add(ordre)
        db.session.commit()
        return redirect(url_for('ordre_maintenance_detail', ordre_id=ordre_id))
    else:
        print(ordreform.errors)
    return render_template('ordre_maintenance/ordre_maintenance_close.html', ordre=ordre, ordreform=ordreform)

# ressource humaine
@app.route('/operateur', methods=['get','post'])
@login_required
def operateur():
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    operateur_add = Operateur()
    operateurform = OperateurForm()
    if operateurform.validate_on_submit():
        #operateur_add.user_id = operateurform.user_id.data
        operateurform.populate_obj(operateur_add)
        db.session.add(operateur_add)
        db.session.commit()
        return redirect(url_for('operateurs'))
    return  render_template('operateur/operateur.html', operateurform=operateurform)

@app.route('/operateurs')
@login_required
def operateurs():
    operateurs_list = Operateur.query.all()
    return render_template('operateur/operateurs.html', operateurs=operateurs_list)

@app.route('/operateur/detail/<int:operateur_id>')
@login_required
def operateur_detail(operateur_id):
    operateur = Operateur.query.get(operateur_id)
    return render_template('operateur/operateur_detail.html', operateur=operateur)

@app.route('/operateur/delete/<int:operateur_id>')
@login_required
def operateur_delete(operateur_id):
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    operateur = Operateur.query.get(operateur_id)
    db.session.delete(operateur)
    db.session.commit()
    return redirect(url_for('operateurs'))

@app.route('/operateur/update/<int:operateur_id>', methods=['get','post'])
@login_required
def operateur_update(operateur_id):
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    operateur = Operateur.query.get(operateur_id)
    operateurform = OperateurForm(data=request.form, obj=operateur)

    if operateurform.validate_on_submit():
        operateurform.populate_obj(operateur)
        db.session.add(operateur)
        db.session.commit()
        return redirect(url_for('operateur_detail', operateur_id=operateur_id))
    return render_template('operateur/operateur_update.html', operateur=operateur, operateurform=operateurform)

# échances
@app.route('/echeance')
@login_required
def echeance():
    #intervention = Intervention.query.filter_by().all()

    om = Ordre_maintenance.query.filter(Ordre_maintenance.origine_om=='preventif').all()

    # liste des materiels avec leur gamme faites
    gamme_fait = dict()
    for diti in om:

        #print(diti.materiel_om, diti.date_cloture, diti.gamme_om)
        try:
            print(gamme_fait[diti.materiel_om])
        except:
            gamme_fait[diti.materiel_om]=list()
        gamme_fait[diti.materiel_om].append(diti.gamme_om)


    #print(gamme_fait)

    # liste des materiels avec leur gamme prevu
    gamme_prevu = dict()
    materiel_gamme = Materiel.query.all()
    for data in materiel_gamme:
        gamme_prevu[data] = data.materiel_type_materiels.gammes



    # tri des tableaux

    #print('prevu',gamme_prevu)
    #print('fait',gamme_fait)
    tab = dict()
    for key, value in gamme_prevu.items():

        try:
            print(key, value, '###########', gamme_fait[key])
            for data in value:

                if data in gamme_fait[key]:
                    #print(gamme_fait[key])
                    #print(value)
                    print(('match'))
                else:
                    print('not match')
                    if key not in tab:
                        tab[key] = []
                    tab[key].append(data)

        except:
            print('pass',key, value)
            tab[key]=value
            pass
    print(tab)
    return render_template('echeance/echeance.html', echeance=tab)

@app.route('/om_create/<int:materiel_id>/<int:gamme_id>', methods=['get','post'])
@login_required
def om_create(materiel_id,gamme_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel = Materiel.query.get(materiel_id)
    ordre_maintenance = Ordre_maintenance()
    gamme = Gamme.query.get(gamme_id)

    ordre_maintenance.gamme_id = gamme.id
    ordre_maintenance.materiel_id = materiel.id
    ordre_maintenance.cause = 'gamme'
    ordre_maintenance.origine_om = 'preventif'
    ordre_maintenanceform = Ordre_maintenance_createForm(data=request.form)
    if ordre_maintenanceform.validate_on_submit():
        ordre_maintenanceform.populate_obj(ordre_maintenance)
        db.session.add(ordre_maintenance)
        db.session.commit()
        return redirect(url_for('ordres_maintenance',page=1))
    else:
        print(ordre_maintenanceform.errors)
    return  render_template('ordre_maintenance/ordre_maintenance_create.html', ordre_maintenanceform=ordre_maintenanceform ,materiel=materiel, gamme=gamme)

# gestion fichier
@app.route('/document_materieltype/<int:materieltype_id>', methods=['get','post'])
@login_required
def document_materiel(materieltype_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    materiel_type = Materieltype.query.get(materieltype_id)

    docuform = Document_materieltypeForm(request.form)
    if docuform.validate_on_submit():
        # check if the post request has the file part
        if 'path' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['path']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            document = Document_materieltype()
            filename = secure_filename(file.filename)

            document.path = filename
            document.descriptif = docuform.description.data
            document.nom = docuform.nom.data
            document.materieltype_id = materiel_type.id
            db.session.add(document)
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('materiel_detail', materiel_id=materiel_type.id, name=filename))
    return render_template('document/document.html', documentform=docuform, materiel_type=materiel_type)

@app.route('/document_om/<int:ordre_id>', methods=['post','get'])
@login_required
def document_om(ordre_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    documentform = Document_omForm(request.form)
    ordre = Ordre_maintenance.query.get(ordre_id)

    if documentform.validate_on_submit():

        if 'path' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['path']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file.filename != '':
            if file and allowed_file(file.filename):
                document = Document_om()
                filename = secure_filename(file.filename).split('.')
                filename.reverse()
                extension = filename[0]
                name = str(time.time()).split('.')[0]
                filename = name+'.'+extension
                document.path = filename
                document.descriptif = documentform.description.data
                document.nom = documentform.nom.data
                document.om_id = ordre_id
                db.session.add(document)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.session.commit()
                return redirect(url_for('ordre_maintenance_detail', ordre_id=ordre_id))
            flash('extension du fichier incorrect')
    print(documentform.errors)
    return render_template('document/document_om.html', ordre=ordre, documentform=documentform)

@app.route('/uploads/<name>')
@login_required
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/file/om/delete/<int:file_id>')
@login_required
def delete_om_file(file_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    file = Document_om.query.get(file_id)
    ordre_id = file.om_id
    filepath = os.path.join(DIR_ROOT,os.path.join(app.config['UPLOAD_FOLDER'], file.path))
    os.remove(filepath)
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('ordre_maintenance_detail', ordre_id=ordre_id))

@app.route('/file/materiel/delete/<int:file_id>')
@login_required
def delete_materiel_file(file_id):
    if not ctrl_autorisation('agent'):
        return redirect(url_for('index'))
    file = Document_materieltype.query.get(file_id)
    materiel_id = file.materieltype_id
    filepath = os.path.join(DIR_ROOT,os.path.join(app.config['UPLOAD_FOLDER'], file.path))
    os.remove(filepath)
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('materiel_detail', materiel_id=materiel_id))

# ########### Importation de donnée
@app.route('/importation/articles',methods=['post','get'])
@login_required
def importation_article():
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    form = Import_dataForm(request.form)
    if form.validate_on_submit():
        if 'fichier' in request.files:
            file = request.files['fichier']
            data = str(file.read()).split("\\n")
            for line in data:
                if len(line.split(";")[0])>0:
                    tab = line.split(';')
                    if len(tab)>2:
                        article = Article()
                        article.designation = tab[0]
                        article.reference = tab[1]
                        db.session.add(article)

            db.session.commit()
        else:
            print('pas de fichier',)
    else:
        print(form.errors)
    return render_template('importation/import_article.html', form=form)

@app.route('/importation/materiels',methods=['post','get'])
@login_required
def importation_materiel():
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    form = Import_dataForm(request.form)
    if form.validate_on_submit():
        if 'fichier' in request.files:
            file = request.files['fichier']
            data = str(file.read()).split("\\n")
            for line in data:
                if len(line.split(";")[0])>0:
                    tab = line.split(';')
                    if len(tab)>2:
                        materiel = Materieltype()
                        materiel.marque = tab[0]
                        materiel.modele = tab[1]
                        materiel.categorie = tab[2]
                        materiel.info = tab[3]
                        materiel.author = current_user.id
                        db.session.add(materiel)

            db.session.commit()
        else:
            print('pas de fichier',)
    else:
        print(form.errors)
    return render_template('importation/import_materiel.html', form=form)

@app.route('/importation/composants',methods=['post','get'])
@login_required
def importation_composant():
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    form = Import_dataForm(request.form)
    if form.validate_on_submit():
        if 'fichier' in request.files:
            file = request.files['fichier']
            data = str(file.read()).split("\\n")
            for line in data:
                if len(line.split(";")[0])>0:
                    tab = line.split(';')
                    if len(tab)>1:
                        composant = Sousensemble()
                        composant.designation = tab[0]
                        composant.info = tab[1]
                        db.session.add(composant)

            db.session.commit()
        else:
            print('pas de fichier',)
    else:
        print(form.errors)
    return render_template('importation/import_composant.html', form=form)

@app.route('/importation/outils',methods=['post','get'])
@login_required
def importation_outil():
    if not ctrl_autorisation('admin'):
        return redirect(url_for('index'))
    form = Import_dataForm(request.form)
    if form.validate_on_submit():
        if 'fichier' in request.files:
            file = request.files['fichier']
            data = str(file.read()).split("\\n")
            for line in data:
                if len(line.split(";")[0])>0:
                    tab = line.split(';')
                    if len(tab)>1:
                        outil = Outils()
                        outil.designation = tab[0]
                        outil.reference = tab[1]
                        outil.prix = 0.00
                        outil.info = tab[3]
                        db.session.add(outil)

            db.session.commit()
        else:
            print('pas de fichier',)
    else:
        print(form.errors)
    return render_template('importation/import_outils.html', form=form)

@app.route('/api/materiel_type/get', methods=['POST'])
@login_required
def api_get_matereil_type():
    if 'data' in request.form:
        data = request.form.get('data')
        response = Materieltype.query.filter(Materieltype.marque.startswith(data) | Materieltype.modele.startswith(data))
        tab= list()
        for data in response:
            tab.append(data.to_json())
        return jsonify(tab)
    return 'false'

@app.route('/api/materiel_type/categorie/get', methods=['POST'])
@login_required
def api_get_matereil_type_categorie():
    if 'data' in request.form:
        data = request.form.get('data')
        response = Materieltype.query.filter(Materieltype.categorie.startswith(data))
        tab= list()
        for data in response:
            tab.append(data.to_json())
        return jsonify(tab)
    return 'false'

@app.route('/api/materiel_type/categories')
@login_required
def api_get_matereil_type_categories():
    categories = [(data.categorie) for data in Materieltype.query.all()]
    return jsonify(list(set(categories)))

@app.route('/api/materiel_type/marques')
@login_required
def api_get_matereil_type_marques():
    marques = [(data.marque) for data in Materieltype.query.all()]
    return jsonify(list(set(marques)))

@app.route('/api/materiel/get', methods=['POST'])
@login_required
def api_get_matereil():
    if 'data' in request.form:
        data = request.form.get('data')
        materiel_type = [(data.id) for data in Materieltype.query.filter(Materieltype.marque.startswith(data)).all()]
        client = [(data.id) for data in Site.query.filter(Site.nom.like('%'+data+'%') | Site.ville.startswith(data))]
        response = Materiel.query.filter(Materiel.materieltype_id.in_(materiel_type)| Materiel.numero_serie.startswith(data) | Materiel.site_id.in_(client)).all()
        #response = Materiel.query.filter(Materiel.materiel_type_materiels.has(Materieltype.marque.startswith(data)))
        tab= list()
        for data in response:
            tab.append(data.to_json())

        return jsonify(tab)
    return 'false'

if __name__ == '__main__':
    role = Role()
    role.start()
    app.debug = True
    db.create_all()
    app.run()
