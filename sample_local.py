# Sample data from the local power monitor and publish it via RabbitMQ.
#
# Kevin Davies
# kdavies@hawaii.edu

from drivers.measurements import LocalMeasurements
from drivers.messaging import MQ

mq = MQ()
measurements = LocalMeasurements(callback=mq.publish)

while True:
    measurements.refresh()
