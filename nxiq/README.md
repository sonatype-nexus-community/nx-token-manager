## nxiq-token-manager

### Description

Create, delete and list Nexus IQ user tokens. 
This script also allows the user to find and delete 'expired' tokens.

&#9888; Nexus IQ does not currently provide any token expiry function.
An 'expired' token is simply a token older than a user-defined period of time at runtime of this script.

By default, the age of a token is set to one year.

### Prerequisites

Python 3.10+

### Defaults

- -r = Internal (IQ Authentication realm) [SAML|Crowd|<LDAP Server Id>]
- -f = ./expire-tokens.json (*--created_since* writes 'expired' tokens to this file)

### Additional argumemts (these are mutually exclusive)

- --created_on <date in yyy-mm-dd format> - find tokens created on this date - 
- --created_since <number of days> - find tokens created since this age in days
- --delete_expired - delete 'expired' tokens  (boolean)
- --list_all - list all tokens (boolean)
- --create_token - create a token (boolean)
- --delete_token - delete a token (boolean)
- --notify - send email notification for 'expiring' tokens (boolean)

### Examples

#### List all tokens 
```bash
python3 nxiq-token-manager.py --list_all -u admin -p admin123 -s http://localhost:8070
````
#### List all tokens created on 'March 7, 2022'
```bash
python3 nxiq-token-manager.py --created_on 2022-03-07 -u admin -p admin123 -s http://localhost:8070
````
#### List all local user tokens that are 'expired' after 1 year old or older. Writes the tokens from the file in -f
```bash
python3 nxiq-token-manager.py --created_since 365 -u admin -p admin123 -s http://localhost:8070
```
#### List all local user tokens that are 'expired' after 30 days or older Writes the tokens from the file in -f
```bash
python3 nxiq-token-manager.py --created_since 30 -u admin -p admin123 -s http://localhost:8070
```
#### List all tokens that are 'expired' after 1 year old or older for SAML users. Writes the tokens from the file in -f
```bash
python3 nxiq-token-manager.py ---created_since 365 -r SAML -u admin -p admin123 -s http://localhost:8070
```
#### Remove 'expired' tokens. Reads the tokens from the file in -f
```bash
python3 nxiq-token-manager.py --delete_expired -u admin -p admin123 -s http://localhost:8070
```
#### Create a token for a  user
```bash
python3 nxiq-token-manager.py --create_token -u sotudeko -p my password -s http://iqserver:8070
```
#### Delete a token for a  user
```bash
python3 nxiq-token-manager.py --delete_token -u sotudeko -p my password -s http://iqserver:8070
```
#### Send notification email to owners of expiring tokens. Reads the tokens from the file in -f
```bash
python3 nxiq-token-manager.py --notify -u admin -p admin123 -s http://iqserver:8070
```


### [The Fine Print](https://github.com/sonatype-nexus-community/nx-token-manager#the-fine-print)




