from iron_mq import IronMQ,Queue

ironmq = IronMQ(project_id='5581dbf2a467f20006000093',
                token='J5A03FJdzjAgPeKWecFLx-UE1kw')
print ironmq.queues()
