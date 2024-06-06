import tkinter.messagebox
import subprocess
import os
result=str(subprocess.run(['tasklist'],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW))
if result.find('Random.exe')!=-1:
    tkinter.messagebox.showerror('错误','Random已在后台运行。')
else:
    os.startfile(r'Random.exe')
