#!/usr/bin/env python3

import argparse
import time
from datetime import datetime
import random

from kazoo.client import KazooClient, NodeExistsError
import os


class ApplicationNode(object):

    lock_time: int

    def __init__(self, chroot, lock_path, lock_identifier, zookeeper_hosts, node_name):
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)
        self.patch_chroot = chroot
        self.lock_path = lock_path
        self.lock_identifier = lock_identifier
        self.connect()
        self.chroot()
        try:
            self.zookeeper.create(path=node_name, ephemeral=True, makepath=True)
        except:
            pass


    def connect(self):
        self.zookeeper.start()

    def chroot(self):
        self.zookeeper.ensure_path(self.patch_chroot)
        self.zookeeper.chroot = self.patch_chroot

    def lock(self):
        lock = self.zookeeper.Lock(self.lock_path, self.lock_identifier)
        with lock:
            lock_time = random.randint(5, 15)
            print("At {0} the {1} got lock {2} (will sleep for {3}s)".format(
                (datetime.now()).strftime("%B %d, %Y %H:%M:%S"), self.lock_identifier,
                self.lock_path,
                lock_time)
            )
            time.sleep(lock_time)

    def __del__(self):
        self.zookeeper.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root')
    parser.add_argument('--lock_path')
    parser.add_argument('--lock_identifier')
    parser.add_argument('--node_name')


    servers = os.environ['ZOO_SERVERS']
    args = parser.parse_args()
    print("Servers will be used", servers)
    locker = ApplicationNode(lock_path=args.lock_path, lock_identifier=args.lock_identifier, chroot=args.root, zookeeper_hosts=servers,
            node_name=args.node_name)

    while True:
        locker.lock()