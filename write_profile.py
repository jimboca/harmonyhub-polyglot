#!/usr/bin/python

import yaml
from pyharmony import ha_get_token,ha_get_client

pfx = "write_profile:"

config_file = open('config.yaml', 'r')
config_data = yaml.load(config_file)
config_file.close

# TODO: Check that server node & name are defined.
#if 'server' in config and config['host'] is not None:
#    # use what the user has defined.
#    this_host = config['host']

NODEDEF_TMPL_A = """
  <nodeDef id="%s" nodeType="139" nls="%s">
    <sts>
      <st id="ST" editor="HUBST" />
      <st id="GV3" editor="%s" />
    </sts>
    <cmds>
      <sends>
	<cmd id="DON" />
      </sends>
      <accepts>
        <cmd id="SET_ACTIVITY">
          <p id="" editor="%s" init="%s"/>
        </cmd>
	<cmd id="REBOOT" />
	<cmd id="QUERY" />
      </accepts>
    </cmds>
  </nodeDef>
"""
NODEDEF_TMPL_D = """
  <nodeDef id="%s" nodeType="139" nls="%s">
    <sts />
    <cmds>
      <sends />
      <accepts>
        <cmd id="SET_BUTTON">
          <p id="" editor="%s"/>
        </cmd>
      </accepts>
    </cmds>
  </nodeDef>
"""
EDITOR_TMPL_S = """
  <editor id="%s">
    <range uom="25" subset="%s" nls="%s"/>
  </editor>
"""
EDITOR_TMPL_MM = """
  <editor id="%s">
    <range uom="25" min="%d" max="%d" nls="%s"/>
  </editor>
"""
# The NLS entries for the node definition
NLS_NODE_TMPL = """
ND-%s-NAME = %s
ND-%s-ICON = Input

"""
# The NLS entry for each indexed item
NLS_TMPL = "%s-%d = %s\n"

nodedef = open("profile/nodedef/custom.xml", "w")
editor  = open("profile/editor/custom.xml", "w")
nls     = open("profile/nls/en_US_c.txt", "w")

editor.write("<editors>\n")
nodedef.write("<nodeDefs>\n")

for key in config_data:
    if key != "server":
        host = config_data[key]['host']
        name = config_data[key]['name']
        info = "Hub: %s '%s'" % (key,name)
        nodedef.write("\n  <!-- === %s -->\n" % (info))
        nodedef.write(NODEDEF_TMPL_A % (key, 'HARMONYHUB', 'Act' + key, 'Act' + key, 'GV3'))
        nls.write("\n# %s\n" % (info))
        nls.write(NLS_NODE_TMPL % (key, name, key))
        print(pfx + " Initializing Client")
        port = 5222;
        token  = ha_get_token(host, port)
        client = ha_get_client(token, host, port)
        print(pfx + " Client: " + str(client))
        harmony_config = client.get_config()
        client.disconnect(send_close=True)
        ids = [0]
        for a in harmony_config['activity']:
            # Print the Harmony Activities to the log
            print("%s Activity: %s  Id: %s" % (pfx, a['label'], a['id']))
            if a['id'] != "-1":
                ids.append(int(a['id']))
                nls.write(NLS_TMPL % (key.upper(), int(a['id']), a['label']))
        ids.sort()                
        editor.write(EDITOR_TMPL_S % ('Act'+key,",".join(map(str,ids)),key.upper()))
        for d in harmony_config['device']:
            info = "Device '%s', Type=%s, Manufacturer=%s, Model=%s" % (d['label'],d['type'],d['manufacturer'],d['model'])
            nodedef.write("\n  <!-- === %s -->" % info)
            nodedef.write(NODEDEF_TMPL_D % ('d' + d['id'], 'D' + d['id'], 'Btn' + d['id']))
            nls.write("\n# %s" % info)
            nls.write(NLS_NODE_TMPL % ('d' + d['id'], d['label'], 'd' + d['id']))
            print("%s   Device: %s  Id: %s" % (pfx, d['label'], d['id']))
            i = -1
            for cg in d['controlGroup']:
                for f in cg['function']:
                    i += 1
                    print("%s     Function: Name: %s  Label: %s" % (pfx, f['name'], f['label']))
                    #nls.write("# Button name: %s, label: %s\n" % (f['name'], f['label']))
                    nls.write(NLS_TMPL % ('BTN' + d['id'], i, f['name']))
            editor.write(EDITOR_TMPL_MM % ('Btn' + d['id'], 0, i, 'BTN' + d['id']))

editor.write("</editors>")
nodedef.write("</nodeDefs>")
            
nodedef.close()
editor.close()
nls.close()

print(pfx + " done.")
exit
