# models/iDRAC.py
# Description: iDRAC model for Dell servers

# This method is used to use SSH-tunnel to the iDRAC and then to the ESXi host.
# Example only, not implemented in the API.

# The SSH-tunnel to the iDRAC works only with older versions iDRAC.
# We have created a ticket with Dell to get this fixed.

import paramiko
from sshtunnel import SSHTunnelForwarder

iDRAC_ip = '10.22.15.87'
iDRAC_username = 'root'
iDRAC_password = 'calvin'
ESXi_ip = '172.16.0.2'


with SSHTunnelForwarder(
    (iDRAC_ip, 22),
    ssh_username=iDRAC_username,
    ssh_password=iDRAC_password,
    remote_bind_address=(ESXi_ip, 22)
) as tunnel:
    local_port = tunnel.local_bind_port
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('localhost', port=local_port, username='root', password='your_esxi_password')
    
    stdin, stdout, stderr = ssh.exec_command('your_esxi_command_here')
    output = stdout.read().decode('utf-8')
    print(output)

    ssh.close()
