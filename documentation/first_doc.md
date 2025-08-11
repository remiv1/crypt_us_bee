# Projet existants et différences

## 🔐 Projets Open Source Connexes

### WooKey – par l’ANSSI

- Type : Disque dur USB sécurisé (open source + open hardware)
- Approche :
  - Chiffrement matériel intégré
  - Résistance aux attaques physiques et logicielles
  - Conçu pour les objets connectés durcis
- Différences :
  - Orienté matériel + firmware
  - Pas d’authentification utilisateur via script Python
  - Projet plus complexe et industriel
👉 [Dépôt WooKey](https://github.com/wookey-project)

### VeraCrypt

- Type : Logiciel de chiffrement de disque
- Approche :
  - Création de volumes chiffrés sur disque ou clé USB
  - Mode portable (exécutable depuis une clé USB)
  - Algorithmes : AES, Serpent, Twofish
- Différences :
  - Pas d’authentification automatisée via clé USB
  - Pas de gestion multi-utilisateurs ou interface web
  - Plutôt orienté confidentialité des fichiers
👉 [Dépôt VeraCrypt](https://github.com/veracrypt/VeraCrypt)

### Picocrypt

- Type : Outil de chiffrement léger et open source
- Approche :
  - Chiffrement de fichiers avec mot de passe ou fichier de clé
  - Très simple à utiliser, sans installation
- Différences :
  - Pas de gestion d’identité ou d’authentification
  - Pas d’interaction directe avec le matériel USB
👉 [Dépôt Picocrypt](https://github.com/Picocrypt/Picocrypt)

### Keycloak

- Type : Système de gestion d’identités et d’accès (IAM)
- Approche :
  - Authentification unique (SSO)
  - Protocoles : OAuth2, OpenID Connect, SAML
  - Intégration avec LDAP, AD, etc.
- Différences :
  - Solution serveur web, pas embarquée sur clé USB
  - Très complet mais complexe à déployer
👉 [Dépôt Keycloak](https://github.com/keycloak/keycloak)

### Proton Authenticator

- Type : Application 2FA open source
- Approche :
  - Génération de codes TOTP
  - Chiffrement de bout en bout
  - Multi-plateforme (mobile et desktop)
- Différences :
  - Pas de clé USB physique comme vecteur d’authentification
  - Plutôt orienté vers la double authentification en ligne

## 🧭 Ce qui rend le projet unique

Élément|Le projet|Autres projets open source
----|----|----
Support physique|Clé USB comme vecteur principal|Souvent logiciel ou serveur web
Langage|Python (simple, accessible)|Java, C#, C++ (plus complexes)
Public cible|Développeurs juniors, makers, Petites et moyennes organisations|Entreprises, experts sécurité
Fonction principale|Authentification locale via USB|Chiffrement ou SSO centralisé
Évolutivité|Interface web, multi-utilisateurs|Parfois limité à un usage précis

Note : Le nom Crypt’Us Bee peut aussi évoquer l'idée de "nous" (us en anglais), renforçant l'aspect collaboratif et communautaire du projet.

## 🎨 Pitch et Visuel

### Pitch

**Crypt’Us Bee : L’authentification qui fait le buzzzzzzzzzzzzz !**

Crypt’Us Bee est une solution d’authentification innovante et sécurisée, conçue pour les développeurs et passionnés de sécurité informatique. Grâce à une clé USB intelligente, elle combine simplicité, rapidité et robustesse pour protéger vos données sensibles.

Avec Crypt’Us Bee, chaque utilisateur devient une abeille dans une ruche numérique, collaborant pour un écosystème sécurisé et efficace.

Envoyer un log à l'administrateur pour signaler l'événement.

Afficher un message à l'utilisateur : “Votre clé a été désactivée pour usage prolongé. Veuillez contacter le service sécurité.”
