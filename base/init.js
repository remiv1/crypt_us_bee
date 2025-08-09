db = db.getSiblingDB('beeDB');

// Création d'un utilisateur administrateur
db.createUser({
  user: "bdd_username_root",
  pwd: "8D46210xO8fgqE6BJ6Hq4rmWi3KqkD",
  roles: [
    { role: "readWrite", db: "beeDB" },
    { role: "dbAdmin", db: "beeDB" }
  ]
});

// Création des collections
db.createCollection('users');
db.createCollection('workstations');
db.createCollection('keys');

// Insertion de données initiales
db.users.insertMany([
  { name: "admin", role: "administrator", createdAt: new Date() },
  { name: "user1", role: "user", createdAt: new Date() }
]);

db.workstations.insertMany([
  { name: "Workstation1", status: "active", createdAt: new Date() },
  { name: "Workstation2", status: "inactive", createdAt: new Date() }
]);

db.keys.insertMany([
  { key: "ABC123", owner: "user1", createdAt: new Date() },
  { key: "XYZ789", owner: "admin", createdAt: new Date() }
]);