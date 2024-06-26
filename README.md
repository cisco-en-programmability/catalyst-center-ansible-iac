# catalyst-center-ansible-iac
[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/DNACENSolutions/dnac_ansible_workflows)
[![Run in Cisco Cloud IDE](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-runable-icon.svg)](https://developer.cisco.com/codeexchange/devenv/DNACENSolutions/dnac_ansible_workflows/)
# dnac_ansible_workflows
Sample Playbooks for workflows to automate Cisco Catalyst Center configurations through cisco.dnac ansible workflow modules. This include Playbooks, Sample inputs and Sample Inventory files.
- A pre-built set of Ansible roles and playbooks: Specifically tailored for Catalyst Center configuration and network deployment.
- Easy to use: Leverages the simplicity of Ansible with the power of Catalyst Center for efficient automation.
- Cisco Validated: Ensures compatibility and functionality with your Cisco devices and Catalyst Center environment.
## What is included?
- Pre-built playbooks for common Catalyst Center tasks, ready to use or customize.
- Sample Inputs to be used as reference while designing the automation using Ansible playbooks.
- Guide to setup your development environment, designing automation using Catalyst Center Workflow Playbooks, organizing inventory, and inputs.
- Guide to setup customized playbooks and creating variable files.

![Catalyst Center Ansible Workflows](https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git)

This repository contains a collection of Ansible workflows for automating Catalyst Center workflows. These workflows help streamline network provisioning, configuration, and management by leveraging the power of Ansible automation.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Update](#update)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before using these Ansible workflows, ensure that you have the following prerequisites:

- Ansible installed on your machine
- Access to a Cisco Catalyst Center instance
- Proper network connectivity to interact with the Catalyst Center APIs


## Installation
    Python 3.7+ is required to install iac-validate. Don't have Python 3.7 or later? 
    See Python 3 Installation & Setup Guide https://realpython.com/installing-python/
    Create your python virtual environment using commend:
    ```bash
        python3 -m venv python3env --prompt "AnsiblePython3 VENV"
        source python3env/bin/activate
   ```


1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git
   ```

1. Navigate to the project directory:
    
    ```bash
    cd catalyst-center-ansible-iac
    ```
2. Install the required dependencies:
   ```bash
    pip install -r requirements.txt
    ```
3. Install the collection (Galaxy link):
    ```bash
    ansible-galaxy collection install cisco.dnac --force
    ```
4.  Create your inventory
    a. Inventory:
     This folder contains inventory file for your dev, lab, sandbox or production env which will be utilised by swim playbooks.
     
     Create your inventory file in below template format to utilize the swim playbooks.
     
     The template for the inventory file is:
     ```bash
         cat inventory/demo_lab/001-dnac_inventory_template.yml
     ```

    Setup up your ansible python interpretor following suitable method for your environment : https://docs.ansible.com/ansible/latest/reference_appendices/interpreter_discovery.html
    
    b. Hairarchical variable files for inputs

        The second folder of the workflows contains playbook and var files for workflows.
        Example:
            workflows/swim
            playbooks/
                swim_workflow_playbook.yml
            schema/
                swim_schema.yml
            vars/
                vars_swim.yml

6. Var files:
        Update var file with your  details and parameter to control playbook
    
7. Playbook: 
        The playbooks can be directly used without any change when inventory and var files created in the above templates.

Schema files:
        Validate the var_file user input against playbook schema. Using the validate tool
        ```bash
            ./validate.sh -s <schema fle> -d <Vars files>
        ```
8. Executing playbook (Sample):

How to Generate your hosts inventory from Cisco Catalyst Center using inventory_gen playbook:

For brownfield Catalyst Center (Network already discovered in Catalyst Center) with devices are in inventory, then automated inventory generation can be performed through inventory_gen playbook. Following the below Steps:

Create a basic inventory file with Cisco Catalyst Center Inputs in inventory folder. for example demo_inv.yml
  ---
    ```bash
        #Inventory file for demo_lab
        catalyst_center_hosts:
            hosts:
            <dnac hostname >:
            dnac_debug: false
            dnac_host: <Cisco Catalyst Center IP Address> #(Mandatory) Cisco Catalyst Center Ip address
            dnac_password: <Cisco Catalyst Center UI admin Password> #(Mandatory) 
            dnac_port: 443 #(Mandatory) 
            dnac_username: <Cisco Catalyst Center UI admin username> #(Mandatory) 
            dnac_verify: false #(Mandatory) 
            dnac_version: <Cisco Catalyst Center Release version> #(Mandatory)  Example: 2.3.5.3
            dnac_debug: true
            dnac_log_level: INFO
            dnac_log: true
    ```


Here are a few examples of Ansible workflows available in this repository:

Example 1: Swim upgrade, this include uploading the images, golden tagging the image filtered location and device family and distributed and activating images on the networkk devices.
    
```bash
 ansible-playbook -i ./inventory_dnaccluster ./workflows/swim/playbook/swim_workflow_playbook.yml --extra-vars VARS_FILE_PATH=< Vars File PATH (Full Path or relative path from playbook)> -vvvv
```
    
Example 2: Create Sites, buildings floors using playbook : workflows/sites/playbook/site_hierarchy_playbook.yml
    
```bash
 ansible-playbook -i ./inventory_dnaccluster ./workflows/site_hierarchy/playbook/site_hierarchy_playbook.yml --extra-vars VARS_FILES_PATH=< Vars File PATH (Full Path or relative path from playbook)> -vvvv
```
    
Feel free to explore the playbooks/ directory for more examples and use cases.

## Attention macOS users:

If you're using macOS you may receive this error when running your playbook:
objc[34120]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called.
objc[34120]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called. We can't safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
ERROR! A worker was found in a dead state
If that's the case try setting this environment variable:

```bash
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## Update
Getting the latest/nightly collection build

Clone the dnacenter-ansible repository if not already cloned.
```bash
 git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git
```
    
Go to the dnacenter-ansible directory
```bash
 cd dnac_ansible_workflows
```
    
Pull the latest master from the repo if you have already cloned.
```bash
    git pull origin master
```

## Raising an issue or enhanceent request
- Visit the Catalyst Center Ansible repository: https://github.com/cisco-en-programmability/dnacenter-ansible/issues
- Click the "New Issue" button.
- Carefully follow the provided issue template, ensuring you include:
- - A clear and concise description of the problem
- - Steps to reproduce the issue.
- - Relevant code snippets or configurations, playbook, variable files.
- - Expected behavior vs. actual behavior.
- - Catalyst Center and Ansible versions you're using.

## Contributing
Contributions are welcome! To contribute to this project, follow these steps:

    Fork the repository.
    Create a new branch for your feature or bug fix.
    Make your changes and commit them with descriptive commit messages.
    Push your changes to your fork.
    Submit a pull request to the main branch of this repository.

Code of Conduct

This collection follows the Ansible project's Code of Conduct. Please read and familiarize yourself with this document.

Releasing, Versioning and Deprecation:
 Version (Beta) : More enhancement might follow based on usage feedback
