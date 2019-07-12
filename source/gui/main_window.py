
from PyQt5 import QtCore, QtWidgets, QtGui

class Event(object):
    """
    Base Event class for event-driven system
    """

    def __init__(self,
                 type: EventType = EventType.HEADER,
                 data: Any = None,
                 des: str = '',
                 src: str = '',
                 msgtype: MSG_TYPE = MSG_TYPE.MSG_TYPE_BASE
                 ):

        self.event_type = type
        self.data = data
        self.destination = des
        self.source = src
        self.msg_type = msgtype

    @property
    def type(self):
        return self.event_type.name

    def serialize(self):
        msg = self.destination + '|' + self.source + \
            '|' + str(self.msg_type.value)
        if self.data:
            if type(self.data) == str:
                msg = msg + '|' + self.data
            else:
                try:
                    msg = msg + '|' + self.data.serialize()
                except Exception as e:
                    print(e)
                    pass
        return msg

    def deserialize(self, msg: str):
        v = msg.split('|', 3)
        try:
            self.destination = v[0]
            self.source = v[1]
            msg2type = MSG_TYPE(int(v[2]))
            if msg2type in [MSG_TYPE.MSG_TYPE_TICK, MSG_TYPE.MSG_TYPE_TICK_L1, MSG_TYPE.MSG_TYPE_TICK_L5]:
                self.event_type = EventType.TICK
                self.data = TickData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif msg2type == MSG_TYPE.MSG_TYPE_RTN_ORDER:
                self.event_type = EventType.ORDERSTATUS
                self.data = OrderData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif msg2type == MSG_TYPE.MSG_TYPE_RTN_TRADE:
                self.event_type = EventType.FILL
                self.data = TradeData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif msg2type == MSG_TYPE.MSG_TYPE_RSP_POS:
                self.event_type = EventType.POSITION
                self.data = PositionData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif msg2type == MSG_TYPE.MSG_TYPE_BAR:
                self.event_type = EventType.BAR
                self.data = BarData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif msg2type == MSG_TYPE.MSG_TYPE_RSP_ACCOUNT:
                self.event_type = EventType.ACCOUNT
                self.data = AccountData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif msg2type == MSG_TYPE.MSG_TYPE_RSP_CONTRACT:
                self.event_type = EventType.CONTRACT
                self.data = ContractData(gateway_name=self.source)
                self.data.deserialize(v[3])
            elif v[2].startswith('11'):
                self.event_type = EventType.ENGINE_CONTROL
                self.msg_type = msg2type
                if len(v) > 3:
                    self.data = v[3]
            elif v[2].startswith('12'):
                self.event_type = EventType.STRATEGY_CONTROL
                self.msg_type = msg2type
                if len(v) > 3:
                    self.data = v[3]
            elif v[2].startswith('14'):
                self.event_type = EventType.RECORDER_CONTROL
                self.msg_type = msg2type
                if len(v) > 3:
                    self.data = v[3]
            elif v[2].startswith('3'):  # msg2type == MSG_TYPE.MSG_TYPE_INFO:
                self.event_type = EventType.INFO
                self.msg_type = msg2type
                self.data = LogData(gateway_name=self.source)
                self.data.deserialize(v[3])
            else:
                self.event_type = EventType.HEADER
                self.msg_type = msg2type
        except Exception as e:
            print(e)
            pass

class MarketDataView(QtWidgets.QWidget):
    tick_signal = QtCore.pyqtSignal(Event)
    symbol_signal = QtCore.pyqtSignal(str)

    def __init__(self, sym: str = ""):
        """"""
        super(MarketDataView, self).__init__()

        self.full_symbol = ""
        self.init_ui()
        self.register_event()

    def init_ui(self):
        self.datachart = QuotesChart(self.full_symbol)
        self.orderbook = OrderBookWidget()
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.datachart)
        self.scroll.setWidgetResizable(True)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.scroll)
        hbox.addWidget(self.orderbook)
        self.setLayout(hbox)

    def register_event(self):
        """"""
        self.tick_signal.connect(self.orderbook.tick_signal.emit)
        self.tick_signal.connect(self.datachart.on_tick)
        self.symbol_signal.connect(self.orderbook.symbol_signal.emit)
        self.orderbook.symbol_signal.connect(self.datachart.reset)
        self.orderbook.day_signal.connect(self.datachart.reload)
        # self.symbol_signal.connect(self.datachart.reset)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.dataviewindow = MarketDataView()