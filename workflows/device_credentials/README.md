# Device Credentials Manager Workflow playbooks
![Catalyst Center Device Credential Manager Workflow Specification] (https://docs.ansible.com/ansible/latest/collections/cisco/dnac/device_credential_workflow_manager_module.html#ansible-collections-cisco-dnac-device-credential-workflow-manager-module)

Streamlines the management of device credentials within a Cisco Catalyst Center. Key Functions includes:
- Creating Global Device Credentials: Establishes new sets of credentials (e.g., CLI usernames, passwords, SNMP, HTTPS etc.) that can be applied across multiple network devices within the Catalyst Center domain.
- Updating Global Device Credentials: Modifies existing global credentials, ensuring they remain current and secure.
- Deleting Global Device Credentials: Removes global credentials that are no longer needed.
- Assigning Credentials to Sites: Links specific global device credentials to chosen sites within your network. This allows for targeted and efficient credential deployment across the managed infrastructure.

# Catalyst Center cisco.dnac.device_credential_workflow_manager Module Parameters: 
https://cisco-en-programmability.github.io/dnacenter-ansible/v6.11.0/plugins/discovery_workflow_manager_module.html


# Creating Device Credentials vars_file:
- CLI credentials same username with different passwords:
- Duplicate CLI usernames with different supported passwords, however, keep a different description for the CLI credentials which have same username to distinguish the credentials for sites assignment.
- Enable sites verification using config_verify:
- Post site creation added validation is done using GET APIs to validate that configurations are created in Catalyst Center. This is optional and enabling this will add more time. Also, this is helpful in DEV environment for cross validation of created configs.

# Execute the sample device credentials playbook:
```bash
    Validate the Inputs using validation tool
    
    ./tools/validate.sh -s workflows/device_credentials/schema/device_credentials_schema.yml -d workflows/device_credentials/vars/device_credentials_vars.yml 
workflows/device_credentials/schema/device_credentials_schema.yml
workflows/device_credentials/vars/device_credentials_vars.yml
yamale   -s workflows/device_credentials/schema/device_credentials_schema.yml  workflows/device_credentials/vars/device_credentials_vars.yml
Validating /Users/pawansi/dnac_ansible_workflows/workflows/device_credentials/vars/device_credentials_vars.yml...
Validation success! 👍


    Run the playbook"

    ansible-playbook -i <inventory file> <Playbooks location> -e  VARS_FILES_PATH=<Vars File location>

    ansible-playbook -i host_inventory_dnac1 workflows/device_credentials/playbook/device_credentials.yml --e VARS_FILES_PATH=device_credentials_vars_file.yml -vvvv

    Sample Results:
    PLAY RECAP **********************************************************************
    catalyst_center53          : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```
