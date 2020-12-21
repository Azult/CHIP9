#!/usr/bin/python

def initiate():
	mach = Machine()
	print "[*] Initiation ROM"
	return mach


class Machine(object):

	breakpoints = []		# Array of breakpoints

	# Initiate machine
	def __init__(self):
		self.A = 0x0				# 8-bit
		self.B = 0x0				# 8-bit
		self.C = 0x0				# 8-bit
		self.D = 0x0				# 8-bit
		self.E = 0x0				# 8-bit
		self.H = 0x0				# 8-bit
		self.L = 0x0				# 8-bit
		self.SP = 0xFFFF			# 16-bit
		self.PC = 0x0000			# 16-bit
		self.F = {"Z":0,"N":0,"H":0,"C":0}
		self.memory = [0]*0x10000
		self.screen = [ [' ']*128 for _ in xrange(64) ] # Screen
		self.run = 0				# Boolean if rom is running
		self.exit = 0				# Exit the debugger
		self.load_bootrom()
		self.load_rom()


	def print_screen(self):
		print '\n'.join([''.join(i) for i in self.screen])
		# with open("screen","w") as matrix:
		# 	matrix.write('\n'.join([''.join(i) for i in self.screen]))

	def clear_screen(self):
		self.screen = [ [' ']*128 for _ in xrange(64) ]

	def set_eflags(self):
		self.F["Z"] = 1
		self.F["N"] = 1
		self.F["H"] = 1
		self.F["C"] = 1

	def zero_eflags(self):
		self.F["Z"] = 0
		self.F["N"] = 0
		self.F["H"] = 0
		self.F["C"] = 0

	def ZN_hc(self, dest):
		self.F["H"] = 0
		self.F["C"] = 0
		if (self.twos_comp(dest) < 0):
			self.F["N"] = 1
			self.F["Z"] = 0
		elif (dest == 0):
			self.F["Z"] = 1
			self.F["N"] = 0
		else:
			self.F["Z"] = 0
			self.F["N"] = 0

	def print_context(self, stack, inst):
		if self.run:
			print "==============Context=============="
			self.print_registers()
			self.print_eflags()
			self.print_stack(stack)
			self.print_instructions(self.PC, inst)
			print "\n"

	
	# Print debug menu
	def print_menu(self):
		print '''
Debug menu
[*] Debug options:
[-] context					# Print context
[-] print instructions				# Print instructions
	Usage: inst 0x1000 10
[-] print memory				# Print memory
	Usage: mem 0x1000 10
[-] next					# Execute next command
[-] break					# Set breakpoint
	Usage: b 0x1000			
[-] db						# Delete breakpoints
[-] help					# Print this help
[-] running					# Starts execution from begining
[-] continue					# Continues execution
[-] find instruction				# Find an instruction
	Usage: find inst "JMP 0x2a"
[-] exit					# Exit debugger
			'''


	# Load the bootrom
	def load_bootrom(self):
		with open('bootrom', 'r') as bootrom:
			bootrom = bootrom.read()
			for i in xrange(779):
				self.memory[i] = ord(bootrom[i])

	# Load the rom
	def load_rom(self):
		with open('rom', 'r') as rom:
			rom = rom.read()
			for i in xrange(3072):
				# self.memory[0x597+i] = ord(rom[i])
				self.memory[0x56e+i] = ord(rom[i])

	# Print EFLAGS
	def print_eflags(self):
		print "EFLAGS: " + \
		"|Z:" + str(self.F["Z"]) + \
		"|N:" + str(self.F["N"]) + \
		"|H:" + str(self.F["H"]) + \
		"|C:" + str(self.F["C"]) +'|'

	def print_registers(self):
		print '''
------------Registers------------:
A: {0}
B: {1}
C: {2}
D: {3}
E: {4}
H: {5}	\\
	[{9}] -----> {10}
L: {6}	/
SP: {7}
PC: {8}
		'''.format(hex(self.A),hex(self.B),hex(self.C),hex(self.D),hex(self.E),hex(self.H),
			hex(self.L),hex(self.SP),hex(self.PC),hex((self.H<<8) + self.L),hex(self.memory[(self.H<<8) + self.L]))
		

	def print_stack(self,len):
		print "\n--------------Stack--------------"
		stack = self.SP+2
		length = min(len,0xffff-stack)
		for i in range(0,length,2):
			print '{0}: {1}'.format(hex(stack + i),hex((self.memory[stack + i]<<8)+self.memory[stack + i + 1]))


	def print_instructions(self,start,count):
		print "\n-----------Instructions-----------"
		pc = start
		for j in xrange(count):
			inst, len = self.read_instruction(pc)
			opcod = ""
			for i in xrange(len):
				opcod += '{0:0{1}X}'.format(self.memory[pc + i],2) + ' '
			print '{0:0{1}X}'.format(pc,4) + ": " + opcod + ' # ' + inst
			pc += len

	def print_memory(self,start,count):
		for i in xrange(count):
			print '{0:0{1}X}'.format(start+i,4) + ': ' + hex(self.memory[start+i])

	def find_instruction(self,instruction):
		for i in xrange(0xFFFF):
			inst, a = self.read_instruction(i)
			if (instruction in str(inst)):
				self.print_instructions(i,1)

	def cmp_regs(self,a,b):
			self.set_eflags()
			if (b == a):
				self.F["Z"] = 1
				self.F["N"] = 0
			elif (b < a):
				self.F["N"] = 1
				self.F["Z"] = 0
			else:
				self.F["N"] = 0
				self.F["Z"] = 0

	def read_instruction(self, addr):

		# Loads
		## LDI R, xx
		if (self.memory[addr] == 0x20):
			return "LDI B, {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x30):
			return "LDI C, {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x40):
			return "LDI D, {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x50):
			return "LDI E, {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x60):
			return "LDI H, {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x70):
			return "LDI L, {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x80):
			return "LDI (HL), {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0x90):
			return "LDI A, {0}".format(hex(self.memory[addr + 1])), 2
		## LDX RR, xxyy
		elif (self.memory[addr] == 0x21):
			return "LDX BC, {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x31):
			return "LDX DE, {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x41):
			return "LDX HL, {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x22):
			return "LDX SP, {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3


		# Stack pushes
		## PUSH R
		elif (self.memory[addr] == 0x81):
			return "PUSH B", 1
		elif (self.memory[addr] == 0x91):
			return "PUSH C", 1
		elif (self.memory[addr] == 0xA1):
			return "PUSH D", 1
		elif (self.memory[addr] == 0xB1):
			return "PUSH E", 1
		elif (self.memory[addr] == 0xC1):
			return "PUSH H", 1
		elif (self.memory[addr] == 0xD1):
			return "PUSH L", 1
		elif (self.memory[addr] == 0xC0):
			return "PUSH (HL)", 1
		elif (self.memory[addr] == 0xD0):
			return "PUSH A", 1
		## PUSH RR
		elif (self.memory[addr] == 0x51):
			return "PUSH BC", 1
		elif (self.memory[addr] == 0x61):
			return "PUSH DE", 1
		elif (self.memory[addr] == 0x71):
			return "PUSH HL", 1


		# Stack pops
		## POP R
		elif (self.memory[addr] == 0x82):
			return "POP B", 1
		elif (self.memory[addr] == 0x92):
			return "POP C", 1
		elif (self.memory[addr] == 0xA2):
			return "POP D", 1
		elif (self.memory[addr] == 0xB2):
			return "POP E", 1
		elif (self.memory[addr] == 0xC2):
			return "POP H", 1
		elif (self.memory[addr] == 0xD2):
			return "POP L", 1
		elif (self.memory[addr] == 0xC3):
			return "POP (HL)", 1
		elif (self.memory[addr] == 0xD3):
			return "POP A", 1
		## POP RR
		elif (self.memory[addr] == 0x52):
			return "POP BC", 1
		elif (self.memory[addr] == 0x62):
			return "POP DE", 1
		elif (self.memory[addr] == 0x72):
			return "POP HL", 1


		# Register movement
		## MOV R1, R2
		elif (self.memory[addr] == 0x09):
			return "MOV B, B", 1
		elif (self.memory[addr] == 0x19):
			return "MOV B, C", 1
		elif (self.memory[addr] == 0x29):
			return "MOV B, D", 1
		elif (self.memory[addr] == 0x39):
			return "MOV B, E", 1
		elif (self.memory[addr] == 0x49):
			return "MOV B, H", 1
		elif (self.memory[addr] == 0x59):
			return "MOV B, L", 1
		elif (self.memory[addr] == 0x69):
			return "MOV B, (HL)", 1
		elif (self.memory[addr] == 0x79):
			return "MOV B, A", 1
		elif (self.memory[addr] == 0x89):
			return "MOV C, B", 1
		elif (self.memory[addr] == 0x99):
			return "MOV C, C", 1
		elif (self.memory[addr] == 0xA9):
			return "MOV C, D", 1
		elif (self.memory[addr] == 0xB9):
			return "MOV C, E", 1
		elif (self.memory[addr] == 0xC9):
			return "MOV C, H", 1
		elif (self.memory[addr] == 0xD9):
			return "MOV C, L", 1
		elif (self.memory[addr] == 0xE9):
			return "MOV C, (HL)", 1
		elif (self.memory[addr] == 0xF9):
			return "MOV C, A", 1	
		elif (self.memory[addr] == 0x0A):
			return "MOV D, B", 1
		elif (self.memory[addr] == 0x1A):
			return "MOV D, C", 1
		elif (self.memory[addr] == 0x2A):
			return "MOV D, D", 1
		elif (self.memory[addr] == 0x3A):
			return "MOV D, E", 1
		elif (self.memory[addr] == 0x4A):
			return "MOV D, H", 1
		elif (self.memory[addr] == 0x5A):
			return "MOV D, L", 1
		elif (self.memory[addr] == 0x6A):
			return "MOV D, (HL)", 1
		elif (self.memory[addr] == 0x7A):
			return "MOV D, A", 1
		elif (self.memory[addr] == 0x8A):
			return "MOV E, B", 1
		elif (self.memory[addr] == 0x9A):
			return "MOV E, C", 1
		elif (self.memory[addr] == 0xAA):
			return "MOV E, D", 1
		elif (self.memory[addr] == 0xBA):
			return "MOV E, E", 1
		elif (self.memory[addr] == 0xCA):
			return "MOV E, H", 1
		elif (self.memory[addr] == 0xDA):
			return "MOV E, L", 1
		elif (self.memory[addr] == 0xEA):
			return "MOV E, (HL)", 1
		elif (self.memory[addr] == 0xFA):
			return "MOV E, A", 1
		elif (self.memory[addr] == 0x0B):
			return "MOV H, B", 1
		elif (self.memory[addr] == 0x1B):
			return "MOV H, C", 1
		elif (self.memory[addr] == 0x2B):
			return "MOV H, D", 1
		elif (self.memory[addr] == 0x3B):
			return "MOV H, E", 1
		elif (self.memory[addr] == 0x4B):
			return "MOV H, H", 1
		elif (self.memory[addr] == 0x5B):
			return "MOV H, L", 1
		elif (self.memory[addr] == 0x6B):
			return "MOV H, (HL)", 1
		elif (self.memory[addr] == 0x7B):
			return "MOV H, A", 1
		elif (self.memory[addr] == 0x8B):
			return "MOV L, B", 1
		elif (self.memory[addr] == 0x9B):
			return "MOV L, C", 1
		elif (self.memory[addr] == 0xAB):
			return "MOV L, D", 1
		elif (self.memory[addr] == 0xBB):
			return "MOV L, E", 1
		elif (self.memory[addr] == 0xCB):
			return "MOV L, H", 1
		elif (self.memory[addr] == 0xDB):
			return "MOV L, L", 1
		elif (self.memory[addr] == 0xEB):
			return "MOV L, (HL)", 1
		elif (self.memory[addr] == 0xFB):
			return "MOV L, A", 1
		elif (self.memory[addr] == 0x0C):
			return "MOV (HL), B", 1
		elif (self.memory[addr] == 0x1C):
			return "MOV (HL), C", 1
		elif (self.memory[addr] == 0x2C):
			return "MOV (HL), D", 1
		elif (self.memory[addr] == 0x3C):
			return "MOV (HL), E", 1
		elif (self.memory[addr] == 0x4C):
			return "MOV (HL), H", 1
		elif (self.memory[addr] == 0x5C):
			return "MOV (HL), L", 1
		elif (self.memory[addr] == 0x6C):
			return "HCF", 1
		elif (self.memory[addr] == 0x7C):
			return "MOV (HL), A", 1
		elif (self.memory[addr] == 0x8C):
			return "MOV A, B", 1
		elif (self.memory[addr] == 0x9C):
			return "MOV A, C", 1
		elif (self.memory[addr] == 0xAC):
			return "MOV A, D", 1
		elif (self.memory[addr] == 0xBC):
			return "MOV A, E", 1
		elif (self.memory[addr] == 0xCC):
			return "MOV A, H", 1
		elif (self.memory[addr] == 0xDC):
			return "MOV A, L", 1
		elif (self.memory[addr] == 0xEC):
			return "MOV A, (HL)", 1
		elif (self.memory[addr] == 0xFC):
			return "MOV A, A", 1
		# MOV RR1, RR2
		elif (self.memory[addr] == 0xED):
			return "MOV HL, BC", 1
		elif (self.memory[addr] == 0xFD):
			return "MOV HL, DE", 1


		# Arithmetic
		## Flag setting
		### CLRFLAG
		elif (self.memory[addr] == 0x08):
			return "CLRFLAG", 1
		### SETFLAG f, x
		elif (self.memory[addr] == 0x08):
			return "SETFLAG Z, 1", 1
		elif (self.memory[addr] == 0x28):
			return "SETFLAG Z, 0", 1
		elif (self.memory[addr] == 0x38):
			return "SETFLAG N, 1", 1
		elif (self.memory[addr] == 0x48):
			return "SETFLAG N, 0", 1
		elif (self.memory[addr] == 0x58):
			return "SETFLAG H, 1", 1
		elif (self.memory[addr] == 0x68):
			return "SETFLAG H, 0", 1
		elif (self.memory[addr] == 0x78):
			return "SETFLAG C, 1", 1
		elif (self.memory[addr] == 0x88):
			return "SETFLAG C, 0", 1

		## Addition
		### ADD R
		elif (self.memory[addr] == 0x04):
			return "ADD B", 1
		elif (self.memory[addr] == 0x14):
			return "ADD C", 1
		elif (self.memory[addr] == 0x24):
			return "ADD D", 1
		elif (self.memory[addr] == 0x34):
			return "ADD E", 1
		elif (self.memory[addr] == 0x44):
			return "ADD H", 1
		elif (self.memory[addr] == 0x54):
			return "ADD L", 1
		elif (self.memory[addr] == 0x64):
			return "ADD (HL)", 1
		elif (self.memory[addr] == 0x74):
			return "ADD A", 1
		### ADDI xx
		elif (self.memory[addr] == 0xA7):
			return "ADDI {0}".format(hex(self.memory[addr + 1])), 2
		### ADDX RR
		elif (self.memory[addr] == 0x83):
			return "ADDX BC", 1
		elif (self.memory[addr] == 0x93):
			return "ADDX DE", 1
		elif (self.memory[addr] == 0xA3):
			return "ADDX HL", 1

		## Substraction
		### SUB R
		elif (self.memory[addr] == 0x84):
			return "SUB B", 1
		elif (self.memory[addr] == 0x94):
			return "SUB C", 1
		elif (self.memory[addr] == 0xA4):
			return "SUB D", 1
		elif (self.memory[addr] == 0xB4):
			return "SUB E", 1
		elif (self.memory[addr] == 0xC4):
			return "SUB H", 1
		elif (self.memory[addr] == 0xD4):
			return "SUB L", 1
		elif (self.memory[addr] == 0xE4):
			return "SUB (HL)", 1
		elif (self.memory[addr] == 0xF4):
			return "SUB A", 1
		### SUBI xx
		elif (self.memory[addr] == 0xB7):
			return "SUBI {0}".format(hex(self.memory[addr + 1])), 2

		## Increment
		### INC R
		elif (self.memory[addr] == 0x03):
			return "INC B", 1
		elif (self.memory[addr] == 0x13):
			return "INC C", 1
		elif (self.memory[addr] == 0x23):
			return "INC D", 1
		elif (self.memory[addr] == 0x33):
			return "INC E", 1
		elif (self.memory[addr] == 0x43):
			return "INC H", 1
		elif (self.memory[addr] == 0x53):
			return "INC L", 1
		elif (self.memory[addr] == 0x63):
			return "INC (HL)", 1
		elif (self.memory[addr] == 0x73):
			return "INC A", 1
		### INX RR
		elif (self.memory[addr] == 0xA8):
			return "INX BC", 1
		elif (self.memory[addr] == 0xB8):
			return "INX DE", 1
		elif (self.memory[addr] == 0xC8):
			return "INX HL", 1

		## Decrement
		### DEC R
		elif (self.memory[addr] == 0x07):
			return "DEC B", 1
		elif (self.memory[addr] == 0x17):
			return "DEC C", 1
		elif (self.memory[addr] == 0x27):
			return "DEC D", 1
		elif (self.memory[addr] == 0x37):
			return "DEC E", 1
		elif (self.memory[addr] == 0x47):
			return "DEC H", 1
		elif (self.memory[addr] == 0x57):
			return "DEC L", 1
		elif (self.memory[addr] == 0x67):
			return "DEC (HL)", 1
		elif (self.memory[addr] == 0x77):
			return "DEC A", 1


		# Logical operations
		## AND
		### AND R
		elif (self.memory[addr] == 0x05):
			return "AND B", 1
		elif (self.memory[addr] == 0x15):
			return "AND C", 1
		elif (self.memory[addr] == 0x25):
			return "AND D", 1
		elif (self.memory[addr] == 0x35):
			return "AND E", 1
		elif (self.memory[addr] == 0x45):
			return "AND H", 1
		elif (self.memory[addr] == 0x55):
			return "AND L", 1
		elif (self.memory[addr] == 0x65):
			return "AND (HL)", 1
		elif (self.memory[addr] == 0x75):
			return "AND A", 1
		### ANDI xx
		elif (self.memory[addr] == 0xC7):
			return "ANDI {0}".format(hex(self.memory[addr + 1])), 2

		## OR
		### OR R
		elif (self.memory[addr] == 0x85):
			return "OR B", 1
		elif (self.memory[addr] == 0x95):
			return "OR C", 1
		elif (self.memory[addr] == 0xA5):
			return "OR D", 1
		elif (self.memory[addr] == 0xB5):
			return "OR E", 1
		elif (self.memory[addr] == 0xC5):
			return "OR H", 1
		elif (self.memory[addr] == 0xD5):
			return "OR L", 1
		elif (self.memory[addr] == 0xE5):
			return "OR (HL)", 1
		elif (self.memory[addr] == 0xF5):
			return "OR A", 1
		### ORI xx
		elif (self.memory[addr] == 0xD7):
			return "ORI {0}".format(hex(self.memory[addr + 1])), 2

		## XOR
		### XOR R
		elif (self.memory[addr] == 0x06):
			return "XOR B", 1
		elif (self.memory[addr] == 0x16):
			return "XOR C", 1
		elif (self.memory[addr] == 0x26):
			return "XOR D", 1
		elif (self.memory[addr] == 0x36):
			return "XOR E", 1
		elif (self.memory[addr] == 0x46):
			return "XOR H", 1
		elif (self.memory[addr] == 0x56):
			return "XOR L", 1
		elif (self.memory[addr] == 0x66):
			return "XOR (HL)", 1
		elif (self.memory[addr] == 0x76):
			return "XOR A", 1
		### ORI xx
		elif (self.memory[addr] == 0xE7):
			return "XORI {0}".format(hex(self.memory[addr + 1])), 2

		## Comparisons
		### CMP R
		elif (self.memory[addr] == 0x86):
			return "CMP B", 1
		elif (self.memory[addr] == 0x96):
			return "CMP C", 1
		elif (self.memory[addr] == 0xA6):
			return "CMP D", 1
		elif (self.memory[addr] == 0xB6):
			return "CMP E", 1
		elif (self.memory[addr] == 0xC6):
			return "CMP H", 1
		elif (self.memory[addr] == 0xD6):
			return "CMP L", 1
		elif (self.memory[addr] == 0xE6):
			return "CMP (HL)", 1
		elif (self.memory[addr] == 0xF6):
			return "CMP A", 1
		### CMPI xx
		elif (self.memory[addr] == 0xF7):
			return "CMPI A {0}".format(hex(self.memory[addr + 1])), 2
		### CMPS R
		elif (self.memory[addr] == 0x0D):
			return "CMP B", 1
		elif (self.memory[addr] == 0x1D):
			return "CMP C", 1
		elif (self.memory[addr] == 0x2D):
			return "CMP D", 1
		elif (self.memory[addr] == 0x3D):
			return "CMP E", 1
		elif (self.memory[addr] == 0x4D):
			return "CMP H", 1
		elif (self.memory[addr] == 0x5D):
			return "CMP L", 1
		elif (self.memory[addr] == 0x6D):
			return "CMP (HL)", 1
		elif (self.memory[addr] == 0x7D):
			return "CMP A", 1


		# I/O
		## Serial
		### SIN
		elif (self.memory[addr] == 0xE0):
			return "SIN", 1
		### SOUT
		elif (self.memory[addr] == 0xE1):
			return "SOUT", 1

		## Screen
		### CLRSCR
		elif (self.memory[addr] == 0xF0):
			return "CLRSCR", 1
		### DRAW
		elif (self.memory[addr] == 0xF1):
			return "DRAW", 1


		# Branching
		## Jumping
		### JMP xxyy
		elif (self.memory[addr] == 0x0F):
			return "JMP {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		### JMPcc xxyy
		elif (self.memory[addr] == 0x1F):
			return "JMPZ {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x2F):
			return "JMPNZ {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x3F):
			return "JMPN {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x4F):
			return "JMPNN {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x5F):
			return "JMPH {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x6F):
			return "JMPNH {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x7F):
			return "JMPC {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		elif (self.memory[addr] == 0x8F):
			return "JMPNC {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3

		## Near-jumping
		### JMP xxyy
		elif (self.memory[addr] == 0x9F):
			return "JMP {0}".format(hex(self.memory[addr + 1])), 2
		### JMPcc xxyy
		elif (self.memory[addr] == 0xAF):
			return "JMPZ {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xBF):
			return "JMPNZ {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xCF):
			return "JMPN {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xDF):
			return "JMPNN {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xEF):
			return "JMPH {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xFF):
			return "JMPNH {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xEE):
			return "JMPC {0}".format(hex(self.memory[addr + 1])), 2
		elif (self.memory[addr] == 0xFE):
			return "JMPNC {0}".format(hex(self.memory[addr + 1])), 2

		## Functions
		### CALL xxyy
		elif (self.memory[addr] == 0x1E):
			return "CALL {0}".format(hex((self.memory[addr + 2]<<8) + self.memory[addr + 1])), 3
		### RET
		elif (self.memory[addr] == 0x0E):
			return "RET", 1


		# Misccellaneous
		## No operration
		### NOP
		elif (self.memory[addr] == 0x00):
			return "NOP", 1


		# Unrecognized instruction
		else:
			return "????" , 1

	
	def execute_instruction(self):

		# Loads
		## LDI R, xx
		if (self.memory[self.PC] == 0x20):
			self.B = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x30):
			self.C = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x40):
			self.D = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x50):
			self.E = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x60):
			self.H = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x70):
			self.L = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x80):
			self.memory[(self.H<<8) + self.L] = self.memory[self.PC + 1]
			self.PC += 2
		elif (self.memory[self.PC] == 0x90):
			self.A = self.memory[self.PC + 1]
			self.PC += 2
		## LDX RR, xxyy
		elif (self.memory[self.PC] == 0x21):
			self.B = self.memory[self.PC+2]
			self.C = self.memory[self.PC+1]
			self.PC += 3
		elif (self.memory[self.PC] == 0x31):
			self.D = self.memory[self.PC+2]
			self.E = self.memory[self.PC+1]
			self.PC += 3
		elif (self.memory[self.PC] == 0x41):
			self.H = self.memory[self.PC+2]
			self.L = self.memory[self.PC+1]
			self.PC += 3
		elif (self.memory[self.PC] == 0x22):
			self.SP = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			self.PC += 3


		# Stack pushes
		## PUSH R
		elif (self.memory[self.PC] == 0x81):
			self.memory[self.SP] = self.B
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0x91):
			self.memory[self.SP] = self.C
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0xA1):
			self.memory[self.SP] = self.D
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0xB1):
			self.memory[self.SP] = self.E
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0xC1):
			self.memory[self.SP] = self.H
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0xD1):
			self.memory[self.SP] = self.L
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0xC0):
			self.memory[self.SP] = self.memory[(self.H<<8) + self.L]
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0xD0):
			self.memory[self.SP] = self.A
			# self.memory[self.SP+1] = 0
			self.SP -= 2
			self.PC += 1
		## PUSH RR
		elif (self.memory[self.PC] == 0x51):
			self.memory[self.SP+1] = self.B
			self.memory[self.SP] = self.C
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0x61):
			self.memory[self.SP+1] = self.D
			self.memory[self.SP] = self.E
			self.SP -= 2
			self.PC += 1
		elif (self.memory[self.PC] == 0x71):
			self.memory[self.SP+1] = self.H
			self.memory[self.SP] = self.L
			self.SP -= 2
			self.PC += 1


		# Stack pops
		## POP R
		elif (self.memory[self.PC] == 0x82):
			self.SP += 2
			self.B = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0x92):
			self.SP += 2
			self.C = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0xA2):
			self.SP += 2
			self.D = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0xB2):
			self.SP += 2
			self.E = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0xC2):
			self.SP += 2
			self.H = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0xD2):
			self.SP += 2
			self.L = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0xC3):
			self.SP += 2
			self.memory[(self.H<<8) + self.L] = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0xD3):
			self.SP += 2
			self.A = self.memory[self.SP]
			self.PC += 1
		## POP RR
		elif (self.memory[self.PC] == 0x52):
			self.SP += 2
			self.B = self.memory[self.SP+1]
			self.C = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0x62):
			self.SP += 2
			self.D = self.memory[self.SP+1]
			self.E = self.memory[self.SP]
			self.PC += 1
		elif (self.memory[self.PC] == 0x72):
			self.SP += 2
			self.H = self.memory[self.SP+1]
			self.L = self.memory[self.SP]
			self.PC += 1


		# Register movement
		## MOV R1, R2
		elif (self.memory[self.PC] == 0x09):
			self.B = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x19):
			self.B = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0x29):
			self.B = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0x39):
			self.B = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0x49):
			self.B = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0x59):
			self.B = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0x69):
			self.B = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0x79):
			self.B = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x89):
			self.C = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x99):
			self.C = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0xA9):
			self.C = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0xB9):
			self.C = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0xC9):
			self.C = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0xD9):
			self.C = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0xE9):
			self.C = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0xF9):
			self.C = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x0A):
			self.D = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x1A):
			self.D = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0x2A):
			self.D = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0x3A):
			self.D = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0x4A):
			self.D = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0x5A):
			self.D = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0x6A):
			self.D = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0x7A):
			self.D = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x8A):
			self.E = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x9A):
			self.E = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0xAA):
			self.E = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0xBA):
			self.E = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0xCA):
			self.E = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0xDA):
			self.E = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0xEA):
			self.E = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0xFA):
			self.E = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x0B):
			self.H = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x1B):
			self.H = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0x2B):
			self.H = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0x3B):
			self.H = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0x4B):
			self.H = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0x5B):
			self.H = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0x6B):
			self.H = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0x7B):
			self.H = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x8B):
			self.L = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x9B):
			self.L = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0xAB):
			self.L = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0xBB):
			self.L = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0xCB):
			self.L = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0xDB):
			self.L = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0xEB):
			self.L = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0xFB):
			self.L = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x0C):
			self.memory[(self.H<<8) + self.L] = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x1C):
			self.memory[(self.H<<8) + self.L] = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0x2C):
			self.memory[(self.H<<8) + self.L] = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0x3C):
			self.memory[(self.H<<8) + self.L] = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0x4C):
			self.memory[(self.H<<8) + self.L] = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0x5C):
			self.memory[(self.H<<8) + self.L] = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0x6C):
			self.memory[(self.H<<8) + self.L] = self.memory[(self.H<<8) + self.L]
			print "Halt!!! Everything burns!!! RUN!!!!!!"
			exit()
			self.PC += 1
		elif (self.memory[self.PC] == 0x7C):
			self.memory[(self.H<<8) + self.L] = self.A
			self.PC += 1
		elif (self.memory[self.PC] == 0x8C):
			self.A = self.B
			self.PC += 1
		elif (self.memory[self.PC] == 0x9C):
			self.A = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0xAC):
			self.A = self.D
			self.PC += 1
		elif (self.memory[self.PC] == 0xBC):
			self.A = self.E
			self.PC += 1
		elif (self.memory[self.PC] == 0xCC):
			self.A = self.H
			self.PC += 1
		elif (self.memory[self.PC] == 0xDC):
			self.A = self.L
			self.PC += 1
		elif (self.memory[self.PC] == 0xEC):
			self.A = self.memory[(self.H<<8) + self.L]
			self.PC += 1
		elif (self.memory[self.PC] == 0xFC):
			self.A = self.A
			self.PC += 1
		# MOV RR1, RR2
		elif (self.memory[self.PC] == 0xED):
			self.H = self.B
			self.L = self.C
			self.PC += 1
		elif (self.memory[self.PC] == 0xFD):
			self.H = self.D
			self.L = self.E
			self.PC += 1


		# Arithmetic
		## Flag setting
		### CLRFLAG
		elif (self.memory[self.PC] == 0x08):
			self.zero_eflags()
			self.PC += 1
		### SETFLAG f, x
		elif (self.memory[self.PC] == 0x08):
			self.F["Z"] = 1
			self.PC += 1
		elif (self.memory[self.PC] == 0x28):
			self.F["Z"] = 0
			self.PC += 1
		elif (self.memory[self.PC] == 0x38):
			self.F["N"] = 1
			self.PC += 1
		elif (self.memory[self.PC] == 0x48):
			self.F["N"] = 0
			self.PC += 1
		elif (self.memory[self.PC] == 0x58):
			self.F["H"] = 1
			self.PC += 1
		elif (self.memory[self.PC] == 0x68):
			self.F["H"] = 0
			self.PC += 1
		elif (self.memory[self.PC] == 0x78):
			self.F["C"] = 1
			self.PC += 1
		elif (self.memory[self.PC] == 0x88):
			self.F["C"] = 0
			self.PC += 1

		## Addition
		### ADD R
		elif (self.memory[self.PC] == 0x04):
			self.B += self.A
			self.B &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x14):
			self.C += self.A
			self.C &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x24):
			self.D += self.A
			self.D &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x34):
			self.E += self.A
			self.E &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x44):
			self.H += self.A
			self.H &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x54):
			self.L += self.A
			self.L &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x64):
			self.memory[(self.H<<8) + self.L] += self.A
			self.memory[(self.H<<8) + self.L] &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x74):
			self.A += self.A
			self.A &= 0xFF
			self.set_eflags()
			self.PC += 1
		### ADDI xx
		elif (self.memory[self.PC] == 0xA7):
			self.A += self.memory[self.PC + 1]
			self.A &= 0xFF
			self.set_eflags()
			self.PC += 2
		### ADDX RR
		elif (self.memory[self.PC] == 0x83):
			sum = (self.B<<8) + self.C + self.A
			sum &= 0xFFFF
			self.B = sum>>8
			self.C = sum & 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x93):
			sum = (self.D<<8) + self.E + self.A
			sum &= 0xFFFF
			self.D = sum>>8
			self.E = sum & 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xA3):
			sum = (self.H<<8) + self.L + self.A
			sum &= 0xFFFF
			self.H = sum>>8
			self.L = sum & 0xff
			self.set_eflags()
			self.PC += 1

		## Substraction
		### SUB R
		elif (self.memory[self.PC] == 0x84):
			self.B -= self.A
			self.B &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x94):
			self.C -= self.A
			self.C &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xA4):
			self.D -= self.A
			self.D &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xB4):
			self.E -= self.A
			self.E &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xC4):
			self.H -= self.A
			self.H &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xD4):
			self.L -= self.A
			self.L &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xE4):
			self.memory[(self.H<<8) + self.L] -= self.A
			self.memory[(self.H<<8) + self.L] &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0xF4):
			self.A -= self.A
			self.A &= 0xFF
			self.set_eflags()
			self.PC += 1
		### SUBI xx
		elif (self.memory[self.PC] == 0xB7):
			self.A -= self.memory[self.PC + 1]
			self.A &= 0xFF
			self.set_eflags()
			self.PC += 2

		## Increment
		### INC R
		elif (self.memory[self.PC] == 0x03):
			self.B += 1
			self.B &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x13):
			self.C += 1
			self.C &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x23):
			self.D += 1
			self.D &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x33):
			self.E += 1
			self.E &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x43):
			self.H += 1
			self.H &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x53):
			self.L += 1
			self.L &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x63):
			self.memory[(self.H<<8) + self.L] += 1
			self.memory[(self.H<<8) + self.L] &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x73):
			self.A += 1
			self.A &= 0xff
			self.set_eflags()
			self.PC += 1
		### INX RR
		elif (self.memory[self.PC] == 0xA8):
			sum = (self.B<<8) + self.C + 1
			sum &= 0xFFFF
			self.B = sum>>8
			self.C = sum & 0xff
			self.PC += 1
		elif (self.memory[self.PC] == 0xB8):
			sum = (self.D<<8) + self.E + 1
			sum &= 0xFFFF
			self.D = sum>>8
			self.E = sum & 0xff
			self.PC += 1
		elif (self.memory[self.PC] == 0xC8):
			sum = (self.H<<8) + self.L + 1
			sum &= 0xFFFF
			self.H = sum>>8
			self.L = sum & 0xff
			self.PC += 1

		## Decrement
		### DEC R
		elif (self.memory[self.PC] == 0x07):
			self.B -= 1
			self.B &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x17):
			self.C -= 1
			self.C &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x27):
			self.D -= 1
			self.D &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x37):
			self.E -= 1
			self.E &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x47):
			self.H -= 1
			self.H &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x57):
			self.L -= 1
			self.L &= 0xff
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x67):
			self.memory[(self.H<<8) + self.L] -= 1
			self.memory[(self.H<<8) + self.L] &= 0xFF
			self.set_eflags()
			self.PC += 1
		elif (self.memory[self.PC] == 0x77):
			self.A -= 1
			self.A &= 0xff
			self.set_eflags()
			self.PC += 1


		# Logical operations
		## AND
		### AND R
		elif (self.memory[self.PC] == 0x05):
			self.B &= self.A
			self.B &= 0xff
			self.ZN_hc(self.B)
			self.PC += 1
		elif (self.memory[self.PC] == 0x15):
			self.C &= self.A
			self.C &= 0xff
			self.ZN_hc(self.C)
			self.PC += 1
		elif (self.memory[self.PC] == 0x25):
			self.D &= self.A
			self.D &= 0xff
			self.ZN_hc(self.D)
			self.PC += 1
		elif (self.memory[self.PC] == 0x35):
			self.E &= self.A
			self.E &= 0xff
			self.ZN_hc(self.E)
			self.PC += 1
		elif (self.memory[self.PC] == 0x45):
			self.H &= self.A
			self.H &= 0xff
			self.ZN_hc(self.H)
			self.PC += 1
		elif (self.memory[self.PC] == 0x55):
			self.L &= self.A
			self.L &= 0xff
			self.ZN_hc(self.L)
			self.PC += 1
		elif (self.memory[self.PC] == 0x65):
			self.memory[(self.H<<8) + self.L] &= self.A
			self.memory[(self.H<<8) + self.L] &= 0xff
			self.ZN_hc(self.memory[(self.H<<8) + self.L])
			self.PC += 1
		elif (self.memory[self.PC] == 0x75):
			self.A &= self.A
			self.A &= 0xff
			self.ZN_hc(self.A)
			self.PC += 1
		### ANDI xx
		elif (self.memory[self.PC] == 0xC7):
			self.A &= self.memory[self.PC + 1]
			self.A &= 0xff
			self.ZN_hc(self.A)
			self.PC += 2

		## OR
		### OR R
		elif (self.memory[self.PC] == 0x85):
			self.B |= self.A
			self.B &= 0xff
			self.ZN_hc(self.B)
			self.PC += 1
		elif (self.memory[self.PC] == 0x95):
			self.C |= self.A
			self.C &= 0xff
			self.ZN_hc(self.C)
			self.PC += 1
		elif (self.memory[self.PC] == 0xA5):
			self.D |= self.A
			self.D &= 0xff
			self.ZN_hc(self.D)
			self.PC += 1
		elif (self.memory[self.PC] == 0xB5):
			self.E |= self.A
			self.E &= 0xff
			self.ZN_hc(self.E)
			self.PC += 1
		elif (self.memory[self.PC] == 0xC5):
			self.H |= self.A
			self.H &= 0xff
			self.ZN_hc(self.H)
			self.PC += 1
		elif (self.memory[self.PC] == 0xD5):
			self.L |= self.A
			self.L &= 0xff
			self.ZN_hc(self.L)
			self.PC += 1
		elif (self.memory[self.PC] == 0xE5):
			self.memory[(self.H<<8) + self.L] |= self.A
			self.memory[(self.H<<8) + self.L] &= 0xff
			self.ZN_hc(self.memory[(self.H<<8) + self.L])
			self.PC += 1
		elif (self.memory[self.PC] == 0xF5):
			self.A |= self.A
			self.A &= 0xff
			self.ZN_hc(self.A)
			self.PC += 1
		### ORI xx
		elif (self.memory[self.PC] == 0xD7):
			self.A |= self.memory[self.PC + 1]
			self.A &= 0xff
			self.ZN_hc(self.A)
			self.PC += 2

		## XOR
		### XOR R
		elif (self.memory[self.PC] == 0x06):
			self.B ^= self.A
			self.B &= 0xff
			self.ZN_hc(self.B)
			self.PC += 1
		elif (self.memory[self.PC] == 0x16):
			self.C ^= self.A
			self.C &= 0xff
			self.ZN_hc(self.C)
			self.PC += 1
		elif (self.memory[self.PC] == 0x26):
			self.D ^= self.A
			self.D &= 0xff
			self.ZN_hc(self.D)
			self.PC += 1
		elif (self.memory[self.PC] == 0x36):
			self.E ^= self.A
			self.E &= 0xff
			self.ZN_hc(self.E)
			self.PC += 1
		elif (self.memory[self.PC] == 0x46):
			self.H ^= self.A
			self.H &= 0xff
			self.ZN_hc(self.H)
			self.PC += 1
		elif (self.memory[self.PC] == 0x56):
			self.L ^= self.A
			self.L &= 0xff
			self.ZN_hc(self.L)
			self.PC += 1
		elif (self.memory[self.PC] == 0x66):
			self.memory[(self.H<<8) + self.L] ^= self.A
			self.memory[(self.H<<8) + self.L] &= 0xff
			self.ZN_hc(self.memory[(self.H<<8) + self.L])
			self.PC += 1
		elif (self.memory[self.PC] == 0x76):
			self.A ^= self.A
			self.A &= 0xff
			self.ZN_hc(self.A)
			self.PC += 1
		### ORI xx
		elif (self.memory[self.PC] == 0xE7):
			self.A ^= self.memory[self.PC + 1]
			self.A &= 0xff
			self.ZN_hc(self.A)
			self.PC += 2

		
		## Comparisons
		### CMP R
		elif (self.memory[self.PC] == 0x86):
			self.cmp_regs(self.A, self.B)
			self.PC += 1
		elif (self.memory[self.PC] == 0x96):
			self.cmp_regs(self.A, self.C)
			self.PC += 1
		elif (self.memory[self.PC] == 0xA6):
			self.cmp_regs(self.A, self.D)
			self.PC += 1
		elif (self.memory[self.PC] == 0xB6):
			self.cmp_regs(self.A, self.E)
			self.PC += 1
		elif (self.memory[self.PC] == 0xC6):
			self.cmp_regs(self.A, self.H)
			self.PC += 1
		elif (self.memory[self.PC] == 0xD6):
			self.cmp_regs(self.A, self.L)
			self.PC += 1
		elif (self.memory[self.PC] == 0xE6):
			self.cmp_regs(self.A, self.memory[(self.H<<8) + self.L])
			self.PC += 1
		elif (self.memory[self.PC] == 0xF6):
			self.cmp_regs(self.A, self.A)
			self.PC += 1
		### CMPI xx
		elif (self.memory[self.PC] == 0xF7):
			self.cmp_regs(self.memory[self.PC + 1], self.A)
			self.PC += 2
		### CMPS R
		elif (self.memory[self.PC] == 0x0D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.B))
			self.PC += 1
		elif (self.memory[self.PC] == 0x1D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.C))
			self.PC += 1
		elif (self.memory[self.PC] == 0x2D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.D))
			self.PC += 1
		elif (self.memory[self.PC] == 0x3D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.E))
			self.PC += 1
		elif (self.memory[self.PC] == 0x4D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.H))
			self.PC += 1
		elif (self.memory[self.PC] == 0x5D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.L))
			self.PC += 1
		elif (self.memory[self.PC] == 0x6D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.memory[(self.H<<8) + self.L]))
			self.PC += 1 
		elif (self.memory[self.PC] == 0x7D):
			self.cmp_regs(self.twos_comp(self.A), self.twos_comp(self.A))
			self.PC += 1


		# I/O
		## Serial
		### SIN
		elif (self.memory[self.PC] == 0xE0):
			self.A = self.SIN()
			self.PC += 1
		### SOUT
		elif (self.memory[self.PC] == 0xE1):
			print "Added " + chr(self.A)
			with open("flag.txt","a") as flag:
				flag.write(chr(self.A))
			self.PC += 1

		## Screen
		### CLRSCR
		elif (self.memory[self.PC] == 0xF0):
			self.clear_screen()
			self.print_screen()
			self.PC += 1
		### DRAW
		elif (self.memory[self.PC] == 0xF1):
			self.draw()
			self.print_screen()
			self.PC += 1


		# Branching
		## Jumping
		### JMP xxyy
		elif (self.memory[self.PC] == 0x0F):
			self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
		### JMPcc xxyy
		elif (self.memory[self.PC] == 0x1F):
			if self.F["Z"]:
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x2F):
			if (self.F["Z"] == 0):
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x3F):
			if self.F["N"]:
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x4F):
			if (self.F["N"] == 0):
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x5F):
			if self.F["H"]:
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x6F):
			if (self.F["H"] == 0):
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x7F):
			if self.F["C"]:
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3
		elif (self.memory[self.PC] == 0x8F):
			if (self.F["C"] == 0):
				self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
			else:
				self.PC += 3

		## Near-jumping
		### JMP xx
		elif (self.memory[self.PC] == 0x9F):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2 + offset
		### JMPcc xx
		elif (self.memory[self.PC] == 0xAF):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if self.F["Z"]:
				self.PC += offset
		elif (self.memory[self.PC] == 0xBF):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if (self.F["Z"] == 0):
				self.PC += offset
		elif (self.memory[self.PC] == 0xCF):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if self.F["N"]:
				self.PC += offset
		elif (self.memory[self.PC] == 0xDF):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if (self.F["N"] == 0):
				self.PC += offset
		elif (self.memory[self.PC] == 0xEF):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if self.F["H"]:
				self.PC += offset
		elif (self.memory[self.PC] == 0xFF):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if (self.F["H"] == 0):
				self.PC += offset
		elif (self.memory[self.PC] == 0xEE):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if self.F["C"]:
				self.PC += offset
		elif (self.memory[self.PC] == 0xFE):
			offset = self.twos_comp(self.memory[self.PC + 1])
			self.PC += 2
			if (self.F["C"] == 0):
				self.PC += offset

		## Functions
		### CALL xxyy
		elif (self.memory[self.PC] == 0x1E):
			next = self.PC + 3
			self.memory[self.SP] = next & 0xff
			self.memory[self.SP+1] = next>>8
			self.SP -= 2
			self.PC = (self.memory[self.PC + 2]<<8) + self.memory[self.PC + 1]
		### RET
		elif (self.memory[self.PC] == 0x0E):
			self.SP += 2
			self.PC = self.memory[self.SP+1]
			self.PC <<= 8
			self.PC += self.memory[self.SP]


		# Misccellaneous
		## No operration
		### NOP
		elif (self.memory[self.PC] == 0x00):
			self.PC += 1

		# Unrecognized instruction
		else:
			print "[****] Unknown instruction"
			exit()

	
	def twos_comp(self, val):
		if (val & (1 << (7))) != 0:
			val = val - (1 << 8)
		return val


	def draw(self):
		A_bin = bin(self.A)[2:]
		pixels = '0'*(8-len(A_bin)) + A_bin
		pixels = pixels.replace('0', ' ').replace('1', '*')
		X = self.twos_comp(self.C)
		Y = self.twos_comp(self.B)
		for i in xrange(8):
			try:
				self.screen[Y][X + i] = pixels[i]
			except Exception as e:
				print str(e)

	def SIN(self):
		while True:
			message = '''
	    	Please press key:
	    	0. START
	    	1. SELECT
	    	2. B
	    	3. A
	    	4. RIGHT
	    	5. DOWN
	    	6. LEFT
	    	7.UP
	    	'''
	    	input_dict = {"0":"START", "1":"SELECT", "2":"B","3":"A",\
	    	"4":"RIGHT","5":"DOWN","6":"LEFT","7":"UP"}
	    	input = raw_input().strip()
	    	if input in input_dict:
	    		print "[-] Excepted :" + input
	    		return int(input)
	    	else:
	    		print "No such input, try again"
    	

	def breakpoint(self):
		previous_command = ""
		while True:
			command = raw_input("[*] break\n")
			if (command == ''):
				command = previous_command
			print "command " + command
			try:
				if (command.split(" ")[0] == "help"):
					self.print_menu()
					previous_command = command
				elif (command.split(" ")[0] == "inst"):
					start = int(command.split(" ")[1][2:].strip(),16)
					count = int(command.split(" ")[2].strip(),10)
					self.print_instructions(start, count)
					previous_command = command
				elif (command.split(" ")[0] == "mem"):
					start = int(command.split(" ")[1][2:].strip(),16)
					count = int(command.split(" ")[2].strip(),10)
					self.print_memory(start, count)
					previous_command = command
				elif (command.split(" ")[0] == "next"):
					if self.run:
						self.print_instructions(self.PC, 1)
						self.execute_instruction()
						self.print_context(10,6)
					else:
						print "[-] The rom is not running"
					previous_command = command
				elif (command.split(" ")[0] == "context"):
					if self.run:
						self.print_context(10, 6)
					else:
						print "[-] The rom is not running"
					previous_command = command
				elif (command.split(" ")[0] == "b"):
					self.breakpoints.append(int(command.split(" ")[1], 16))
					print "[-] Breakpoint " + hex(int(command.split(" ")[1], 16)) + " is set"
					previous_command = command
				elif (command.split(" ")[0] == "breakpoints"):
					for b in self.breakpoints:
						print hex(b)
					previous_command = command
				elif (command.split(" ")[0] == "db"):
					self.breakpoints = []
					print "[-] Breakpoints clear"
					previous_command = command
				elif (command.split(" ")[0] == "run"):
					self.__init__()
					self.run = 1
					self.run_execution()
					previous_command = command
				elif (command.split(" ")[0] == "continue"):
					if (self.run):
						self.execute_instruction()
						self.run_execution()
					else:
						print "[-] The rom is not running"
					previous_command = command
				elif (command.split('"')[0].strip() == "find inst"):
					inst_command = command.split('"')[1].split('"')[0]
					self.find_instruction(inst_command)
					previous_command = command
				elif (command.split(" ")[0] == "exit"):
					print "[-] Exiting"
					exit()
				else:
					print "[-] No such command"
					# break
			except Exception as e:
				print "Error: " + str(e)

	# Execute the rom
	def run_execution(self):
		while True:

			if (self.PC in self.breakpoints):
				self.print_context(10, 6)
				print "[-] Breakpoint reached: \nAddress: " + hex(self.PC)
				return
			else:
				# self.print_instructions(self.PC, 1)
				# self.print_context(10,6)
				self.execute_instruction()


	def exit(self):
		self.exit = 1

	def exit_status(self):
		return self.exit


if __name__ == "__main__":
	new_machine = initiate()
	new_machine.print_menu()
	new_machine.breakpoint()

