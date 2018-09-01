#!/usr/bin/python3

import time
import rxv

class SCENES:

	def __init__(self):
		self.macrolist = {} # {'name':['m','a','c','r','o'], 'name2':[...]}
		self.rcfile = "./.remctrl.rc"
		self._readMacros()
		# receivers = rxv.find()
		# print(receivers)
		# rx = receivers[0]
		self.rx = rxv.RXV('http://varshneyarxv675/YamahaRemoteControl/ctrl', 'RX-V675')

	def _readMacros(self):
		f = open(self.rcfile,"r")
		for l in f:
			l = l.strip()
			a = l.split("|")
			self.macrolist[a[0]] = a[1:]
		f.close()

	def _runMacro(self, macro):
		for m in range(int(len(macro)/2)):
			try:
				if macro[2*m] == 'v':
					finvol = float(macro[2*m+1])
					ifinvol = int(finvol)
					icurvol = int(self.rx.volume)
					step = -1 if ifinvol < icurvol else 1
					for vv in range(icurvol,ifinvol,step):
						self.rx.volume = vv
						# time.sleep(0.25)
					self.rx.volume = finvol
				if macro[2*m] == 'p':
					self.rx.on = (int(macro[2*m+1]) != 0)
				if macro[2*m] == 'i':
					self.rx.input = macro[2*m+1]
					time.sleep(2)
				if macro[2*m] == 'd':
					self.rx.surround_program = macro[2*m+1]
			except:
				print("Error in parameter value: "+macro[2*m]+" = "+macro[2*m+1])
		self._dispStatus()

	def _dispStatus(self):
		print("Power  = ",self.rx.on)
		print("Input  = ",self.rx.input)
		print("Volume = ",self.rx.volume)
		print("DSP    = ",self.rx.surround_program)

	def run(self):
		while True:
			cmdline = input("> ")
			inp = cmdline.strip()
			cmdlist = inp.split()

			if len(inp) == 0:
				pass
			else:
				# first check for meta commands
				if (inp == 'D'):
					# display the current status
					self._dispStatus()
				elif (inp == 'Q'):
					# quit
					quit()
				elif (inp == '?'):
					# help
					print("D		display the current Yamaha status")
					print("Q		Quit the cli")
					print("?		this help text")
					for c in sorted(self.macrolist.keys()):
						print(c+"		MACRO",self.macrolist[c])
				else:
					# check for the remote control commands, and build the macro
					if (inp in self.macrolist.keys()):
						self._runMacro(self.macrolist[inp])
					else:
						print("Unknown command: "+inp)

if __name__ == '__main__':
	rc = SCENES()
	rc.run()
