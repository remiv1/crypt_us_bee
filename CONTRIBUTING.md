# Contribuer à Crypt'Us Bee

Merci de votre intérêt pour contribuer à ce projet ! Ce guide vous aidera à comprendre comment vous pouvez participer efficacement.

## Méthodes de contribution

- Méthode 1 :
  1. Forkez le dépôt.
  2. Créez une branche pour votre contribution (`git checkout -b feature/nom-de-la-fonctionnalité`).
  3. Faites vos modifications et ajoutez des commits clairs.
  4. Assurez-vous que les tests passent (`pytest` ou autre).
  5. Soumettez une Pull Request (PR) avec une description détaillée.
- Méthode 2 :
  1. Créez un problème (issue) pour discuter de votre idée.
  2. Participez aux discussions et affinez votre proposition.
  3. Implémentez les changements dans une branche dédiée.
  4. Soumettez une Pull Request (PR) lorsque vous êtes prêt.
- Méthode 3 :
  1. Envoyer un e-mail à mailto:remiv1@gmail.com
  2. Mettre en sujet "Contribution à Crypt'Us Bee"
  3. Décrire votre proposition de manière détaillée.
  4. Donnez votre pseudo github pour pouvoir être ajouté à l'équipe de développement.

## Etapes de développement

### 1. Daemon multi-os

Il faut prévoir un système anti-copy de la clé.

- Windows Win USB / API PC/SC
  - Surveillance des évènements :
    - Device Arrival
    - Device Removal
- Linux
  - déploiement d'un daemon lié à udev ou pcscd
  - Ecouter les règles pour le device (ID) de la clé :
    - ACTION=="add"
    - ACTION=="remove"
- MacOS
  - Utiliser IOKit ou s'appuyer sur pcscd

### 2. Canal sécurisé client --> navigateur

- Création d'un websocket local (ws://localhost:port)
- Connection au socket local avec un token JWT
- A réception de { event: "key-removed" }, JS déclenche une routine de logout

### 3. Déclanchement de la déconnexion

- Lancement de la déconnexion lorsque JS détecte un événement de clé retirée.
- purge locale de tous les jetons
- redirection vers la page de connexion

### 4. Sécurité et robustesse

- Authentification mutuelle entre services OS et client web
  - Joken JWT à durée de vie courte
  - Certificats client TLS auto-signés vérifiés par l'extension
- [Optional] Heartbeat régulier entre le client et le serveur
- Journalisation horodatée des insertions retraits et des déconnexions.

### 5. Distribution et déploiement

- Packager les services et agents pour chaque OS :
  - MSI pour Windows
  - DEB/RPM pour Linux
  - PKG pour MacOS
- Gérer les mise à jour

## Besoins

### Développeurs

- python
- packaging / distribution
- architectures
- database (noSQL et SQL)
- front-end (HTML/Jinja)
- compléments de navigateurs (chromium, firefox, brave, safari)

### Financements

- ~~support financier~~

## Souhaits

- contributeurs
  - idées pour de nouvelles fonctionnalités
  - améliorations de la documentation
  - tests et retours d'expérience
  - participation à l'élaboration du projet lui-même
    - développement HTML/CSS
    - développement Python
    - création de tests automatisés
    - amélioration de la sécurité (JWA, OAuth)
    - gestion de bases de données (SQLAlchemy)
    - documentation technique

## Concept Simplifié

Le projet vise à créer un système d'authentification sécurisé basé sur une clé USB comme token et validée par une API lors de son utilisation. Objectif principal : Permettre une authentification rapide et sécurisée grâce à une clé USB contenant des données cryptées.

Public cible :

- Développeurs juniors, passionnés de sécurité informatique, et utilisateurs souhaitant une solution simple et efficace.
- Organisations

## Briques Techniques à Développer

Langages recommandés :

- Python pour la simplicité et la flexibilité.
- Exécutables linux/MacOS/Windows pour la création de la base du token.

Modules nécessaires :

- pycryptodome pour le chiffrement et déchiffrement des données.
- usb.core et usb.util pour l'interaction avec la clé USB.

Structure du projet :

- Un script principal pour gérer l'authentification.
- Un fichier de configuration pour personnaliser les paramètres.
- Une documentation claire pour guider les utilisateurs.

## Pistes d'Évolution

- Chiffrement de dossiers : Permettre à la clé USB de crypter le contenu d'un dossier spécifique sur l'ordinateur. Sans la clé, le contenu reste inaccessible et indéchiffrable.
- Ajouter un fichier indicateur dans le dossier à crypter/décrypter, généré par la clé USB, pour signaler les dossiers concernés.
- Système de Kill : Implémenter un mécanisme de désactivation automatique de la clé USB si elle reste connectée trop longtemps à un ordinateur. Ce système pourrait :
  1. Détecter une durée maximale de connexion de 24 heures.
  2. Émettre un avertissement 8 heures avant la désactivation.
  3. Désactiver la clé via un verrouillage logiciel, rendant toute opération impossible jusqu'à réactivation.
  4. Obliger l'utilisation de la clé sur un poste dans le réseau entreprise.
