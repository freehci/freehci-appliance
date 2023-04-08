# file: models/vncCommand.py
#
# This is a simple example of how to use the vncdotool API to automate a VNC-server.
# This example is used to automate the installation of ESXi 7.0 on a Dell PowerEdge R740xd.


from vncdotool import api


client = api.connect('192.168.1.100::5900', password='myvncpassword')

# Press and release F2
client.keyPress('F2')
client.keyRelease('F2')

# Type "root" and press Enter
client.type('root')
client.keyPress('enter')
client.keyRelease('enter')

# Type "Passw0rd!" and press Enter
client.type('Passw0rd!')
client.keyPress('enter')
client.keyRelease('enter')

# Press arrow down 6 times
for _ in range(6):
    client.keyPress('down')
    client.keyRelease('down')

# Press and release Alt+F1
client.keyPress('alt')
client.keyPress('F1')
client.keyRelease('F1')
client.keyRelease('alt')

# Type "root" and press Enter
client.type('root')
client.keyPress('enter')
client.keyRelease('enter')

# Type "Passw0rd!" and press Enter
client.type('Passw0rd!')
client.keyPress('enter')
client.keyRelease('enter')

# Configure the portgroups
client.type('esxcli network vswitch standard portgroup set -v 3884 -p "VM Network"')
client.keyPress('enter')
client.keyRelease('enter')

client.type('esxcli network vswitch standard portgroup set -v 3939 -p "Private VM Network"')
client.keyPress('enter')
client.keyRelease('enter')

# Disconnect from the VNC-server
client.disconnect()
