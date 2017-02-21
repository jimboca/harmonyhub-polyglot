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

NODEDEF_TMPL = """
  <nodeDef id="%s" nodeType="139" nls="HARMONYHUB">
    <sts>
      <st id="ST" editor="HUBST" />
      <st id="GV3" editor="Act%s" />
    </sts>
    <cmds>
      <sends>
	<cmd id="DON" />
      </sends>
      <accepts>
        <cmd id="SET_ACTIVITY">
          <p id="" editor="Act%s" init="GV3"/>
        </cmd>
	<cmd id="REBOOT" />
	<cmd id="QUERY" />
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
ND-%s-ICON = Input"""
# The NLS entry for each indexed item
NLS_TMPL = "%s-%d = %s"

for key in config_data:
    if key != "server":
        host = config_data[key]['host']
        name = config_data[key]['name']
        print NODEDEF_TMPL % (key, key, key)
        print NLS_NODE_TMPL % (key, name, key)
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
                print NLS_TMPL % (key.upper(), int(a['id']), a['label'])
        ids.sort()                
        print EDITOR_TMPL_S % ('Act'+key,",".join(map(str,ids)),key.upper())
        for d in harmony_config['device']:
            print NLS_NODE_TMPL % ('d' + d['id'], d['label'], 'd' + d['id'])
            print("%s   Device: %s  Id: %s" % (pfx, d['label'], d['id']))
            #print d
            #print d['controlGroup']
            i = -1
            for cg in d['controlGroup']:
                #print cg
                for f in cg['function']:
                    i += 1
                    print("%s     Function: Name: %s  Label: %s" % (pfx, f['name'], f['label']))
                    print NLS_TMPL % ('BTN' + d['id'], i, f['label'])
            print EDITOR_TMPL_MM % ('Btn' + d['id'], 0, i, 'BTN' + d['id'])

print(pfx + " done.")
exit
