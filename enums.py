from enum import Enum, IntFlag, auto


class OpcodeEnum(Enum):
    ADD = 1
    MUL = 2
    INPUT = 3
    OUTPUT = 4
    JNZ = 5
    JZ = 6
    LT = 7
    EQ = 8
    RB = 9
    HALT = 99


class AddressMode(Enum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2


class BreakOn(IntFlag):
    ADD = auto()
    MUL = auto()
    INPUT = auto()
    OUTPUT = auto()
    JNZ = auto()
    JZ = auto()
    LT = auto()
    EQ = auto()
    RB = auto()
    HALT = auto()


opcode_to_fname = {
    OpcodeEnum.ADD: '_add',
    OpcodeEnum.MUL: '_mul',
    OpcodeEnum.INPUT: '_in',
    OpcodeEnum.OUTPUT: '_out',
    OpcodeEnum.JNZ: '_jnz',
    OpcodeEnum.JZ: '_jz',
    OpcodeEnum.LT: '_lt',
    OpcodeEnum.EQ: '_eq',
    OpcodeEnum.RB: '_rb',
    OpcodeEnum.HALT: '_hlt',
}

opcode_length = {OpcodeEnum.ADD: 4,
                 OpcodeEnum.MUL: 4,
                 OpcodeEnum.LT: 4,
                 OpcodeEnum.EQ: 4,
                 OpcodeEnum.JNZ: 3,
                 OpcodeEnum.JZ: 3,
                 OpcodeEnum.INPUT: 2,
                 OpcodeEnum.OUTPUT: 2,
                 OpcodeEnum.RB: 2,
                 OpcodeEnum.HALT: 1}
