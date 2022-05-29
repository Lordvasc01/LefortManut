from config import db
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin
import datetime


roles = db.Table('roles',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(200))
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))
    roles = db.relationship('Role', secondary=roles, lazy='subquery',
        backref=db.backref('roles', lazy=True))
    materiel_types = db.relationship('Materieltype', backref='user', lazy=True)
    operateur = db.relationship('Operateur', backref='user', lazy=True)

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(150))
    description = db.Column(db.String(250))

    def start(self):
        roles_data = [('operateur', 'Operateur de maintenance. Saisie uniquement les D.I'), ('admin', 'Administreur'), ('agent', 'Agent')]
        roles = [(data.role) for data in Role.query.all()]
        for role in roles_data:
            if role[0] not in roles:
                role_add = Role()
                role_add.role = role[0]
                role_add.description = role[1]
                db.session.add(role_add)
        db.session.commit()



sousensembles = db.Table('sousensembles',
                          db.Column('sousensemble_id', db.Integer, db.ForeignKey('sousensemble.id'), primary_key=True),
                          db.Column('materieltype_id', db.Integer, db.ForeignKey('materieltype.id'), primary_key=True)
                          )

listeoutils = db.Table('listeoutils',
                          db.Column('outils_id', db.Integer, db.ForeignKey('outils.id'), primary_key=True),
                          db.Column('materieltype_id', db.Integer, db.ForeignKey('materieltype.id'), primary_key=True)
                          )

gammes = db.Table('gammes',
                  db.Column('gamme_id', db.Integer, db.ForeignKey('gamme.id'), primary_key=True),
                  db.Column('materieltype_id', db.Integer, db.ForeignKey('materieltype.id'), primary_key=True)
                  )

interventions = db.Table('interventions',
                          db.Column('intervention_id', db.Integer, db.ForeignKey('intervention.id'), primary_key=True),
                          db.Column('materiel_id', db.Integer, db.ForeignKey('materiel.id'), primary_key=True)
                          )

class Materieltype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(200))
    modele = db.Column(db.String(200))
    categorie = db.Column(db.String(200))
    document = db.relationship('Document_materieltype', backref='documents', lazy=True)
    sousensembles = db.relationship('Sousensemble', secondary=sousensembles, lazy='subquery',
                                    backref=db.backref('materieltypes', lazy=True))

    info = db.Column(db.String(200))
    listeoutils = db.relationship('Outils', secondary=listeoutils, lazy='subquery',
                                    backref=db.backref('materieltypes_outils', lazy=True))

    materiels = db.relationship('Materiel', backref='materiel_type_materiels', lazy=True)

    gammes = db.relationship('Gamme', secondary=gammes, lazy='subquery',
                             backref=db.backref('materieltype_gammes', lazy=True))
    author = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    def to_json(self):
        return{
            'id':self.id,
            'marque':self.marque,
            'modele':self.modele,
            'categorie':self.categorie
        }


class Sousensemble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200))
    info = db.Column(db.String(200))


class Outils(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200))
    reference = db.Column(db.String(200))
    prix = db.Column(db.Float())
    fournisseur = db.Column(db.String(200))
    info = db.Column(db.String(200))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200))
    reference = db.Column(db.String(200))
    prix = db.Column(db.Float())
    fournisseur = db.Column(db.String(200))
    info = db.Column(db.String(200))


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    ville = db.Column(db.String(200))
    info = db.Column(db.String(200))
    materiels = db.relationship('Materiel', backref='site_materiels', lazy=True)


class Materiel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_serie = db.Column(db.String(200))
    site_id = db.Column(db.Integer,db.ForeignKey('site.id'), nullable=False, default='')
    materieltype_id = db.Column(db.Integer,db.ForeignKey('materieltype.id'), nullable=False, default='')
    info = db.Column(db.String(200))
    interventions = db.relationship('Intervention', secondary=interventions, lazy='subquery',
                                        backref=db.backref('materiel_interventions', lazy=True))
    oms = db.relationship('Ordre_maintenance', uselist=False, backref='materiel_om', lazy=True)

    def to_json(self):
        return{
            'id':self.id,
            'marque':self.materiel_type_materiels.marque,
            'modele':self.materiel_type_materiels.modele,
            'client':self.site_materiels.nom,
            'ville':self.site_materiels.ville,
            'categorie':self.materiel_type_materiels.categorie,
            'numero_serie':self.numero_serie,
        }


class Gamme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    categorie = db.Column(db.String(200))
    descriptif = db.Column(db.Text())
    periodicite  = db.Column(db.Integer, default=0)
    unite = db.Column(db.String())
    om = db.relationship('Ordre_maintenance', uselist=False, backref='gamme_om', lazy=True)
    cout = db.Column(db.Float(),default=0)

    def get_gamme(self):
        return self.query.get(1)


class Ordre_maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origine_om = db.Column(db.String(30)) # gamme panne
    materiel_id = db.Column(db.Integer, db.ForeignKey('materiel.id'), nullable=False)
    date_debut = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_cloture = db.Column(db.DateTime, nullable=True)
    om_status = db.Column(db.String(30), nullable=False, default='declenche')
    objet = db.Column(db.Text())
    cause = db.Column(db.String(30)) # cause client/ mauvaise maintenance
    amelioration = db.Column(db.Text()) # porposition d'amélioration
    gamme_id = db.Column(db.Integer, db.ForeignKey('gamme.id'), nullable=True, default=None)
    interventions = db.relationship('Intervention', backref='om_interventions', lazy=True)
    documents = db.relationship('Document_om', backref='om_documents', lazy=True)

    # retourne les interventions de moins de 6 mois
    def get_last(self):
        # voir comment traverser table
        #data = datetime.datetime(year=2021, month=7, day=12)
        return self.query.filter_by(materiel_id=self.materiel_id ).all()
        #return Intervention.query.filter(Intervention.heure_debut<data).first()


class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    om_id = db.Column(db.Integer, db.ForeignKey('ordre_maintenance.id'), nullable=False)
    date_intervention = db.Column(db.DateTime, default=None) # AA supprimer
    heure_debut = db.Column(db.DateTime, default=None)
    heure_fin = db.Column(db.DateTime, default=None)
    operateur_id = db.Column(db.Integer, db.ForeignKey('operateur.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    action = db.Column(db.Text())
    status = db.Column(db.String(200))
    document = db.relationship('Document_inter', backref='intervention_doc', lazy=True)
    materiel = db.relationship('Materiel', secondary=interventions, lazy='subquery',
                                    backref=db.backref('materiel_interventions', lazy=True))


class Operateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    metier = db.Column(db.String(200))
    #oms = db.relationship('Ordre_maintenance',backref='operateur_om', lazy=True)
    intervention = db.relationship('Intervention', backref='operateur_intervention', lazy=True)


class Document_materieltype(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    nom = db.Column(db.String(250))
    descriptif = db.Column(db.String(250))
    materieltype_id = db.Column(db.Integer, db.ForeignKey('materieltype.id'))
    path = db.Column(db.String(250))


class Document_inter(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    nom = db.Column(db.String(250))
    descriptif = db.Column(db.String(250))
    intervention_id = db.Column(db.Integer, db.ForeignKey('intervention.id'))
    path = db.Column(db.String(250))

class Document_om(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    nom = db.Column(db.String(250))
    descriptif = db.Column(db.String(250))
    om_id = db.Column(db.Integer, db.ForeignKey('ordre_maintenance.id'))
    path = db.Column(db.String(250))