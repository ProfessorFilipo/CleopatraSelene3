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
        self.symbols = {}  # Inicializa a tabela de símbolos

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

    def getMemoryMap(self, posIni=0, posFin=255):
        buffer = ''
        pos = 0
        for _ in range(posIni, posFin + 1):
            memPos = self.memory[pos]
            buffer += f'{pos:0>{2}X} :: {memPos:0>{2}X} ({memPos:0>3})\n'
            pos += 1
        return buffer

    def getSymbolsTable(self):
        buffer = ''
        maiorSimbolo = max(self.symbols, key=len)
        for chave, valor in self.symbols.items():
            buffer += f'{chave:>{len(maiorSimbolo)}}: {valor:0>{2}X} ({valor:0>3})\n'
        return buffer


    def load_program(self, assembly_code):
        """Monta o código assembly e carrega na memória."""
        address = 0
        code_mode = False
        data_mode = False
        self.symbols = {}  # Limpa a tabela de símbolos

        # Primeira Passagem: Coletar rótulos
        for line_number, line in enumerate(assembly_code.splitlines(), 1):
            line = line.strip()

            # Remove comentários e ignora linhas vazias
            comment_start = line.find(';')
            if comment_start != -1:
                line = line[:comment_start].strip()
            if not line:
                continue

            parts = line.split()
            if not parts:
                continue

            label = None
            instruction = None
            operand = None

            # Rótulo é a primeira coisa na linha, se houver
            if parts[0].endswith(':'):
                label = parts[0][:-1]  # Remove os dois pontos
                self.symbols[label] = address
                parts = parts[1:]  # Remove o rótulo da lista

            # Instrução é a próxima coisa, se houver
            if parts:
                instruction = parts[0]
                if len(parts) > 1:
                    operand = parts[1]

            # Trata diretivas
            if instruction == '.CODE':
                if operand:
                    try:
                        address = int(operand[1:], 16)  # Converte o endereço para inteiro
                    except ValueError:
                        print(f"Erro na linha {line_number}: Endereço .CODE inválido: {operand}")
                        return False
                code_mode = True
                data_mode = False
            elif instruction == '.ENDCODE':
                if not code_mode:
                    print(f"Erro na linha {line_number}: .ENDCODE sem .CODE correspondente.")
                    return False
                code_mode = False
            elif instruction == '.DATA':
                if operand:
                    try:
                        address = int(operand[1:], 16)  # Converte o endereço para inteiro
                    except ValueError:
                        print(f"Erro na linha {line_number}: Endereço .DATA inválido: {operand}")
                        return False
                data_mode = True
                code_mode = False
            elif instruction == '.ENDDATA':
                if not data_mode:
                    print(f"Erro na linha {line_number}: .ENDDATA sem .CODE correspondente.")
                    return False
                data_mode = False
            elif instruction == 'ORG':
                if operand:
                    try:
                        address = int(operand[1:], 16)  # Converte o endereço para inteiro
                    except ValueError:
                        print(f"Erro na linha {line_number}: Endereço ORG inválido: {operand}")
                        return False
            elif instruction == 'DB':
                if not data_mode:
                    print(f"Erro na linha {line_number}: DB fora da seção .DATA.")
                    return False
                if not operand:
                    print(f"Erro na linha {line_number}: DB sem operando.")
                    return False
                try:
                    value = int(operand[1:], 16) if operand.startswith('#') else self.symbols.get(operand)
                    if value is None:
                        print(f"Erro na linha {line_number}: Rótulo não definido: {operand}")
                        return False
                    self.memory[address] = value & 0xFF
                    address += 1
                except ValueError:
                    print(f"Erro na linha {line_number}: Valor inválido: {operand}")
                    return False

        # Se não for diretiva, é instrução
        else:
            address += 2 if operand else 1

        # Segunda Passagem: Gerar código de máquina
        address = 0
        code_mode = False
        data_mode = False

        for line_number, line in enumerate(assembly_code.splitlines(), 1):
            line = line.strip()

            # Remove comentários e ignora linhas vazias
            comment_start = line.find(';')
            if comment_start != -1:
                line = line[:comment_start].strip()
            if not line:
                continue

            parts = line.split()
            if not parts:
                continue

            label = None
            instruction = None
            operand = None

            # Rótulo é a primeira coisa na linha, se houver
            if parts[0].endswith(':'):
                label = parts[0][:-1]  # Remove os dois pontos
                parts = parts[1:]  # Remove o rótulo da lista

            # Instrução é a próxima coisa, se houver
            if parts:
                instruction = parts[0]
                if len(parts) > 1:
                    operand = parts[1]

            # Trata diretivas
            if instruction == '.CODE':
                if operand:
                    try:
                        address = int(operand[1:], 16)  # Converte o endereço para inteiro
                    except ValueError:
                        print(f"Erro na linha {line_number}: Endereço .CODE inválido: {operand}")
                        return False
                code_mode = True
                data_mode = False
            elif instruction == '.ENDCODE':
                code_mode = False
            elif instruction == '.DATA':
                if operand:
                    try:
                        address = int(operand[1:], 16)  # Converte o endereço para inteiro
                    except ValueError:
                        print(f"Erro na linha {line_number}: Endereço .DATA inválido: {operand}")
                        return False
                data_mode = True
                code_mode = False
            elif instruction == '.ENDDATA':
                data_mode = False
            elif instruction == 'ORG':
                if operand:
                    try:
                        address = int(operand[1:], 16)  # Converte o endereço para inteiro
                    except ValueError:
                        print(f"Erro na linha {line_number}: Endereço ORG inválido: {operand}")
                        return False
            elif instruction == 'DB':
                continue  # DBs são tratadas apenas na primeira passagem

            # Se não for diretiva, é instrução
            else:
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
                            value = int(operand[:-2], 16) if operand[:-2].startswith('#') else self.symbols.get(operand[:-2])
                        elif operand.endswith(',R'):
                            value = int(operand[:-2], 16) if operand[:-2].startswith('#') else self.symbols.get(operand[:-2])
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

    # Verifica se as seções .CODE e .DATA foram finalizadas
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
        """Busca a instrução na memória."""
        instruction = self.memory[self.pc]
        self.pc += 1
        opcode, mode = self.decode(instruction)
        continue_execution = self.execute(opcode, mode)
        return continue_execution

    def decode(self, instruction):
        """Decodifica a instrução."""
        opcode = (instruction >> 2) & 0x0F  # Extrai os 4 bits mais significativos (opcode)
        mode = instruction & 0x03  # Extrai os 2 bits menos significativos (modo de endereçamento)
        return opcode, mode

    def execute(self, opcode, mode):
        """Executa a instrução."""
        if opcode == 0xF:  # HLT
            return False  # Indica que a execução deve parar

        elif opcode == 0x0:  # NOT
            self.ac = ~self.ac & 0xFF  # Complementa o acumulador (8 bits)
            self.update_flags(self.ac)  # Atualiza as flags

        elif opcode == 0x2:  # LDA
            if mode == 0x0:  # Imediato
                self.ac = self.memory[self.pc]
                self.pc += 1
            elif mode == 0x1:  # Direto
                address = self.memory[self.pc]
                self.pc += 1
                self.ac = self.memory[address]
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.pc += 1
                address = self.memory[address_ptr]
                self.ac = self.memory[address]
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.pc += 1
                address = (self.pc + offset) & 0xFF  # Endereço relativo
                self.ac = self.memory[address]
            self.update_flags(self.ac)  # Atualiza as flags

        elif opcode == 0x1:  # STA
            if mode == 0x1:  # Direto
                address = self.memory[self.pc]
                self.pc += 1
                self.memory[address] = self.ac
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.pc += 1
                address = self.memory[address_ptr]
                self.memory[address] = self.ac
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.pc += 1
                address = (self.pc + offset) & 0xFF  # Endereço relativo
                self.memory[address] = self.ac

        elif opcode == 0x3:  # ADD
            operand = 0
            if mode == 0x0:  # Imediato
                operand = self.memory[self.pc]
                self.pc += 1
            elif mode == 0x1:  # Direto
                address = self.memory[self.pc]
                self.pc += 1
                operand = self.memory[address]
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.pc += 1
                address = self.memory[address_ptr]
                operand = self.memory[address]
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.pc += 1
                address = (self.pc + offset) & 0xFF  # Endereço relativo
                operand = self.memory[address]

            result = self.ac + operand
            self.carry = 1 if result > 0xFF else 0  # Define a flag de carry
            self.overflow = 1 if ((self.ac ^ operand) & 0x80 == 0) and ((self.ac ^ result) & 0x80 != 0) else 0  # Define a flag de overflow

            self.ac = result & 0xFF  # Trunca o resultado para 8 bits
            self.update_flags(self.ac)  # Atualiza as flags N e Z

        elif opcode == 0x4:  # OR
            if mode == 0x0:  # Imediato
                self.ac |= self.memory[self.pc]
                self.pc += 1
            elif mode == 0x1:  # Direto
                address = self.memory[self.pc]
                self.pc += 1
                self.ac |= self.memory[address]
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.pc += 1
                address = self.memory[address_ptr]
                self.ac |= self.memory[address]
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.pc += 1
                address = (self.pc + offset) & 0xFF  # Endereço relativo
                self.ac |= self.memory[address]
            self.update_flags(self.ac)  # Atualiza as flags N e Z

        elif opcode == 0x5:  # AND
            if mode == 0x0:  # Imediato
                self.ac &= self.memory[self.pc]
                self.pc += 1
            elif mode == 0x1:  # Direto
                address = self.memory[self.pc]
                self.pc += 1
                self.ac &= self.memory[address]
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.pc += 1
                address = self.memory[address_ptr]
                self.ac &= self.memory[address]
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.pc += 1
                address = self.pc # (self.pc + offset) & 0xFF  # Endereço relativo
                self.ac &= self.memory[address]
            self.update_flags(self.ac)  # Atualiza as flags N e Z

        elif opcode == 0x8:  # JMP
            if mode == 0x0 or mode == 0x1:  # Imediato ou Direto (são iguais para JMP)
                self.pc = self.memory[self.pc]
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.pc = self.memory[address_ptr]
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.pc = (self.pc + offset) & 0xFF
            else:
                print(f"Erro: Modo de endereçamento inválido para JMP: {mode:02X}")
                return False  # Para a execução em caso de erro

        elif opcode == 0x9:  # JC
            if self.carry == 1:
                if mode == 0x0 or mode == 0x1:  # Imediato ou Direto (são iguais para JC)
                    self.pc = self.memory[self.pc]
                elif mode == 0x2:  # Indireto
                    address_ptr = self.memory[self.pc]
                    self.pc = self.memory[address_ptr]
                elif mode == 0x3:  # Relativo
                    offset = self.memory[self.pc]
                    self.pc = (self.pc + offset) & 0xFF
            else:
                self.pc += 1  # Pula o operando se a condição não for atendida

        elif opcode == 0xA:  # JV
            if self.overflow == 1:
                if mode == 0x0 or mode == 0x1:  # Imediato ou Direto (são iguais para JV)
                    self.pc = self.memory[self.pc]
                elif mode == 0x2:  # Indireto
                    address_ptr = self.memory[self.pc]
                    self.pc = self.memory[address_ptr]
                elif mode == 0x3:  # Relativo
                    offset = self.memory[self.pc]
                    self.pc = (self.pc + offset) & 0xFF
            else:
                self.pc += 1  # Pula o operando se a condição não for atendida

        elif opcode == 0xB:  # JN
            if self.negative == 1:
                if mode == 0x0 or mode == 0x1:  # Imediato ou Direto (são iguais para JN)
                    self.pc = self.memory[self.pc]
                elif mode == 0x2:  # Indireto
                    address_ptr = self.memory[self.pc]
                    self.pc = self.memory[address_ptr]
                elif mode == 0x3:  # Relativo
                    offset = self.memory[self.pc]
                    self.pc = (self.pc + offset) & 0xFF
            else:
                self.pc += 1  # Pula o operando se a condição não for atendida

        elif opcode == 0xC:  # JZ
            if self.zero == 1:
                if mode == 0x0 or mode == 0x1:  # Imediato ou Direto (são iguais para JZ)
                    self.pc = self.memory[self.pc]
                elif mode == 0x2:  # Indireto
                    address_ptr = self.memory[self.pc]
                    self.pc = self.memory[address_ptr]
                elif mode == 0x3:  # Relativo
                    offset = self.memory[self.pc]
                    self.pc = (self.pc + offset) & 0xFF
            else:
                self.pc += 1  # Pula o operando se a condição não for atendida

        elif opcode == 0xD:  # JSR
            if mode == 0x0 or mode == 0x1:  # Imediato ou Direto (são iguais para JSR)
                self.rs = self.pc + 1  # Salva o endereço de retorno
                self.pc = self.memory[self.pc]  # Desvia para a subrotina
            elif mode == 0x2:  # Indireto
                address_ptr = self.memory[self.pc]
                self.rs = self.pc + 1
                self.pc = self.memory[address_ptr]
            elif mode == 0x3:  # Relativo
                offset = self.memory[self.pc]
                self.rs = self.pc + 1
                self.pc = (self.pc + offset) & 0xFF
            else:
                print(f"Erro: Modo de endereçamento inválido para JSR: {mode:02X}")
                return False  # Para a execução em caso de erro

            self.pc &= 0xFF  # Garante que PC permaneça dentro do limite da memória

        elif opcode == 0xE:  # RTS
            self.pc = self.rs  # Retorna da subrotina
        else:
            print(f"Erro: Opcode inválido: {opcode:02X}")
            return False

        return True  # Indica que a execução deve continuar

    def update_flags(self, result):
        """Atualiza as flags N (negativo) e Z (zero)."""
        result = result & 0xFF  # Garante que o resultado esteja em 8 bits
        self.negative = 1 if (result & 0x80) else 0  # Define N se o bit 7 estiver setado
        self.zero = 1 if result == 0 else 0  # Define Z se o resultado for zero

# Exemplo de uso:
cpu = CPU()
assembly_code = """
; Exemplo de programa para testar o simulador CLEÓPATRA 3.0

.CODE #00      ; Início da seção de código no endereço 0x00
START:  LDA  B
        NOT
        ADD  #1
        ADD  A     
        STA  C    
END:    HLT          ; Encerra a execução do programa
.ENDCODE    ; Fim da seção de código

.DATA #0A      ; Início da seção de dados no endereço 0x90
   A:  DB  #05     
   B:  DB  #04     
   C:  DB  #00
   D:  DB  #FE
.ENDDATA    ; Fim da seção de dados
"""
if cpu.load_program(assembly_code):
    print("Programa carregado com sucesso!\n ::: Log de Execução:\n")
    #print("Tabela de símbolos:", cpu.symbols)
    #print("Memória:", cpu.memory[0:32])

    cpu.pc = 0  # Define o PC para o início do código
    while True:  # Executa o programa até o HLT
        continue_execution = cpu.fetch()
        print(f"PC: {cpu.pc:02X} AC: {cpu.ac:02X} N: {cpu.negative} Z: {cpu.zero} C: {cpu.carry} V: {cpu.overflow}")
        if not continue_execution:
            break

    print(f"Tabela de Simbolos:\n{cpu.getSymbolsTable()}")
    print(f"Mapa de Memoria: \n{cpu.getMemoryMap(0, 20)}")
    #print("Memória (fim da execução):", cpu.memory[0:32])

    print("Fim da execução.")
else:
    print("Erro ao carregar o programa.")
