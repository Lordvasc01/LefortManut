import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField, SelectMultipleField, DecimalField,\
    IntegerField, FieldList, FormField, BooleanField, TextAreaField, DateTimeField, DateField, FileField, Form, widgets, RadioField


import sys, inspect
from models import Sousensemble, Outils, Site, Materieltype, Materiel, Gamme, Intervention, Ordre_maintenance,\
    Operateur, Article, Document_materieltype, Role, User

class UserForm(FlaskForm):
    try:
        choices = [(data.id,data.role) for data in Role.query.all()]
    except:
        choices = []
    username = StringField()
    first_name = StringField()
    last_name = StringField()
    email = StringField()
    roles = SelectMultipleField(coerce=int, validate_choice=False, choices=choices)
    password = PasswordField(validators=[
        validators.EqualTo(
            "verif_password",
            message="Les mots de passe ne correspondent pas"
            )
        ])
    verif_password = PasswordField(label="Confirm password")


class LoginForm(FlaskForm):
    username = StringField()
    password = PasswordField()


class EditUserForm(FlaskForm):
    try:
        choices = [(data.id, data.role) for data in Role.query.all()]
    except:
        choices =[]
    first_name = StringField()
    last_name = StringField()
    email = StringField()
    roles = SelectMultipleField(coerce=int, validate_choice=False,
                                choices=choices)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class CheckboxField(RadioField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()

class MaterielForm(FlaskForm):
    marque = StringField(render_kw={'class':'form-control', 'placeholder':'Marque','autocomplete':'off'})
    modele = StringField(render_kw={'class':'form-control', 'placeholder':'Modèle'})
    categorie = StringField(render_kw={'class':'form-control', 'placeholder':'Catégorie', 'autocomplete':'off'})
    sousensembles = MultiCheckboxField(coerce=int, validate_choice=False, render_kw={'class':'form-check mx-1',})
    info =TextAreaField(render_kw={'cols':40, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    gammes = MultiCheckboxField(coerce=int, validate_choice=False)

    def __init__(self, *args, **kwargs):
        super(MaterielForm, self).__init__(*args, **kwargs)
        self.sousensembles.choices = [(data.id,data.designation) for data in Sousensemble.query.all()]
        self.gammes.choices = [(data.id, data.nom+' # '+data.categorie) for data in Gamme.query.all()]


class SousensembleForm(FlaskForm):
    designation = StringField(render_kw={'class':'form-control', 'placeholder':'Désignation'})
    info = TextAreaField(render_kw={'class':'form-control', 'placeholder':'Info'})


class ArticleForm(FlaskForm):
    designation = StringField(render_kw={'class':'form-control','placeholder':'Désignation'})
    reference = StringField(render_kw={'class':'form-control','placeholder':'Référence'})
    prix = DecimalField(render_kw={'class':'form-control'}, default=0.00)
    fournisseur = StringField(render_kw={'class':'form-control', 'placeholder':'Fournisseur'})
    info = TextAreaField(render_kw={'class':'form-control', 'placeholder':'Info'})


class OutilForm(FlaskForm):
    designation = StringField(render_kw={'class':'form-control','placeholder':'Désignation'})
    reference = StringField(render_kw={'class':'form-control','placeholder':'Référence'}, validators=[validators.input_required()])
    prix = DecimalField(render_kw={'class':'form-control'}, default=0.00)
    fournisseur = StringField(render_kw={'class':'form-control', 'placeholder':'Fournisseur'})
    info = TextAreaField(render_kw={'class':'form-control', 'placeholder':'Info'})


class MaterieladdoutilForm(FlaskForm):
    outils = MultiCheckboxField(coerce=int, validate_choice=False)

    def __init__(self, *args, **kwargs):
        super(MaterieladdoutilForm,self).__init__(*args, **kwargs)
        self.outils.choices = [(data.id,data.designation) for data in Outils.query.all()]


class SiteForm(FlaskForm):
    nom = StringField(render_kw={'class':'form-control','placeholder':'Nom'})
    ville = StringField(render_kw={'class':'form-control','placeholder':'Ville'})
    info = TextAreaField(render_kw={'cols':40, 'rows':3, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})


class MaterielinsiteForm(FlaskForm):
    numero_serie = StringField(render_kw={'class':'form-control'})
    site_id = SelectField(coerce=int, validate_choice=False,render_kw={'class':'form-select'})
    materieltype_id = CheckboxField(coerce=int, validate_choice=False, render_kw={'style':'display:none'})
    info = TextAreaField(render_kw={'cols':40, 'rows':3, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})

    def __init__(self, *args, **kwargs):
        super(MaterielinsiteForm, self).__init__(*args, **kwargs)
        self.site_id.choices = [(data.id, data.nom+'-'+data.ville) for data in Site.query.all()]
        self.materieltype_id.choices = [(data.id, data.marque+'-'+data.modele) for data in Materieltype.query.all()]


class GammeForm(FlaskForm):
    choices = [('mecanique', 'Mecanique'),('electrique', 'Electrique'),('hydraulique', 'Hydaulique')]
    nom = StringField(render_kw={'class':'form-control','placeholder':'Nom'})
    categorie = SelectField(choices=choices, render_kw={'class':'form-select'})
    descriptif = TextAreaField(render_kw={'cols':40, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    periodicite = IntegerField('Périodicité', render_kw={'class':'form-control','placeholder':'Périodicité'})
    cout = DecimalField(render_kw={'class':'form-control','placeholder':'Cout'}, default=0.00)
    unite = SelectField(choices=[('heures','Heures'),('copies','Copies'),('km','Kilomètre'),('jours','Jours')], render_kw={'class':'form-select'})

    materieltype = MultiCheckboxField('Matériel', coerce=int, validate_choice=False, render_kw={'class':'form-control'})

    def __init__(self, *args, **kwargs):
        super(GammeForm, self).__init__(*args, **kwargs)
        self.materieltype.choices = [ (data.id, data.marque+'-'+data.modele) for data in Materieltype.query.all()]


class InterventionForm(FlaskForm):
    choices = [('declenche','Déclenché'), ('en_cours','En cours'),('termine','Terminé')]
    om_id = SelectField(validate_choice=False, render_kw={'class':'form-select'})
    action = TextAreaField('Travaux réalisés',render_kw={'cols':40, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%','placeholder':'Travaux réalisés'})
    status = SelectField(choices=choices, render_kw={'class':'form-select'})
    article_id = SelectField(validate_choice=False, render_kw={'class':'form-select'})
    date_intervention = DateField( render_kw={'class':'form-control','required':''},format='%d-%m-%Y', default=None )
    heure_debut = DateTimeField(render_kw={'class':'form-control'},format='%d-%m-%Y %H:%M')
    heure_fin = DateTimeField(render_kw={'class':'form-control'},format='%d-%m-%Y %H:%M')
    status = SelectField(choices=[('a_suivre','A suivre'),('termine', 'Terminé')], validate_choice=False, render_kw={'class':'form-select'})
    operateur_id = SelectField(validate_choice=False,render_kw={'class':'form-select'})

    def __init__(self, *args, **kwargs):
        super(InterventionForm, self).__init__(*args, **kwargs)
        self.om_id.choices = [(data.id, data.id) for data in Ordre_maintenance.query.all()]
        self.article_id.choices = [(data.id, data.id) for data in Article.query.all()]
        self.operateur_id.choices = [(data.id, data.user.first_name+' '+data.user.last_name) for data in Operateur.query.all()if data.user != None]



class Ordre_updateForm(FlaskForm):
    gamme_id = SelectField()


class Ordre_maintenanceForm(FlaskForm):
    class Meta:
        locales = ['fr_FR', 'fr']

        def get_translations(self, form):
            return super(FlaskForm.Meta, self).get_translations(form)


    origine_om = SelectField(render_kw={'class':'form-select'},
                             choices=[('preventif','Préventif'), ('curatif','Dépannage')], default='curatif')  # gamme panne
    materiel_id = SelectField(render_kw={'class':'d-none'})
    date_debut = DateTimeField(render_kw={'class':'form-control'},format='%d-%m-%Y %H:%M')
    date_cloture = DateTimeField(render_kw={'class':'form-control'},format='%d-%m-%Y %H:%M')
    om_status = SelectField(render_kw={'class':'form-select'},
                            choices=[('declenche','Déclenché'),('suivre','A suivre'),('clos','Clos')], validate_choice=False)
    objet = TextAreaField(render_kw={'cols':40, 'rows':5, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    cause = SelectField(render_kw={'class':'form-select'},
                        choices=[('a_definir','A définir'),('gamme','Préventif'),('client','Client'),('maintenance','Maintenance à optimiser')], validate_choice=False)  # cause client/ mauvaise maintenance
    amelioration = TextAreaField(render_kw={'cols':40, 'rows':3, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})  # porposition d'amélioration


    def __init__(self, *args, **kwargs):
        super(Ordre_maintenanceForm, self).__init__(*args, **kwargs)
        self.materiel_id.choices = [(data.id, data.materiel_type_materiels.marque+'-'+data.materiel_type_materiels.modele+' ** N° série:'+data.numero_serie) for data in Materiel.query.all()]
        #self.operateur_id.choices = [(data.id, data.nom) for data in Operateur.query.all()]
        #self.gamme_id.choices = [(data.id, data.nom) for data in Gamme.query.all()]
        self.date_debut.data = datetime.datetime.today()


class Ordre_maintenance_createForm(FlaskForm):
    class Meta:
        locales = ['fr_FR', 'fr']

        def get_translations(self, form):
            return super(FlaskForm.Meta, self).get_translations(form)


    date_debut = DateTimeField(render_kw={'class':"form-control"})
    #date_cloture = DateTimeField()
    #om_status = SelectField(choices=[('declenche','Déclenché'),('suive','A suivre'),('clos','Clos')])
    objet = TextAreaField(render_kw={'cols':40, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    #amelioration = TextAreaField()  # porposition d'amélioration
    #document = FileField(render_kw={'class':"form-control"})

    def __init__(self, *args, **kwargs):
        super(Ordre_maintenance_createForm, self).__init__(*args, **kwargs)

        self.date_debut.data = datetime.datetime.today()


class OperateurForm(FlaskForm):
    choices = [(data.id, data.first_name+' '+data.last_name) for data in User.query.all()]
    user_id = SelectField(choices=choices,coerce=int, validate_choice=False)
    matricule = StringField()
    nom = StringField()
    prenom = StringField()
    metier = SelectField(choices=[('mecanicien','Mécanicien'),('electricien','Electricien'),
                                  ('hydraulicien','Hydraylicien'),('electromecano','Electro-mécanicien')])


class Document_materieltypeForm(FlaskForm):
    nom = StringField(render_kw={'class':'form-control'})
    description = TextAreaField(render_kw={'cols':40, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    path = FileField(render_kw={'class':'form-control','style':'width:100%;'})


class Document_interForm(FlaskForm):
    nom = StringField(render_kw={'class':'form-control'})
    description = TextAreaField(render_kw={'cols':40, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    path = FileField(render_kw={'class':'form-control','style':'width:100%;'})


class Document_omForm(FlaskForm):
    nom = StringField(render_kw={'class':'form-control'})
    description = TextAreaField(render_kw={'cols':32, 'rows':7, 'style':'border: 1px solid #ced4da; border-radius:0.25rem;width:100%'})
    path = FileField(render_kw={'class':'form-control','style':'width:100%;'})

class Delete_composantForm(FlaskForm):
    composant_id = IntegerField(render_kw={'hidden':'hidden'})
    materiel_id = IntegerField(render_kw={'hidden':'hidden'})


class Add_composantForm(FlaskForm):
    sousensembles = SelectField()
    materiel_id = IntegerField()

    """def __init__(self, *args, **kwargs):
        super(Add_composantForm, self).__init__(*args, **kwargs)
        self.sousensembles.choices = [(data.id, data.designation) for data in Sousensemble.query.all()]"""


class Import_dataForm(FlaskForm):
    fichier = FileField()


class FilterForm(FlaskForm):
    om_status = CheckboxField('Status', choices=[('true','Clos'),('false','Ouvert'),('none','les 2')], default='false', render_kw={'style':'list-style:none'})
    om_origine = RadioField('Type d\'o.m', choices=[('true','Préventif'),('false','Curatif'),('none','Les 2')], default='none' , render_kw={'style':'list-style:none'})
    om_si = RadioField('Avec interventions', choices=[('false','Avec'),('true','Sans'),('all','Les 2')],default='all', render_kw={'style':'list-style:none'})
    date_depart = DateTimeField(render_kw={'class':'form-control'},format='%d-%m-%Y')
    date_fin = DateTimeField(render_kw={'class':'form-control'},format='%d-%m-%Y')
