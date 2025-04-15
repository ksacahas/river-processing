# Refactored GUI Script (Full Functionality Retained)
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import re
import glob
import sys
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

# Setup paths and imports
if getattr(sys, 'frozen', False):
    # If running as a bundled executable
    script_path = os.path.dirname(sys.executable)
else:
    # If running as a .py file
    script_path = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(script_path, 'utils'))

# Local imports
from generate_points_multiprocessing import generate_points_multiprocessing  # type: ignore
from generate_replicates import generate_replicates  # type: ignore
from check_bimodality_across_replicates import check_bimodality_across_replicates  # type: ignore
from bimodality_significance import bimodality_significance  # type: ignore
from classify_rosediagrams_manually import classify_rosediagrams_manually  # type: ignore
from optimize_bandwidth import optimize_bandwidth  # type: ignore

# Utility function

def validate_name(name):
    if name[0].isdigit():
        return False, "Name must not start with a number."
    if not re.match(r'^[\w_]+$', name):
        return False, "Only letters, numbers, and underscores allowed."
    return True, ""

# GUI Functions

def show_upload_window(root):
    win = tk.Toplevel(root)
    win.title("Upload Image")
    tk.Label(win, text="Enter Image Name:").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()

    def upload_image():
        file_path = filedialog.askopenfilename(filetypes=[
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg"),
            ("JPEG files", "*.jpeg"),
            ("Bitmap files", "*.bmp"),
            ("GIF files", "*.gif"),
            ("TIF files", "*.tif"),
            ("TIFF files", "*.tiff")
            ]
            )
        if not file_path:
            return
        name = name_entry.get()
        valid, msg = validate_name(name)
        if not valid:
            messagebox.showerror("Invalid Name", msg)
            return

        def save_image(image_type):
            folder = os.path.join(script_path, 'my_controls' if image_type == 'control' else 'my_unknowns', 'Images')
            os.makedirs(folder, exist_ok=True)
            shutil.copy(file_path, os.path.join(folder, f"{name}.png"))
            messagebox.showinfo("Success", f"Saved to {folder}.")
            win.destroy()

        type_win = tk.Toplevel(win)
        type_win.title("Image Type")
        tk.Label(type_win, text="Is this image an Unknown or a Control?").pack()
        tk.Button(type_win, text="Unknown", command=lambda: save_image("unknown")).pack(side="left", padx=10)
        tk.Button(type_win, text="Control", command=lambda: save_image("control")).pack(side="right", padx=10)

    tk.Button(win, text="Upload Image", command=upload_image).pack(pady=10)

def show_generate_points_window(root):
    win = tk.Toplevel(root)
    win.title("Generate Points")
    tk.Label(win, text="Select Image Type:").pack()
    folder_var = tk.StringVar(value="my_unknowns")
    folder_dropdown = ttk.Combobox(win, textvariable=folder_var, values=["my_unknowns", "my_controls"])
    folder_dropdown.pack()

    tk.Label(win, text="Select an Image:").pack()
    image_var = tk.StringVar()
    image_dropdown = ttk.Combobox(win, textvariable=image_var)
    image_dropdown.pack()

    def update_image_list():
        folder = os.path.join(script_path, folder_var.get(), "Images")
        image_dropdown["values"] = [f for f in os.listdir(folder) if f.endswith((".png", ".jpg", ".jpeg"))] if os.path.exists(folder) else []
        if image_dropdown["values"]:
            image_dropdown.current(0)



    folder_dropdown.bind("<<ComboboxSelected>>", lambda _: update_image_list())
    update_image_list()

    tk.Label(win, text="Enter K (Number of Points):").pack()
    k_entry = tk.Entry(win)
    k_entry.pack()

    tk.Label(win, text="Enter Output File Name:").pack()
    filename_entry = tk.Entry(win)
    filename_entry.pack()

    plot_var = tk.IntVar()
    tk.Checkbutton(win, text="Plot Results", variable=plot_var).pack()

    def run():
        folder = folder_var.get()
        image = image_var.get()
        k = k_entry.get()
        filename = filename_entry.get().strip()
        if not image:
            return messagebox.showerror("Error", "No image selected.")
        if not k.isdigit():
            return messagebox.showerror("Error", "K must be an integer.")
        valid, msg = validate_name(filename)
        if not valid:
            return messagebox.showerror("Invalid Filename", msg)

        image_path = os.path.join(script_path, folder, "Images", image)
        file_path = os.path.join(script_path, folder, "Points", f"{filename}.csv")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        generate_points_multiprocessing([image_path, file_path, int(k), bool(plot_var.get())])
        messagebox.showinfo("Success", f"Points saved to {file_path}")

    tk.Button(win, text="Run", command=run).pack(pady=10)

    # Bimodality Test Window (fully embedded)
def show_bimodality_test_window(root):
    bimodality_window = tk.Toplevel(root)
    bimodality_window.title("Bimodality Test")

    def open_generate_replicates_window():
        win = tk.Toplevel(bimodality_window)
        win.title("Generate Replicates")

        tk.Label(win, text="Select Data File:").pack()
        selected_dir = os.path.join(script_path, "my_unknowns", "Points")
        os.makedirs(selected_dir, exist_ok=True)
        file_names = [f for f in os.listdir(selected_dir) if f.endswith(".csv")]

        file_dropdown = ttk.Combobox(win, values=file_names)
        file_dropdown.pack()

        status_label = tk.Label(win, text="")
        status_label.pack()

        def run():
            selected_file = file_dropdown.get()
            if not selected_file:
                return status_label.config(text="Please select a file.")
            input_path = os.path.join(selected_dir, selected_file)
            output_dir = os.path.join(script_path, "my_bimodality_tests", "Unknowns", os.path.splitext(selected_file)[0])
            os.makedirs(output_dir, exist_ok=True)
            generate_replicates([input_path, output_dir, 100])
            status_label.config(text=f"Replicates in {output_dir}")

        tk.Button(win, text="Run", command=run).pack()

    def open_apply_bimodality_test_window():
        win = tk.Toplevel(bimodality_window)
        win.title("Apply Bimodality Test")

        tk.Label(win, text="Select File:").pack()
        unknown_tests_dir = os.path.join(script_path, "my_bimodality_tests", "Unknowns")
        test_dirs = [d for d in os.listdir(unknown_tests_dir) if os.path.isdir(os.path.join(unknown_tests_dir, d))]
        dir_dropdown = ttk.Combobox(win, values=test_dirs)
        dir_dropdown.pack()

        use_custom_var = tk.BooleanVar(value=True)
        tk.Radiobutton(win, text="Enter Custom Bandwidth:", variable=use_custom_var, value=True).pack()
        custom_bw_entry = tk.Entry(win)
        custom_bw_entry.insert(0, "8")
        custom_bw_entry.pack()

        tk.Radiobutton(win, text="Select Bandwidth from Calibrations:", variable=use_custom_var, value=False).pack()
        bw_options = []
        try:
            df = pd.read_csv(os.path.join(script_path, "bimodality_calibration", "optimal_bandwidth.csv"))
            bw_options = df["Optimal bandwidth"].dropna().unique().tolist()
        except: pass
        dropdown_var = tk.StringVar()
        tk.OptionMenu(win, dropdown_var, *(bw_options if bw_options else ["No options"])).pack()

        status_label = tk.Label(win, text="")
        status_label.pack()

        def get_bw():
            try:
                return int(custom_bw_entry.get()) if use_custom_var.get() else int(float(dropdown_var.get()))
            except:
                status_label.config(text="Invalid bandwidth.")
                return None

        def run():
            d = dir_dropdown.get()
            if not d: return status_label.config(text="Please select dir.")
            bw = get_bw()
            if bw is None: return
            folder = os.path.join(script_path, "my_bimodality_tests", "Unknowns", d)
            out_path = os.path.join(folder, f"{d}_bimodality_results.csv")
            check_bimodality_across_replicates([folder, bw, out_path])
            status_label.config(text=f"Saved to {out_path}")

        tk.Button(win, text="Run", command=run).pack()

    def open_statistical_significance_window():
        win = tk.Toplevel(bimodality_window)
        win.title("Statistical Significance")

        tk.Label(win, text="Select Bimodality Result File:").pack()
        all_files = glob.glob(os.path.join(script_path, "my_bimodality_tests", "Unknowns", "**", "*.csv"), recursive=True)
        result_files = [os.path.basename(f) for f in all_files if f.endswith("_bimodality_results.csv")]
        result_dropdown = ttk.Combobox(win, values=result_files)
        result_dropdown.pack()

        tk.Label(win, text="Number of Meanders:").pack()
        meanders_entry = tk.Entry(win)
        meanders_entry.pack()

        tk.Button(win, text="Show Image", command=lambda: show_image(result_dropdown.get())).pack()

        tk.Label(win, text="Select Control File:").pack()
        control_files = glob.glob(os.path.join(script_path, "control_files", "*.csv"))
        control_dropdown = ttk.Combobox(win, values=[os.path.basename(f) for f in control_files])
        control_dropdown.pack()

        status_label = tk.Label(win, text="")
        status_label.pack()

        def show_image(filename):
            basename = filename.replace("_bimodality_results.csv", "")
            img_path = os.path.join(script_path, "my_unknowns", "Images", f"{basename}.png")
            if os.path.exists(img_path):
                img = plt.imread(img_path)
                plt.figure()
                plt.imshow(img)
                plt.axis('off')
                plt.title(f"{basename}.png")
                plt.tight_layout()
                plt.show()
            else:
                status_label.config(text="Image not found.")

        def run():
            file = result_dropdown.get()
            if not file: return status_label.config(text="No bimodality file.")
            paths = glob.glob(os.path.join(script_path, "my_bimodality_tests/Unknowns", "**", file), recursive=True)
            if not paths:
                return status_label.config(text="File not found.")
            upath = paths[0]
            try:
                n_meanders = int(meanders_entry.get())
            except:
                return status_label.config(text="Invalid meanders.")
            ctrl_file = control_dropdown.get()
            if not ctrl_file:
                return status_label.config(text="No control file.")
            
            ctrl_path = os.path.join(script_path, "control_files", ctrl_file)

            try:
                bimodality_significance(upath, ctrl_path, n_meanders)
                status_label.config(text=f"Completed for {file}")
            except Exception as e:
                status_label.config(text=f"Error: {e}")

        tk.Button(win, text="Run", command=run).pack()

    def open_calibrate_bimodality_window():
        win = tk.Toplevel(bimodality_window)
        win.title("Calibrate Bimodality Test")

        def make_set():
            if not messagebox.askokcancel("Instructions", "Classify river plots manually. Proceed?"): return
            input_dir = os.path.join(script_path, "sgr")
            output_dir = os.path.join(script_path, "bimodality_calibration")
            os.makedirs(output_dir, exist_ok=True)
            ts = datetime.now().strftime("%m%d%y_%H%M")
            out_file = f"bimodality_calibration_set_{ts}.csv"
            output_path = os.path.join(output_dir, out_file)
            classify_rosediagrams_manually(input_dir, output_path)
            messagebox.showinfo("Done", f"Saved to {output_path}")

        def optimize():
            calibration_dir = os.path.join(script_path, "bimodality_calibration")
            sgr_dir = os.path.join(script_path, "sgr")
            bw = optimize_bandwidth(calibration_dir, sgr_dir, plot_var.get())

            if messagebox.askyesno(title="Bandwidth Optimization Complete",
                                   message=f"Optimal bandwidth is {bw}. Save this value?"):
                file_path = os.path.join(calibration_dir, "optimal_bandwidth.csv")
                d = datetime.today().strftime("%Y-%m-%d")
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.DataFrame(columns=["Date", "Type", "Optimal bandwidth"])
                if bw not in df["Optimal bandwidth"].values:
                    new_row = pd.DataFrame({
                        "Date": [d],
                        "Type": ["user-defined"],
                        "Optimal bandwidth": [bw]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df.loc[df["Optimal bandwidth"] == bw, "Date"] = d
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Saved", f"Saved to {file_path}")

        plot_var = tk.BooleanVar()
        tk.Button(win, text="Make Calibration Set", command=make_set).pack(pady=5)
        tk.Button(win, text="Optimize KDE Bandwidth", command=optimize).pack(pady=5)
        tk.Checkbutton(win, text="Plot bandwidth results", variable=plot_var).pack()

    def open_make_new_control_set_window():
        win = tk.Toplevel(bimodality_window)
        win.title("Make New Control Set")

        use_custom_var = tk.BooleanVar(value=True)
        tk.Radiobutton(win, text="Enter Custom Bandwidth:", variable=use_custom_var, value=True).pack()
        custom_bw_entry = tk.Entry(win)
        custom_bw_entry.insert(0, "8")
        custom_bw_entry.pack()

        tk.Radiobutton(win, text="Select Bandwidth from Calibrations:", variable=use_custom_var, value=False).pack()
        try:
            bw_path = os.path.join(script_path, "bimodality_calibration", "optimal_bandwidth.csv")
            bw_opts = pd.read_csv(bw_path)["Optimal bandwidth"].dropna().unique().tolist()
        except: bw_opts = []
        dropdown_var = tk.StringVar()
        tk.OptionMenu(win, dropdown_var, *(bw_opts if bw_opts else ["No options"])).pack()

        status_label = tk.Label(win, text="")
        status_label.pack()

        def get_bw():
            try:
                return int(custom_bw_entry.get()) if use_custom_var.get() else int(float(dropdown_var.get()))
            except:
                status_label.config(text="Invalid bandwidth.")
                return None

        def run():
            bw = get_bw()
            if bw is None: return
            if not messagebox.askokcancel("Warning", "This may take a while."): return

            input_dir = os.path.join(script_path, "my_controls", "Points")
            output_dir = os.path.join(script_path, "my_bimodality_tests", "Controls")
            if not os.path.exists(input_dir) or not os.listdir(input_dir):
                return messagebox.showerror("Error", "my_controls/Points is empty")
            os.makedirs(output_dir, exist_ok=True)
            for f in os.listdir(input_dir):
                if f.endswith(".csv"):
                    src = os.path.join(input_dir, f)
                    dest = os.path.join(output_dir, os.path.splitext(f)[0])
                    os.makedirs(dest, exist_ok=True)
                    generate_replicates([src, dest, 100])
                    result_file = os.path.join(dest, f"{os.path.basename(dest)}_bimodality_results.csv")
                    check_bimodality_across_replicates([dest, bw, result_file])

            all_results = [pd.read_csv(os.path.join(r, f))
                           for r, _, fs in os.walk(output_dir)
                           for f in fs if f.endswith("bimodality_results.csv")]
            if all_results:
                outdf = pd.concat(all_results)
                outpath = os.path.join(script_path, "control_files", f"user_controls_{datetime.now().strftime('%m%d%y')}.csv")
                outdf.to_csv(outpath, index=False)
                messagebox.showinfo("Success", f"Control set saved to {outpath}")
            else:
                messagebox.showerror("Error", "No result files found.")

        tk.Button(win, text="Run", command=run).pack()

    # Main options
    tk.Button(bimodality_window, text="Generate Replicates", command=open_generate_replicates_window).pack()
    tk.Button(bimodality_window, text="Apply Bimodality Test", command=open_apply_bimodality_test_window).pack()
    tk.Button(bimodality_window, text="Statistical Significance", command=open_statistical_significance_window).pack()
    tk.Button(bimodality_window, text="Calibrate Bimodality Test", command=open_calibrate_bimodality_window).pack()
    tk.Button(bimodality_window, text="Make New Control Set", command=open_make_new_control_set_window).pack()

def main():
    root = tk.Tk()
    root.title("Main Menu")
    tk.Button(root, text="Upload Image", command=lambda: show_upload_window(root), width=20).pack(pady=5)
    tk.Button(root, text="Generate Points", command=lambda: show_generate_points_window(root), width=20).pack(pady=5)
    tk.Button(root, text="Bimodality Test", command=lambda: show_bimodality_test_window(root), width=20).pack(pady=5)
    root.mainloop()

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()  # required on Windows/macOS with PyInstaller
    main()
