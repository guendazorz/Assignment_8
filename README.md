# Assignment 8 – Networking Automation with Python (IPv6, DHCP, AWS)

## Overview
This project demonstrates an automated DHCP assignment system using Python, Django, and MongoDB.
It allocates both IPv4 and IPv6 addresses dynamically and stores lease information in MongoDB,
deployed across two AWS EC2 instances.

## Architecture
- **Web Server (Django)** – Handles DHCP requests and web interface.
- **MongoDB Server** – Stores assigned IP leases.
- **AWS VPC** – Private network linking both instances.

## Features
- IPv4 & IPv6 support  
- Lease expiration logic  
- MongoDB backend for persistence  
- Dynamic web UI for assignment and lease viewing

## Deployment
- Django running on port 8000 (WebServer EC2)
- MongoDB on port 27017 (MongoDB EC2)
- Connected via private IP within the same VPC

## Example
```json
{
  "mac_address": "00:1A:2B:3C:4D:5E",
  "dhcp_version": "DHCPv6",
  "assigned_ip": "2001:db8::021a:2bff:fe3c:4d5e",
  "lease_time": "3600 seconds"
}
