# pan-automator-cli
A script to generate a Panorama ( PaloAltoNetworks ) network stack/template & device group via YAML & Jinja2.
The script will generate PAN/OS command line and leverage PANOS  API to push the entire config on Panorama.

## Explanation & Motivation
This script is an evolution of my original small project pan-automator-cli but now support Device Group and automatic push via API.

## How does it work
The script will read your YAML file, get the variables, fill the Jinja2 and generate API call ready to be pushed in Panorama.
Once done it will use the credentials provided in CLI to push the entire configuration to Panorama.

```
hostname: akira

interfaces:

 - id: ethernet1/1
   address: 192.168.1.254/24
   zone: trust
   comment: trust_Zone
   dhcprelay: True

 - id: ethernet1/2
   address: 192.168.2.254/24
   zone: untrust
   comment: trust_Zone
   dhcprelay: False
....
   
routes:
 - name: default_route
   destination: 0.0.0.0/0
   interface: ethernet1/2
   nexthop: 192.168.2.253

policies:

 - rule: r1
   source_zone: 
     - trust
   destination_zone: 
     - untrust
   source_prefix: 
     - 10.10.10.0/24
   destination_prefix: 
     - 11.0.0.0/24
   application: 
     - web-browsing
   service: 
     - application-default
   security_profile: strict
   action: allow
   logsetting: log-to-panorama
```

You can add extra interfaces, routes & policies in the YAML file if needed. The script also support multi-zone policies.
IMPORTANT: Security profile & Log Setting profile must exist on Panorama using the example above.

## How to Run it
```
$ python pan-automator-api.py -pi <panorama_ip_address> -pl <admin_username> -pp <admin_password> -ym <yaml_file>

[SUCCESS] : Creation of the temporary local configuration file

[SUCCESS] : Connecting to Panorama and pushing the configuration. The action should not exceed 1 min

...............................................................

[SUCCESS] : The template has been created on Panorama

[SUCCESS] : The stack has been created on Panorama

[SUCCESS] : The device group has been created on Panorama

[SUCCESS] : Removal of the temporary local configuration file
```
