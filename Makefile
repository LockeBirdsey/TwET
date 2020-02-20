darwin:
	pyinstaller --debug all -F builder.py --name TwEGeT.app --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl'	
