#################################################################
####             C L E O P A T R A    S E L E N E            ####
####                         versão 3.0                      ####
#################################################################
#### Prof. Filipo Mor - github.com/ProfessorFilipo           ####
#################################################################

class CPU:
    def __init__(self):
        self.memory = [0]*256
        self.ac = 0
        self.pc = 0
        self.rs = 0
        self.carry = 0
        self.overflow = 0
        self.negative = 0
        self.zero = 0
        self.symbols = {}

    def signed8(self, v):
        v &= 0xFF
        return v if v < 0x80 else v-0x100

    def parse_value(self, token):
        if token is None: return None
        t = token.strip()
        if t.startswith('#'): t = t[1:]
        if t.endswith('H') or t.endswith('h'):
            try: return int(t[:-1],16)&0xFF
            except: return None
        if t.endswith('B') or t.endswith('b'):
            try: return int(t[:-1],2)&0xFF
            except: return None
        try:
            return int(t,10)&0xFF
        except:
            pass
        if t.lower().startswith('0x'):
            try: return int(t,16)&0xFF
            except: return None
        import re
        if re.fullmatch(r'[0-9A-Fa-f]+', t):
            try: return int(t,16)&0xFF
            except: return None
        return self.symbols.get(t)

    def get_opcode(self, mnem):
        table = {
            'NOT':0x0,'STA':0x1,'LDA':0x4,'ADD':0x5,'OR':0x6,'AND':0x7,
            'JMP':0x8,'JC':0x9,'JN':0xA,'JZ':0xB,'JSR':0xC,'RTS':0xD,'JV':0xE,'HLT':0xF
        }
        return table.get(mnem)

    def get_mode(self, operand):
        if operand is None: return None
        t = operand.strip()
        if t.startswith('#'): return 0x0
        if t.upper().endswith(',I'): return 0x2
        if t.upper().endswith(',R'): return 0x3
        return 0x1

    def assemble(self, src):
        addr = 0
        self.symbols = {}
        lines = src.splitlines()
        mode_code = False
        mode_data = False
        for ln,line in enumerate(lines,1):
            s = line.split(';',1)[0].strip()
            if not s: continue
            parts = s.split()
            if parts[0].endswith(':'):
                lbl = parts[0][:-1]; self.symbols[lbl]=addr; parts=parts[1:]
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
                if not mode_data: raise Exception(f'Linha {ln}: DB fora de .DATA')
                val = self.parse_value(op)
                if val is None: raise Exception(f'Linha {ln}: valor DB inválido {op}')
                self.memory[addr]=val; addr=(addr+1)&0xFF; continue
            if not mode_code: raise Exception(f'Linha {ln}: instrução fora de .CODE')
            addr=(addr+1)&0xFF
            if op is not None: addr=(addr+1)&0xFF
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
            if instr=='DB': continue
            if not mode_code: raise Exception(f'Linha {ln}: instrução fora de .CODE')
            opc = self.get_opcode(instr)
            if opc is None: raise Exception(f'Linha {ln}: opcode inválido {instr}')
            mode = self.get_mode(op)
            mode_bits = (mode if mode is not None else 0)&0x03
            first = ((opc&0x0F)<<4) | (mode_bits<<2)
            self.memory[addr]=first; addr=(addr+1)&0xFF
            if op is not None:
                tok = op
                if tok.upper().endswith(',I') or tok.upper().endswith(',R'): tok=tok[:-2]
                val = self.parse_value(tok)
                if val is None:
                    val = 0
                self.memory[addr]=val; addr=(addr+1)&0xFF
        return True

    def decode(self, b): return (b>>4)&0x0F, (b>>2)&0x03

    def fetch(self):
        instr = self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
        opc,mode = self.decode(instr); return self.execute(opc,mode)

    def execute(self, opc, mode):
        if opc==0xF: return False
        if opc==0x0:
            self.ac=(~self.ac)&0xFF; self.update_flags(self.ac); return True
        if opc==0x1:
            if mode==0x1:
                addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; self.memory[addr]=self.ac&0xFF
            elif mode==0x2:
                ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=self.memory[ptr]; self.memory[addr]=self.ac&0xFF
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=(self.pc+self.signed8(off))&0xFF; self.memory[addr]=self.ac&0xFF
            else: raise Exception('STA modo inválido')
            return True
        if opc==0x4:
            if mode==0x0:
                self.ac=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
            elif mode==0x1:
                addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; self.ac=self.memory[addr]
            elif mode==0x2:
                ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=self.memory[ptr]; self.ac=self.memory[addr]
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=(self.pc+self.signed8(off))&0xFF; self.ac=self.memory[addr]
            self.update_flags(self.ac); return True
        if opc==0x5:
            if mode==0x0:
                op=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
            elif mode==0x1:
                addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; op=self.memory[addr]
            elif mode==0x2:
                ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=self.memory[ptr]; op=self.memory[addr]
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=(self.pc+self.signed8(off))&0xFF; op=self.memory[addr]
            else: raise Exception('ADD modo inválido')
            res=self.ac+op; self.carry=1 if res>0xFF else 0; self.overflow=1 if (((self.ac^op)&0x80)==0 and ((self.ac^res)&0x80)!=0) else 0
            self.ac=res&0xFF; self.update_flags(self.ac); return True
        if opc==0x6:
            if mode==0x0:
                self.ac |= self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
            elif mode==0x1:
                addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; self.ac |= self.memory[addr]
            elif mode==0x2:
                ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=self.memory[ptr]; self.ac |= self.memory[addr]
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=(self.pc+self.signed8(off))&0xFF; self.ac |= self.memory[addr]
            self.update_flags(self.ac); return True
        if opc==0x7:
            if mode==0x0:
                self.ac &= self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
            elif mode==0x1:
                addr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; self.ac &= self.memory[addr]
            elif mode==0x2:
                ptr=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=self.memory[ptr]; self.ac &= self.memory[addr]
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; addr=(self.pc+self.signed8(off))&0xFF; self.ac &= self.memory[addr]
            self.update_flags(self.ac); return True
        if opc in (0x8,0x9,0xA,0xB,0xC):
            take=False
            if opc==0x8: take=True
            elif opc==0x9: take=(self.carry==1)
            elif opc==0xA: take=(self.negative==1)
            elif opc==0xB: take=(self.zero==1)
            elif opc==0xC: take=True
            if mode==0x0 or mode==0x1:
                a=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                if take:
                    if opc==0xC: self.rs=self.pc; self.pc=a
                    else: self.pc=a
            elif mode==0x2:
                p=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; t=self.memory[p]
                if take:
                    if opc==0xC: self.rs=self.pc; self.pc=t
                    else: self.pc=t
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF; t=(self.pc+self.signed8(off))&0xFF
                if take:
                    if opc==0xC: self.rs=self.pc; self.pc=t
                    else: self.pc=t
            return True
        if opc==0xD:
            self.pc=self.rs&0xFF; return True
        if opc==0xE:
            take=(self.overflow==1)
            if mode==0x0 or mode==0x1:
                a=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                if take: self.pc=a
            elif mode==0x2:
                p=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                if take: self.pc=self.memory[p]
            elif mode==0x3:
                off=self.memory[self.pc]; self.pc=(self.pc+1)&0xFF
                if take: self.pc=(self.pc+self.signed8(off))&0xFF
            return True
        raise Exception(f'opc desconhecido {opc}')

    def update_flags(self, r):
        r &= 0xFF; self.negative = 1 if (r&0x80) else 0; self.zero = 1 if r==0 else 0

    def getMemoryMap(self,posIni=0,posFin=255):
        buf=''; p=posIni
        for _ in range(posIni,posFin+1):
            buf += f'{p:02X} :: {self.memory[p]:02X} ({self.memory[p]:03})\n'; p+=1
        return buf

    def getSymbolsTable(self):
        if not self.symbols: return ''
        m = max(self.symbols,key=len); s=''
        for k,v in self.symbols.items(): s += f'{k:>{len(m)}}: {v:02X} ({v:03})\n'
        return s

if __name__=='__main__':
    cpu=CPU()
    asm = """
; Exemplo de programa para testar o simulador CLEÓPATRA 3.0
.CODE
LDA in
JZ jp_else
LDA #01
JMP end_if
jp_else:
LDA #02
end_if:
STA s
HLT
.ENDCODE

.DATA
in: DB #01
s: DB #00
.ENDDATA

"""
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
