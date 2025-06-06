import tkinter as tk
from tkinter import filedialog, messagebox
import re

class BitmapEditor:
    def __init__(self, master, width=5, height=7, pixel_size=20):
        self.master = master
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        canvas_width = self.width * self.pixel_size
        canvas_height = self.height * self.pixel_size

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(master, width=canvas_width, height=canvas_height)
        self.canvas.grid(row=0, column=1, rowspan=6, sticky="nsew", padx=5, pady=5)

        self.bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]

        self.canvas.bind('<Button-1>', self.toggle_pixel)

        self.listbox = tk.Listbox(master, width=20)
        self.listbox.grid(row=0, column=0, rowspan=5, sticky="nsw", padx=(5, 2), pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.load_selected_bitmap)

        btn_frame = tk.Frame(master)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_bitmap)
        self.clear_btn.grid(row=0, column=0)

        self.save_btn = tk.Button(btn_frame, text="Save Glyph", command=self.save_glyph)
        self.save_btn.grid(row=0, column=1)

        self.import_btn = tk.Button(btn_frame, text="Import Charset", command=self.import_charset)
        self.import_btn.grid(row=0, column=2)

        self.export_btn = tk.Button(btn_frame, text="Export Charset", command=self.export_charset)
        self.export_btn.grid(row=0, column=3)

        self.switch_btn = tk.Button(btn_frame, text="Switch ASCII/ICONS", command=self.switch_charset)
        self.switch_btn.grid(row=0, column=4)

        self.current_charset = "ASCII"
        self.charsets = {"ASCII": [], "ICONS": []}
        self.current_index = None

        self.draw_bitmap()

        # Set minimum window size
        min_width = 200 + canvas_width + 50
        min_height = canvas_height + 100
        self.master.minsize(min_width, min_height)

    def toggle_pixel(self, event):
        col = event.x // self.pixel_size
        row = event.y // self.pixel_size
        if 0 <= row < self.height and 0 <= col < self.width:
            self.bitmap[row][col] = 1 - self.bitmap[row][col]
            self.draw_bitmap()

    def draw_bitmap(self):
        self.canvas.delete("all")
        for row in range(self.height):
            for col in range(self.width):
                color = "black" if self.bitmap[row][col] else "white"
                x1 = col * self.pixel_size
                y1 = row * self.pixel_size
                x2 = x1 + self.pixel_size
                y2 = y1 + self.pixel_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def clear_bitmap(self):
        self.bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.draw_bitmap()

    def save_glyph(self):
        if self.current_index is not None:
            encoded = self.bitmap_to_bytes()
            self.charsets[self.current_charset][self.current_index] = encoded
            messagebox.showinfo("Saved", f"Saved glyph {self.current_index} in {self.current_charset}")

    def load_selected_bitmap(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.current_index = selection[0]
            encoded = self.charsets[self.current_charset][self.current_index]
            self.bytes_to_bitmap(encoded)
            self.draw_bitmap()

    def switch_charset(self):
        if self.current_charset == "ASCII":
            self.current_charset = "ICONS"
            self.width, self.height = 12, 12
        else:
            self.current_charset = "ASCII"
            self.width, self.height = 5, 7
        canvas_width = self.width * self.pixel_size
        canvas_height = self.height * self.pixel_size
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.master.minsize(200 + canvas_width + 50, canvas_height + 100)
        self.refresh_listbox()
        self.clear_bitmap()

    def import_charset(self):
        file_path = filedialog.askopenfilename(filetypes=[("Header Files", "*.h"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()

            content = re.sub(r'//.*', '', content)

            ascii_match = re.search(r'ASCII\[\]\[5\][^=]*=\s*\{(.*?)\};', content, re.S)
            icons_match = re.search(r'ICONS\[\]\[12\][^=]*=\s*\{(.*?)\};', content, re.S)

            if not ascii_match or not icons_match:
                messagebox.showerror("Import Error", "Cannot find ASCII or ICONS data.")
                return

            ascii_data = re.findall(r'\{([^}]*)\}', ascii_match.group(1))
            icons_data = re.findall(r'\{([^}]*)\}', icons_match.group(1))

            self.charsets = {"ASCII": [], "ICONS": []}

            for block in ascii_data:
                bytes_list = [int(x.strip(), 16) for x in block.split(',') if x.strip()]
                self.charsets["ASCII"].append(bytes_list)
            for block in icons_data:
                bytes_list = [int(x.strip(), 16) for x in block.split(',') if x.strip()]
                self.charsets["ICONS"].append(bytes_list)

            self.current_charset = "ASCII"
            self.width, self.height = 5, 7
            self.refresh_listbox()
            messagebox.showinfo("Import", "Charset imported successfully.")

    def export_charset(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".h", filetypes=[("Header Files", "*.h")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("const unsigned char ASCII[][5] PROGMEM =\n{\n")
                for glyph in self.charsets["ASCII"]:
                    f.write("    {" + ", ".join(f"0x{b:02X}" for b in glyph) + "},\n")
                f.write("};\n\n")
                f.write("const unsigned char ICONS[][12] PROGMEM =\n{\n")
                for icon in self.charsets["ICONS"]:
                    f.write("    {" + ", ".join(f"0x{b:02X}" for b in icon) + "},\n")
                f.write("};\n")
            messagebox.showinfo("Export", f"Charset exported to {file_path}")

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i in range(len(self.charsets[self.current_charset])):
            self.listbox.insert(tk.END, f"{self.current_charset} {i}")

    def bitmap_to_bytes(self):
        result = []
        for col in range(self.width):
            byte = 0
            for row in range(self.height):
                if self.bitmap[row][col]:
                    byte |= (1 << row)
            result.append(byte)
        return result

    def bytes_to_bitmap(self, encoded):
        self.bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for col in range(self.width):
            byte = encoded[col]
            for row in range(self.height):
                self.bitmap[row][col] = (byte >> row) & 1

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bitmap Editor")
    root.resizable(True, True)
    app = BitmapEditor(root)
    root.mainloop()
