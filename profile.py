"""Setup for TAPIR for distributed transaction experiments."""

import ast
# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object,
pc = portal.Context()

portal.context.defineParameter("replicas", "Number of Replicas", portal.ParameterType.STRING, "['us-east-1-0', 'us-east-1-1', 'us-east-1-2', 'eu-west-1-0', 'eu-west-1-1', 'eu-west-1-2', 'ap-northeast-1-0', 'ap-northeast-1-1', 'ap-northeast-1-2', 'us-west-1-0', 'us-west-1-1', 'us-west-1-2', 'eu-central-1-0', 'eu-central-1-1', 'eu-central-1-2', 'ap-southeast-2-0', 'ap-southeast-2-1', 'ap-southeast-2-2']")
portal.context.defineParameter("num_sites", "Number of Sites (DCs)", portal.ParameterType.INTEGER, 6)
portal.context.defineParameter("replica_type", "Replica Hardware Type", portal.ParameterType.STRING, "m510")
portal.context.defineParameter("replica_disk_image", "Replica Disk Image", portal.ParameterType.STRING, "urn:publicid:IDN+utah.cloudlab.us+image+morty-PG0:indicus.node.server")
portal.context.defineParameter("replica_storage", "Replica Storage Space", portal.ParameterType.STRING, "64GB")
portal.context.defineParameter("clients_per_replica", "Number of Clients per Replica", portal.ParameterType.INTEGER, 1)
portal.context.defineParameter("clients_total", "Total Number of Clients", portal.ParameterType.INTEGER, 0)
portal.context.defineParameter("client_type", "Client Hardware Type", portal.ParameterType.STRING, "'m510'")
portal.context.defineParameter("client_disk_image", "Client Disk Image", portal.ParameterType.STRING, "urn:publicid:IDN+utah.cloudlab.us+image+morty-PG0:indicus.node")
portal.context.defineParameter("client_storage", "Client Storage Space", portal.ParameterType.STRING, "16GB")
portal.context.defineParameter("control_machine", "Use Control Machine?", portal.ParameterType.BOOLEAN, False)
portal.context.defineParameter("control_type", "Control Hardware Type", portal.ParameterType.STRING, "m510")

params = portal.context.bindParameters()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()
replicas = ast.literal_eval(params.replicas)
client_type = ast.literal_eval(params.client_type)

lan_list = []
total_clients = 0
for i in range(len(replicas)):
    replica = request.RawPC(replicas[i])
    site = i // params.num_sites
    lan_list.append(replica)
    replica.hardware_type = params.replica_type
    replica.disk_image = params.replica_disk_image
    replica.Site('Site %d' % site)
    replica_bs = replica.Blockstore("%s-bs" % replicas[i], "/mnt/extra")
    replica_bs.size = params.replica_storage
    replica_bs.placement = "any"
    for j in range(params.clients_per_replica):
        if params.clients_total > 0 and total_clients >= params.clients_total:
            break
        client = request.RawPC('client-%d-%d' % (i, j))
        lan_list.append(client)
        if isinstance(client_type, list):
            client.hardware_type = client_type[i % len(client_type)]
        else:
            client.hardware_type = client_type
        client.disk_image = params.client_disk_image
        client.Site('Site %d' % site)
        client_bs = client.Blockstore("client-%d-%d-bs" % (i, j), "/mnt/extra")
        client_bs.size = params.client_storage
        client_bs.placement = "any"
        total_clients += 1

if params.control_machine:
    control = request.RawPC('control')
    lan_list.append(control)
    control.hardware_type = params.control_type
    control.disk_image = params.replica_disk_image
    
lan = request.Link(members=lan_list)
lan.best_effort = True

# Print the generated rspec
pc.printRequestRSpec(request)

