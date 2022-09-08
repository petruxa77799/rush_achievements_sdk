from enum import Enum


class TriggerTypes(str, Enum):
    USER_PLAYS_MARKETS = 'USER_PLAYS_MARKETS'
    USER_WON_IN_A_ROW = 'USER_WON_IN_A_ROW'
    QUARTER_CLOCK = 'QUARTER_CLOCK'
