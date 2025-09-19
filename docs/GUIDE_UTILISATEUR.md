# Guide Utilisateur - CARPEM Oncocentre

## 📋 Présentation

CARPEM Oncocentre est une application web sécurisée destinée à la gestion des identifiants patients pour la collecte de données biologiques CARPEM. L'application génère des identifiants uniques au format `ONCOCENTRE_YYYY_NNNNN` et permet la gestion d'un registre de patients.

## 🔐 Connexion à l'Application

### Accès à l'Application

L'application est accessible via votre navigateur web aux adresses suivantes :
- **Version HTTP (développement)** : `http://localhost:5000`
- **Version HTTPS (production)** : `https://localhost:5000`

### Page de Connexion

1. Ouvrez votre navigateur web
2. Accédez à l'URL de l'application
3. Vous serez automatiquement redirigé vers la page de connexion
4. Saisissez vos identifiants :
   - **Nom d'utilisateur** : votre identifiant fourni par l'administrateur
   - **Mot de passe** : votre mot de passe personnel
   - **Méthode d'authentification** : choisissez parmi les options disponibles

### 🔑 Méthodes d'Authentification

L'application supporte plusieurs méthodes d'authentification :

#### **Auto-détection (Recommandée)**
- Tente d'abord l'authentification locale
- En cas d'échec, essaie automatiquement l'authentification LDAP
- Option idéale pour la plupart des utilisateurs

#### **Compte Local**
- Utilise uniquement les comptes créés localement dans l'application
- Mots de passe stockés de manière sécurisée dans la base de données

#### **LDAP/Active Directory**
- Utilise vos identifiants institutionnels
- Se connecte au serveur LDAP/Active Directory de l'organisation
- Création automatique de votre profil local à la première connexion

### Comptes de Test (Environnement de Développement)

Pour les tests et la formation, les comptes suivants sont disponibles :
- `admin` / `admin123` (Administrateur)
- `user1` / `user1123` (Utilisateur standard)
- `user2` / `user2123` (Utilisateur standard)
- `doctor1` / `doctor123` (Utilisateur standard)
- `researcher1` / `research123` (Utilisateur standard)

⚠️ **Important** : Changez ces mots de passe par défaut en production !

## 🏠 Page Principale - Création de Patients

### Vue d'Ensemble

Après connexion, vous accédez à la page principale qui permet la création de nouveaux patients. Cette page comprend :

- **Menu de navigation** : accès aux différentes sections
- **Formulaire de création** : saisie des informations patient
- **Aperçu de l'identifiant** : prévisualisation du prochain ID
- **Messages de statut** : confirmations et erreurs

### Création d'un Nouveau Patient

#### 1. Remplissage du Formulaire

**Champs Obligatoires :**
- **IPP (Identifiant Permanent du Patient)** : Identifiant unique du patient dans votre système
- **Prénom** : Prénom du patient
- **Nom** : Nom de famille du patient
- **Date de naissance** : Format JJ/MM/AAAA
- **Sexe** : Masculin (M) ou Féminin (F)

#### 2. Prévisualisation de l'Identifiant

- Un aperçu de l'identifiant ONCOCENTRE est affiché automatiquement
- Format : `ONCOCENTRE_YYYY_NNNNN` (année courante + numéro séquentiel)
- Exemple : `ONCOCENTRE_2025_00001`

#### 3. Validation et Création

1. Vérifiez que tous les champs sont correctement remplis
2. Cliquez sur **"Créer Patient"**
3. Un message de confirmation s'affiche avec l'identifiant généré
4. Le patient est ajouté à votre liste personnelle

#### 4. Gestion des Doublons

- Le système vérifie automatiquement les doublons d'IPP
- Si un patient avec le même IPP existe déjà, un message d'avertissement s'affiche
- L'identifiant ONCOCENTRE existant est rappelé

## 👥 Liste des Patients

### Accès à la Liste

- Cliquez sur **"Patients"** dans le menu de navigation
- Ou utilisez l'URL directe : `/patients`

### Contenu de la Liste

La liste affiche vos patients dans un tableau avec :
- **Identifiant ONCOCENTRE** : ID unique généré
- **IPP** : Votre identifiant patient interne
- **Nom complet** : Nom et prénom du patient
- **Date de naissance** : Date fournie lors de la création
- **Sexe** : M ou F
- **Date de création** : Quand l'enregistrement a été créé

### Caractéristiques de Sécurité

- **Isolation des données** : Vous ne voyez que vos propres patients
- **Chiffrement** : Les données sensibles sont chiffrées en base
- **Tri** : Les patients sont triés par date de création (plus récents en premier)

## ⚙️ Fonctionnalités Utilisateur

### Menu de Navigation

Le menu principal vous donne accès à :
- **Accueil** : Retour à la page de création
- **Patients** : Liste de vos patients
- **Administration** : (Administrateurs uniquement)
- **Déconnexion** : Fermeture de session sécurisée

### Messages du Système

L'application affiche différents types de messages :
- 🟢 **Succès** : Opération réussie (fond vert)
- 🟠 **Avertissement** : Information importante (fond orange)
- 🔴 **Erreur** : Problème à résoudre (fond rouge)
- 🔵 **Information** : Message informatif (fond bleu)

### Déconnexion

1. Cliquez sur **"Déconnexion"** dans le menu
2. Votre session est fermée automatiquement
3. Vous êtes redirigé vers la page de connexion
4. Un message de confirmation s'affiche

## 👑 Fonctionnalités Administrateur

*Cette section s'applique uniquement aux utilisateurs avec des privilèges administrateur*

### Accès au Tableau de Bord

- Connectez-vous avec un compte administrateur
- Cliquez sur **"Administration"** dans le menu
- Sélectionnez **"Tableau de bord"**

### Tableau de Bord

Le tableau de bord administrateur affiche :
- **Statistiques générales** :
  - Nombre total d'utilisateurs
  - Utilisateurs actifs
  - Administrateurs
  - Total des patients dans le système
- **Liens rapides** vers la gestion des utilisateurs
- **Informations système**

### Gestion des Utilisateurs

#### Accéder à la Gestion des Utilisateurs
- **Administration** → **Gestion des utilisateurs**

#### Liste des Utilisateurs
La liste affiche pour chaque utilisateur :
- **Nom d'utilisateur**
- **Statut** : Actif/Inactif
- **Rôle** : Administrateur/Utilisateur
- **Nombre de patients** créés
- **Date de création**
- **Actions** disponibles

#### Créer un Nouvel Utilisateur

1. Cliquez sur **"Créer un utilisateur"**
2. Remplissez le formulaire :
   - **Nom d'utilisateur** : Identifiant unique (min. 4 caractères)
   - **Mot de passe** : Mot de passe sécurisé (min. 8 caractères)
   - **Confirmer le mot de passe** : Répétez le mot de passe
   - **Privilèges administrateur** : Cochez si nécessaire
3. Cliquez sur **"Créer l'utilisateur"**

#### Modifier un Utilisateur

1. Dans la liste des utilisateurs, cliquez sur **"Modifier"**
2. Modifiez les paramètres :
   - **Compte actif** : Activer/désactiver le compte
   - **Privilèges administrateur** : Accorder/retirer les droits admin
   - **Nouveau mot de passe** : Laissez vide pour conserver l'actuel
3. Cliquez sur **"Mettre à jour"**

#### Supprimer un Utilisateur

1. Cliquez sur **"Supprimer"** dans la liste
2. **Comportement intelligent** :
   - Si l'utilisateur a créé des patients : le compte est désactivé
   - Si aucun patient : l'utilisateur est supprimé définitivement
3. Confirmez l'action

### Informations Système

- **Administration** → **Informations système**
- Affiche :
  - État de la clé de chiffrement
  - Chemin de la base de données
  - Utilisateurs autorisés
  - Environnement de l'application

## 🔒 Sécurité et Confidentialité

### Protection des Données

- **Chiffrement** : Toutes les données sensibles (IPP, noms, dates de naissance) sont chiffrées
- **Isolation** : Chaque utilisateur ne voit que ses propres patients
- **Authentification** : Connexion sécurisée avec mots de passe hachés
- **HTTPS** : Communications chiffrées en production

### Bonnes Pratiques

1. **Mot de passe** :
   - Utilisez un mot de passe fort et unique
   - Ne partagez jamais vos identifiants
   - Changez régulièrement votre mot de passe

2. **Session** :
   - Déconnectez-vous toujours après utilisation
   - Ne laissez pas votre session ouverte sans surveillance

3. **Données** :
   - Vérifiez toujours les informations avant validation
   - Signalez immédiatement toute anomalie

## ❓ Dépannage et Support

### Problèmes de Connexion

**Je ne peux pas me connecter :**
- Vérifiez votre nom d'utilisateur et mot de passe
- Essayez différentes méthodes d'authentification :
  - Si vous avez un compte local, utilisez "Compte Local"
  - Si vous utilisez vos identifiants institutionnels, utilisez "LDAP/Active Directory"
  - En cas de doute, utilisez "Auto-détection"
- Assurez-vous que votre compte est dans la liste des utilisateurs autorisés
- Contactez votre administrateur si le problème persiste

**Message "Accès non autorisé" :**
- Votre nom d'utilisateur n'est pas dans la liste des utilisateurs autorisés
- Contactez l'administrateur pour être ajouté à la liste

**Problèmes spécifiques à l'authentification LDAP :**
- Vérifiez que vous utilisez vos identifiants institutionnels corrects
- Le serveur LDAP doit être accessible et configuré
- Contactez l'administrateur système si l'authentification LDAP ne fonctionne pas

**Mon compte LDAP se connecte mais je n'ai pas accès :**
- L'authentification LDAP peut réussir mais votre nom d'utilisateur doit toujours être autorisé
- Votre profil local est créé automatiquement à la première connexion LDAP
- Contactez l'administrateur pour être ajouté à la liste des utilisateurs autorisés

### Problèmes de Fonctionnement

**Je ne vois pas mes patients :**
- Vérifiez que vous êtes bien connecté avec le bon compte
- Les patients sont isolés par utilisateur (vous ne voyez que les vôtres)

**Erreur lors de la création d'un patient :**
- Vérifiez que tous les champs obligatoires sont remplis
- Assurez-vous que l'IPP n'existe pas déjà
- Vérifiez le format de la date de naissance

**Page d'erreur 403 (Accès interdit) :**
- Vous tentez d'accéder à une page réservée aux administrateurs
- Connectez-vous avec un compte administrateur ou demandez les droits nécessaires

### Messages d'Erreur Courants

| Message | Signification | Solution |
|---------|---------------|----------|
| "Veuillez vous connecter" | Session expirée | Reconnectez-vous |
| "Patient avec IPP XXX existe déjà" | Doublon détecté | Utilisez un IPP différent |
| "Accès non autorisé" | Utilisateur non autorisé | Contactez l'administrateur |
| "Erreur 500" | Erreur serveur | Rechargez la page ou contactez l'administrateur |

## 📞 Contact et Support

### Obtenir de l'Aide

1. **Documentation** : Consultez d'abord ce guide
2. **Administrateur local** : Contactez votre administrateur système
3. **Support technique** : Reportez les problèmes techniques via les canaux officiels

### Signalement de Problèmes

Lors d'un signalement, incluez :
- **Description du problème** : Que s'est-il passé ?
- **Étapes pour reproduire** : Comment reproduire l'erreur ?
- **Message d'erreur** : Copie exacte du message affiché
- **Navigateur utilisé** : Chrome, Firefox, Safari, etc.
- **Heure et date** : Quand le problème s'est produit

### Formation et Assistance

- **Formation initiale** : Demandez une session de formation si nécessaire
- **Assistance ponctuelle** : Support disponible pour les questions spécifiques
- **Mises à jour** : Vous serez informé des nouvelles fonctionnalités

## 📚 Annexes

### Glossaire

- **IPP** : Identifiant Permanent du Patient - votre numéro patient interne
- **ONCOCENTRE ID** : Identifiant unique généré par l'application
- **CSRF** : Protection contre les attaques de falsification de requêtes
- **HTTPS** : Protocole sécurisé pour les communications web
- **Session** : Période de connexion active à l'application

### Formats de Données

- **Date de naissance** : JJ/MM/AAAA (ex: 15/03/1980)
- **Identifiant ONCOCENTRE** : ONCOCENTRE_YYYY_NNNNN (ex: ONCOCENTRE_2025_00001)
- **Sexe** : M (Masculin) ou F (Féminin)

### Raccourcis Clavier

- **Tab** : Passer au champ suivant
- **Shift + Tab** : Revenir au champ précédent
- **Entrée** : Valider le formulaire (si tous les champs sont remplis)
- **Échap** : Annuler l'action en cours

---

*Guide utilisateur CARPEM Oncocentre - Version 1.0*  
*Dernière mise à jour : Septembre 2025*