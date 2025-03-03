# Wireless Accesspoint Configuration
    Provision and customize access points configuration.​

    Bulk AP Configuration: Automate multi-AP setup, including frequency and power settings across sites.​

    Dynamic Channel and Power Assignment: Assign channels and power levels globally or customize individually to minimize interference and enhance signal strength.​

    Centralized AP Location Management: Assign APs to specific sites and floors, facilitating organized and efficient AP deployment.​

    Reboot and Update Management: Easily reboot individual or multiple APs and update configurations through Catalyst Center with logging for audits and compliance.
### Galaxy: 
![Access Point Workflow Manager]​(https://galaxy.ansible.com/ui/repo/published/cisco/dnac/content/module/accesspoint_workflow_manager)

# Procedure
1. ## Prepare your Ansible environment:

Install Ansible if you haven't already
Ensure you have network connectivity to your Catalyst Center instance.
Checkout the project and playbooks: git@github.com:cisco-en-programmability/catalyst-center-ansible-iac.git

2. ## Configure Host Inventory:

The host_inventory_dnac1/hosts.yml file specifies the connection details (IP address, credentials, etc.) for your Catalyst Center instance.
Make sure the dnac_version in this file matches your actual Catalyst Center version.
##The Sample host_inventory_dnac1/hosts.yml

```bash
catalyst_center_hosts:
    hosts:
        catalyst_center220:
            #(Mandatory) CatC Ip address
            catalyst_center_host:  <DNAC IP Address>
            #(Mandatory) CatC UI admin Password
            catalyst_center_password: <DNAC UI admin Password>
            catalyst_center_port: 443
            catalyst_center_timeout: 60
            #(Mandatory) CatC UI admin username
            catalyst_center_username: <DNAC UI admin username> 
            catalyst_center_verify: false
            #(Mandatory) DNAC Release version
            catalyst_center_version: <DNAC Release version>
            catalyst_center_debug: true
            catalyst_center_log_level: INFO
            catalyst_center_log: true
```
