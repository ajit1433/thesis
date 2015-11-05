-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 15, 2015 at 10:12 AM
-- Server version: 5.5.44-0ubuntu0.14.04.1
-- PHP Version: 5.5.9-1ubuntu4.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `thesis_tor`
--

-- --------------------------------------------------------

--
-- Table structure for table `delay_tor_vpn`
--

CREATE TABLE IF NOT EXISTS `delay_tor_vpn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vmid` varchar(20) NOT NULL,
  `call_id` varchar(50) NOT NULL,
  `dirty` tinyint(1) NOT NULL DEFAULT '0',
  `or1_hash` varchar(50) NOT NULL,
  `or2_hash` varchar(50) NOT NULL,
  `or3_hash` varchar(50) NOT NULL,
  `or1_name` varchar(50) NOT NULL,
  `or2_name` varchar(50) NOT NULL,
  `or3_name` varchar(50) NOT NULL,
  `iperf_output` text NOT NULL,
  `wav` varchar(50) DEFAULT NULL,
  `pcap` varchar(50) DEFAULT NULL,
  `rfactor` decimal(11,2) NOT NULL DEFAULT '0.00',
  `pesq` decimal(11,2) NOT NULL DEFAULT '0.00',
  `experiment_id` int(11) NOT NULL DEFAULT '1',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `call_id` (`call_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
