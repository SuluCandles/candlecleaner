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
try:
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog, messagebox, ttk
    from PIL import Image, ImageTk
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
            image = Image.open(icon_path)
            photo = ImageTk.PhotoImage(image)

            # Set the photo as the icon image
            self.iconphoto(True, photo)

        self.directory_frame = tk.Frame(self)
        self.directory_frame.grid(row=1, column=1, pady=10, padx=10, sticky="we")
        self.string_frame = tk.Frame(self)
        self.string_frame.grid(row=1, column=2, pady=10, padx=10, sticky="we")

        self.directory_var = tk.StringVar()
        self.string_var = tk.StringVar()
        self.regex_list = []

        self.select_button = tk.Button(self.directory_frame, text="Select Directory", command=self.select_directory, padx=10, anchor="w", justify=CENTER)
        self.select_button.pack(side="left")

        self.spacer = tk.Frame(self.directory_frame, width=10, height=1, bg=self.directory_frame["bg"])
        self.spacer.pack(side="left")

        # Associate the validation function with the directory variable
        self.directory_var.trace("w", lambda *args: self.check_box.config(state=tk.NORMAL if self.validate_directory() else tk.DISABLED))

        self.directory_label = tk.Entry(self.directory_frame, textvariable=self.directory_var, bd=5)
        self.directory_label.pack(side="right", fill=X, expand=True)

        self.smart_update_var = tk.BooleanVar()
        self.check_box = tk.Checkbutton(self.string_frame, text="Candle Clean", variable=self.smart_update_var, command=self.update_file_list, state=tk.DISABLED)
        self.check_box.pack(side="right")

        self.string_label = tk.Label(self.string_frame, text="Text to remove:", padx=5)
        self.string_label.pack(side="left", anchor="center")

        self.string_entry = tk.Entry(self.string_frame, textvariable=self.string_var)
        self.string_entry.pack(side="left", anchor="w")
        self.string_entry.config(state='normal')

        # Associate the validation function with the string variable
        self.string_var.trace("w", lambda *args: self.validate_string_entry())
        self.string_var.trace("w", lambda *args: (self.validate_string_entry(), self.update_file_list()) )

        self.scroll_sync_var = tk.BooleanVar()
        self.scroll_sync_check_box = tk.Checkbutton(self, text="Scroll Sync", variable=self.scroll_sync_var, command=self.scroll_sync_toggle)
        self.scroll_sync_check_box.grid(row=6, column=2, pady=10, sticky="w")
        self.scroll_sync_check_box.select()

        self.file_tree = ttk.Treeview(self, columns=("size"))
        self.file_tree.heading("#0", text="Files", anchor="w")
        self.file_tree.heading("size", text="Size", anchor="w")
        self.file_tree.column("size", width=int(self.file_tree.column("#0")["width"] * 0.2))
        self.file_tree.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        self.updated_file_tree = ttk.Treeview(self, columns=("size"))
        self.updated_file_tree.heading("#0", text="Files", anchor="w")
        self.updated_file_tree.heading("size", text="Size", anchor="w")
        self.updated_file_tree.column("size", width=int(self.updated_file_tree.column("#0")["width"] * 0.2))
        self.updated_file_tree.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")

        self.file_tree_scroll = tk.Scrollbar(self, orient="vertical", command=self.file_tree_yview)
        self.file_tree_scroll.grid(row=3, column=1, rowspan=3, padx=10, pady=10, sticky="nse")
        self.file_tree.configure(yscrollcommand=self.file_tree_scroll.set)
        self.file_tree.bind("<MouseWheel>", self.file_tree_scroll_mouse_wheel)

        self.updated_file_tree_scroll = tk.Scrollbar(self, orient="vertical", command=self.updated_file_tree_yview)
        self.updated_file_tree_scroll.grid(row=3, column=2, rowspan=3, padx=10, pady=10, sticky="nse")
        self.updated_file_tree.configure(yscrollcommand=self.updated_file_tree_scroll.set)
        self.updated_file_tree.bind("<MouseWheel>", self.updated_file_tree_scroll_mouse_wheel)

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

        #self.update_button = tk.Button(self, text="Update Right Column", command=self.update_file_list, justify=CENTER)
        #self.update_button.grid(row=6, column=1, pady=5)

        self.rename_button = tk.Button(self, text="Rename Files", command=self.rename_files, justify=CENTER)
        self.rename_button.grid(row=6, column=2, pady=5)

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

    def file_tree_yview(self, *args):
        self.file_tree.yview(*args)
        self.updated_file_tree.yview(*args)

    def updated_file_tree_yview(self, *args):
        self.updated_file_tree.yview(*args)
        self.file_tree.yview(*args)

    # If checkbox is selected, string entry should be disabled
    def validate_string_entry(self):
        if self.smart_update_var.get():
            self.string_entry.config(state='disabled')
        else:
            self.string_entry.config(state='normal')
    
    # Only allow smart cleaning if a valid directory is selected
    def validate_directory(self):
        directory = self.directory_var.get()
        return os.path.isdir(directory)

    def select_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.directory_var.set(directory_path)
            self.update_file_list()

    def update_file_list(self):
        directory_path = self.directory_var.get()
        smart_update = self.smart_update_var.get()
        self.regex_list = []
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
                        else:
                            string_to_remove = self.string_var.get()
                            file_shown = filename
                        if string_to_remove:
                            pattern = re.compile(re.escape(string_to_remove), re.IGNORECASE)
                            updated_file_name = re.sub(pattern, "", file_shown)
                            updated_file_size = os.path.getsize(file_path)
                            self.updated_file_tree.insert(parent_ids[dirpath]['updated_file_tree'], END, text=updated_file_name, values=(updated_file_size,))
                        else:
                            self.updated_file_tree.insert(parent_ids[dirpath]['updated_file_tree'], END, text=filename, values=(file_size,))
    
    def rename_files(self):
        directory_path = self.directory_var.get()
        smart_update = self.smart_update_var.get()
        success = True

        if os.path.isdir(directory_path):
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    if filename != ".DS_Store" and filename != "":
                        if smart_update:
                            current_directory = os.path.basename(dirpath)
                            current_regex = next((regex[0] for regex in self.regex_list if regex[1] == current_directory), "")
                            string_to_remove = current_regex
                            file_shown = re.sub(r'[ \-_]+', '_', os.path.splitext(filename)[0].lower()) + os.path.splitext(filename)[1]
                        else:
                            string_to_remove = self.string_var.get()
                            file_shown = filename
                        pattern = re.compile(re.escape(string_to_remove), re.IGNORECASE)
                        updated_file_name = re.sub(pattern, "", file_shown)
                        src = os.path.join(dirpath, filename)
                        dst = os.path.join(dirpath, updated_file_name)
                        try:
                            os.rename(src, dst)
                        except:
                            success = False
                            messagebox.showerror("Failed" "Couldn't rename file: " + file_shown)

            self.update_file_list()
            if success:
                messagebox.showinfo("Success", "Files renamed successfully!")
            

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
            prefix_regex = re.escape(common_prefix).replace('\\_', '[ _-]')
            pattern = prefix_regex# + ".*"
            regex = pattern.replace('\\-', '-')
            # Add the regex and the directory to the regex list
            self.regex_list.append((regex, dirname))

if __name__ == '__main__':
    # create the application instance
    app = CleanerApp()
    
    # start the main event loop
    app.mainloop()            