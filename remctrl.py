#!/usr/bin/python3

import time
import rxv

class REMCTRL:

	def __init__(self):
		self.ctrlist = {  'p': 'power',           'v': 'volume',        'd': 'DSP',           'i': 'input'}
		self.ctrprompt = {'p': self._powerprompt, 'v': self._volprompt, 'd': self._dspprompt, 'i': self._inpprompt}
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

	def _writeMacros(self):
		f = open(self.rcfile,"w")
		for k in sorted(self.macrolist):
			str = k
			for v in self.macrolist[k]:
				str = str+"|"+v
			f.write(str+"\n")
		f.close()

	def _powerprompt(self):
		print("--\t"+"0 for OFF, 1 for ON")

	def _volprompt(self):
		print("--\t"+"volume level in negative db")

	def _dspprompt(self):
		dspopts = self.rx.surround_programs()
		for i in dspopts:
			print ("--\t"+i)

	def _inpprompt(self):
		inpopts = self.rx.inputs()
		for i in inpopts:
			print ("--\t"+i)

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

	def _saveMacro(self, name, macro):
		self.macrolist[name] = macro
		## write into the file .remctrl.rc to persist
		self._writeMacros()

	def _delMacro(self, macname):
		if macname in self.macrolist:
			del self.macrolist[macname]
		## write into the file .remctrl.rc to persist
		self._writeMacros()

	def run(self):
		oldmacro = []
		macro = []
		mode = ""
		while True:
			print("Macro:",macro)
			cmdline = input(mode+"> ")
			inp = cmdline.strip()
			cmdlist = inp.split()

			if len(inp) == 0:
				pass
			else:
				if (mode == ""):
					# first check for meta commands
					if (inp == '..'):
						# run the current macro
						self._runMacro(macro)
						oldmacro = macro
						macro = []
					elif (cmdlist[0] == '.'):
						# execute the named macro
						if (len(cmdlist) != 2):
							print("command syntax: . macroName")
						else:
							self._runMacro(self.macrolist[cmdlist[1]])
							# do not reset the current macro
					elif (cmdlist[0] == 'X'):
						# reset the macro contents
						macro = []
					elif (cmdlist[0] == '+'):
						# save the macro with the name
						if (len(cmdlist) != 2):
							print("command syntax: + macroName")
						else:
							self._saveMacro(cmdlist[1],macro)
							oldmacro = macro
							macro = []
					elif (cmdlist[0] == '-'):
						# delete the macro with the name
						if (len(cmdlist) != 2):
							print("command syntax: + macroName")
						else:
							self._delMacro(cmdlist[1])
					elif (cmdlist[0] == '/'):
						# recall the old macro
						macro = oldmacro
						oldmacro = []
					elif (inp == 'M'):
						# list the named macros
						if len(self.macrolist.keys()) == 0:
							print("No Macros saved")
						for k in self.macrolist.keys():
							print("--\t"+k+"\t",self.macrolist[k])
						print("")
					elif (inp == 'D'):
						# display the current status
						self._dispStatus()
					elif (inp == 'Q'):
						# quit
						quit()
					elif (inp == '?'):
						# help
						print("..		run the currently constructed macro")
						print(". name		run the named macro")
						print("X		discard the currently constructed macro")
						print("+ name		save and name the currently constructed macro")
						print("- name		delete the saved named macro")
						print("/		recall the previous macro")
						print("M		list the saved macros")
						print("D		display the current Yamaha status")
						print("Q		Quit the cli")
						print("?		this help text")
						for c in self.ctrlist.keys():
							print(c+"		"+self.ctrlist[c])
					else:
						# check for the remote control commands, and build the macro
						if (inp in self.ctrlist.keys()):
							macro.append(inp)
							mode = self.ctrlist[inp]
							(self.ctrprompt[inp])()
						else:
							print("Unknown command: "+inp)
				else:
					macro.append(inp)
					mode = ""

if __name__ == '__main__':
	rc = REMCTRL()
	rc.run()
