###################################################################################################
# candlecleaner.py
#
# A GUI application that allows the user to select a directory and remove a specified string from 
# the names of the files within the selected directory recursively. Features a smart cleaning 
# feature which generates regular expressions to remove, by normalizing (all lowercase, with spaces,
# hyphens turned into underscores) all file names and finding a common prefix for each subdirectory.
#
# Author: Filip "a candle"
# Date created: 4/4/23
# Python Version: 3.10.6
#
###################################################################################################

import os
import re
import webbrowser
try:
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog, messagebox, ttk
    from PIL.Image import open as popen
    from PIL.ImageTk import PhotoImage
except ImportError:
    print("Tkinter is not installed. Please install it before running this script.")
    exit()

class CleanerApp(tk.Tk):

    def file_tree_scroll_mouse_wheel(self, event):
        self.updated_file_tree.yview_scroll(int(-1*(event.delta/120)), "units")

    def updated_file_tree_scroll_mouse_wheel(self, event):
        self.file_tree.yview_scroll(int(-1*(event.delta/120)), "units")

    def __init__(self, is_unit_test=False):
        super().__init__()
        self.title("candlecleaner")
        self.geometry('1000x800')

        # Check if the script is being run as a patch unit test
        self.is_unit_test = is_unit_test
        if not self.is_unit_test:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "icon.ico")

            # Load the image file using PIL
            image = popen(icon_path)
            photo = PhotoImage(image)

            # Set the photo as the icon image
            self.iconphoto(True, photo)

        self.directory_var = tk.StringVar()
        self.string_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.scroll_sync_var = tk.BooleanVar(value=True)
        self.leading_zero_var = tk.BooleanVar(value=True)
        self.smart_update_var = tk.BooleanVar()
        self.upper_bpm_var = tk.BooleanVar()
        self.capitalize_var = tk.BooleanVar()
        self.underscore_var = tk.BooleanVar()
        self.regex_list = []

        self.directory_frame = tk.Frame(self)
        self.directory_frame.grid(row=1, column=1, pady=10, padx=10, sticky="we")

        self.string_frame = tk.Frame(self)
        self.string_frame.grid(row=1, column=2, pady=10, padx=10, sticky="we")

        self.to_replace = tk.Frame(self.string_frame, bg=self.directory_frame["bg"])
        self.to_replace.pack(side="left")

        self.replacer = tk.Frame(self.string_frame, bg=self.directory_frame["bg"])
        self.replacer.pack(side="left")

        self.spacer = tk.Label(self.directory_frame, text="", padx=5)
        self.spacer.pack(side="right")
        self.directory_label = tk.Entry(self.directory_frame, textvariable=self.directory_var, bd=5)
        self.directory_label.pack(side="right", fill=X, expand=True)

        self.string_label = tk.Label(self.to_replace, text="Text to replace:", padx=5)
        self.string_label.pack(side="left", anchor="center")

        self.string_entry = tk.Entry(self.to_replace, textvariable=self.string_var)
        self.string_entry.pack(side="left", anchor="w")
        self.string_entry.config(state='normal')

        self.string_remove = tk.Label(self.replacer, text="Replacement:", padx=5)
        self.string_remove.pack(side="left", anchor="center")

        self.replace_entry = tk.Entry(self.replacer, textvariable=self.replace_var)
        self.replace_entry.pack(side="left", anchor="w")
        self.replace_entry.config(state='normal')

        self.rename_button = tk.Button(self, text="Rename Files", command=self.rename_files, justify=CENTER, bd=3)
        self.rename_button.grid(row=4, column=2, pady=10)

        # Associate the validation function with the string variable
        self.string_var.trace("w", lambda *args: (self.validate_string_entry(), self.update_file_list()) )
        self.replace_var.trace("w", lambda *args: (self.validate_string_entry(), self.update_file_list()) )
        self.directory_var.trace("w", lambda *args: (self.verify_directory()))

        self.file_tree = ttk.Treeview(self, columns=("size"))
        self.file_tree.heading("#0", text="Files", anchor="w")
        self.file_tree.heading("size", text="Size", anchor="w")
        self.file_tree.column("#0", width=300)
        self.file_tree.column("size", width=100)
        self.file_tree.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        self.updated_file_tree = ttk.Treeview(self, columns=("size"))
        self.updated_file_tree.heading("#0", text="Files", anchor="w")
        self.updated_file_tree.heading("size", text="Size", anchor="w")
        self.updated_file_tree.column("#0", width=300)
        self.updated_file_tree.column("size", width=100)
        self.updated_file_tree.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")

        self.file_tree_scroll = tk.Scrollbar(self, orient="vertical")
        self.file_tree_scroll.grid(row=3, column=1, rowspan=1, padx=10, pady=10, sticky="nse")
        self.file_tree.configure(yscrollcommand=self.file_tree_scroll.set)
        self.file_tree.bind("<MouseWheel>", self.file_tree_scroll_mouse_wheel)

        self.updated_file_tree_scroll = tk.Scrollbar(self, orient="vertical")
        self.updated_file_tree_scroll.grid(row=3, column=2, rowspan=1, padx=10, pady=10, sticky="nse")
        self.updated_file_tree.configure(yscrollcommand=self.updated_file_tree_scroll.set)
        self.updated_file_tree.bind("<MouseWheel>", self.updated_file_tree_scroll_mouse_wheel)

        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Select Directory", command=self.select_directory)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.options_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=self.options_menu)
        self.options_menu.add_checkbutton(label="Scroll Sync", variable=self.scroll_sync_var, command=self.scroll_sync_toggle, state='active')

        self.cleaner_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Candle Cleaner", menu=self.cleaner_menu)
        self.cleaner_menu.add_checkbutton(label="Enable", variable=self.smart_update_var, command=lambda : self.update_file_list(True))
        self.cleaner_menu.add_separator()
        self.cleaner_menu.add_checkbutton(label="Including Leading 0s", variable=self.leading_zero_var, state='disabled', command=lambda : self.update_file_list(True))
        self.cleaner_menu.add_checkbutton(label="Capitalize BPM", variable=self.upper_bpm_var, state='disabled', command=lambda : self.update_file_list(True))
        self.cleaner_menu.add_checkbutton(label="Capitalize Words", variable=self.capitalize_var, state='disabled', command=lambda : self.update_file_list(True))
        self.cleaner_menu.add_checkbutton(label="Replace Underscores", variable=self.underscore_var, state='disabled', command=lambda : self.update_file_list(True))

        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_help)
        self.help_menu.add_command(label="Source", command=self.show_source)

        # Add a callback to each scrollbar that sets the position of the other scrollbar
        def sync_scrolls(first_treeview, second_treeview):
            def scroll_handler(*args):
                if self.scroll_sync_var.get():
                    first_treeview.yview_moveto(args[1])
                    second_treeview.yview_moveto(args[1])
                else:
                    first_treeview.yview_moveto(args[1])
            return scroll_handler

        self.file_tree_scroll.config(command=sync_scrolls(self.file_tree, self.updated_file_tree))
        self.updated_file_tree_scroll.config(command=sync_scrolls(self.updated_file_tree, self.file_tree))

        # Configure the grid layout
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def scroll_sync_toggle(self):
        if self.scroll_sync_var.get():
            self.file_tree.bind("<MouseWheel>", self.file_tree_scroll_mouse_wheel)
            self.updated_file_tree.bind("<MouseWheel>", self.updated_file_tree_scroll_mouse_wheel)
            self.updated_file_tree.yview_moveto(self.file_tree.yview()[0])
        else:
            self.file_tree.unbind("<MouseWheel>")
            self.updated_file_tree.unbind("<MouseWheel>")

    # If checkbox is selected, string entry should be disabled
    def validate_string_entry(self):
        if self.smart_update_var.get():
            self.cleaner_menu.entryconfig(2, state='normal')
            self.cleaner_menu.entryconfig(3, state='normal')
            self.cleaner_menu.entryconfig(4, state='normal')
            self.cleaner_menu.entryconfig(5, state='normal')
            self.string_entry.config(state='disabled')
            self.replace_entry.config(state='disabled')
        else:
            self.cleaner_menu.entryconfig(2, state='disabled')
            self.cleaner_menu.entryconfig(3, state='disabled')
            self.cleaner_menu.entryconfig(4, state='disabled')
            self.cleaner_menu.entryconfig(5, state='disabled')
            self.string_entry.config(state='normal')
            self.replace_entry.config(state='normal')

    def verify_directory(self):
        if os.path.isdir(self.directory_var.get()):
            self.update_file_list(True)

    def select_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.directory_var.set(directory_path)
            self.update_file_list(True)

    def update_file_list(self, make_regex = False):
        directory_path = self.directory_var.get()
        smart_update = self.smart_update_var.get()
        if make_regex: self.regex_list = []
        self.validate_string_entry()
        if os.path.isdir(directory_path):
            # Clear the file tree
            self.file_tree.delete(*self.file_tree.get_children())
            self.updated_file_tree.delete(*self.updated_file_tree.get_children())
            # Dictionary to hold parent node IDs
            parent_ids = {}
            # Traverse the directory tree
            for dirpath, dirnames, filenames in os.walk(directory_path):
                # Get the name of the current folder
                folder_name = os.path.basename(dirpath)

                # Create a new node in the tree for the current folder
                if not parent_ids.get(dirpath):
                    if not os.path.samefile(dirpath, directory_path):
                        parent_dirpath = os.path.dirname(dirpath)
                        parent_id = parent_ids.get(parent_dirpath)['file_tree']
                        updated_parent_id = parent_ids.get(parent_dirpath)['updated_file_tree']
                    else:
                        parent_id = ""
                        updated_parent_id = ""
                    parent_id = self.file_tree.insert(parent_id, END, text=folder_name, open=True)
                    updated_parent_id = self.updated_file_tree.insert(updated_parent_id, END, text=folder_name, open=True)
                    parent_ids[dirpath] = {'file_tree': parent_id, 'updated_file_tree': updated_parent_id}

                # Add subdirectories to the current folder node
                for dirname in dirnames:
                    sub_dirpath = os.path.join(dirpath, dirname)
                    if not parent_ids.get(sub_dirpath):
                        parent_id = parent_ids.get(dirpath)['file_tree']
                        updated_parent_id = parent_ids.get(dirpath)['updated_file_tree']
                        sub_dirname = os.path.basename(sub_dirpath)
                        sub_parent_id = self.file_tree.insert(parent_id, END, text=sub_dirname, open=True)
                        updated_sub_parent_id = self.updated_file_tree.insert(updated_parent_id, END, text=sub_dirname, open=True)
                        parent_ids[sub_dirpath] = {'file_tree': sub_parent_id, 'updated_file_tree': updated_sub_parent_id}

                # Create regex list for selected directory
                if make_regex:
                    if filenames:
                        directory_name = os.path.basename(dirpath)
                        self.generate_regex(filenames, directory_name)

                # Add files to the current folder node
                for filename in filenames:
                    if not filename.startswith("."):  # Ignore hidden files
                        file_path = os.path.join(dirpath, filename)
                        file_size = os.path.getsize(file_path)
                        self.file_tree.insert(parent_ids[dirpath]['file_tree'], END, text=filename, values=(file_size,))
                        if smart_update:
                            current_directory = os.path.basename(dirpath)
                            current_regex = next((regex[0] for regex in self.regex_list if regex[1] == current_directory), "")
                            string_to_remove = current_regex
                            file_shown = re.sub(r'[ \-_]+', '_', os.path.splitext(filename)[0].lower()) + os.path.splitext(filename)[1]
                            replacement = ""
                        else:
                            string_to_remove = self.string_var.get()
                            replacement = self.replace_var.get()
                            file_shown = filename
                        if string_to_remove:
                            pattern = re.compile(re.escape(string_to_remove), re.IGNORECASE)
                            updated_file_name = re.sub(pattern, replacement, file_shown)
                            updated_file_size = os.path.getsize(file_path)
                            if self.upper_bpm_var.get(): updated_file_name = updated_file_name.replace('bpm', 'BPM')
                            if self.capitalize_var.get(): updated_file_name = self.capitalize_string(updated_file_name)
                            if self.underscore_var.get(): updated_file_name = self.replace_underscore(updated_file_name)
                            self.updated_file_tree.insert(parent_ids[dirpath]['updated_file_tree'], END, text=updated_file_name, values=(updated_file_size,))
                        else:
                            self.updated_file_tree.insert(parent_ids[dirpath]['updated_file_tree'], END, text=filename, values=(file_size,))
    
    def rename_files(self):
        directory_path = self.directory_var.get()
        smart_update = self.smart_update_var.get()
        success = True

        if messagebox.askyesno("Confirmation", "Rename Files?"):
            if os.path.isdir(directory_path):
                for dirpath, dirnames, filenames in os.walk(directory_path):
                    for filename in filenames:
                        if filename != ".DS_Store" and filename != "":
                            if smart_update:
                                current_directory = os.path.basename(dirpath)
                                current_regex = next((regex[0] for regex in self.regex_list if regex[1] == current_directory), "")
                                string_to_remove = current_regex
                                file_shown = re.sub(r'[ \-_]+', '_', os.path.splitext(filename)[0].lower()) + os.path.splitext(filename)[1]
                                replacement = ""
                            else:
                                string_to_remove = self.string_var.get()
                                replacement = self.replace_var.get()
                                file_shown = filename
                            pattern = re.compile(re.escape(string_to_remove), re.IGNORECASE)
                            updated_file_name = re.sub(pattern, replacement, file_shown)
                            if self.upper_bpm_var.get(): updated_file_name = updated_file_name.replace('bpm', 'BPM')
                            if self.capitalize_var.get(): updated_file_name = self.capitalize_string(updated_file_name)
                            if self.underscore_var.get(): updated_file_name = self.replace_underscore(updated_file_name)
                            src = os.path.join(dirpath, filename)
                            dst = os.path.join(dirpath, updated_file_name)
                            try:
                                os.rename(src, dst)
                            except:
                                success = False
                                messagebox.showerror("Failed" "Couldn't rename file: " + file_shown)
                self.smart_update_var.set(False)
                self.update_file_list()
                if success:
                    messagebox.showinfo("Success", "Files renamed successfully!")

    def show_help(self):
        messagebox.showinfo("About", "Mass file renamer, specifically geared toward audio sample libraries.")

    def show_source(self):
        webbrowser.open_new_tab("https://github.com/SuluCandles/candlecleaner")
            
    def generate_regex(self, filenames, dirname):
            # Filter out any filenames that are not hidden
            filenames = [f for f in filenames if not f.startswith(".")]
            if not filenames:
                # If all filenames were named .DS_Store, return an empty string
                return ""

            # Normalize the filenames by replacing spaces, underscores, and hyphens with a common separator,
            # and removing the file extension from each filename
            normalized_filenames = [re.sub(r'[ \-_]+', '_', os.path.splitext(f)[0].lower()) for f in filenames]
            common_prefix = os.path.commonprefix(normalized_filenames)
            if not common_prefix:
                common_prefix = "*"
            else:
                if self.leading_zero_var.get():
                    common_prefix = common_prefix.removesuffix('0')
            prefix_regex = re.escape(common_prefix).replace('\\_', '[ _-]')

            regex = prefix_regex.replace('\\-', '-')
            # Add the regex and the directory to the regex list
            self.regex_list.append((regex, dirname))

    def capitalize_string(self, filename):
        words = filename.split("_")
        capitalized_words = []
        if words[0].lower() == "the":
            words[0] = words[0].capitalize()
        for word in words:
            if not (word.lower() in {"and", "the", "of", "or", "a", "an", "in", "to", "for", "with", "on", "at", "by", "but", "nor", "from", "bpm"}):
                word = word.capitalize()
            capitalized_words.append(word)
        output_string = "_".join(capitalized_words)
        return output_string

    def replace_underscore(self, filename):
        words = filename.split("_")
        words = " ".join(words)
        return words

if __name__ == '__main__':
    # create the application instance
    app = CleanerApp()
    
    # start the main event loop
    app.mainloop()