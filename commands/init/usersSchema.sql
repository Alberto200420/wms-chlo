-- Create the User table
CREATE TABLE "User" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" VARCHAR(50) UNIQUE NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "role" VARCHAR(9) NOT NULL CHECK ("role" IN ('ADMIN', 'BOATMAN', 'DRIVER', 'WAREHOUSE'))
);