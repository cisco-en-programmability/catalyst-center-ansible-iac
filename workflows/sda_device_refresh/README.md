# SDA Device Refresh Workflow

This workflow performs SDA device refresh in waves. Each `job` can contain multiple source-to-replacement refresh pairs that share the same fabric site and, when needed, the same LAN automation session.

It composes the existing brownfield building blocks:

- `sda_fabric_discover_and_onboard_fabric_devices`
- `sda_port_assignment_migration`
- `sda_device_removal_and_unprovision`

## What Runs in Bulk Per Job

For each job, the workflow batches the stages that Catalyst Center already supports in bulk:

1. Resolve all source devices.
2. Export source provision data in bulk.
3. Export source fabric data in bulk.
4. Optionally LAN automate all replacement devices that need first-time onboarding.
5. Wait for all LAN-automated replacements to become managed.
6. Apply replacement inventory roles in bulk.
7. Apply replacement provisioning in bulk.
8. Apply replacement fabric onboarding in bulk.
9. Validate all replacements in fabric in one job-level check.

Stages that remain per pair:

1. Host port migration from source to replacement.
2. Source cleanup after successful migration.

## Data Model

Top-level structure:

```yaml
sda_device_refresh:
  jobs:
    - job_name: "optional"
      fabric_site_name_hierarchy: "Global/USA/SAN JOSE/SJ_BLD23"
      lan_automation:               # optional, shared by all pairs in the job
        seed_device_management_ip_address: "204.1.1.6"
        seed_peer_device_management_ip_address: "204.1.1.2"
        seed_device_interface_names:
          - "TenGigabitEthernet1/1/1"
        ip_pools:
          - ip_pool_name: "LAN_POOL_SJ_BLD23"
            ip_pool_role: "MAIN_POOL"
          - ip_pool_name: "LAN_LINK_POOL_SJ_BLD23"
            ip_pool_role: "PHYSICAL_LINK_POOL"
      device_refreshes:
        - refresh_name: "edge_1"
          source_device:
            serial_number: "FJC27172JDX"
          replacement_device:
            onboarding_method: "lan_automation"
            serial_number: "FDO1234ABCD"
            management_ip_address: "204.1.2.110"
            expected_hostname: "SJ-ACCESS-9350-1"
          port_migration:
            interface_mappings:
              - source_interface_name: "GigabitEthernet1/0/1"
                destination_interface_name: "GigabitEthernet1/0/25"
          overrides:
            inventory_role: "ACCESS"
            device_roles:
              - "EDGE_NODE"
          cleanup_source_device: true
```

## Pair Rules

- `source_device` must define exactly one of `ip_address`, `serial_number`, or `hostname`.
- `replacement_device.onboarding_method` is required and must be either `managed` or `lan_automation`.
- For `managed` replacements, define exactly one of `ip_address`, `serial_number`, or `hostname`.
- For `lan_automation` replacements, use `serial_number` as the identifier and also provide `management_ip_address`.
- All refresh pairs in a job share the same `fabric_site_name_hierarchy`.
- All pairs using LAN automation in the same job must resolve to the same provision site. If they do not, split them into separate jobs.

## LAN Automation Input Model

When replacement devices are coming up for the first time, the job-level `lan_automation` block explicitly takes:

- `seed_device_management_ip_address`
- `seed_peer_device_management_ip_address` (optional)
- `seed_device_interface_names`
- `ip_pools`

For each replacement pair using `onboarding_method: lan_automation`, the workflow automatically builds a `discovery_devices` entry from:

- `replacement_device.serial_number`
- `replacement_device.management_ip_address`
- `replacement_device.expected_hostname` when provided

## Examples

### Example 1: One Job Refreshing Multiple Devices

```yaml
sda_device_refresh:
  jobs:
    - job_name: "sj_bld23_refresh_wave1"
      fabric_site_name_hierarchy: "Global/USA/SAN JOSE/SJ_BLD23"
      lan_automation:
        seed_device_management_ip_address: "204.1.1.6"
        seed_peer_device_management_ip_address: "204.1.1.2"
        seed_device_interface_names:
          - "TenGigabitEthernet1/1/1"
          - "TenGigabitEthernet1/1/2"
        ip_pools:
          - ip_pool_name: "LAN_POOL_SJ_BLD23"
            ip_pool_role: "MAIN_POOL"
          - ip_pool_name: "LAN_LINK_POOL_SJ_BLD23"
            ip_pool_role: "PHYSICAL_LINK_POOL"
      device_refreshes:
        - refresh_name: "edge_1"
          source_device:
            serial_number: "FJC27172JDX"
          replacement_device:
            onboarding_method: "lan_automation"
            serial_number: "FDO1234ABCD"
            management_ip_address: "204.1.2.110"
            expected_hostname: "SJ-ACCESS-9350-1"
          cleanup_source_device: true
        - refresh_name: "edge_2"
          source_device:
            hostname: "SJ-ACCESS-9300-2"
          replacement_device:
            onboarding_method: "lan_automation"
            serial_number: "FDO1234EFGH"
            management_ip_address: "204.1.2.111"
            expected_hostname: "SJ-ACCESS-9350-2"
          cleanup_source_device: true
        - refresh_name: "edge_3_managed"
          source_device:
            ip_address: "204.1.2.71"
          replacement_device:
            onboarding_method: "managed"
            hostname: "SJ-ACCESS-9350-3"
          cleanup_source_device: true
```

### Example 2: Managed Replacements Only

```yaml
sda_device_refresh:
  jobs:
    - job_name: "sj_bld23_managed_refresh_wave2"
      fabric_site_name_hierarchy: "Global/USA/SAN JOSE/SJ_BLD23"
      device_refreshes:
        - refresh_name: "edge_4"
          source_device:
            serial_number: "FJC27190001"
          replacement_device:
            onboarding_method: "managed"
            serial_number: "FDO1234IJKL"
          cleanup_source_device: true
        - refresh_name: "edge_5"
          source_device:
            hostname: "SJ-ACCESS-9300-5"
          replacement_device:
            onboarding_method: "managed"
            hostname: "SJ-ACCESS-9350-5"
          cleanup_source_device: true
```

## Files

- `playbook/sda_device_refresh_playbook.yml`
- `playbook/tasks/refresh_single_device.yml`
- `playbook/tasks/prepare_refresh_pair_context.yml`
- `playbook/tasks/enrich_refresh_pair_context.yml`
- `playbook/tasks/finalize_refresh_pair_context.yml`
- `playbook/tasks/migrate_refresh_pair.yml`
- `playbook/tasks/cleanup_refresh_pair.yml`
- `schema/sda_device_refresh_schema.yml`
- `vars/sda_device_refresh_input.yml`

## Validate the Schema

```bash
yamale -s workflows/sda_device_refresh/schema/sda_device_refresh_schema.yml \
  workflows/sda_device_refresh/vars/sda_device_refresh_input.yml
```

## Run the Workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install cisco.catalystcenter --force

export HOSTIP=<catalyst-center-ip-or-fqdn>
export CATALYST_CENTER_USERNAME=<username>
export CATALYST_CENTER_PASSWORD='<password>'

ansible-playbook -i ./inventory/demo_lab/hosts.yaml \
  ./workflows/sda_device_refresh/playbook/sda_device_refresh_playbook.yml \
  --extra-vars VARS_FILE_PATH=${PWD}/workflows/sda_device_refresh/vars/sda_device_refresh_input.yml \
  -vvvv
```

## Summary Behavior

- The workflow reports results per job and per refresh pair.
- Bulk onboarding failures fail the whole job before migration starts.
- Migration failures are isolated to the affected pair.
- Source cleanup runs only for pairs whose migration succeeded and whose `cleanup_source_device` flag is `true`.
- The summary does not include skipped counters.
