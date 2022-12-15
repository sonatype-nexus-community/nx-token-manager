## nxiq-token-manager

### Prerequisites

Python 3.10+

### Defaults

User (-u) = admin
Password (-p) = admin123
Server (-s) = http://localhost:8070
Mode (-m) = list
IQ Authentication realm (-r) = Internal
Expire (-x) = False
Age (-a) = 365 (days)

### Examples

#### List all tokens (with defaults)
```bash
python3 nxiq-token-manager
````
#### List all tokens that are 1 year old or older
```bash
python3 nxiq-token-manager -m expire
```
#### List all tokens that are 30 days or older
```bash
python3 nxiq-token-manager -m expire -a 30
```
#### List all tokens that are 1 year old or older using SAML authentication
```bash
python3 nxiq-token-manager -m list -r SAML
```
#### Expire all tokens that are 1 year old or older
```bash
python3 nxiq-token-manager -m expire -x
```
#### Create a token (with default admin user credentials and server)
```bash
python3 nxiq-token-manager -create
```
#### Create a token for a local user
```bash
python3 nxiq-token-manager -m create -u sotudeko -p my password -s http://iqserver:8070
```






