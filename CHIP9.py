#!/usr/bin/python
import sys
import pygame

def initiate():
	mach = Machine()
	mach.run_execution()

class Machine(object):

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
		pygame.init ()
		pygame.display.set_mode ((128, 64))
		self.surface = pygame.Surface ((128, 64))
		pygame.display.flip ()
		if (len(sys.argv) == 1):
			print "Please provide path to rom"
			exit()
		elif (len(sys.argv) == 2):
			self.load_bootrom()
		elif (len(sys.argv) == 3):
			self.load_bootrom()
			self.load_rom()
		

	def clear_screen(self):
		ar = pygame.PixelArray (self.surface)
		ar[:,:] = (0,0,0)
		del ar

	def show(self):
	    screen = pygame.display.get_surface()
	    screen.fill ((255, 255, 255))
	    screen.blit (self.surface, (0, 0))
	    pygame.display.flip ()
	    # raw_input("break")


	def print_screen(self):
		self.show()

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


	# Load the bootrom
	def load_bootrom(self):
		with open(sys.argv[1], 'r') as bootrom:
			bootrom = bootrom.read()
			for i in xrange(len(bootrom)):
				self.memory[i] = ord(bootrom[i])

	# Load the rom
	def load_rom(self):
		with open(sys.argv[2], 'r') as rom:
			rom = rom.read()
			for i in xrange(len(rom)):
				self.memory[0x56e+i] = ord(rom[i])


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
			self.PC += 1
		### SOUT
		elif (self.memory[self.PC] == 0xE1):
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
		X = self.twos_comp(self.C)
		Y = self.twos_comp(self.B)
		ar = pygame.PixelArray (self.surface)
		for i in xrange(8):
			try:
				ar[X + i][Y] = (int(pixels[i])*255,int(pixels[i])*255,int(pixels[i])*255)
			except Exception as e:
				print str(e)
		del ar
   	

	# Execute the rom
	def run_execution(self):
		while True:
			self.execute_instruction()

	def exit(self):
		self.exit = 1

	def exit_status(self):
		return self.exit


if __name__ == "__main__":
	initiate()

