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
        """Monta o código assembly e carrega na memória."""
        # TODO: Implementar a lógica de montagem (assembler)
        # Por enquanto, apenas carrega os bytes diretamente na memória
        address = 0
        for line in assembly_code.splitlines():
            line = line.strip()
            if not line or line.startswith(';'):
                continue  # Ignora linhas vazias e comentários

            parts = line.split()
            if len(parts) > 1 and parts[1].startswith('#'):
                try:
                    value = int(parts[1][1:], 16)  # Converte para inteiro (base 16)
                    self.memory[address] = value & 0xFF  # Garante que caiba em 1 byte
                    address += 1
                except ValueError:
                    print(f"Erro: Valor inválido: {parts[1]}")
                    return False
        return True


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
; Exemplo de código assembly
#30 ; Carrega o valor 30H na memória
#5B ; Carrega o valor 5BH na memória
#00 ; Carrega o valor 00H na memória
#93 ; Carrega o valor 93H na memória
"""
if cpu.load_program(assembly_code):
    print("Programa carregado com sucesso!")
    # Teste simples de fetch
    instruction = cpu.fetch()
    print(f"Instrução buscada: {instruction:02X}")


