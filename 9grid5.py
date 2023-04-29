import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import re
import json
import time
from tkinter import filedialog


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("知识九宫格")
        self.geometry("350x350")

        self.create_input_widget()
        self.create_grid()
        self.create_save_load_buttons()  # Add save and load buttons

        self.error_shown = False
        self.target_label = None  # Added for tracking the target label

        # Initialize a dictionary that maps label objects to their grid positions
        self.label_positions = {label: i for i, frame in enumerate(self.frames) for label in frame.winfo_children()}

        # Initialize loading_from_file attribute
        self.loading_from_file = False

        
    def create_input_widget(self):
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(padx=5, pady=5, fill="x")

        self.input_label = ttk.Label(self.input_frame, text="请输入文本:")
        self.input_label.pack(side="left", padx=5)

        self.input_var = tk.StringVar()
        self.input_var.trace("w", self.load_words_into_grid)

        self.input_text = tk.Text(self.input_frame, height=5)
        self.input_text.pack(side="left", padx=5, fill="x", expand=True)

        # Link the text widget to the StringVar
        self.input_text.bind("<<Modified>>", self.update_input_var)

        # Create the context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Paste", command=self.paste_text)

        # Bind the right-click event to the show_context_menu function depending on the platform
        if self.tk.call("tk", "windowingsystem") == "aqua":  # macOS
            self.input_text.bind("<Button-2>", self.show_context_menu)
        else:  # Windows and Linux
            self.input_text.bind("<Button-3>", self.show_context_menu)

    def update_input_var(self, event=None):
        self.input_text.edit_modified(False)
        self.input_var.set(self.input_text.get("1.0", "end-1c"))
        if not self.loading_from_file:
            self.load_words_into_grid()

    def paste_text(self):
        clipboard_content = self.clipboard_get()
        self.input_text.insert(tk.END, clipboard_content)  # Insert into Text widget

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def create_grid(self):
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.frames = []
        for i in range(3):
            self.grid_frame.columnconfigure(i, weight=1, minsize=75)
            self.grid_frame.rowconfigure(i, weight=1, minsize=75)

            for j in range(3):
                frame = tk.Frame(
                    self.grid_frame,
                    relief=tk.RAISED,
                    borderwidth=1
                )
                frame.grid(row=i, column=j, padx=5, pady=5, sticky="nswe")
                self.frames.append(frame)

                label = tk.Label(frame, text="", anchor="center", justify="center")
                label.pack(padx=5, pady=5, fill="both", expand=True)

                label.bind("<Button-1>", self.on_press_highlight)
                label.bind("<ButtonRelease-1>", self.on_release_unhighlight)

    def load_words_into_grid(self, *args):
        if self.loading_from_file:  # If loading from a file, use the loaded positions
            for i, frame in enumerate(self.frames):
                label = frame.winfo_children()[0]
                if i in [pos for pos, _ in self.loaded_positions]:
                    _, text = next((pos, text) for pos, text in self.loaded_positions if pos == i)
                    label.config(text=text)
                else:
                    label.config(text="")
            self.loading_from_file = False  # Reset the flag
            self.loaded_positions = None  # Reset the loaded positions
                
        else:  
            input_sentence = self.input_var.get().replace('\r\n','\n').replace('\r', '\n')  # Replace all line endings with \n

            if '\n' in input_sentence:  # Check if the input contains newlines
                segments = input_sentence.split('\n')  # Split by \n
            else:  # Otherwise, split by punctuation
                segments = re.split(r'[，。,]', input_sentence)

            if len(segments) > 9:
                if not self.error_shown:  # Check if the error is already shown
                    self.error_shown = True
                    tkinter.messagebox.showerror("Error", "Please provide no more than 9 segments.")
                return
            else:
                self.error_shown = False

            custom_order = [4, 3, 5, 1, 7, 0, 2, 6, 8]  # The corrected sequence

            for i, frame in enumerate(self.frames):
                label = frame.winfo_children()[0]
                if i in custom_order[:len(segments)]:
                    label.config(text=segments[custom_order.index(i)])
                else:
                    label.config(text="")
        if self.loading_from_file:
            sloading_from_filem_file = False

    def on_press_highlight(self, event):
        self.start_label = event.widget
        self.start_label.lift()
        self.start_label.config(background="orange")

    def on_release_unhighlight(self, event):
        target_widget = self.winfo_containing(event.x_root, event.y_root)
        target_frame = None

        for frame in self.frames:
            if target_widget is frame or target_widget in frame.winfo_children():
                target_frame = frame
                break

        if target_frame is not None:
            self.target_label = target_frame.winfo_children()[0]
            source_text = self.start_label.cget("text")
            target_text = self.target_label.cget("text")

            # Highlight the second cell in a different color, let's say 'cyan'
            self.target_label.config(background="orange")
            self.update_idletasks()
            time.sleep(0.2)  # pause for effect

            # Now swap the texts
            self.start_label.config(text=target_text)
            self.target_label.config(text=source_text)

            # Also swap the positions in the dictionary
            start_position = self.label_positions[self.start_label]
            target_position = self.label_positions[self.target_label]
            self.label_positions[self.start_label], self.label_positions[self.target_label] = target_position, start_position

            self.update_idletasks()
            time.sleep(0.2)  # pause for effect

            # Reset the background color to default
            self.start_label.config(background=self.start_label.master['bg'])
            self.target_label.config(background=self.target_label.master['bg'])

        self.start_label = None
        self.target_label = None  # Reset the target label


    def create_save_load_buttons(self):
        self.save_load_frame = ttk.Frame(self)
        self.save_load_frame.pack(padx=5, pady=5, fill="x")

        self.save_button = ttk.Button(self.save_load_frame, text="Save", command=self.save_words)
        self.save_button.pack(side="left", padx=5)

        self.load_button = ttk.Button(self.save_load_frame, text="Load", command=self.load_words)
        self.load_button.pack(side="left", padx=5)

    def save_words(self):
        input_word = self.input_text.get("1.0", "end-1c").strip()  # Get the input word

        # Get positions and corresponding labels' text
        positions = {}
        for i, frame in enumerate(self.frames):
            label = frame.winfo_children()[0]
            text = label.cget("text").strip()
            if text:
                positions[i] = text

        data_to_save = {
            "input_word": input_word,
            "positions": list(positions.items())
        }

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if filename:
            with open(filename, "w") as f:
                json.dump(data_to_save, f)

    def load_words(self):
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if filename:
            with open(filename, "r") as f:
                data_to_load = json.load(f)

            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, data_to_load["input_word"])

            self.loaded_positions = data_to_load["positions"]  # Store the loaded positions

            # Update the input_var to load words into the grid
            self.input_var.set(self.input_text.get("1.0", "end-1c"))

            # After the UI update finishes, rearrange the labels according to the loaded positions
            self.after(100, self.rearrange_labels)

    def rearrange_labels(self):
        # Create a list of all labels
        labels = [frame.winfo_children()[0] for frame in self.frames]

        # For each loaded position...
        for pos, text in self.loaded_positions:
            # Find the label that currently has this text
            for label in labels:
                if label.cget("text") == text:
                    # Swap the texts of the labels
                    temp = labels[pos].cget("text")
                    labels[pos].config(text=text)
                    label.config(text=temp)
                    break


if __name__ == "__main__":
    app = App()
    app.mainloop()
