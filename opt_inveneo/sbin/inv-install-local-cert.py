#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import sys
import syslog
import subprocess as sp
import os.path
from inveneo import constants, fileutils

class InstallSelfSignedCert:
    def __init__(self):
        pass	

    def main(self):
        cert_dir=constants.INV_HUB_CERTS_PATH

        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)

	cert=os.path.join(constants.INV_HUB_CERTS_PATH, constants.INV_HUB_PUB_CERT)
	pem=os.path.join(constants.INV_HUB_CERTS_PATH, constants.INV_HUB_PEM)
	pkey=os.path.join(constants.INV_HUB_CERTS_PATH, constants.INV_HUB_PRIV_KEY)

	sys.stdout.write("key: %s\ncert: %s\npem: %s\n" % (pkey,cert,pem))

	# try to erase old files	
	for f in (cert,pem,pkey):
            fileutils.safe_delete_node(f)

        # generate a new private key
        with open(pkey, 'w') as f:
            sp.Popen(['openssl','genrsa','1024'], stdout=f).wait()

        # make private
        os.chmod(pkey, 0400)

        cnf=constants.INV_HUB_CERT_SSL_CONF
        # create self-signed cert from the key
        with open(cert,'w') as f:
            sp.Popen(['openssl','req','-new','-x509','-nodes','-sha1','-days','3650','-key',pkey,'-config',cnf,'-batch'], \
                     stdout=f).wait()

        # create pem file
        with open(pem,'w') as f:
            sp.Popen(['cat',pkey,cert],stdout=f).wait()

if __name__ == '__main__':
    if len(sys.argv) != 1:
        sys.stderr.write("Usage: %s",sys.argv[0])
        sys.exit(1)
        
    sys.exit(InstallSelfSignedCert().main())
