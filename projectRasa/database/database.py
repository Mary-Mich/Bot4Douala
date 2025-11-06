import sqlite3
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class UniversityDatabase:
    def __init__(self, db_path: str = "university_douala.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Établir une connexion à la base de données"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialiser la structure de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table des établissements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etablissements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                contact TEXT,
                site_web TEXT
            )
        ''')

        # Table des filières
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filieres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type TEXT NOT NULL, -- 'professionnelle' ou 'classique'
                duree TEXT,
                description TEXT,
                debouches TEXT,
                conditions_admission TEXT,
                etablissement_id INTEGER,
                frais_inscription TEXT,
                FOREIGN KEY (etablissement_id) REFERENCES etablissements (id)
            )
        ''')

        # Table des domaines d'intérêt
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domaines_interet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                description TEXT
            )
        ''')

        # Table de liaison filières-domaines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filiere_domaines (
                filiere_id INTEGER,
                domaine_id INTEGER,
                PRIMARY KEY (filiere_id, domaine_id),
                FOREIGN KEY (filiere_id) REFERENCES filieres (id),
                FOREIGN KEY (domaine_id) REFERENCES domaines_interet (id)
            )
        ''')

        # Table du processus de préinscription
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processus_preinscription (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etape INTEGER NOT NULL,
                description TEXT NOT NULL,
                details TEXT,
                liens_utiles TEXT
            )
        ''')

        # Table des documents requis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents_requis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_document TEXT NOT NULL,
                description TEXT,
                obligatoire BOOLEAN DEFAULT 1
            )
        ''')

        # Table des dates importantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dates_importantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement TEXT NOT NULL,
                date_debut TEXT,
                date_fin TEXT,
                annee_academique TEXT
            )
        ''')

        conn.commit()
        self.populate_sample_data(conn)
        conn.close()

    def populate_sample_data(self, conn):
        """Peupler la base avec des données d'exemple pour l'Université de Douala"""
        cursor = conn.cursor()

        # Vérifier si les données existent déjà
        cursor.execute("SELECT COUNT(*) FROM etablissements")
        if cursor.fetchone()[0] > 0:
            return

        # Établissements
        etablissements = [
            ("Faculté des Sciences", "Faculté", 
             "Formation en sciences fondamentales et appliquées", 
             "+237 233 40 20 10", "http://sciences.univ-douala.cm"),
            ("Faculté de Médecine et des Sciences Biomédicales", "Faculté",
             "Formation des professionnels de santé",
             "+237 233 40 20 20", "http://medecine.univ-douala.cm"),
            ("Faculté des Sciences Juridiques et Politiques", "Faculté",
             "Formation en droit et sciences politiques",
             "+237 233 40 20 30", "http://droit.univ-douala.cm"),
            ("Institut Universitaire de Technologie (IUT)", "Institut",
             "Formations technologiques et professionnelles",
             "+237 233 40 20 40", "http://iut.univ-douala.cm"),
            ("École Normale Supérieure (ENS)", "École",
             "Formation des enseignants",
             "+237 233 40 20 50", "http://ens.univ-douala.cm")
        ]

        cursor.executemany(
            "INSERT INTO etablissements (nom, type, description, contact, site_web) VALUES (?, ?, ?, ?, ?)",
            etablissements
        )

        # Domaines d'intérêt
        domaines = [
            ("Sciences et Technologies", "Domaines scientifiques et technologiques"),
            ("Santé et Médecine", "Domaines de la santé et médecine"),
            ("Droit et Sciences Politiques", "Domaines juridiques et politiques"),
            ("Sciences Économiques", "Domaines économiques et de gestion"),
            ("Lettres et Sciences Humaines", "Domaines littéraires et humaines"),
            ("Éducation et Formation", "Domaines de l'éducation et formation")
        ]

        cursor.executemany(
            "INSERT INTO domaines_interet (nom, description) VALUES (?, ?)",
            domaines
        )

        # Filieres pour la Faculté des Sciences (professionnelles et classiques)
        filieres_sciences = [
            # Filieres classiques
            ("Licence en Mathématiques", "classique", "3 ans", 
             "Formation fondamentale en mathématiques pures et appliquées",
             "Enseignement, Recherche, Industries", "Baccalauréat C ou D", 1, "50,000 FCFA"),
            
            ("Licence en Physique", "classique", "3 ans",
             "Formation en physique fondamentale et expérimentale",
             "Enseignement, Recherche, Laboratoires", "Baccalauréat C ou D", 1, "50,000 FCFA"),
            
            ("Licence en Chimie", "classique", "3 ans",
             "Formation en chimie analytique et organique",
             "Industries chimiques, Laboratoires, Recherche", "Baccalauréat C ou D", 1, "50,000 FCFA"),
            
            # Filieres professionnelles
            ("Licence Professionnelle en Informatique", "professionnelle", "3 ans",
             "Formation pratique en développement logiciel et réseaux",
             "Développeur, Administrateur réseaux, Analyste", "Baccalauréat C, D ou E", 1, "75,000 FCFA"),
            
            ("Licence Professionnelle en Électronique", "professionnelle", "3 ans",
             "Formation en électronique et télécommunications",
             "Technicien supérieur, Maintenance électronique", "Baccalauréat C, D ou E", 1, "75,000 FCFA"),
            
            ("Licence Professionnelle en Génie Civil", "professionnelle", "3 ans",
             "Formation technique en construction et bâtiment",
             "Technicien BTP, Conducteur de travaux", "Baccalauréat C, D ou E", 1, "75,000 FCFA")
        ]

        cursor.executemany(
            "INSERT INTO filieres (nom, type, duree, description, debouches, conditions_admission, etablissement_id, frais_inscription) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            filieres_sciences
        )

        # Autres filières
        autres_filieres = [
            ("Médecine Générale", "classique", "7 ans",
             "Formation complète en médecine générale",
             "Médecin généraliste, Spécialisation", "Baccalauréat C avec mention", 2, "100,000 FCFA"),
            
            ("Droit Privé", "classique", "4 ans",
             "Formation en droit civil et commercial",
             "Avocat, Juriste d'entreprise, Notaire", "Baccalauréat toutes séries", 3, "45,000 FCFA"),
            
            ("DUT en Génie Informatique", "professionnelle", "2 ans",
             "Formation technique en informatique industrielle",
             "Technicien informatique, Support technique", "Baccalauréat C, D ou technique", 4, "60,000 FCFA")
        ]

        cursor.executemany(
            "INSERT INTO filieres (nom, type, duree, description, debouches, conditions_admission, etablissement_id, frais_inscription) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            autres_filieres
        )

        # Liaisons filières-domaines
        filiere_domaines = [
            (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),  # Sciences
            (7, 2),  # Santé
            (8, 3), (9, 3),  # Droit
            (4, 1), (5, 1), (6, 1), (9, 1)  # Technologies
        ]

        cursor.executemany(
            "INSERT OR IGNORE INTO filiere_domaines (filiere_id, domaine_id) VALUES (?, ?)",
            filiere_domaines
        )

        # Processus de préinscription
        processus = [
            (1, "Création de compte", 
             "Se créer un compte sur la plateforme de préinscription",
             "Rendez-vous sur http://preinscription.univ-douala.cm et cliquez sur 'Créer un compte'"),
            
            (2, "Remplissage du formulaire",
             "Compléter le formulaire de préinscription en ligne",
             "Fournir toutes les informations personnelles et académiques requises"),
            
            (3, "Upload des documents",
             "Téléverser les documents numérisés requis",
             "Documents à fournir : BAC, relevés de notes, photo d'identité, acte de naissance"),
            
            (4, "Validation du dossier",
             "Soumission et validation finale du dossier",
             "Vérifier toutes les informations avant soumission définitive")
        ]

        cursor.executemany(
            "INSERT INTO processus_preinscription (etape, description, details, liens_utiles) VALUES (?, ?, ?, ?)",
            processus
        )

        # Documents requis
        documents = [
            ("BAC ou équivalent", "Diplôme du Baccalauréat ou équivalent", 1),
            ("Relevés de notes", "Relevés de notes du secondaire", 1),
            ("Photo d'identité", "Photo d'identité récente format 4x4", 1),
            ("Acte de naissance", "Copie d'acte de naissance", 1),
            ("Certificat médical", "Certificat médical de non contre-indication", 0),
            ("Lettre de motivation", "Lettre de motivation (pour certaines filières)", 0)
        ]

        cursor.executemany(
            "INSERT INTO documents_requis (type_document, description, obligatoire) VALUES (?, ?, ?)",
            documents
        )

        # Dates importantes
        dates = [
            ("Ouverture préinscription", "2024-06-01", "2024-07-15", "2024-2025"),
            ("Clôture préinscription", "2024-07-15", "2024-07-15", "2024-2025"),
            ("Début des cours", "2024-09-02", "2024-09-02", "2024-2025")
        ]

        cursor.executemany(
            "INSERT INTO dates_importantes (evenement, date_debut, date_fin, annee_academique) VALUES (?, ?, ?, ?)",
            dates
        )

        conn.commit()

    # Méthodes pour récupérer les données
    def get_filieres_by_etablissement(self, etablissement_id: int) -> List[Dict]:
        """Récupérer les filières d'un établissement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, e.nom as etablissement_nom 
            FROM filieres f 
            JOIN etablissements e ON f.etablissement_id = e.id 
            WHERE f.etablissement_id = ?
        ''', (etablissement_id,))
        
        filieres = []
        for row in cursor.fetchall():
            filieres.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'duree': row[3],
                'description': row[4],
                'debouches': row[5],
                'conditions_admission': row[6],
                'etablissement_id': row[7],
                'frais_inscription': row[8],
                'etablissement_nom': row[9]
            })
        
        conn.close()
        return filieres

    def get_filiere_details(self, filiere_nom: str) -> Optional[Dict]:
        """Récupérer les détails d'une filière spécifique"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, e.nom as etablissement_nom, e.contact, e.site_web
            FROM filieres f 
            JOIN etablissements e ON f.etablissement_id = e.id 
            WHERE f.nom LIKE ?
        ''', (f'%{filiere_nom}%',))
        
        row = cursor.fetchone()
        if row:
            result = {
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'duree': row[3],
                'description': row[4],
                'debouches': row[5],
                'conditions_admission': row[6],
                'etablissement_id': row[7],
                'frais_inscription': row[8],
                'etablissement_nom': row[9],
                'contact_etablissement': row[10],
                'site_web_etablissement': row[11]
            }
        else:
            result = None
        
        conn.close()
        return result

    def get_filieres_by_domaine(self, domaine: str) -> List[Dict]:
        """Récupérer les filières par domaine d'intérêt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, e.nom as etablissement_nom, d.nom as domaine_nom
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            JOIN filiere_domaines fd ON f.id = fd.filiere_id
            JOIN domaines_interet d ON fd.domaine_id = d.id
            WHERE d.nom LIKE ?
        ''', (f'%{domaine}%',))
        
        filieres = []
        for row in cursor.fetchall():
            filieres.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'duree': row[3],
                'description': row[4],
                'debouches': row[5],
                'conditions_admission': row[6],
                'etablissement_id': row[7],
                'frais_inscription': row[8],
                'etablissement_nom': row[9],
                'domaine_nom': row[10]
            })
        
        conn.close()
        return filieres

    def get_filieres_by_type(self, type_filiere: str, etablissement: str = None) -> List[Dict]:
        """Récupérer les filières par type (professionnelle/classique)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if etablissement:
            cursor.execute('''
                SELECT f.*, e.nom as etablissement_nom
                FROM filieres f
                JOIN etablissements e ON f.etablissement_id = e.id
                WHERE f.type = ? AND e.nom LIKE ?
            ''', (type_filiere, f'%{etablissement}%'))
        else:
            cursor.execute('''
                SELECT f.*, e.nom as etablissement_nom
                FROM filieres f
                JOIN etablissements e ON f.etablissement_id = e.id
                WHERE f.type = ?
            ''', (type_filiere,))
        
        filieres = []
        for row in cursor.fetchall():
            filieres.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'duree': row[3],
                'description': row[4],
                'debouches': row[5],
                'conditions_admission': row[6],
                'etablissement_id': row[7],
                'frais_inscription': row[8],
                'etablissement_nom': row[9]
            })
        
        conn.close()
        return filieres

    def get_etablissements(self) -> List[Dict]:
        """Récupérer tous les établissements"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM etablissements')
        
        etablissements = []
        for row in cursor.fetchall():
            etablissements.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'description': row[3],
                'contact': row[4],
                'site_web': row[5]
            })
        
        conn.close()
        return etablissements

    def get_processus_preinscription(self) -> List[Dict]:
        """Récupérer le processus de préinscription"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM processus_preinscription ORDER BY etape')
        
        processus = []
        for row in cursor.fetchall():
            processus.append({
                'id': row[0],
                'etape': row[1],
                'description': row[2],
                'details': row[3],
                'liens_utiles': row[4]
            })
        
        conn.close()
        return processus

    def get_documents_requis(self) -> List[Dict]:
        """Récupérer la liste des documents requis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents_requis')
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'id': row[0],
                'type_document': row[1],
                'description': row[2],
                'obligatoire': bool(row[3])
            })
        
        conn.close()
        return documents

    def get_dates_importantes(self) -> List[Dict]:
        """Récupérer les dates importantes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM dates_importantes ORDER BY date_debut')
        
        dates = []
        for row in cursor.fetchall():
            dates.append({
                'id': row[0],
                'evenement': row[1],
                'date_debut': row[2],
                'date_fin': row[3],
                'annee_academique': row[4]
            })
        
        conn.close()
        return dates

    def search_filieres(self, query: str) -> List[Dict]:
        """Rechercher des filières par nom ou description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, e.nom as etablissement_nom
            FROM filieres f
            JOIN etablissements e ON f.etablissement_id = e.id
            WHERE f.nom LIKE ? OR f.description LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        
        filieres = []
        for row in cursor.fetchall():
            filieres.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'duree': row[3],
                'description': row[4],
                'debouches': row[5],
                'conditions_admission': row[6],
                'etablissement_id': row[7],
                'frais_inscription': row[8],
                'etablissement_nom': row[9]
            })
        
        conn.close()
        return filieres

    def get_etablissements_by_domaine(self, domaine: str) -> List[Dict]:
        """Récupérer les établissements par domaine d'intérêt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT e.*, d.nom as domaine_nom
            FROM etablissements e
            JOIN filieres f ON f.etablissement_id = e.id
            JOIN filiere_domaines fd ON f.id = fd.filiere_id
            JOIN domaines_interet d ON fd.domaine_id = d.id
            WHERE d.nom LIKE ?
            ORDER BY e.nom
        ''', (f'%{domaine}%',))
        
        etablissements = []
        for row in cursor.fetchall():
            etablissements.append({
                'id': row[0],
                'nom': row[1],
                'type': row[2],
                'description': row[3],
                'contact': row[4],
                'site_web': row[5],
                'domaine_nom': row[6]
            })
        
        conn.close()
        return etablissements