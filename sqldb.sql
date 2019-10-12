-- drop database WC if exists WC;
-- create database WC;
use WC;

-- grant select, insert, update, delete on WC.* to '%'@'%' identified by 'WC.123';

create table devices (
    `uuid` varchar(50) not null,
    `parid` varchar(50) not null,
    `status` bool not null,
    key `idx_parid` (`parid`),
    primary key (`uuid`)
) engine=innodb default charset=utf8;

create table toilets (
    `selfid` varchar(50) not null,
    `sex` bool not null,
    `name` varchar(50) not null,
    `parid` varchar(50) not null,
    key `idx_parid` (`parid`),
    primary key (`selfid`)
) engine=innodb default charset=utf8;

create table buildings (
    `selfid` varchar(50) not null,
    `name` varchar(50) not null,
    `parid` varchar(50) not null,
    key `idx_parid` (`parid`),
    primary key (`selfid`)
) engine=innodb default charset=utf8;

create table areas (
    `selfid` varchar(50) not null,
    `name` varchar(50) not null,
    `parid` varchar(50) not null,
    key `idx_parid` (`parid`),
    primary key (`selfid`)
) engine=innodb default charset=utf8;

create table scenes (
    `selfid` varchar(50) not null,
    `name` varchar(50) not null,
    `parid` varchar(50) not null,
    key `idx_parid` (`parid`),
    primary key (`selfid`)
) engine=innodb default charset=utf8;