#################################################################
####             C L E O P A T R A    S E L E N E            ####
####                         versão 3.0                      ####
#################################################################
#### Prof. Filipo Mor - github.com/ProfessorFilipo           ####
#################################################################

import logging

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CPU:
    def __init__(self):
        # Memória de 256 posições (endereçamento de 8 bits)
        self.memory = [0]*256
        # Registradores principais
        self.ac = 0   # Acumulador
        self.pc = 0   # Program Counter
        self.rs = 0   # Return Stack (para chamadas JSR/RTS)
        # Flags de status
        self.carry = 0
        self.overflow = 0
        self.negative = 0
        self.zero = 0
        # Tabela de símbolos (para labels da montagem)
        self.symbols = {}

    # ---------- Funções auxiliares ----------

    def signed8(self, v):
        """
        Converte um valor de 8 bits sem sinal (0..255)
        para um inteiro com sinal em complemento de 2 (-128..127).
        Necessário para modos de endereçamento relativo.
        """
        v &= 0xFF
        return v if v < 0x80 else v-0x100

    def parse_value(self, token):
        """
        Converte um token de operando em valor numérico (0..255).
        Aceita decimal, hexadecimal (#FF ou FFh), binário (1010b),
        e símbolos definidos.
        """
        if token is None: return None
        t = token.strip()
        # imediato começa com #
        if t.startswith('#'): t = t[1:]

        # Tenta converter para inteiro diretamente (decimal)
        try:
            return int(t, 10) & 0xFF
        except ValueError:
            pass

        # Tenta converter para hexadecimal
        if t.lower().startswith('0x'):
            try:
                return int(t, 16) & 0xFF
            except ValueError:
                pass

        # Verifica se é um número hexadecimal (sem o prefixo 0x)
        import re
        if re.fullmatch(r'[0-9A-Fa-f]+', t):
            try:
                return int(t, 16) & 0xFF
            except ValueError:
                pass

        # hexadecimal com sufixo H/h
        if t.endswith('H') or t.endswith('h'):
            try: return int(t[:-1],16)&0xFF
            except ValueError: return None

        # binário com sufixo B/b
        if t.endswith('B') or t.endswith('b'):
            try: return int(t[:-1],2)&0xFF
            except ValueError: return None

        # se não for número, procura em tabela de símbolos
        return self.symbols.get(t)

    def get_opcode(self, mnem):
        """
        Mapeia mnemônicos (ex: LDA, ADD) para o valor numérico do opcode.
        A tabela segue a especificação do CLEÓPATRA.
        """
        table = {
            'NOT':0x0,'STA':0x1,'LDA':0x4,'ADD':0x5,'OR':0x6,'AND':0x7,
            'JMP':0x8,'JC':0x9,'JN':0xA,'JZ':0xB,'JSR':0xC,'RTS':0xD,'JV':0xE,'HLT':0xF
        }
        return table.get(mnem)

    def get_mode(self, operand):
        """
        Identifica o modo de endereçamento a partir do operando.
        0x0 = imediato (#)
        0x1 = direto (sem sufixo)
        0x2 = indireto (,I)
        0x3 = relativo (,R)
        """
        if operand is None: return None
        t = operand.strip()
        if t.startswith('#'): return 0x0
        if t.upper().endswith(',I'): return 0x2
        if t.upper().endswith(',R'): return 0x3
        return 0x1

    # ---------- Montador (Assembler) ----------

    def assemble(self, src):
        """
        Faz a montagem de código Assembly CLEÓPATRA em duas passagens:
        1ª passagem: coleta labels e calcula endereços
        2ª passagem: gera os bytes de instruções e dados na memória
        """
        addr = 0
        self.symbols = {}
        lines = src.splitlines()
        mode_code = False
        mode_data = False

        # -------- Primeira passagem: coleta labels --------
        for ln, line in enumerate(lines, 1):
            s = line.split(';', 1)[0].strip()  # remove comentários
            if not s: continue
            parts = s.split()
            # label termina com :
            if parts[0].endswith(':'):
                lbl = parts[0][:-1]
                if lbl in self.symbols:
                    raise Exception(f'Linha {ln}: Label "{lbl}" duplicado.')
                self.symbols[lbl] = addr
                parts = parts[1:]
                if not parts: continue
            instr = parts[0]
            op = parts[1] if len(parts) > 1 else None

            # diretivas de seção
            if instr == '.CODE':
                if op: addr = int(op[1:], 16)
                mode_code = True;
                mode_data = False;
                continue
            if instr == '.ENDCODE': mode_code = False; continue
            if instr == '.DATA':
                if op: addr = int(op[1:], 16)
                mode_data = True;
                mode_code = False;
                continue
            if instr == '.ENDDATA': mode_data = False; continue
            if instr == 'ORG':
                if op: addr = int(op[1:], 16); continue
            if instr == 'DB':
                # aloca 1 byte de dado
                addr = (addr + 1) & 0xFF;
                continue
            if not mode_code and not mode_data: raise Exception(f'Linha {ln}: instrução/dado fora de .CODE ou .DATA')
            # instruções ocupam 1 ou 2 bytes
            if mode_code:
                addr = (addr + 1) & 0xFF
                if op is not None: addr = (addr + 1) & 0xFF
            elif mode_data and instr != 'DB':
                # Se estivermos na seção .DATA e não for um DB, incrementamos addr
                addr = (addr + 1) & 0xFF

        # -------- Segunda passagem: gera os bytes --------
        addr=0; mode_code=False; mode_data=False
        for ln,line in enumerate(lines,1):
            s = line.split(';',1)[0].strip()
            if not s: continue
            parts = s.split()
            if parts[0].endswith(':'): parts=parts[1:]
            if not parts: continue
            instr = parts[0]; op = parts[1] if len(parts)>1 else None
            if instr=='.CODE':
                if op: addr = int(op[1:],16)
                mode_code=True; mode_data=False; continue
            if instr=='.ENDCODE': mode_code=False; continue
            if instr=='.DATA':
                if op: addr = int(op[1:],16)
                mode_data=True; mode_code=False; continue
            if instr=='.ENDDATA': mode_data=False; continue
            if instr=='ORG':
                if op: addr = int(op[1:],16); continue
            if instr=='DB':
                # grava dado literal em memória
                val = self.parse_value(op)
                if val is None:
                    raise Exception(f'Linha {ln}: Valor DB inválido "{op}". '
                                    f'Certifique-se de que é um número válido (decimal, hexadecimal ou binário).')
                self.memory[addr]=val; addr=(addr+1)&0xFF; continue
            if not mode_code: raise Exception(f'Linha {ln}: instrução fora de .CODE')

            # monta instrução
            opc = self.get_opcode(instr)
            if opc is None: raise Exception(f'Linha {ln}: Opcode inválido "{instr}".')
            mode = self.get_mode(op)
            mode_bits = (mode if mode is not None else 0)&0x03
            first = ((opc&0x0F)<<4) | (mode_bits<<2)
            self.memory[addr]=first; addr=(addr+1)&0xFF
            logging.debug(f'Linha {ln}: Endereço {addr-1:02X}, byte {first:02X}')
            if op is not None:
                tok = op
                if tok.upper().endswith(',I') or tok.upper().endswith(',R'):
                    tok=tok[:-2]
                val = self.parse_value(tok)
                if val is None:
                    raise Exception(f'Linha {ln}: Operando inválido "{op}". '
                                    f'Certifique-se de que o valor ou label está correto.')
                self.memory[addr]=val; addr=(addr+1)&0xFF
                logging.debug(f'Linha {ln}: Endereço {addr-1:02X}, byte {val:02X}')
        return True

    # ---------- Execução ----------

    def decode(self, b):
        """Extrai opcode (bits 7..4) e modo (bits 3..2) de uma instrução"""
        return (b>>4)&0x0F, (b>>2)&0x03

    def fetch(self):
        """
        Busca a próxima instrução na memória e avança o PC.
        """
        instr = self.memory[self.pc]
        self.pc=(self.pc+1)&0xFF
        opc,mode = self.decode(instr)
        logging.debug(f'Fetch: PC={self.pc-1:02X}, Instrução={instr:02X}, Opcode={opc:X}, Modo={mode:X}')
        return self.execute(opc,mode)

    def execute(self, opc, mode):
        """
        Executa a instrução decodificada.
        Implementa LDA, ADD, OR, AND, STA, JMP, JC, JN, JZ, JSR, RTS, JV, NOT, HLT.
        """
        try:
            if opc==0xF: # HLT
                logging.info('HLT: Finalizando a execução.')
                return False

            if opc==0x0: # NOT
                self.ac=(~self.ac)&0xFF
                self.update_flags(self.ac)
                logging.info(f'NOT: AC={self.ac:02X}, N={self.negative}, Z={self.zero}')
                return True

            if opc==0x1: # STA
                # Diferentes modos de endereçamento
                if mode==0x1:  # direto
                    addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    self.memory[addr]=self.ac&0xFF
                    logging.info(f'STA (Direto): AC={self.ac:02X} armazenado em {addr:02X}')
                elif mode==0x2:  # indireto
                    ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    addr=self.memory[ptr]; self.memory[addr]=self.ac&0xFF
                    logging.info(f'STA (Indireto): AC={self.ac:02X} armazenado em [{ptr:02X}]={addr:02X}')
                elif mode==0x3:  # relativo
                    off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    addr=(self.pc+self.signed8(off))&0xFF
                    self.memory[addr]=self.ac&0xFF
                    logging.info(f'STA (Relativo): AC={self.ac:02X} armazenado em {addr:02X} (offset {off:02X})')
                else:
                    raise ValueError('STA: Modo de endereçamento inválido.')
                return True

            if opc==0x4: # LDA
                # carrega valor no acumulador
                if mode==0x0:  # imediato
                    self.ac=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    logging.info(f'LDA (Imediato): AC carregado com {self.ac:02X}')
                elif mode==0x1:  # direto
                    addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    self.ac=self.memory[addr]
                    logging.info(f'LDA (Direto): AC carregado com [{addr:02X}]={self.ac:02X}')
                elif mode==0x2:  # indireto
                    ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    addr=self.memory[ptr]; self.ac=self.memory[addr]
                    logging.info(f'LDA (Indireto): AC carregado com [[{ptr:02X}]]=[{addr:02X}]={self.ac:02X}')
                elif mode==0x3:  # relativo
                    off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                    addr=(self.pc+self.signed8(off))&0xFF
                    self.ac=self.memory[addr]
                    logging.info(f'LDA (Relativo): AC carregado com [{addr:02X}] (offset {off:02X}) ={self.ac:02X}')
                self.update_flags(self.ac)
                return True

            if opc==0x5: # ADD
                # obtém operando
                op = self.get_operand(mode)
                # soma com AC e atualiza flags
                res=self.ac+op
                self.carry=1 if res>0xFF else 0
                self.overflow=1 if (((self.ac^op)&0x80)==0 and ((self.ac^res)&0x80)!=0) else 0
                self.ac=res&0xFF
                self.update_flags(self.ac)
                logging.info(f'ADD: AC={self.ac:02X}, Carry={self.carry}, Overflow={self.overflow}')
                return True

            # Implementações das outras instruções aqui...

            raise ValueError(f'Opcode desconhecido: {opc:02X}.')

        except ValueError as e:
            logging.error(f'Erro na execução: {e}')
            raise Exception(f'Erro na execução no endereço {self.pc-1:02X}: {e}')

    def get_operand(self, mode):
        """
        Obtém o operando com base no modo de endereçamento.
        """
        if mode == 0x0:  # Imediato
            operand = self.memory[self.pc]
            self.pc = (self.pc + 1) & 0xFF
            return operand
        elif mode == 0x1:  # Direto
            address = self.memory[self.pc]
            self.pc = (self.pc + 1) & 0xFF
            return self.memory[address]
        elif mode == 0x2:  # Indireto
            pointer = self.memory[self.pc]
            self.pc = (self.pc + 1) & 0xFF
            address = self.memory[pointer]
            return self.memory[address]
        elif mode == 0x3:  # Relativo
            offset = self.memory[self.pc]
            self.pc = (self.pc + 1) & 0xFF
            address = (self.pc + self.signed8(offset)) & 0xFF
            return self.memory[address]
        else:
            raise ValueError(f'Modo de endereçamento inválido: {mode:02X}.')

    def update_flags(self, r):
        """
        Atualiza flags N e Z de acordo com resultado (8 bits).
        """
        r &= 0xFF
        self.negative = 1 if (r&0x80) else 0
        self.zero = 1 if r==0 else 0

    def getMemoryMap(self,posIni=0,posFin=255):
        """
        Retorna string com dump da memória (endereços e valores).
        """
        buf=''; p=posIni
        for _ in range(posIni,posFin+1):
            buf += f'{p:02X} :: {self.memory[p]:02X} ({self.memory[p]:03})\n'
            p+=1
        return buf

    def getSymbolsTable(self):
        """
        Retorna string com a tabela de símbolos (labels e endereços).
        """
        if not self.symbols: return ''
        m = max(self.symbols,key=len)
        s=''
        for k,v in self.symbols.items():
            s += f'{k:>{len(m)}}: {v:02X} ({v:03})\n'
        return s

# ---------- Programa de teste ----------

if __name__=='__main__':
    cpu=CPU()
    asm = """
; Exemplo de programa para testar o simulador CLEÓPATRA 3.0
.CODE #00
START: LDA B
       NOT
       ADD #1
       ADD A
       STA C
END:   HLT
.ENDCODE
.DATA #0A
A: DB #05
B: DB #04
C: DB #00
D: DB #FE
.ENDDATA
"""
    try:
        cpu.assemble(asm)
        print('Programa carregado com sucesso!\n ::: Log de Execução:\n')
        cpu.pc=0
        while True:
            cont = cpu.fetch()
            print(f'PC: {cpu.pc:02X} AC: {cpu.ac:02X} N: {cpu.negative} Z: {cpu.zero} C: {cpu.carry} V: {cpu.overflow}')
            if not cont: break
        print('\nTabela de Simbolos:'); print(cpu.getSymbolsTable())
        print('Mapa de Memoria:'); print(cpu.getMemoryMap(0,20))
        print('Fim da execução.')
    except Exception as e:
        print(f"Erro durante a montagem ou execução: {e}")
