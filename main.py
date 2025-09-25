#################################################################
####             C L E O P A T R A    S E L E N E            ####
####                         versão 3.0                      ####
#################################################################
#### Prof. Filipo Mor - github.com/ProfessorFilipo           ####
#################################################################

class CPU:
    def __init__(self):
        self.memory = [0] * 256
        self.ac = 0
        self.pc = 0
        self.rs = 0
        self.carry = 0
        self.overflow = 0
        self.negative = 0
        self.zero = 0
        self.symbols = {}

    def reset(self):
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
        address = 0
        code_mode = False
        data_mode = False

        # Primeira Passagem: Coletar rótulos
        for line_number, line in enumerate(assembly_code.splitlines(), 1):
            line = line.strip()

            # Remove comentários
            comment_start = line.find(';')
            if comment_start != -1:
                line = line[:comment_start].strip()

            # Ignora linhas vazias
            if not line:
                continue

            parts = line.split()
            label = None
            instruction = None
            operand = None

            # Rótulo é a primeira coisa na linha, se houver
            if len(parts) > 0 and parts[0].endswith(':'):
                label = parts[0][:-1]  # Remove os dois pontos
                self.symbols[label] = address
                parts = parts[1:]  # Remove o rótulo da lista

            # Instrução é a próxima coisa, se houver
            if len(parts) > 0:
                instruction = parts[0]
                parts = parts[1:]

            # Operando é o que sobrar, se houver
            if len(parts) > 0:
                operand = parts[0]

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
                address += 1  # Incrementa o endereço, mesmo que não haja rótulo

            elif instruction:
                address += 2 if operand else 1  # Incrementa para outras instruções

        # Segunda Passagem: Gerar código de máquina
        address = 0
        code_mode = False
        data_mode = False

        for line_number, line in enumerate(assembly_code.splitlines(), 1):
            line = line.strip()

            # Remove comentários
            comment_start = line.find(';')
            if comment_start != -1:
                line = line[:comment_start].strip()

            # Ignora linhas vazias
            if not line:
                continue

            parts = line.split()
            label = None
            instruction = None
            operand = None

            # Rótulo é a primeira coisa na linha, se houver
            if len(parts) > 0 and parts[0].endswith(':'):
                label = parts[0][:-1]  # Remove os dois pontos
                parts = parts[1:]  # Remove o rótulo da lista

            # Instrução é a próxima coisa, se houver
            if len(parts) > 0:
                instruction = parts[0]
                parts = parts[1:]

            # Operando é o que sobrar, se houver
            if len(parts) > 0:
                operand = parts[0]

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
                    if operand:
                        value = int(operand[1:], 16) if operand.startswith('#') else self.symbols.get(operand)
                        if value is None:
                            print(f"Erro na linha {line_number}: Rótulo não definido: {operand}")
                            return False
                        self.memory[address] = value & 0xFF
                    else:
                        print(f"Erro na linha {line_number}: DB sem operando.")
                        return False
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
        opcodes = {
            "NOT": 0x0, "STA": 0x1, "LDA": 0x2, "ADD": 0x3,
            "OR": 0x4, "AND": 0x5, "JMP": 0x8, "JC": 0x9,
            "JV": 0xA, "JN": 0xB, "JZ": 0xC, "JSR": 0xD,
            "RTS": 0xE, "HLT": 0xF
        }
        return opcodes.get(instruction)

    def get_addressing_mode(self, operand):
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
        instruction = self.memory[self.pc]
        self.pc += 1
        return instruction

    def decode(self, instruction):
        return instruction

    def execute(self, instruction):
        pass

    def update_flags(self, result):
        pass


# Exemplo de uso:
cpu = CPU()
assembly_code = """
; Exemplo de programa para testar o simulador CLEÓPATRA 3.0

.CODE #00      ; Início da seção de código no endereço 0x00
START:  LDA  DATA1     ; Carrega o valor de DATA1 no acumulador
        ADD  DATA2     ; Adiciona o valor de DATA2 ao acumulador
        STA  RESULT    ; Armazena o resultado (acumulador) em RESULT
        LDA  RESULT    ; Carrega o valor de RESULT de volta no acumulador
        AND  #0F       ; Aplica um "E" lógico com o valor 0x0F
        STA  RESULT    ; Armazena o resultado em RESULT
        LDA  RESULT
        OR   #F0
        STA RESULT
        JMP  END       ; Desvia para o rótulo END
END:    HLT          ; Encerra a execução do programa
.ENDCODE    ; Fim da seção de código

.DATA #90      ; Início da seção de dados no endereço 0x90
DATA1:  DB  #15     ; Define o byte DATA1 com o valor 0x15 (21 decimal)
DATA2:  DB  #2A     ; Define o byte DATA2 com o valor 0x2A (42 decimal)
RESULT: DB  #00     ; Define o byte RESULT com o valor inicial 0x00
.ENDDATA    ; Fim da seção de dados
"""
if cpu.load_program(assembly_code):
    print("Programa carregado com sucesso!")
    print(cpu.symbols)
    print(cpu.memory[0:16])
    cpu.pc = 0
    instruction = cpu.fetch()
    print(f"Instrução buscada: {instruction:02X}")
else:
    print("Erro ao carregar o programa.")
