# Sample data from the remote power monitors and publish it via RabbitMQ.
#
# Kevin Davies
# kdavies@hawaii.edu

from drivers.measurements import RemoteMeasurements
from drivers.messaging import MQ

mq = MQ()
measurements = RemoteMeasurements(callback=mq.publish)

while True:
    measurements.refresh()
