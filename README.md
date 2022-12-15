## nxiq-token-manager

### Prerequisites

Python 3.10+

### Defaults

- -u = admin
- -p = admin123
- -s = http://localhost:8070
- -m = Mode 
- -r = Internal IQ Authentication realm
- -a = 365 (period at which tokens expire - days)

### Examples

#### List all tokens (with defaults)
```bash
python3 nxiq-token-manager -m list
````
#### List all tokens that are 'expired' at 1 year old or older (with defaults)
```bash
python3 nxiq-token-manager
```
#### List all tokens that are 'expired' at 30 days or older (with defaults)
```bash
python3 nxiq-token-manager -a 30
```
#### List all tokens that are 'expired' at 1 year old or older using SAML authentication (with defaults)
```bash
python3 nxiq-token-manager -r SAML
```
#### Remove 'expired' tokens that are 1 year old or older (with defaults)
```bash
python3 nxiq-token-manager -m delete_expired 
```
#### Create a token (with default admin user credentials and server)
```bash
python3 nxiq-token-manager -create
```
#### Create a token for a local user
```bash
python3 nxiq-token-manager -m create -u sotudeko -p my password -s http://iqserver:8070
```
#### Create a token for a SAML user
```bash
python3 nxiq-token-manager -m create -u sotudeko -p my password -s http://iqserver:8070 -r SAML
```






