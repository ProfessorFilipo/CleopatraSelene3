#################################################################
####             C L E O P A T R A    S E L E N E            ####
####                           versão 3.0                    ####
#################################################################
#### Prof. Filipo Mor - github.com/ProfessorFilipo           ####
#################################################################

class CPU:
    def __init__(self):
        self.memory = [0] * 256  # 256 bytes de memória
        self.ac = 0  # Acumulador
        self.pc = 0  # Contador de Programa
        self.rs = 0  # Registrador de Subrotina
        self.carry = 0
        self.overflow = 0
        self.negative = 0
        self.zero = 0
        self.symbols = {}  # Tabela de símbolos

    def reset(self):
        """Reseta o estado da CPU."""
        self.memory = [0] * 256
        self.ac = 0
        self.pc = 0
        self.rs = 0
        self.carry = 0
        self.overflow = 0
        self.negative = 0
        self.zero = 0
        self.symbols = {}

    def load_program(self, assembly_code):
        """Monta o código assembly e carrega na memória (duas passagens)."""

        # Primeira Passagem: Coletar rótulos
        address = 0
        code_mode = False
        data_mode = False

        for line_number, line in enumerate(assembly_code.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            parts = line.split()
            label = None
            instruction = None
            operand = None

            if len(parts) >= 1 and parts[0].endswith(':'):
                label = parts[0][:-1]
                if len(parts) > 1:
                    instruction = parts[1]
                    if len(parts) > 2:
                        operand = parts[2]
                else:
                    instruction = None
            elif len(parts) >= 1:
                instruction = parts[0]
                if len(parts) > 1:
                    operand = parts[1]

            if instruction == '.CODE':
                code_address = int(operand[1:], 16) if operand else 0
                address = code_address
                code_mode = True
                data_mode = False
            elif instruction == '.ENDCODE':
                if not code_mode:
                    print(f"Erro na linha {line_number}: .ENDCODE sem .CODE correspondente.")
                    return False
                code_mode = False
            elif instruction == '.DATA':
                data_address = int(operand[1:], 16) if operand else 0
                address = data_address
                data_mode = True
                code_mode = False
            elif instruction == '.ENDDATA':
                if not data_mode:
                    print(f"Erro na linha {line_number}: .ENDDATA sem .DATA correspondente.")
                    return False
                data_mode = False
            elif instruction == 'ORG':
                address = int(operand[1:], 16)
            elif instruction == 'DB':
                if label:
                    self.symbols[label] = address  # Define rótulo para DB
                address += 1
            elif instruction:
                if label:
                    self.symbols[label] = address  # Define rótulo para instruções
                address += 2 if operand else 1

        # Segunda Passagem: Gerar código de máquina
        address = 0
        code_mode = False
        data_mode = False

        for line_number, line in enumerate(assembly_code.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            parts = line.split()
            label = None
            instruction = None
            operand = None

            if len(parts) >= 1 and parts[0].endswith(':'):
                label = parts[0][:-1]
                if len(parts) > 1:
                    instruction = parts[1]
                    if len(parts) > 2:
                        operand = parts[2]
                else:
                    instruction = None
            elif len(parts) >= 1:
                instruction = parts[0]
                if len(parts) > 1:
                    operand = parts[1]

            if instruction == '.CODE':
                code_address = int(operand[1:], 16) if operand else 0
                address = code_address
                code_mode = True
                data_mode = False
            elif instruction == '.ENDCODE':
                code_mode = False
            elif instruction == '.DATA':
                data_address = int(operand[1:], 16) if operand else 0
                address = data_address
                data_mode = True
                code_mode = False
            elif instruction == '.ENDDATA':
                data_mode = False
            elif instruction == 'ORG':
                address = int(operand[1:], 16)
            elif instruction == 'DB':
                try:
                    value = int(operand[1:], 16) if operand and operand.startswith('#') else self.symbols.get(operand)
                    if value is None:
                        print(f"Erro na linha {line_number}: Rótulo não definido: {operand}")
                        return False
                    self.memory[address] = value & 0xFF
                    address += 1
                except ValueError:
                    print(f"Erro na linha {line_number}: Valor inválido: {operand}")
                    return False
            elif instruction:
                if not code_mode:
                    print(f"Erro na linha {line_number}: Instrução fora da seção .CODE.")
                    return False

                opcode = self.get_opcode(instruction)
                if opcode is None:
                    print(f"Erro na linha {line_number}: Instrução inválida: {instruction}")
                    return False

                mode = self.get_addressing_mode(operand)
                if mode is None and operand is not None:
                    print(f"Erro na linha {line_number}: Modo de endereçamento inválido: {operand}")
                    return False

                first_byte = (opcode << 2) | (mode if mode is not None else 0)

                self.memory[address] = first_byte & 0xFF
                address += 1

                if operand:
                    try:
                        if operand.startswith('#'):
                            value = int(operand[1:], 16)
                        elif operand.endswith(',I'):
                            value = int(operand[:-2], 16) if operand[:-2].startswith('#') else self.symbols.get(
                                operand[:-2])
                        elif operand.endswith(',R'):
                            value = int(operand[:-2], 16) if operand[:-2].startswith('#') else self.symbols.get(
                                operand[:-2])
                        else:
                            value = self.symbols.get(operand)
                        if value is None:
                            print(f"Erro na linha {line_number}: Rótulo não definido: {operand}")
                            return False
                        self.memory[address] = value & 0xFF
                        address += 1
                    except ValueError:
                        print(f"Erro na linha {line_number}: Valor inválido: {operand}")
                        return False

        if code_mode:
            print(f"Erro: .CODE não foi finalizado com .ENDCODE.")
            return False
        if data_mode:
            print(f"Erro: .DATA não foi finalizado com .ENDDATA.")
            return False

        return True

    def get_opcode(self, instruction):
        """Retorna o opcode da instrução."""
        opcodes = {
            "NOT": 0x0, "STA": 0x1, "LDA": 0x2, "ADD": 0x3,
            "OR": 0x4, "AND": 0x5, "JMP": 0x8, "JC": 0x9,
            "JV": 0xA, "JN": 0xB, "JZ": 0xC, "JSR": 0xD,
            "RTS": 0xE, "HLT": 0xF
        }
        return opcodes.get(instruction)

    def get_addressing_mode(self, operand):
        """Retorna o modo de endereçamento do operando."""
        if operand is None:
            return None
        if operand.startswith('#'):
            return 0x0  # Imediato
        elif operand.endswith(',I'):
            return 0x2  # Indireto
        elif operand.endswith(',R'):
            return 0x3  # Relativo
        else:
            return 0x1  # Direto

    def fetch(self):
        """Busca a instrução na memória."""
        instruction = self.memory[self.pc]
        self.pc += 1
        return instruction

    def decode(self, instruction):
        """Decodifica a instrução."""
        # TODO: Implementar a lógica de decodificação
        return instruction  # Por enquanto, retorna a instrução original

    def execute(self, instruction):
        """Executa a instrução."""
        # TODO: Implementar a lógica de execução para cada instrução
        pass  # Por enquanto, não faz nada

    def update_flags(self, result):
        """Atualiza as flags."""
        # TODO: Implementar a lógica de atualização das flags
        pass  # Por enquanto, não faz nada


# Exemplo de uso:
cpu = CPU()
assembly_code = """
.CODE #00
START: LDA DATA1
       ADD DATA2
       STA RESULT
       HLT
.ENDCODE

.DATA #90
DATA1: DB #10
DATA2: DB #20
RESULT: DB #00
.ENDDATA
"""
if cpu.load_program(assembly_code):
    print("Programa carregado com sucesso!")
    print(cpu.symbols)  # Imprime a tabela de símbolos
    print(cpu.memory[0:10])  # Imprime os primeiros 10 bytes da memória
    # Teste simples de fetch
    cpu.pc = 0  # Reinicia o PC
    instruction = cpu.fetch()
    print(f"Instrução buscada: {instruction:02X}")
else:
    print("Erro ao carregar o programa.")
