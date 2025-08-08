# Crypt'Us Bee
## Stack Technique

Le projet utilise les technologies suivantes :

- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
- ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
- ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
- ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
- ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
- ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
- ![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

## Titre

Crypt'Us Bee
![Logo](./interface/statics/statics_admin/img/Logo.svg)

## Description
Projet d'outil de sécurité (interface à distance + poste local + cryptage de données). L'adminstrateur de l'organisation pourra sur une interface conteneurisée et kubernetisée, créer des tocken sur des clés USB [biométrique] ou non et enregistrer les éléments dans une base de données sécurisée.

L'utilisateur aura besoin du Token pour se connecter sur son poste enrôlé ou sur l'Intranet de l'organisation ou encore pour décoder les fichiers cryptés.

Le projet repose sur un triple niveau de sécurité :
 - Ce que **je sais** (mot de passe)
 - Ce que **j'ai** (token)
 - [Ce que **je suis** (biométrie)]

## Installation
### Prérequis

-[ ] Kubernetes (K8S)
-[ ] Docker
-[ ] Make (Windows)
    -[ ] Lancement du fichier Make
-[ ] Bash (Linux/MacOs)
    -[ ] Lancement du script d'installation

## Utilisation
### Interface

L'interface est divisée en deux types d'accès : administrateur et utilisateur.

#### Accès Utilisateur
L'utilisateur peut gérer ses propres usages, notamment :
- Gestion des tokens personnels.
- Gestion des postes associés.
- Gestion des fichiers et dossiers cryptés.

#### Accès Administrateur
L'administrateur dispose de droits étendus pour gérer l'ensemble des usages, incluant :
- Gestion des tokens de tous les utilisateurs.
- Gestion des postes associés à tous les utilisateurs.
- Révocation des tokens, postes et accès des utilisateurs.
- Supervision globale des activités liées au cryptage et à la sécurité.

## Contributions

Indications de contributions au projet et soumission d'amélioration
