import logging
from collections import deque
from copy import *
from enums import OpcodeEnum, AddressMode, BreakOn, opcode_length, opcode_to_fname
from helpers import pad, is_relevant, process_intcode_exception

if not __name__ == '__main__':
    print('IntcodeComputer loading')


##############################################
#  Computer
##############################################


class IntcodeComputer:
    """
    todo: write docstring
    """

    def __init__(self, program: list, computer_id: int = 0, break_on=BreakOn.OUTPUT):
        self.id = computer_id
        # TODO: Figure out how to avoid re-allocating this... It's super slow.
        self.program = pad(deepcopy(program), 1024 * 1024 * 1, 0)
        self.pc: int = 0
        self.relative_base: int = 0
        self.halted: bool = False
        self.logger = logging.getLogger(f'Computer {computer_id}')
        self.logger.setLevel('DEBUG')
        self.started = False
        self.break_on = break_on
        self.is_break = False
        self.logger.debug(f'break_on: {break_on.name}')
        self.waiting_for_input = False
        self.funcs = self._get_func_dict()

    def get_params(self):
        """

        :return:
        """
        opcode: int = self.program[self.pc]
        self.logger.info(f'Opcode is: {opcode}')
        op_enum: OpcodeEnum = OpcodeEnum(opcode % 100)
        divisor: int = 100
        num_params: int = (opcode_length[op_enum] - 1)
        params: list = [0] * num_params
        dest: int = 0
        for i in range(opcode_length[op_enum] - 1):
            mode: int = opcode // divisor % 10
            value: int = self.program[self.pc + 1 + i]
            if AddressMode(mode) == AddressMode.POSITION:
                assert value < len(self.program), \
                    f'Attempt to access position {value} when program size is {len(self.program)} in computer {self.id}.'
                params[i] = self.program[value]
                dest: int = value  # this is a dirty hack lifted from trevor's implementation.
                # it assumes the destination is the last positional parameter.
                # it overwrites itself and whatever the final value is gets used.
                self.logger.info(f'Position params[{i}] = {self.program[value]}, dest = {dest}')
            elif AddressMode(mode) == AddressMode.IMMEDIATE:
                params[i] = value
                self.logger.info(f'Immediate params[{i}] = {value}')
            elif AddressMode(mode) == AddressMode.RELATIVE:
                params[i] = self.program[value + self.relative_base]
                dest: int = value + self.relative_base
                self.logger.info(f'Relative params[{i}] = {self.program[value + self.relative_base]}, '
                                 f'value = {value}, relative base = {self.relative_base}, dest = {dest}')
            divisor *= 10
        return params, dest

    def _log(self, opcode, fun, *args, **kwargs):
        self.logger.info(f'[{fun.__name__}] {opcode.name} executed.')
        fun(self, *args, **kwargs)

    # noinspection SpellCheckingInspection
    def run(self, input_queue: deque):
        """
        Takes a queue for input and output functionality, loops through the computer's program until it hits an
        instruction which the computer must stop at temporarily. Must be called continually until computer.halted is
        True.
        :param input_queue: The queue to use for communication.
        :return: none
        """
        if not self.started:
            self.started = True
        self.logger.info(f'Beginning execution on computer {self.id}')
        try:
            while True:
                self.logger.info('===============\n\t\tNEW INSTRUCTION')
                opcode = self.program[self.pc]
                self.logger.debug(f'Raw Opcode input: {opcode}, {opcode % 100}')
                assert OpcodeEnum(
                    opcode % 100) in OpcodeEnum, f'Opcode {opcode % 100} at position {self.pc} in computer ' \
                                                 f'{self.id} is not a known opcode.'
                parameters, dest = self.get_params()
                opcode = OpcodeEnum(opcode % 100)
                self.logger.info(f'PC: {self.pc}')
                self._conditional_dispatch(opcode, self.funcs[opcode_to_fname[opcode]],
                                           params=parameters,
                                           io_queue=input_queue,
                                           dest=dest)
                # note: consider refactor that can remove those kwargs from above.
                # note: this could involve wrapping those things in some kind of state
                # note: containing object.
                if self.is_break or self.halted:
                    return
                # print(opcode)
                if opcode not in [OpcodeEnum.JZ, OpcodeEnum.JNZ]:
                    self.pc += opcode_length[opcode]
                    self.logger.debug(f'Increased PC by: {opcode_length[opcode]}')
        except (IndexError, ValueError) as err:
            process_intcode_exception(self.logger, self.pc, self.program, err)

    def _hlt(self, **kwargs):
        self.halted = True
        # process_intcode_exception(self.logger, self.pc, self.program, RuntimeError("test"))

    ##############################################
    #  Internal functions
    ##############################################

    # takes the current opcode, and the function for that opcode.
    # checks if we break on that opcode or not
    # returns True when we are breaking
    # runs the function at the correct time
    # must take into account the fact that output breaks late, others break early
    def _conditional_dispatch(self, opcode: OpcodeEnum, fun, *args, **kwargs):
        op = BreakOn[opcode.name]
        if op == BreakOn.OUTPUT and not self.is_break:
            self.is_break = True
            self._log(opcode, fun, *args, **kwargs)
            return True
        elif op == BreakOn.OUTPUT and self.is_break:
            self.logger.info(f'Resuming from break on {op.name}')
            self.is_break = False
            return
        elif self.break_on & op and not self.is_break:  # something funky here, probably dont want &
            self.logger.info(f'Breaking on {op.name}')
            self.is_break = True
            return True
        else:
            self.is_break = False
            self._log(opcode, fun, *args, **kwargs)
            return

    def _in(self, *, dest, io_queue, **kwargs):
        input_value = io_queue.popleft()
        self.logger.debug(f'IN program[{dest}] = {self.program[dest]} value = {input_value}')
        self.program[dest] = input_value

    def _rb(self, *, params, **kwargs):
        self.relative_base += params[0]
        assert self.relative_base > 0
        self.logger.debug(f'RB relative base = {self.relative_base}')

    def _eq(self, *, dest, params, **kwargs):
        self.program[dest] = 1 if params[0] == params[1] else 0
        self.logger.debug(f'EQ program[{dest}] = {self.program[dest]}')

    def _lt(self, *, dest, params, **kwargs):
        self.program[dest] = 1 if params[0] < params[1] else 0
        self.logger.debug(f'LT program[{dest}] = {self.program[dest]}')

    def _jz(self, *, params, **kwargs):
        if not params[0]:
            self.logger.debug(f'JZ PC = {params[1]}')
            self.pc = params[1]
        else:
            self.logger.debug(f'JZ continue')
            self.pc += opcode_length[OpcodeEnum.JZ]

    def _jnz(self, *, params, **kwargs):
        if params[0]:
            self.logger.debug(f'JNZ PC = {params[1]}')
            self.pc = params[1]
        else:
            self.logger.debug(f'JNZ Continue')
            self.pc += opcode_length[OpcodeEnum.JNZ]

    def _out(self, *, io_queue, params, **kwargs):
        io_queue.append(params[0])

    def _mul(self, *, dest, params, **kwargs):
        self.program[dest] = params[0] * params[1]
        self.logger.info(f'MUL {params[0]} * {params[1]} = {self.program[dest]}')

    def _add(self, *, dest, params, **kwargs):
        self.program[dest] = params[0] + params[1]
        self.logger.info(f'ADD {params[0]} + {params[1]} = {self.program[dest]}')

    def _get_func_dict(self):
        return {k: v for k, v in filter(is_relevant, self.__class__.__dict__.items())}


##############################################
#  Main
##############################################


if __name__ == '__main__':
    cmp = IntcodeComputer([99])
    print(cmp._get_func_dict())
