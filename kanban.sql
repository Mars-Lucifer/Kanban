-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 22, 2024 at 06:28 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `kanban`
--

-- --------------------------------------------------------

--
-- Table structure for table `activation_codes`
--

CREATE TABLE `activation_codes` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `code` varchar(12) NOT NULL,
  `status` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `activation_codes`
--

INSERT INTO `activation_codes` (`id`, `user_id`, `code`, `status`) VALUES
(10, 1, '29AnTwwVCOO', 1),
(11, 2, '2qWItp4ZWQM', 1),
(12, 3, 'ReL360injoq', 1),
(13, 4, 'TuGWSphQSkr', 1),
(14, 5, 'Azd6Upe7mky', 1),
(15, 1, '1bu1YfsokvC', 0),
(16, 1, 'ZBxrVKtp5gr', 0),
(17, 1, '1ficomIoGto', 0),
(18, 2, '067Mk79bxY2', 1),
(19, 3, 'WyRlx9DX3J3', 0);

-- --------------------------------------------------------

--
-- Table structure for table `files`
--

CREATE TABLE `files` (
  `id` int(11) NOT NULL,
  `resume_id` int(11) NOT NULL,
  `file_url` varchar(255) NOT NULL,
  `mode` int(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `files`
--

INSERT INTO `files` (`id`, `resume_id`, `file_url`, `mode`) VALUES
(1, 2, 'static\\uploads\\img\\-_No4.pdf', 3),
(3, 3, 'static\\uploads\\img\\32a167de4a3ac7c9bf66a6b83066e6e2.jpg', 1),
(4, 2, 'static\\uploads\\img\\previewfile_1701938032.jpg', 1);

-- --------------------------------------------------------

--
-- Table structure for table `resumes`
--

CREATE TABLE `resumes` (
  `id` int(11) NOT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `surname` varchar(100) DEFAULT NULL,
  `patronymic` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `salary` decimal(10,2) DEFAULT NULL,
  `experience` text DEFAULT NULL,
  `dateBirth` date DEFAULT NULL,
  `telephone` varchar(15) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `education` text DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `glass` int(11) DEFAULT 1,
  `hr_fio` varchar(255) DEFAULT NULL,
  `creation_date` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `resumes`
--

INSERT INTO `resumes` (`id`, `photo`, `name`, `surname`, `patronymic`, `position`, `salary`, `experience`, `dateBirth`, `telephone`, `email`, `education`, `comment`, `glass`, `hr_fio`, `creation_date`) VALUES
(1, '\\static\\uploads\\img\\konata-izumi-konata.gif', 'Мун', 'Никита', 'Станиславович', 'Человек', 100000.00, '19', '1111-11-11', '89955376981', 'nikitarybalko897@gmail.com', '      Школьное неоконченное', 'Подписывайтесь на меня=\r\n                \r\n                \r\n                \r\n                \r\n                \r\n                ', 6, 'Никита Рыбалко', '2024-11-21 03:52:12'),
(2, '\\static\\uploads\\img\\32a167de4a3ac7c9bf66a6b83066e6e2.jpg', 'Senko', 'San', 'Kitsune', 'Kitsune', 3333333.00, '500', '1111-11-11', '+138977908200', 'keithengel@gmail.com', '   Oxf', 'cutie kitsune senko san\r\n                \r\n                \r\n                ', 3, 'Василий Абоба', '2024-11-21 19:06:55'),
(3, 'https://i.imgur.com/YdbHCxp.jpeg', 'John', 'Smith', 'None', 'Actor', 905000.00, '20', '1981-09-01', '+199840276945', 'johnsmith@gmail.com', 'oxford', 'No comments', 4, 'HR Name', '2024-11-18 22:47:38');

-- --------------------------------------------------------

--
-- Table structure for table `tags`
--

CREATE TABLE `tags` (
  `id` int(11) NOT NULL,
  `resume_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tags`
--

INSERT INTO `tags` (`id`, `resume_id`, `name`) VALUES
(2, 1, '456'),
(3, 1, '345'),
(4, 2, 'kitsune'),
(5, 2, 'senko'),
(6, 2, 'cute'),
(7, 1, '1');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  `surname` varchar(255) NOT NULL,
  `patronymic` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `verification` int(11) NOT NULL,
  `role` varchar(222) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `surname`, `patronymic`, `email`, `password`, `verification`, `role`) VALUES
(1, 'Никита', 'Рыбалко', 'Станиславович', 'nikitarybalko897@gmail.com', '12345678', 1, 'moderator'),

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activation_codes`
--
ALTER TABLE `activation_codes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `files`
--
ALTER TABLE `files`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `resumes`
--
ALTER TABLE `resumes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tags`
--
ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_unique` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activation_codes`
--
ALTER TABLE `activation_codes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `files`
--
ALTER TABLE `files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `resumes`
--
ALTER TABLE `resumes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tags`
--
ALTER TABLE `tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
