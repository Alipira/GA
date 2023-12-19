from dataclasses import dataclass


@dataclass
class ClientSplit:
    demand = 0
    service_time = 0
    d0_x = 0
    dx_0 = 0
    dnext = 0
