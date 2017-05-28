# Quick Setup Guide:

This guide assumes that the user has MySQL 5.7+ installed and has a user
with CREATE, CREATE_USER, CREATE_TEMPORARY_TABLE, GRANT_OPTION, DROP, INDEX, SELECT, and UPDATE
privileges.

To quickly setup the database run the command below:

`$ mysql -u <user> -p < setup.mysql`

To cleanup everything done by the setup script run the command below:

`$ mysql -u <user> -p < cleanup.mysql`

**Note: <user> must have all aforementioned privileges.**

Below is all of the information created by the setup script:

- DATABASE:

   `SearchEngineDB` - Database used for all project transactions
- TABLES:

   `Words`        - All words found from the crawler
   
   `Links`        - All links found from the crawler
   
   `WordMeta`     - Information about each word
   
   `Hyperlinks`   - The link ids that are related to one another
   
- USERS:

   `searchEngineUser` - The user used for all project transactions
   
## Database Schema
#### Words
|id|word  |
|--|------|
|1 |computer |

#### Links
|id|link|
|-|-|
|5|csc.calpoly.edu|
|7|calpoly.edu|

#### WordMeta
|wordId|linkId|position|
|-|-|-|
|1|5|15|

#### Hyperlinks
|baselink|hyperlink|
|-|-|
|5|7|
