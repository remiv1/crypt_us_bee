Feuille de Route pour Projet Open Source avec Clé USB

1. Concept Simplifié

Le projet vise à créer un système d'authentification sécurisé basé sur une clé USB.

Objectif principal : Permettre une authentification rapide et sécurisée grâce à une clé USB contenant des données cryptées.

Public cible : Développeurs juniors, passionnés de sécurité informatique, et utilisateurs souhaitant une solution simple et efficace.

2. Briques Techniques à Développer

Langages recommandés : Python pour la simplicité et la flexibilité.

Modules nécessaires :

pycryptodome pour le chiffrement et déchiffrement des données.

usb.core et usb.util pour l'interaction avec la clé USB.

Structure du projet :

Un script principal pour gérer l'authentification.

Un fichier de configuration pour personnaliser les paramètres.

Une documentation claire pour guider les utilisateurs.

3. Pistes d'Évolution

Multi-utilisateurs : Ajouter la possibilité de gérer plusieurs utilisateurs avec des clés USB distinctes.

Compatibilité Linux : Assurer la compatibilité avec les systèmes Linux pour une adoption plus large.

Interface web : Créer une interface web pour faciliter la gestion et le suivi des authentifications.

Chiffrement de dossiers : Permettre à la clé USB de crypter le contenu d'un dossier spécifique sur l'ordinateur. Sans la clé, le contenu reste inaccessible et indéchiffrable.

Ajouter un fichier indicateur dans le dossier à crypter/décrypter, généré par la clé USB, pour signaler les dossiers concernés.

Système de Kill : Implémenter un mécanisme de désactivation automatique de la clé USB si elle reste connectée trop longtemps à un ordinateur. Ce système pourrait :

Détecter une durée maximale de connexion de 24 heures.

Émettre un avertissement 8 heures avant la désactivation.

Désactiver la clé via un verrouillage logiciel, rendant toute opération impossible jusqu'à réactivation.

Obliger l'utilisation de la clé sur un poste dans le réseau entreprise.

🔐 Projets Open Source Similaires

1. WooKey – par l’ANSSI

Type : Disque dur USB sécurisé (open source + open hardware)

Approche :

Chiffrement matériel intégré

Résistance aux attaques physiques et logicielles

Conçu pour les objets connectés durcis

Différences :

Orienté matériel + firmware

Pas d’authentification utilisateur via script Python

Projet plus complexe et industriel

👉 Site officiel WooKey

2. VeraCrypt

Type : Logiciel de chiffrement de disque

Approche :

Création de volumes chiffrés sur disque ou clé USB

Mode portable (exécutable depuis une clé USB)

Algorithmes : AES, Serpent, Twofish

Différences :

Pas d’authentification automatisée via clé USB

Pas de gestion multi-utilisateurs ou interface web

Plutôt orienté confidentialité des fichiers

3. Picocrypt

Type : Outil de chiffrement léger et open source

Approche :

Chiffrement de fichiers avec mot de passe ou fichier de clé

Très simple à utiliser, sans installation

Différences :

Pas de gestion d’identité ou d’authentification

Pas d’interaction directe avec le matériel USB

4. Keycloak

Type : Système de gestion d’identités et d’accès (IAM)

Approche :

Authentification unique (SSO)

Protocoles : OAuth2, OpenID Connect, SAML

Intégration avec LDAP, AD, etc.

Différences :

Solution serveur web, pas embarquée sur clé USB

Très complet mais complexe à déployer

5. Proton Authenticator

Type : Application 2FA open source

Approche :

Génération de codes TOTP

Chiffrement de bout en bout

Multi-plateforme (mobile et desktop)

Différences :

Pas de clé USB physique comme vecteur d’authentification

Plutôt orienté vers la double authentification en ligne

🧭 Ce qui rend ton projet unique

Élément

Ton projet

Autres projets open source

Support physique

Clé USB comme vecteur principal

Souvent logiciel ou serveur web

Langage

Python (simple, accessible)

Java, C#, C++ (plus complexes)

Public cible

Développeurs juniors, makers

Entreprises, experts sécurité

Fonction principale

Authentification locale via USB

Chiffrement ou SSO centralisé

Évolutivité

Interface web, multi-utilisateurs

Parfois limité à un usage précis

Note : Le nom Crypt’Us Bee peut aussi évoquer l'idée de "nous" (us en anglais), renforçant l'aspect collaboratif et communautaire du projet.

🎨 Pitch et Visuel

Pitch

Crypt’Us Bee : L’authentification qui fait le buzz !

Crypt’Us Bee est une solution d’authentification innovante et sécurisée, conçue pour les développeurs et passionnés de sécurité informatique. Grâce à une clé USB intelligente, elle combine simplicité, rapidité et robustesse pour protéger vos données sensibles.

Avec Crypt’Us Bee, chaque utilisateur devient une abeille dans une ruche numérique, collaborant pour un écosystème sécurisé et efficace.

Envoyer un log à l'administrateur pour signaler l'événement.

Afficher un message à l'utilisateur : “Votre clé a été désactivée pour usage prolongé. Veuillez contacter le service sécurité.”
