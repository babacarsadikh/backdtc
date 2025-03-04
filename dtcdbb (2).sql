-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : mar. 04 mars 2025 à 12:12
-- Version du serveur : 10.4.28-MariaDB
-- Version de PHP : 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `dtcdbb`
--

-- --------------------------------------------------------

--
-- Structure de la table `AdressesChantier`
--

CREATE TABLE `AdressesChantier` (
  `id_adresse` int(11) NOT NULL,
  `id_client` int(11) DEFAULT NULL,
  `adresse` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `AdressesChantier`
--

INSERT INTO `AdressesChantier` (`id_adresse`, `id_client`, `adresse`) VALUES
(2, 1, 'OUKAM'),
(3, 2, 'DIAMNIADIO'),
(4, 2, 'FASS MBSO'),
(5, 4, 'THIES'),
(6, 6, 'SANGALKAM'),
(7, 7, 'THIES'),
(8, 8, 'PIKINE'),
(9, 9, 'KEUR MASSAR');

-- --------------------------------------------------------

--
-- Structure de la table `Chauffeurs`
--

CREATE TABLE `Chauffeurs` (
  `id_chauffeur` int(11) NOT NULL,
  `nom_chauffeur` varchar(100) NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `plaque_camion` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `Chauffeurs`
--

INSERT INTO `Chauffeurs` (`id_chauffeur`, `nom_chauffeur`, `telephone`, `plaque_camion`) VALUES
(1, 'Modou Diagne', '772981278', 'AA-3844-DK'),
(2, 'SOULYEMANE FAYE', '772981278', 'AA-739-BP'),
(3, 'MOR SALL', '772293992', 'AA-263-PH'),
(4, 'PAPE OMAR SENE', '771022340', 'AA-237-PH'),
(5, 'MAMADOU SARR', '777320284', 'AA-716-WA'),
(6, 'baba ndiaye ', '+221772981201', 'AA-483-PR');

-- --------------------------------------------------------

--
-- Structure de la table `Clients`
--

CREATE TABLE `Clients` (
  `id_client` int(11) NOT NULL,
  `nom_client` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `Clients`
--

INSERT INTO `Clients` (`id_client`, `nom_client`) VALUES
(1, 'Entreprise Alpha'),
(2, 'Alioune Niang'),
(4, 'TAPHA SECK'),
(6, 'MOUHAMED FALL'),
(7, 'TAPHA SECK'),
(8, 'CCBM'),
(9, 'TALLA');

-- --------------------------------------------------------

--
-- Structure de la table `Commandes`
--

CREATE TABLE `Commandes` (
  `id_commande` int(11) NOT NULL,
  `id_client` int(11) DEFAULT NULL,
  `formule` varchar(50) NOT NULL,
  `quantite_commandee` decimal(10,2) NOT NULL,
  `quantite_restante` decimal(10,2) NOT NULL,
  `date_production` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `Commandes`
--

INSERT INTO `Commandes` (`id_commande`, `id_client`, `formule`, `quantite_commandee`, `quantite_restante`, `date_production`) VALUES
(26, 8, 'C30 HYDROFUGE', 50.00, 30.00, '2025-03-01'),
(27, 9, 'C25', 75.00, 45.00, '2025-03-01');

-- --------------------------------------------------------

--
-- Structure de la table `Livraisons`
--

CREATE TABLE `Livraisons` (
  `id_livraison` int(11) NOT NULL,
  `id_commande` int(11) DEFAULT NULL,
  `id_chauffeur` int(11) DEFAULT NULL,
  `id_adresse` int(11) DEFAULT NULL,
  `quantite_commandee` decimal(10,2) DEFAULT NULL,
  `quantite_chargee` decimal(10,2) NOT NULL,
  `quantite_totale_chargee` decimal(10,2) DEFAULT NULL,
  `quantite_restante` decimal(10,2) DEFAULT NULL,
  `heure_depart` time DEFAULT NULL,
  `date_production` date DEFAULT NULL,
  `etat_livraison` varchar(20) DEFAULT 'en attente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `Livraisons`
--

INSERT INTO `Livraisons` (`id_livraison`, `id_commande`, `id_chauffeur`, `id_adresse`, `quantite_commandee`, `quantite_chargee`, `quantite_totale_chargee`, `quantite_restante`, `heure_depart`, `date_production`, `etat_livraison`) VALUES
(88, 26, 3, 4, 50.00, 10.00, 10.00, 40.00, '19:11:00', '2025-03-01', 'en attente'),
(89, 27, 3, 8, 75.00, 10.00, 10.00, 65.00, '19:12:00', '2025-03-01', 'en attente'),
(90, 27, 4, 8, 75.00, 10.00, 20.00, 55.00, '19:12:00', '2025-03-01', 'en attente'),
(91, 26, 4, 6, 50.00, 10.00, 20.00, 30.00, '19:12:00', '2025-03-01', 'en attente'),
(92, 27, 3, 8, 75.00, 10.00, 30.00, 45.00, '19:33:00', '2025-03-01', 'en attente');

-- --------------------------------------------------------

--
-- Structure de la table `Rapports`
--

CREATE TABLE `Rapports` (
  `id_rapport` int(11) NOT NULL,
  `id_livraison` int(11) DEFAULT NULL,
  `date_livraison` date DEFAULT NULL,
  `details_livraison` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `Rapports`
--

INSERT INTO `Rapports` (`id_rapport`, `id_livraison`, `date_livraison`, `details_livraison`) VALUES
(73, 88, '2025-03-01', 'Client: CCBM, Adresse Chantier: PIKINE, Formule: C30 HYDROFUGE, Quantité Chargée: 10 unités.'),
(74, 89, '2025-03-01', 'Client: TALLA, Adresse Chantier: KEUR MASSAR, Formule: C25, Quantité Chargée: 10 unités.'),
(75, 90, '2025-03-01', 'Client: TALLA, Adresse Chantier: KEUR MASSAR, Formule: C25, Quantité Chargée: 10 unités.'),
(76, 91, '2025-03-01', 'Client: CCBM, Adresse Chantier: PIKINE, Formule: C30 HYDROFUGE, Quantité Chargée: 10 unités.'),
(77, 92, '2025-03-01', 'Client: TALLA, Adresse Chantier: KEUR MASSAR, Formule: C25, Quantité Chargée: 10 unités.');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `AdressesChantier`
--
ALTER TABLE `AdressesChantier`
  ADD PRIMARY KEY (`id_adresse`),
  ADD KEY `id_client` (`id_client`);

--
-- Index pour la table `Chauffeurs`
--
ALTER TABLE `Chauffeurs`
  ADD PRIMARY KEY (`id_chauffeur`);

--
-- Index pour la table `Clients`
--
ALTER TABLE `Clients`
  ADD PRIMARY KEY (`id_client`);

--
-- Index pour la table `Commandes`
--
ALTER TABLE `Commandes`
  ADD PRIMARY KEY (`id_commande`),
  ADD KEY `id_client` (`id_client`);

--
-- Index pour la table `Livraisons`
--
ALTER TABLE `Livraisons`
  ADD PRIMARY KEY (`id_livraison`),
  ADD KEY `id_commande` (`id_commande`),
  ADD KEY `id_chauffeur` (`id_chauffeur`),
  ADD KEY `id_adresse` (`id_adresse`);

--
-- Index pour la table `Rapports`
--
ALTER TABLE `Rapports`
  ADD PRIMARY KEY (`id_rapport`),
  ADD KEY `id_livraison` (`id_livraison`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `AdressesChantier`
--
ALTER TABLE `AdressesChantier`
  MODIFY `id_adresse` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT pour la table `Chauffeurs`
--
ALTER TABLE `Chauffeurs`
  MODIFY `id_chauffeur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `Clients`
--
ALTER TABLE `Clients`
  MODIFY `id_client` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT pour la table `Commandes`
--
ALTER TABLE `Commandes`
  MODIFY `id_commande` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT pour la table `Livraisons`
--
ALTER TABLE `Livraisons`
  MODIFY `id_livraison` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=93;

--
-- AUTO_INCREMENT pour la table `Rapports`
--
ALTER TABLE `Rapports`
  MODIFY `id_rapport` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=78;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `AdressesChantier`
--
ALTER TABLE `AdressesChantier`
  ADD CONSTRAINT `adresseschantier_ibfk_1` FOREIGN KEY (`id_client`) REFERENCES `Clients` (`id_client`);

--
-- Contraintes pour la table `Commandes`
--
ALTER TABLE `Commandes`
  ADD CONSTRAINT `commandes_ibfk_1` FOREIGN KEY (`id_client`) REFERENCES `Clients` (`id_client`);

--
-- Contraintes pour la table `Livraisons`
--
ALTER TABLE `Livraisons`
  ADD CONSTRAINT `livraisons_ibfk_1` FOREIGN KEY (`id_commande`) REFERENCES `Commandes` (`id_commande`),
  ADD CONSTRAINT `livraisons_ibfk_2` FOREIGN KEY (`id_chauffeur`) REFERENCES `Chauffeurs` (`id_chauffeur`),
  ADD CONSTRAINT `livraisons_ibfk_3` FOREIGN KEY (`id_adresse`) REFERENCES `AdressesChantier` (`id_adresse`);

--
-- Contraintes pour la table `Rapports`
--
ALTER TABLE `Rapports`
  ADD CONSTRAINT `rapports_ibfk_1` FOREIGN KEY (`id_livraison`) REFERENCES `Livraisons` (`id_livraison`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
