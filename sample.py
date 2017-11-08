# Sample data from power monitor(s) and publish it via RabbitMQ.
#
# Kevin Davies
# kdavies@hawaii.edu

import argparse
from drivers.measurements import LocalMeasurements, RemoteMeasurements
from drivers.messaging import MQ

# Parse arguments.
parser = argparse.ArgumentParser(description='Start sampling power monitor data.')
parser.add_argument('port', metavar='p', type=str, nargs='?', 
                    help='port where data is received', default='/dev/ttyS1')
parser.add_argument('-r, --remote', dest='remote', action='store_true',
                    help='read data from the remote PICs via XBee')
args = parser.parse_args()

# Read and publish the data.
mq = MQ()
measurements = RemoteMeasurements(callback=mq.publish) if args.remote else \
               LocalMeasurements(callback=mq.publish)
while True:
    measurements.refresh()
