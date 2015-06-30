import uuid
from construct import *

class IpAddressAdapter(Adapter):
    def _encode(self, obj, context):
        return "".join(chr(int(b)) for b in obj.split("."))
    def _decode(self, obj, context):
        return ".".join(str(ord(b)) for b in obj)

class UUID4Adapter(Adapter):

    def _encode(self,obj,context):
        return obj.replace('-','')

    def _decode(self,obj,context):
        first = obj[0:8]
        second = obj[8:12]
        third = obj[12:16]
        fourth = obj[16:20]
        fifth = obj[20:32]

        return '{first}-{second}-{third}-{fourth}-{fifth}'.format(first=first,
                                                                second=second,
                                                                  third=third,
                                                                  fourth=fourth,
                                                                  fifth=fifth)

rnd = uuid.uuid4()
PAYLOAD_BOT_ID = Struct('bot_id',
                    UBInt8("length"),
                    Bytes('bot_name',lambda ctx : ctx.length),
                )


PAYLOAD_STATUS = Enum(UBInt8('status'),
                      SENT = 1,
                      RECEIVED = 2,
                      COMPLETED = 3
                )
print PAYLOAD_STATUS.build('SENT')
PAYLOAD_TIMESTAMPS = Struct('timestamps',
                        UBInt32('sent'),
                        UBInt32('received'),
                        UBInt32('completed')
                        )
PAYLOAD_ADDRESSES = Struct('addresses',
                        IpAddressAdapter(Bytes('source_ip',4)),
                        UBInt16('source_port'),
                        IpAddressAdapter(Bytes('destination_ip',4)),
                        UBInt16('destination_port')
                        )

PAYLOAD_ID = UUID4Adapter(Bytes('payload_id',32))
PAYLOAD_HEADERS = Struct('payload_headers',
                        PAYLOAD_TIMESTAMPS,
                        PAYLOAD_STATUS,
                        PAYLOAD_ADDRESSES,
                        PAYLOAD_BOT_ID,
                        PAYLOAD_ID
                        )

timestamp = PAYLOAD_TIMESTAMPS.build(Container(sent=1433990675,
                                               received=0,
                                               completed=0)
                                     )
status = PAYLOAD_STATUS.build('\x01')
source = PAYLOAD_ADDRESSES.build(Container(source_ip='127.0.0.1',
                                        source_port=148,
                                        destination_ip='104.13.11.111',
                                        destination_port=332)
                              )
bot_id = PAYLOAD_BOT_ID.build(Container(length=11,bot_name='FuckOffbot2'))
random_id = PAYLOAD_ID.build(str(rnd))

headers = '{t}{s}{sc}{b}{r}'.format(t=timestamp,
                                  s=status,
                                  sc=source,
                                  b=bot_id,
                                  r=random_id)
print len(headers)
payload = PAYLOAD_HEADERS.parse(headers)
print payload



