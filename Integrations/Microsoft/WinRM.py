# file: models/Microsoft/WinRM.py
#
# Description: This script retrieves the list of virtual machines in a cluster using WinRM
import winrm

host = 'your_remote_host'
username = 'your_username'
password = 'your_password'

# Create a WinRM session on the remote host
session = winrm.Session(host, auth=(username, password), transport='ntlm')

# Define the PowerShell command to retrieve the list of virtual machines in the cluster
ps_script = """
$nodes = Get-ClusterNode
Write-Output $nodes
$vm_list = Get-ClusterGroup -Cluster $env:computername  | Where-Object {$_.GroupType -eq 'VirtualMachine' -and $_.OwnerNode.Name -in $nodes.Name} | Get-VM
$vm_names = $vm_list.Name
Write-Output $vm_names
"""

# Execute the PowerShell command and retrieve the output
result = session.run_ps(ps_script)

if result.status_code == 0:
    # Parse the output to get the list of virtual machines
    vm_info = result.std_out.decode('utf-8').strip()

    # Print the list of virtual machines
    print(vm_info)
else:
    # Print the full error message
    print("Error message: " + result.std_err.decode('utf-8').strip())
