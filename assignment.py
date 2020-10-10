#!/usr/bin/env python
import argparse
import openstack

import time

connection = openstack.connect(cloud_name='openstack')

IMAGE = 'ubuntu-minimal-16.04-x86_64'
FLAVOUR = 'c1.c1r1'
KEYPAIR = 'tawaab1-key'
NETWORK = 'tawaab1-network'
GROUP = 'assignment2'
SUBNET_NAME = 'tawaab1-subnet'
IP_VERSION='4'
CIDR='192.168.50.0/24'


def create():
    ''' Create a set of Openstack resources '''

    '''Creating the network - tawaab1-network'''
    network = connection.network.find_network('tawaab1-network')
    if network is None:
        network = connection.network.create_network(name='tawaab1-network')
        print("Network created")
    else: 
        print("Network already exists")

    '''Creating the subnet - tawaab1-subnet'''

    subnet = connection.network.find_subnet('tawaab1-subnet')
    if subnet is None:
         subnet = connection.network.create_subnet(
         name=SUBNET_NAME,
         network_id=network.id,
         ip_version=IP_VERSION,
         cidr=CIDR
         )
         print("Subnet created")
    else:
         print("Subnet already exists")

    '''Creating the Router - tawaab1-rtr'''
    public_net = connection.network.find_network('public-net')
    tawaab1_rtr = connection.network.find_router('tawaab1-rtr')

    if tawaab1_rtr is None:
        tawaab1_rtr = connection.network.create_router(name='tawaab1-rtr',
        admin_state_up=True,
        ext_gateway_net_id=public_net.id)
        print("Router created")

    else:
        print("Router already exists")

    image = connection.compute.find_image(IMAGE)
    flavor = connection.compute.find_flavor(FLAVOUR)
    keypair2 = connection.compute.find_keypair(KEYPAIR)
    network2 = connection.network.find_network(NETWORK)
    group = connection.network.find_security_group(GROUP)

    '''Creating the server'''

    server = connection.compute.find_server('tawaab1-web')
    if server is None:
           print("Creating the Web server")
           server = connection.compute.create_server(
            name ='tawaab1-web',
            image_id=image.id,
            flavor_id=flavor.id,
            key_name=keypair2.name,
            networks=[{"uuid": connection.network.find_network(NETWORK).id}],
            security_groups=[{"sgid": group.id}]
         )
    else:
            print("Web server already exists")

    server2 = connection.compute.find_server('tawaab1-app')
    if server2 is None:
        print("Creating the App server")
        server2 = connection.compute.create_server(
                name='tawaab1-app',
                image_id=image.id,
                flavor_id=flavor.id,
                key_name=keypair2.name,
                networks=[{"uuid": connection.network.find_network(NETWORK).id}],
                security_groups=[{"sgid": group.id}]
                )
    else:
        print("App server already exists")

    server3 = connection.compute.find_server('tawaab1-db')
    if server3 is None:
        print("Creating the DB server")
        server3 = connection.compute.create_server(
                name='tawaab1-db',
                image_id=image.id,
                flavor_id=flavor.id,
                key_name=keypair2.name,
                networks=[{"uuid": connection.network.find_network(NETWORK).id}],
                security_groups=[{"sgid": group.id}]
                )
    else:
        print("DB server already exists")

        '''Create and Assign the floating IP'''
        server = connection.compute.find_server('tawaab1-web')
        floating_ip = connection.network.create_ip(floating_network_id=public_net.id)
        connection.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

def run():
    ''' Start  a set of Openstack virtual machines
    if they are not already running.
    '''
    server_list = ['tawaab1-web', 'tawaab1-app', 'tawaab1-db']
    for serv in server_list:
        server = connection.compute.find_server(serv)
        if server is None:
            print("Attempted to start " + serv + " but it doesn't exist")
        else:
            if connection.compute.get_server(server).status != "ACTIVE":
                connection.compute.start_server(server)
            else:
                print(serv + " is already active")



def stop():
    ''' Stop  a set of Openstack virtual machines
    if they are running.
    '''
    server_list = ['tawaab1-web', 'tawaab1-app', 'tawaab1-db']
    for serv in server_list:
        server = connection.compute.find_server(serv)
        if server is None:
            print(serv + "not found")
        else:
            if connection.compute.get_server(server).status == "ACTIVE":
                connection.compute.stop_server(server)
                print(serv + " has been stopped successfully")
            else:
                print(serv + " is not active so has not been changed")


def destroy():
    ''' Tear down the set of Openstack resources 
    produced by the create action
    '''
    server_list = ['tawaab1-web', 'tawaab1-app', 'tawaab1-db']
    for serv in server_list:
        server = connection.compute.find_server(serv)
        if server is None:
            print(serv + " server already does not exist")
        else:
            connection.compute.delete_server(server)
            print(serv + "server has been deleted")

    tawaab1_rtr = connection.network.find_router('tawaab1-rtr')
    if tawaab1_rtr is None:
        print("router already does not exist")
    else:
        connection.network.delete_router(tawaab1_rtr)
        print("router has been deleted")

    time.sleep(5)
    tawaab1_subnet = connection.network.find_subnet('tawaab1-subnet')
    if tawaab1_subnet is None:
        print("subnet already does not exist")
    else:
        connection.network.delete_subnet(tawaab1_subnet)
        print("subnet has been deleted")

    tawaab1_network = connection.network.find_network('tawaab1-network')
    if tawaab1_network is None:
        print("network already does not exist")
    else:
        connection.network.delete_network(tawaab1_network)
        print("network has been deleted")


def status():
    ''' Print a status report on the OpenStack
    virtual machines created by the create action.
    '''
    server_list = ['tawaab1-web', 'tawaab1-app', 'tawaab1-db']
    for serve in server_list:
        server = connection.compute.find_server(serve)
        if server is None:
            print(serve + " was not found")
        else:
            server = connection.compute.get_server(server)
            status = server.status
            print(serve + " status is " + status)


### You should not modify anything below this line ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        help='One of "create", "run", "stop", "destroy", or "status"')
    args = parser.parse_args()
    operation = args.operation

    operations = {
        'create'  : create,
        'run'     : run,
        'stop'    : stop,
        'destroy' : destroy,
        'status'  : status
        }

    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))
    action()