/*
P5 — Schéma MySQL des sept tables du projet.

Les CREATE TABLE ci-dessous proviennent des sept exports de
dumps/Dump20261015/. Leur ordre respecte les clés étrangères.
Les compteurs AUTO_INCREMENT propres à l'instance exportée ont été omis.

À exécuter dans une base vide choisie par l'utilisateur. Ce fichier
ne supprime aucune table et ne charge aucune donnée.
*/

CREATE TABLE `region` (
  `REG_Code` varchar(3) NOT NULL,
  `REG_Nom` varchar(100) NOT NULL,
  PRIMARY KEY (`REG_Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `departement` (
  `DEP_Code` varchar(3) NOT NULL,
  `DEP_Nom` varchar(100) NOT NULL,
  `REG_Code` varchar(3) NOT NULL,
  PRIMARY KEY (`DEP_Code`),
  KEY `FK_DEPARTEMENT_Region_idx` (`REG_Code`),
  CONSTRAINT `FK_DEPARTEMENT_Region`
    FOREIGN KEY (`REG_Code`) REFERENCES `region` (`REG_Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `commune` (
  `COM_Nom` varchar(100) NOT NULL,
  `DEP_Code` varchar(3) NOT NULL,
  `REG_Code` varchar(3) DEFAULT NULL,
  `COM_Code` varchar(6) NOT NULL,
  PRIMARY KEY (`COM_Code`),
  KEY `FK_COMMUNE_Departement_idx` (`DEP_Code`),
  KEY `FK_COMMUNE_Region_idx` (`REG_Code`),
  KEY `idx_commune_comcode` (`COM_Code`),
  CONSTRAINT `FK_COMMUNE_Departement`
    FOREIGN KEY (`DEP_Code`) REFERENCES `departement` (`DEP_Code`),
  CONSTRAINT `FK_COMMUNE_Region`
    FOREIGN KEY (`REG_Code`) REFERENCES `region` (`REG_Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `mutation` (
  `ID_Mutation` int NOT NULL AUTO_INCREMENT,
  `Date_Mutation` date NOT NULL,
  `NATURE_Mutation` varchar(50) NOT NULL,
  `VALEUR_Fonciere` decimal(12,2) DEFAULT NULL,
  `COM_Code` varchar(6) NOT NULL,
  PRIMARY KEY (`ID_Mutation`),
  KEY `FK_MUTATION_Commune_idx` (`COM_Code`),
  CONSTRAINT `com_code`
    FOREIGN KEY (`COM_Code`) REFERENCES `commune` (`COM_Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `local` (
  `ID_Local` int NOT NULL AUTO_INCREMENT,
  `ID_Mutation` int NOT NULL,
  `CODE_Type_Local` varchar(5) NOT NULL,
  `TYPE_Local` varchar(50) NOT NULL,
  `SURFACE_Reele_Batie` decimal(10,2) DEFAULT NULL,
  `NOMBRE_Pieces` int DEFAULT NULL,
  `Surface_Carrez` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_Local`),
  KEY `FK_LOCAL_Mutation_idx` (`ID_Mutation`),
  CONSTRAINT `FK_LOCAL_Mutation`
    FOREIGN KEY (`ID_Mutation`) REFERENCES `mutation` (`ID_Mutation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `parcelle` (
  `ID_Parcelle` int NOT NULL AUTO_INCREMENT,
  `ID_Mutation` int NOT NULL,
  `PREFIXE_Section` varchar(5) DEFAULT NULL,
  `Section` varchar(5) NOT NULL,
  `NUM_Plan` varchar(10) NOT NULL,
  `SURFACE_Terrain` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_Parcelle`),
  KEY `FK_PARCELLE_Mutation_idx` (`ID_Mutation`),
  CONSTRAINT `FK_PARCELLE_Mutation`
    FOREIGN KEY (`ID_Mutation`) REFERENCES `mutation` (`ID_Mutation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `population` (
  `COM_Code` varchar(6) NOT NULL,
  `PMUN` int DEFAULT NULL,
  `PCAP` int DEFAULT NULL,
  `PTOT` int DEFAULT NULL,
  `Annee` int NOT NULL,
  PRIMARY KEY (`COM_Code`, `Annee`),
  CONSTRAINT `FK_population_commune`
    FOREIGN KEY (`COM_Code`) REFERENCES `commune` (`COM_Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
