import funcs

import tkinter
import tkinter.ttk
import tkinter.filedialog

import os
from functools import partial

from PIL import Image, ImageTk, ImageDraw

class MyFrame(tkinter.Frame):
    def __init__(self, root):
        tkinter.Frame.__init__(self, master=root, width=600, height=400)
        self.filepath = None

        self.label_frame = tkinter.ttk.LabelFrame(self, text='  Encrypt  /  Decrypt')
        self.label_frame.grid(row=1, column=2, padx=4, pady=4, sticky=tkinter.NSEW)

##        self.image_frame = tkinter.ttk.LabelFrame(self, text='  Image  ')
##        self.image_frame.grid(row=1, column=1, padx=4, pady=4, sticky=tkinter.NSEW)

        self.image = tkinter.Button(self.label_frame, text='Image', width=120, height=30, command=self.choose_image)
        self.image.grid(row=2, column=1, rowspan=10, padx=4, pady=4)

        self.rowconfigure(0, weight=1)        
        
        self.choice_var = tkinter.StringVar(value='encode')
        self.encrypt_var = tkinter.BooleanVar(value=False)
        self.type_var = tkinter.StringVar(value='text')

        tkinter.Label(self.label_frame, text='Encode / Decode:').grid(row=2, column=2)
        tkinter.ttk.Radiobutton(self.label_frame, text='Encode', command=self.mode_changed, variable=self.choice_var, value='encode').grid(row=2, column=4)
        tkinter.ttk.Radiobutton(self.label_frame, text='Decode', command=self.mode_changed, variable=self.choice_var, value='decode').grid(row=2, column=5)

        tkinter.Label(self.label_frame, text='Encryption:').grid(row=3, column=2)
        tkinter.ttk.Checkbutton(self.label_frame, variable=self.encrypt_var, command=self.encrypt_changed).grid(row=3, column=4)
        self.passphrase = tkinter.ttk.Entry(self.label_frame)
        self.passphrase.grid(row=3, column=5)

        tkinter.Label(self.label_frame, text='Data Type:').grid(row=4, column=2)
        tkinter.ttk.Radiobutton(self.label_frame, text='Text', variable=self.type_var, value='text', command=self.input_method).grid(row=5, column=3, padx=4, pady=4)

        self.textarea = tkinter.Text(self.label_frame, height=8, width=40, state=tkinter.DISABLED, bg='#F0F0F0')
        self.textarea.grid(row=5, column=4, columnspan=3, padx=4, pady=4)
        
        tkinter.ttk.Radiobutton(self.label_frame, text='Document', variable=self.type_var, value='doc', command=self.input_method).grid(row=6, column=3)

        self.open = tkinter.ttk.Button(self.label_frame, text='Open', command=self.open_doc, state=tkinter.DISABLED)
        self.open.grid(row=6, column=4, columnspan=3, padx=4, pady=4)

        self.button = tkinter.ttk.Button(self.label_frame, text='Execute', state=tkinter.DISABLED, command=self.execute)
        self.button.grid(row=10, column=2, columnspan=4)

        self.encrypt_changed()
        self.input_method()

    def encrypt_changed(self):
        if self.encrypt_var.get() == True:
            self.passphrase['state'] = tkinter.NORMAL

        else:
            self.passphrase['state'] = tkinter.DISABLED

    def mode_changed(self):
        value = self.choice_var.get()

        if value == 'encode':
            self.input_method()

        elif value == 'decode':
            self.textarea.configure(state=tkinter.DISABLED, bg='#F0F0F0')
            self.open['state'] = tkinter.DISABLED
            

    def input_method(self):
        choice = self.choice_var.get()
        value = self.type_var.get()

        if choice == 'encode':
            if value == 'text':
                self.textarea.configure(state=tkinter.NORMAL, bg='#FFFFFF')
                self.open.config(state=tkinter.DISABLED)
                
            elif value == 'doc':
                self.textarea.configure(state=tkinter.DISABLED, bg='#F0F0F0')
                self.open.config(state=tkinter.NORMAL)

    def choose_image(self):
        img_menu = tkinter.filedialog.askopenfile(mode='r', filetypes=[('PNG Images', '.png'), ('BMP Images', '.bmp'),])
        
        if img_menu is None:
            return None

        else:
            self.filepath = img_menu.name

            image = Image.open(self.filepath)
            width, height = image.size

            if width <= 1280 and height <= 768:
                pass

            elif width/height >= 640/384:
                height *= (1280/width)
                width = 1280

            else:
                width *= (768/height)
                height = 768

            width, height = int(width), int(height)
            
            image = image.resize((width, height), Image.ANTIALIAS)

            # image.save(os.path.dirname(self.filepath) + '/new' + os.path.basename(self.filepath), 'PNG')
            # self.filepath = os.path.dirname(self.filepath) + '/new-' + os.path.basename(self.filepath)

            self.img = ImageTk.PhotoImage(image)

            self.image.config(image=self.img, width=width, height=height)
            self.image.image = self.img
            self.image.grid(row=1, column=1)
            
            self.button['state'] = tkinter.ACTIVE

    def open_doc(self):
        file = tkinter.filedialog.askopenfile(mode='rb')

        if file is None:
            return None

        else:
            self.docname = file.name

    def execute(self):
        choice = self.choice_var.get()
        encrypt = self.encrypt_var.get()
        
        if encrypt:
            passphrase = self.passphrase.get()
        else:
            passphrase = None
            
        data_type = self.type_var.get()

        if self.filepath is None:
            return None

        if choice == 'encode':
            if data_type == 'text':
                text = self.textarea.get("1.0", tkinter.END)
                text = bytes(text, 'utf-8')
                try:
                    funcs.encode(self.filepath, text, passphrase)
                except Exception:
                    tkinter.messagebox.showerror('Invalid Passphrase', 'The passphrase you entered was invalid. Enter a proper passphrase.')
            
                self.textarea.delete("1.0", tkinter.END)

                self.filepath = None
                self.image.image = None
                self.image.config(image=None)
                self.image.grid(row=1, column=1)

            elif data_type == 'doc':
                file = open(self.docname, mode='rb')
                funcs.encode(self.filepath, file.read(), passphrase)
                file.close()

        elif choice == 'decode':
            if data_type == 'text':
                text = funcs.decode(self.filepath, passphrase)
                self.textarea.configure(state=tkinter.NORMAL)
                self.textarea.delete("1.0", tkinter.END)
                self.textarea.insert(tkinter.END, text)
                self.textarea.configure(state=tkinter.DISABLED)

            elif data_type == 'doc':
                new_file = tkinter.filedialog.asksaveasfilename()

                if new_file is None:
                    return None

                else:
                    file = open(new_file, mode='wb')
                    file.write(funcs.decode(self.filepath, passphrase))
                    file.close()


##class ButtonGroup(tkinter.Frame):
##    def __init__(self, master, buttons=[]):
##        tkinter.Frame.__init__(self, master=master)
##
##        self.value = tkinter.Variable()
##
##        self.buttons = buttons
##
##    def initialize(self):
##        for button in self.buttons:
##            def command(button_group, button):
##                button_group.value.set(button.size)
##                for butt in button_group.buttons:
##                    butt['relief'] = tkinter.RAISED
##                button['relief'] = tkinter.SUNKEN
##
##            button.config(command=partial(command, self, button))
##            button.grid(row=1, column=button.index+1, padx=4, pady=4)        
##
##
##class DrawingCanvas(tkinter.Toplevel):
##    def __init__(self, root, width, height, filepath, editable=True):
##        tkinter.Toplevel.__init__(self, master=root)
##        self.resizable(False, False)
##        self.filepath = filepath
##
##        self.width = width
##        self.height = height
##
##        self.editable = editable
##
##        self.canvas = tkinter.Canvas(self, width=width, height=height, bg='#FFFFFF', cursor='crosshair')
##        self.canvas.grid(row=1, column=1, columnspan=3, padx=4, pady=4)
##
##        # Brush Group
##        self.brush_frame = ButtonGroup(self)
##        brush_buttons = []
##
##        for index in range(0, 8):
##            butt = tkinter.Button(self.brush_frame, text=str(2**index), width=4)
##            butt.index = index
##            butt.size = 2**index
##            brush_buttons.append(butt)
##        self.brush_frame.buttons = brush_buttons
##
##        self.brush_frame.initialize()
##        self.brush_frame.grid(row=2, column=1, padx=4, pady=4)
##        self.brush_frame.value.set(4)
##
##        # Colors Group
##        self.colors_frame = ButtonGroup(self)
##        color_buttons = []
##
##        colors = ['#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#800080', '#FFA500']
##
##        for index in range(0, 8):
##            butt = tkinter.Button(self.colors_frame, text='        ', bg=colors[index])
##            butt.index = index
##            butt.size = colors[index]
##            color_buttons.append(butt)
##        self.colors_frame.buttons = color_buttons
##
##        self.colors_frame.initialize()
##        self.colors_frame.grid(row=2, column=2, padx=4, pady=4)
##        self.colors_frame.value.set('#000000')
##
##        # Done Button
##        self.button = tkinter.ttk.Button(self, text='Done', command=self.save)
##        self.button.grid(row=2, column=3, rowspan=2, padx=4, pady=4)
##
##        self.image = Image.new('RGB', (width, height), '#FFFFFF')
##        self.imagedraw = ImageDraw.Draw(self.image)
##
##        self.brush = tkinter.IntVar(value=4)
##
##        if self.editable:
##            self.canvas.bind('<B1-Motion>', self.draw)
##
##    def draw(self, event):
##        x, y = event.x, event.y
##
##        brush = int(self.brush_frame.value.get())
##        fill = self.colors_frame.value.get()
##
##        self.canvas.create_oval(x - (brush  / 2), y - (brush / 2), x + (brush / 2), y + (brush / 2), fill=fill, outline=fill)
##        self.imagedraw.ellipse([x - (brush  / 2), y - (brush / 2), x + (brush / 2), y + (brush / 2)], fill=fill, outline=fill)
##
##    def save(self):
##        funcs.hide_img(self.filepath, self.image)


class Steganographer(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.wm_state('zoomed')

        self.title("Steganographer")

        frame = MyFrame(self)
        frame.grid(row=1, column=1, padx=4, pady=4, sticky=tkinter.NSEW)

##        self.columnconfigure(0, weight=1)
##        self.rowconfigure(0, weight=1)


if __name__ == '__main__':
    app = Steganographer()
    app.mainloop()
