# Copyright 2018 Cable Television Laboratories, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from drp_python.subnet import Subnet, get_all_subnets
from drp_python.network_layer.http_session import HttpSession
from drp_python.exceptions.drb_exceptions import NotFoundError, \
    AlreadyExistsError
from drp_python.model_layer.subnet_config_model import SubnetConfigModel
import logging
from uuid import uuid4

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] '
           '%(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.WARNING)

logger = logging.getLogger('drp-python')

# TODO: Replace this with some kinda of inject for address and such
login = {'username': 'rocketskates', 'password': 'r0cketsk8ts'}
subnet_object = {
    'address': '10.197.111.0',
    'broadcast_address': '10.197.111.255',
    'default_lease': 7200,
    'dn': 'cablelabs.com',
    'dns': '8.8.8.8',
    'listen_iface': 'eno1',
    'max_lease': 7200,
    'name': 'subnet-' + str(uuid4()),
    'netmask': '255.255.255.0',
    'range': '10.197.111.12 10.197.111.16',
    'router': '10.197.111.1',
    'next_server': '10.197.111.131',
    'type': 'management'
}


class SubnetTest(unittest.TestCase):

    def setUp(self):
        self.session = HttpSession('https://10.197.113.126:8092',
                                   login['username'],
                                   login['password'])

        self.subnet_config = SubnetConfigModel(**subnet_object)
        self.subnet = Subnet(self.session, self.subnet_config)

    def tearDown(self):
        if self.subnet is not None:
            self.subnet.delete()

    """
    Tests for functions located in SubnetHttps
    1. Create it if it doesn't exist
    2. Verify the subnet_model equals the subnet_config
    3. Update the subnet
    4. Verify the update matches the subnet_config
    5. Get all subnets
    6. Validate the count
    7. Delete the subnet
    8. Validate it was deleted
    """

    def test_basic_create_subnet_flow(self):
        if not self.subnet.is_valid():
            self.subnet.create()
        model = self.subnet.get()
        self.assertEqual(model.address, self.subnet_config.address)
        self.assertEqual(model.broadcast_address,
                         self.subnet_config.broadcast_address)
        self.assertEqual(model.default_lease, self.subnet_config.default_lease)
        self.assertEqual(model.dn, self.subnet_config.dn)
        self.assertEqual(model.listen_iface, self.subnet_config.listen_iface)
        self.assertEqual(model.max_lease, self.subnet_config.max_lease)
        self.assertEqual(model.netmask, self.subnet_config.netmask)
        self.assertEqual(model.range, self.subnet_config.range)
        self.assertEqual(model.router, self.subnet_config.router)
        self.assertEqual(model.next_server, self.subnet_config.next_server)
        self.assertEqual(model.type, self.subnet_config.type)
        self.assertEquals(model.extension, {})
        self.assertTrue(model.available)
        self.assertEqual(model.errors, [])
        self.assertTrue(model.validated)
        self.assertFalse(model.read_only)

        self.subnet_config.default_lease = 8000
        self.subnet_config.max_lease = 8000
        self.subnet_config.range = '10.197.111.10 10.197.111.20'

        self.subnet.update(self.subnet_config)

        temp = self.subnet.get()
        self.assertEqual(self.subnet_config.range, temp.range)
        self.assertEqual(self.subnet_config.max_lease, temp.max_lease)
        self.assertEqual(self.subnet_config.default_lease, temp.default_lease)

        temp = get_all_subnets(self.session)
        count = len(temp)

        self.subnet.delete()
        self.assertFalse(self.subnet.is_valid())

        temp = get_all_subnets(self.session)
        self.assertEqual(len(temp), count-1)

        try:
            self.subnet.get()
            self.fail('Resource should be deleted')
        except NotFoundError:
            self.assertTrue(True)

    def test_create_existing_subnet_flow(self):
        self.subnet.create()
        self.assertTrue(self.subnet.is_valid())
        try:
            self.subnet.create()
            self.fail('Should throw already exists error')
        except AlreadyExistsError as error:
            print error
