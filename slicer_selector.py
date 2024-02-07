import shutil
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from tkinter import ttk
import os
import configparser
import sys
import subprocess
import sysconfig


def get_ini_file_path():
    # Get the directory of the executable file
    exe_dir = "./"
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    elif __file__:
        exe_dir = os.path.dirname(__file__)
    return os.path.join(exe_dir, 'config.ini')


def open_with(file_path, root=None):
    config = configparser.ConfigParser()

    ini_file_path = get_ini_file_path()

    if not os.path.exists(ini_file_path):
        editor(file_path)
        return

    config.read(ini_file_path)

    slicers = config.sections()

    last_used_slicer = None
    for slicer in slicers:
        if config.getboolean(slicer, "last_used", fallback=False):
            last_used_slicer = slicer
            break

    slicer_names = [config[slicer].get("name", slicer) for slicer in slicers]

    if root is None:
        root = tk.Tk()
        root.withdraw()
        root.deiconify()
        root.title("Open With")

        style = ttk.Style(root)
        style.theme_use("clam")

        main_frame = ttk.Frame(root, padding=10)
        main_frame.grid()

        slicer_dropdown_label = ttk.Label(main_frame, text="Select Slicer:")
        slicer_dropdown_label.grid(row=0, column=0, padx=(0, 5), sticky=tk.W)

        slicer_dropdown = ttk.Combobox(main_frame, values=slicer_names, state="readonly")
        slicer_dropdown.grid(row=0, column=1, sticky=tk.W)

        if last_used_slicer and last_used_slicer in slicers:
            slicer_dropdown.set(config[last_used_slicer].get("name", last_used_slicer))
        else:
            slicer_dropdown.set(slicer_names[0])

        def save_file():
            print(file_path)
            file_name = os.path.basename(file_path)
            file_extension = file_name.split(".")[-1]
            save_path = filedialog.asksaveasfilename(
                initialfile=file_name,
                defaultextension=f".{file_extension}",
                filetypes=[
                    ("All Files", "*.*"),
                    ("STL File", "*.stl"),
                    ("3MF File", "*.3mf"),
                    ("Object File", "*.obj")
                ]
            )
            print(save_path)
            shutil.copyfile(file_path, save_path)

        save_button = ttk.Button(main_frame, text="Save", command=save_file)
        save_button.grid(row=1, column=0, columnspan=2, padx=(0, 90*2), pady=(5, 0), sticky=tk.E)

        def open_editor():
            editor(file_path, root)

        edit_button = ttk.Button(main_frame, text="Edit Slicers", command=open_editor)
        edit_button.grid(row=1, column=0, columnspan=2, padx=(0, 90), pady=(5, 0), sticky=tk.E)

        def open_file():
            slicer_name = slicer_dropdown.get()
            slicer = None
            for prog in slicers:
                if config[prog].get("name", prog) == slicer_name:
                    slicer = prog
                    break
            if slicer:

                if config[slicer]["history"]:
                    file_name = os.path.basename(file_path)
                    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #2023‐09‐05_00-15-08
                    if not os.path.exists(config[slicer]["history_path"]):
                        os.makedirs(config[slicer]["history_path"])
                    save_path = os.path.join(config[slicer]["history_path"], date+"_"+file_name)
                    print(save_path)
                    shutil.copyfile(file_path, save_path)

                slicer_path = config[slicer]["path"]
                subprocess.Popen([slicer_path, file_path])
                for prog in slicers:
                    config.set(prog, "last_used", str(prog == slicer))
                with open(ini_file_path, "w+") as config_file:
                    config.write(config_file)
            root.destroy()

        open_button = ttk.Button(main_frame, text="Open", command=open_file)
        open_button.grid(row=1, column=0, columnspan=2, padx=(0, 0), pady=(5, 0), sticky=tk.E)

        root.mainloop()
    else:
        slicer_dropdown = root.children.get("!frame").children.get("!combobox")
        slicer_dropdown.config(values=slicer_names)

        if last_used_slicer and last_used_slicer in slicers:
            slicer_dropdown.set(config[last_used_slicer].get("name", last_used_slicer))
        else:
            slicer_dropdown.set(slicer_names[0])


def editor(file_path, parent=None):
    config = configparser.ConfigParser()

    ini_file_path = get_ini_file_path()

    if os.path.exists(ini_file_path):
        config.read(ini_file_path)

    slicers = config.sections()
    slicer_names = [config[slicer].get("name", slicer) for slicer in slicers]

    editor_window = tk.Toplevel(parent) if parent else tk.Tk()
    editor_window.title("Slicer Editor")

    style = ttk.Style(editor_window)
    style.theme_use("clam")

    main_frame = ttk.Frame(editor_window, padding=10)
    main_frame.grid()

    slicer_dropdown_label = ttk.Label(main_frame, text="Select Slicer:")
    slicer_dropdown_label.grid(row=0, column=0, padx=(0, 5), sticky=tk.E)

    slicer_dropdown = ttk.Combobox(main_frame, values=slicer_names, state="readonly")
    slicer_dropdown.grid(row=0, column=1, sticky=tk.W)

    slicer_label = ttk.Label(main_frame, text="Slicer Name:")
    slicer_label.grid(row=1, column=0, padx=(0, 5), sticky=tk.E)

    slicer_name_entry = ttk.Entry(main_frame)
    slicer_name_entry.grid(row=1, column=1, pady=(5, 0), sticky=tk.W)

    slicer_path_label = ttk.Label(main_frame, text="Slicer Path:")
    slicer_path_label.grid(row=2, column=0, padx=(0, 5), sticky=tk.E)

    slicer_path_entry = ttk.Entry(main_frame)
    slicer_path_entry.grid(row=2, column=1, pady=(5, 0), sticky=tk.W)

    history_enable_label = ttk.Label(main_frame, text="Save History:")
    history_enable_label.grid(row=3, column=0, padx=(0, 5), sticky=tk.E)

    def change_save_history():
        if "selected" in history_enable_entry.state():
            history_path_entry.state(["!disabled"])
        else:
            history_path_entry.state(["disabled"])

    history_enable_entry = ttk.Checkbutton(main_frame, command=change_save_history)
    history_enable_entry.grid(row=3, column=1, pady=(5, 0), sticky=tk.W)

    history_path_label = ttk.Label(main_frame, text="History Path:")
    history_path_label.grid(row=4, column=0, padx=(0, 5), sticky=tk.E)

    history_path_entry = ttk.Entry(main_frame, state="disabled")
    history_path_entry.grid(row=4, column=1, pady=(5, 0), sticky=tk.W)

    def load_slicer_details(event=None):
        selected_slicer = slicer_dropdown.get()
        if selected_slicer:
            slicer_name = config[selected_slicer].get("name", selected_slicer)
            slicer_path = config[selected_slicer].get("path", "")
            history_enable = config[selected_slicer].get("history", "False")
            history_path = config[selected_slicer].get("history_path", "")
            slicer_name_entry.delete(0, tk.END)
            slicer_name_entry.insert(0, slicer_name)
            slicer_path_entry.delete(0, tk.END)
            slicer_path_entry.insert(0, slicer_path)
            if history_enable == "True":
                history_enable_entry.state(["selected"])
                history_path_entry.state(["!disabled"])
            else:
                history_enable_entry.state(["!selected"])
                history_path_entry.state(["disabled"])
            history_path_entry.delete(0, tk.END)
            history_path_entry.insert(0, history_path)

    slicer_dropdown.bind("<<ComboboxSelected>>", load_slicer_details)

    def add_slicer():
        slicer_name = slicer_name_entry.get()
        slicer_path = slicer_path_entry.get()
        history_enable = str("selected" in history_enable_entry.state())
        history_path = history_path_entry.get()
        if slicer_name and slicer_path:
            if slicer_name not in slicers:
                config.add_section(slicer_name)
            config.set(slicer_name, "name", slicer_name)
            config.set(slicer_name, "path", slicer_path)
            config.set(slicer_name, "history", history_enable)
            config.set(slicer_name, "history_path", history_path)
            with open(ini_file_path, "w+") as config_file:
                config.write(config_file)
            slicer_dropdown.configure(values=config.sections())
            slicer_dropdown.set(slicer_name)
            slicer_name_entry.delete(0, tk.END)
            slicer_path_entry.delete(0, tk.END)

    add_button = ttk.Button(main_frame, text="Add Slicer", command=add_slicer)
    add_button.grid(row=5, column=0, columnspan=2, padx=(0, 102), pady=(5, 0), sticky=tk.E)

    def delete_slicer():
        selected_slicer = slicer_dropdown.get()
        if selected_slicer:
            config.remove_section(selected_slicer)
            with open(ini_file_path, "w") as config_file:
                config.write(config_file)
            slicer_dropdown.configure(values=config.sections())
            slicer_name_entry.delete(0, tk.END)
            slicer_path_entry.delete(0, tk.END)

    delete_button = ttk.Button(main_frame, text="Delete Slicer", command=delete_slicer)
    delete_button.grid(row=5, column=0, columnspan=2, padx=(0, 14), pady=(5, 0), sticky=tk.E)

    def done():
        editor_window.destroy()
        open_with(file_path, parent)

    done_button = ttk.Button(main_frame, text="Done", command=done)
    done_button.grid(row=6, column=1, padx=(0, 14), pady=(5, 0), sticky=tk.E)

    load_slicer_details()

    editor_window.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        open_with(file_path)
    else:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select STL")
        if file_path:
            open_with(file_path)
