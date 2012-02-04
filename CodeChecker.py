#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: CodeChecker.py

from Tkinter import *
from PIL import Image, ImageTk

class App:
	def __init__(self, image):
		# root window
		self.master = Tk()
		self.code = None

		self.frame = Frame(self.master)
		self.frame.pack()

		self.top = Frame(self.frame)
		self.top.pack()
		# show check code
		self.check_code = Label(self.top, text="验证码")
		self.check_code.pack(side=LEFT)

		# gif pgm/ppm images format
		photo = PhotoImage(file=image)
		# other filie format
		#img = Image.open(image)
		#photo = ImageTk.PhotoImage(img)

		# show check code pic
#		self.canvas = Canvas(frame, width=200, height=100)
#		self.canvas.pack()
#		self.canvas.create_image((4, 8), state=NORMAL, anchor=CENTER, image=photo)

		img = Label(self.top, image=photo)
		img.image = photo
		img.pack()

		self.middle = Frame(self.frame)
		self.middle.pack()

		ilab = Label(self.middle, text="请输入")
		ilab.pack(side=LEFT)

		self.entry = Entry(self.middle, bg="white", takefocus=1)
		self.entry.pack()
		
		self.bottom = Frame(self.frame)
		self.bottom.pack()

		self.hi_there = Button(self.bottom, text="Go", command=lambda: self.setCode())
		self.hi_there.pack(side=LEFT)
		self.hi_there.bind("<Return>", self.setCode)

		self.button = Button(self.bottom, text="Quit", fg="red", command=self.frame.quit)
		#self.button.pack()
		self.master.mainloop()

	def setCode(self, event=None):
		self.code = self.entry.get()
		self.frame.quit()

if __name__ == "__main__":
	app = App("2.gif")
	print app.code

