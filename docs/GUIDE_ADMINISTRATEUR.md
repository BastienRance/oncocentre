# Guide Administrateur - CARPEM Oncocentre

## 🔑 Vue d'Ensemble

Ce guide est destiné aux administrateurs système de CARPEM Oncocentre. Il couvre l'installation, la configuration, la gestion des utilisateurs et la maintenance de l'application.

## ⚙️ Administration des Utilisateurs

### Gestion via Interface Web

#### Accès au Panneau d'Administration
1. Connectez-vous avec un compte administrateur
2. Cliquez sur **"Administration"** dans le menu
3. Accédez aux différentes sections

#### Créer un Nouvel Utilisateur
```
Administration → Gestion des utilisateurs → Créer un utilisateur
```
- **Nom d'utilisateur** : 4-80 caractères, unique
- **Mot de passe** : Minimum 8 caractères
- **Rôle** : Utilisateur standard ou Administrateur

#### Modifier un Utilisateur Existant
- **Statut du compte** : Activer/Désactiver
- **Privilèges** : Accorder/Retirer les droits administrateur
- **Réinitialisation** : Changer le mot de passe

#### Suppression Intelligente
- **Utilisateur sans patients** : Suppression complète
- **Utilisateur avec patients** : Désactivation automatique (préservation des données)

### Gestion via Ligne de Commande

#### Créer des Utilisateurs de Test
```bash
python scripts/create_users.py
```
Crée 5 utilisateurs par défaut avec mots de passe prédéfinis.

#### Accorder des Privilèges Administrateur
```bash
# Faire un utilisateur administrateur
python scripts/make_admin.py <nom_utilisateur>

# Lister les administrateurs actuels
python scripts/make_admin.py list
```

#### Gestion de la Base de Données
```bash
# Réinitialiser complètement la base
python migrations/reset.py

# Migrer une base existante
python migrations/migrate.py
```

## 🔐 Configuration de Sécurité

### Variables d'Environnement Requises

```bash
# Clé secrète de l'application (OBLIGATOIRE en production)
export SECRET_KEY="votre-cle-secrete-complexe-ici"

# Liste des utilisateurs autorisés (séparés par des virgules)
export AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"

# Environnement d'exécution
export FLASK_CONFIG="production"  # ou "development"
```

### Génération d'une Clé Secrète Sécurisée
```bash
# Générer une clé aléatoire sécurisée
export SECRET_KEY="$(openssl rand -hex 32)"
```

### Configuration HTTPS

#### Certificats Auto-Signés (Développement)
```bash
python scripts/run_https.py
```
Les certificats sont générés automatiquement.

#### Certificats de Production
1. Obtenez des certificats SSL auprès d'une autorité de certification
2. Remplacez `server.crt` et `server.key`
3. Vérifiez les permissions des fichiers
4. Redémarrez le serveur HTTPS

## 🚀 Déploiement et Exécution

### Serveur de Développement
```bash
# HTTP (développement)
python run.py

# HTTPS (développement avec certificats auto-signés)
python scripts/run_https.py
```

### Déploiement de Production

#### Checklist Pré-Déploiement
- [ ] Modifier la `SECRET_KEY` par une valeur forte
- [ ] Configurer `AUTHORIZED_USERS` avec les vrais utilisateurs
- [ ] Installer des certificats SSL valides
- [ ] Configurer le pare-feu (autoriser HTTPS, bloquer HTTP)
- [ ] Mettre en place une stratégie de sauvegarde
- [ ] Configurer la surveillance et les alertes
- [ ] Changer le mot de passe administrateur par défaut
- [ ] Tester toutes les fonctionnalités en environnement de test

#### Variables d'Environnement de Production
```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export AUTHORIZED_USERS="admin,docteur1,chercheur1,infirmiere1"
export FLASK_CONFIG="production"
```

#### Commande de Déploiement
```bash
# Serveur HTTPS de production
python scripts/run_https.py
```

## 📊 Surveillance et Maintenance

### Tableau de Bord Administrateur

Le tableau de bord fournit :
- **Statistiques** : Nombre d'utilisateurs, patients, administrateurs
- **État du système** : Configuration, clés, base de données
- **Liens rapides** : Accès aux fonctions d'administration

### Tâches de Maintenance Régulières

#### Hebdomadaires
- Vérifier les journaux d'accès utilisateur
- Contrôler les tentatives de connexion échouées
- Vérifier l'intégrité de la base de données

#### Mensuelles
- Mettre à jour les dépendances Python
- Réviser les comptes utilisateurs actifs
- Vérifier l'espace disque disponible

#### Trimestrielles
- Rotation des clés de chiffrement
- Audit des permissions utilisateurs
- Test de restauration des sauvegardes

#### Annuelles
- Évaluation de sécurité complète
- Renouvellement des certificats SSL
- Révision de la politique de sécurité

### Commandes de Maintenance

#### Mise à Jour des Dépendances
```bash
# Mettre à jour les packages Python
pip install --upgrade -r requirements.txt

# Vérifier les vulnérabilités de sécurité
pip audit
```

#### Sauvegarde des Données Critiques
```bash
# Fichiers essentiels à sauvegarder :
# - instance/oncocentre.db (base de données)
# - encryption.key (clé de chiffrement)
# - server.crt et server.key (certificats SSL)
# - fichiers de configuration et variables d'environnement
```

## 🛠️ Dépannage Administrateur

### Problèmes Courants

#### Base de Données
```bash
# Vérifier le schéma de la base
python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    print('Tables:', db.engine.table_names())
"

# Vérifier la connectivité
sqlite3 instance/oncocentre.db ".tables"
```

#### Utilisateurs et Permissions
```bash
# Lister tous les utilisateurs
sqlite3 instance/oncocentre.db "SELECT username, is_active, is_admin FROM user;"

# Vérifier les utilisateurs autorisés
echo $AUTHORIZED_USERS
```

#### Problèmes de Chiffrement
```bash
# Vérifier la présence de la clé de chiffrement
ls -la encryption.key

# Tester la lecture de la clé
python -c "
from app.utils.crypto import ENCRYPTION_KEY
print('Clé chargée:', len(ENCRYPTION_KEY), 'bytes')
"
```

### Messages d'Erreur et Solutions

| Erreur | Cause | Solution |
|--------|-------|----------|
| `TemplateNotFound` | Templates mal configurés | Vérifier les chemins des templates |
| `InvalidToken` | Clé de chiffrement incorrecte | Restaurer la bonne clé ou réinitialiser |
| `BuildError` | Route inexistante | Vérifier les URL dans les templates |
| `403 Forbidden` | Permissions insuffisantes | Vérifier les droits administrateur |
| `500 Internal Error` | Erreur applicative | Consulter les logs détaillés |

## 📈 Monitoring et Journalisation

### Événements à Surveiller
- Tentatives de connexion échouées
- Accès aux fonctions administratives
- Création/modification d'utilisateurs
- Erreurs d'application (500, 403)
- Utilisation anormale des ressources

### Logs d'Application
Les logs incluent automatiquement :
- Authentifications réussies/échouées
- Actions administratives
- Erreurs système
- Accès aux données patients

### Alertes Recommandées
- Trop de tentatives de connexion échouées
- Accès non autorisé aux données
- Erreurs critiques de l'application
- Espace disque faible
- Certificats SSL proches de l'expiration

## 🔄 Procédures d'Urgence

### En Cas de Compromission Suspectée

#### Actions Immédiates
1. **Désactiver les comptes** affectés
2. **Changer les clés de chiffrement** si compromission suspectée
3. **Examiner les logs** pour détecter les activités non autorisées

#### Investigation
1. **Exécuter la suite de tests** de sécurité pour vérifier l'intégrité
2. **Vérifier la base de données** pour des modifications non autorisées
3. **Analyser les logs** pour identifier des patterns suspects

#### Récupération
1. **Restaurer** à partir de sauvegardes propres si nécessaire
2. **Réinitialiser** tous les mots de passe utilisateur
3. **Mettre à jour** les configurations de sécurité

### Contacts d'Urgence
- **Administrateur système principal** : [À définir]
- **Équipe sécurité CARPEM** : [À définir]
- **Support technique** : [À définir]

## 📋 Checklist de Déploiement Initial

### Installation
- [ ] Python 3.11+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Variables d'environnement configurées
- [ ] Base de données initialisée
- [ ] Utilisateurs de test créés
- [ ] Privilèges administrateur accordés

### Sécurité
- [ ] SECRET_KEY forte définie
- [ ] AUTHORIZED_USERS configuré
- [ ] Certificats SSL en place (production)
- [ ] Pare-feu configuré
- [ ] Stratégie de sauvegarde définie

### Tests
- [ ] Suite de tests exécutée avec succès
- [ ] Connexion utilisateur testée
- [ ] Fonctions administrateur vérifiées
- [ ] Création de patients testée
- [ ] Accès HTTPS vérifié

### Documentation
- [ ] Guide utilisateur fourni aux utilisateurs finaux
- [ ] Procédures d'administration documentées
- [ ] Contacts de support définis
- [ ] Formation utilisateur planifiée

---

*Guide administrateur CARPEM Oncocentre - Version 1.0*  
*Dernière mise à jour : Septembre 2025*