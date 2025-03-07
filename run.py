if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    import os
    import shutil
    import re
    import glob
    import sys
    from PIL import Image
    import matplotlib.pyplot as plt
    import pandas as pd
    import matplotlib.image as mpimg
    from datetime import datetime

    script_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(script_path)

    sys.path.append(os.path.join(script_path, 'utils'))
    from generate_points import generate_points # type: ignore
    from generate_points_multiprocessing import generate_points_multiprocessing # type: ignore
    from generate_replicates import generate_replicates # type: ignore
    from check_bimodality import check_bimodality # type: ignore
    from check_bimodality_across_replicates import check_bimodality_across_replicates # type: ignore
    from bimodality_significance import bimodality_significance # type: ignore
    from classify_rosediagrams_manually import classify_rosediagrams_manually # type: ignore
    from optimize_bandwidth import optimize_bandwidth # type: ignore

    # Ensure directories exist
    os.makedirs('my_unknowns/Images', exist_ok=True)
    os.makedirs('my_controls/Images', exist_ok=True)

    # Main Window
    root = tk.Tk()
    root.title("Main Menu")

    # --- Functions ---

    def validate_name(name):
        """Ensures the image name follows the required format."""
        if name[0].isdigit():
            return False, "Name must not start with a number."
        if not re.match(r'^[\w_]+$', name):  # Only letters, numbers, and underscores
            return False, "Name must not contain spaces or special characters except underscores."
        return True, ""

    def show_upload_window():
        """Opens the Upload Image window."""
        upload_win = tk.Toplevel(root)
        upload_win.title("Upload Image")

        tk.Label(upload_win, text="Enter Image Name:").pack()
        name_entry = tk.Entry(upload_win)
        name_entry.pack()

        def upload_image():
            file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[
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
            is_valid, error_message = validate_name(name)
            if not is_valid:
                messagebox.showerror("Invalid Name", error_message)
                return
            
            def save_image(image_type):
                folder = 'my_controls/Images' if image_type == 'control' else 'my_unknowns/Images'
                new_file_path = os.path.join(folder, f"{name}.png")
                shutil.copy(file_path, new_file_path)
                messagebox.showinfo("Success", f"Image saved as {name} in {folder}.")
                upload_win.destroy()
            
            # Ask if image is unknown or control
            type_win = tk.Toplevel(upload_win)
            type_win.title("Image Type")

            tk.Label(type_win, text="Is this image an Unknown or a Control?").pack()
            tk.Button(type_win, text="Unknown", command=lambda: save_image("unknown")).pack(side="left", padx=10)
            tk.Button(type_win, text="Control", command=lambda: save_image("control")).pack(side="right", padx=10)

        tk.Button(upload_win, text="Upload Image", command=upload_image).pack(pady=10)

    def show_generate_points_window():
        """Opens the Generate Points window."""
        gen_win = tk.Toplevel(root)
        gen_win.title("Generate Points")

        # Select Image Type (my_unknowns or my_controls)
        tk.Label(gen_win, text="Select Image Type:").pack()
        folder_var = tk.StringVar(value="my_unknowns")
        folder_dropdown = ttk.Combobox(gen_win, textvariable=folder_var, values=["my_unknowns", "my_controls"])
        folder_dropdown.pack()

        # Select Image from Dropdown
        tk.Label(gen_win, text="Select an Image:").pack()
        image_var = tk.StringVar()
        image_dropdown = ttk.Combobox(gen_win, textvariable=image_var)
        image_dropdown.pack()

        def update_image_list():
            """Updates the dropdown list based on selected folder."""
            selected_folder = folder_var.get()
            image_folder = os.path.join(selected_folder, "Images")
            images = [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))] if os.path.exists(image_folder) else []
            image_dropdown["values"] = images
            if images:
                image_dropdown.current(0)

        folder_dropdown.bind("<<ComboboxSelected>>", lambda e: update_image_list())
        update_image_list()

        # Number of Points (K)
        tk.Label(gen_win, text="Enter K (Number of Points):").pack()
        k_entry = tk.Entry(gen_win)
        k_entry.pack()

        # Filename Input (CSV)
        tk.Label(gen_win, text="Enter Output File Name:").pack()
        filename_entry = tk.Entry(gen_win)
        filename_entry.pack()

        # Plot Option
        plot_var = tk.IntVar()
        tk.Checkbutton(gen_win, text="Plot Results", variable=plot_var).pack()

        def run_generate_points():
            """Runs the generate_points function."""
            selected_folder = folder_var.get()
            selected_image = image_var.get()
            k_value = k_entry.get()
            filename = filename_entry.get().strip()

            if not selected_image:
                messagebox.showerror("Error", "No image selected.")
                return

            if not k_value.isdigit():
                messagebox.showerror("Error", "K must be an integer.")
                return

            is_valid, error_message = validate_name(filename)
            if not is_valid:
                messagebox.showerror("Invalid Filename", error_message)
                return

            image_path = os.path.join(selected_folder, "Images", selected_image)
            file_path = os.path.join(selected_folder, "Points", f"{filename}.csv")

            args = [image_path, file_path, int(k_value), bool(plot_var.get())]
            generate_points_multiprocessing(args)

            messagebox.showinfo("Success", f"Points generated and saved to {file_path}")

        tk.Button(gen_win, text="Run", command=run_generate_points).pack(pady=10)

    def show_bimodality_test_window():
        def open_generate_replicates_window():
            def run_generate_replicates():
                selected_file = file_dropdown.get()
                if not selected_file:
                    status_label.config(text="Please select a file.")
                    return
                
                data_path = os.path.join(selected_dir, selected_file)
                output_dir = os.path.join("my_bimodality_tests/Unknowns", os.path.splitext(selected_file)[0])
                
                # Ensure the output directory exists
                os.makedirs("my_bimodality_tests/Unknowns", exist_ok=True)
                os.makedirs(output_dir, exist_ok=True)
                
                # Run the replicate generation function
                generate_replicates([data_path, output_dir, 100])
                
                status_label.config(text=f"Replicates generated in {output_dir}")

            # Create a new window
            replicates_window = tk.Toplevel(bimodality_window)
            replicates_window.title("Generate Replicates")

            # Dropdown to select file
            tk.Label(replicates_window, text="Select Data File:").pack()
            
            # Determine the directory
            selected_dir = "my_unknowns/Points" if os.path.exists("my_unknowns/Points") else "my_controls/Points"
            files = glob.glob(os.path.join(selected_dir, "*.csv"))
            file_names = [os.path.basename(f) for f in files]

            file_dropdown = ttk.Combobox(replicates_window, values=file_names)
            file_dropdown.pack()

            # Button to generate replicates
            generate_button = tk.Button(replicates_window, text="Run", command=run_generate_replicates)
            generate_button.pack()

            # Status label
            status_label = tk.Label(replicates_window, text="")
            status_label.pack()

        def open_apply_bimodality_test_window():
            def load_calibrated_bandwidths():
                """Loads 'Optimal bandwidth' values from CSV into the dropdown menu."""
                try:
                    df = pd.read_csv("bimodality_calibration/optimal_bandwidth.csv")
                    return df["Optimal bandwidth"].dropna().unique().tolist()
                except (FileNotFoundError, KeyError):
                    messagebox.showerror("Error", "Could not load 'Optimal bandwidth' values.")
                    return []

            def get_selected_bandwidth():
                """Retrieves and validates the selected or entered bandwidth."""
                if use_custom_var.get():  # Custom input selected
                    bw = custom_bw_entry.get()
                    try:
                        return int(bw)
                    except ValueError:
                        status_label.config(text="Bandwidth must be an integer.")
                        return None
                else:  # Dropdown selection used
                    bw = float(dropdown_var.get())
                    try:
                        return int(bw)
                    except ValueError:
                        status_label.config(text="Invalid selection from dropdown.")
                        return None
                    
            def run_bimodality_test():
                selected_dir = dir_dropdown.get()
                if not selected_dir:
                    status_label.config(text="Please select a directory.")
                    return
                
                bw = get_selected_bandwidth()

                if bw is None:
                    return  # Stop execution if bandwidth is invalid

                data_dir = os.path.join("my_bimodality_tests/Unknowns", selected_dir)

                file_path = os.path.join(data_dir, f"{selected_dir}_bimodality_results.csv")

                # Run the bimodality test function
                check_bimodality_across_replicates([data_dir, bw, file_path])

                status_label.config(text=f"Bimodality results saved to {file_path}")

            # Create the new window
            bimodality_test_window = tk.Toplevel(bimodality_window)
            bimodality_test_window.title("Apply Bimodality Test")

            # Dropdown to select bimodality test directory
            tk.Label(bimodality_test_window, text="Select File:").pack()

            test_dirs = [d for d in os.listdir("my_bimodality_tests/Unknowns") if os.path.isdir(os.path.join("my_bimodality_tests/Unknowns", d))]
            dir_dropdown = ttk.Combobox(bimodality_test_window, values=test_dirs)
            dir_dropdown.pack()

            # Option 1: Custom input field
            use_custom_var = tk.BooleanVar(value=True)  # Default to custom input
            custom_radio = tk.Radiobutton(bimodality_test_window, text="Enter Custom Bandwidth:", variable=use_custom_var, value=True)
            custom_radio.pack()

            custom_bw_entry = tk.Entry(bimodality_test_window)
            custom_bw_entry.insert(0, "8")  # Default value
            custom_bw_entry.pack()

            # Option 2: Dropdown menu
            dropdown_radio = tk.Radiobutton(bimodality_test_window, text="Select Bandwidth from Calibrations:", variable=use_custom_var, value=False)
            dropdown_radio.pack()

            dropdown_var = tk.StringVar(value="")
            dropdown_menu = tk.OptionMenu(bimodality_test_window, dropdown_var, *load_calibrated_bandwidths())
            dropdown_menu.pack()

            # Button to apply bimodality test
            apply_button = tk.Button(bimodality_test_window, text="Run", command=run_bimodality_test)
            apply_button.pack()

            # Status label
            status_label = tk.Label(bimodality_test_window, text="")
            status_label.pack()

        def open_statistical_significance_window():
            def show_image():
                # Get the selected bimodality result file
                selected_bimodality_file = bimodality_file_dropdown.get()
                if not selected_bimodality_file:
                    status_label.config(text="Please select a bimodality result file.")
                    return
                
                # Get the basename without '_bimodality_result.csv'
                basename = selected_bimodality_file.replace("_bimodality_results.csv", "")

                # Search for the corresponding image
                image_path = os.path.join("my_unknowns", "Images", f"{basename}.png")
        
                if os.path.exists(image_path):
                    # Show the image (you can use a library like PIL to display the image or just mention its path)
                    status_label.config(text=f"Image found: {image_path}")
                    #image = Image.open(image_path)
                    #image.show()
                    img = mpimg.imread(image_path)
                    plt.imshow(img)
                    plt.title(f"Image: {basename}")  # Set the title of the window
                    plt.axis('off')  # Hide axes for a cleaner look
                    plt.show()


                else:
                    status_label.config(text="Image not found.")

            def run_bimodality_significance():
                # Get the selected bimodality result file
                selected_bimodality_file = bimodality_file_dropdown.get()
                if not selected_bimodality_file:
                    status_label.config(text="Please select a bimodality result file.")
                    return
                
                # Search for the selected bimodality result file in 'my_bimodality_tests' and its subdirectories
                bimodality_file_paths = glob.glob(os.path.join("my_bimodality_tests/Unknowns", "**", selected_bimodality_file), recursive=True)
                if not bimodality_file_paths:
                    status_label.config(text=f"Bimodality result file not found: {selected_bimodality_file}")
                    return
                
                # Use the first match (if multiple files are found)
                unknown_file_path = bimodality_file_paths[0]
                
                # Get the basename without '_bimodality_result.csv'
                basename = selected_bimodality_file.rsplit(".", 1)[0]

                # Get the number of meanders
                try:
                    n_meanders = int(meanders_entry.get())
                except ValueError:
                    status_label.config(text="Please enter a valid number of meanders.")
                    return

                # Get the path for the control file
                selected_control_file = control_file_dropdown.get()
                if not selected_control_file:
                    status_label.config(text="Please select a control file.")
                    return
                
                # Construct the full path for the control file
                control_file_path = os.path.join("control_files", selected_control_file) 

                # Run the bimodality significance function
                try:
                    bimodality_significance(unknown_file_path, control_file_path, n_meanders)
                except ValueError as e:
                    messagebox.showerror("Error", str(e))

                # Show completion status
                status_label.config(text=f"Bimodality significance analysis completed for {basename}.")

            # Create a new window
            significance_window = tk.Toplevel(bimodality_window)
            significance_window.title("Statistical Significance")

            # Dropdown to select bimodality result file
            tk.Label(significance_window, text="Select Bimodality Result File:").pack()

            # Search for all "_bimodality_result.csv" files in "my_bimodality_tests" and subdirectories
            bimodality_files = glob.glob("my_bimodality_tests/Unknowns/**/*.csv", recursive=True)
            bimodality_result_files = [os.path.basename(f) for f in bimodality_files if f.endswith("_bimodality_results.csv")]

            bimodality_file_dropdown = ttk.Combobox(significance_window, values=bimodality_result_files)
            bimodality_file_dropdown.pack()

            # Input for number of meanders
            tk.Label(significance_window, text="Number of Meanders:").pack()
            meanders_entry = tk.Entry(significance_window)
            meanders_entry.pack()

            # Button to show image
            show_image_button = tk.Button(significance_window, text="Show Image", command=show_image)
            show_image_button.pack()

            # Dropdown to select control file
            tk.Label(significance_window, text="Select Control File:").pack()

            # Get list of control files in 'control_files'
            control_files = glob.glob(os.path.join("control_files", "*.csv"))
            control_file_names = [os.path.basename(f) for f in control_files]

            control_file_dropdown = ttk.Combobox(significance_window, values=control_file_names)
            control_file_dropdown.pack()

            # Button to run the bimodality significance test
            run_test_button = tk.Button(significance_window, text="Run", command=run_bimodality_significance)
            run_test_button.pack()

            # Status label
            status_label = tk.Label(significance_window, text="")
            status_label.pack()


        def open_calibrate_bimodality_window():
            """Opens the Calibration Bimodality Test window."""
            cal_win = tk.Toplevel(bimodality_window)
            cal_win.title("Calibrate Bimodality Test")

            def make_calibration_set():
                """Runs the manual classification process and saves the results."""
                proceed = messagebox.askokcancel(
                    "Instructions",
                    "You will see a series of distributions from sine-generated meandering rivers.\n"
                    "For each distribution, decide whether or not it is bimodal.\n"
                    "Your choices will be saved and used to determine the optimal bandwidth for the bimodality test."
                )

                if not proceed:  # If the user clicks "Cancel", stop execution
                    return

                # Set input/output directories
                input_dir = "sgr"
                output_dir = "bimodality_calibration"
                timestamp = datetime.now().strftime("%m%d%y_%H%M")
                output_file_name = f"bimodality_calibration_set_{timestamp}.csv"
                output_path = os.path.join(output_dir, output_file_name)

                # Run the classification function
                classify_rosediagrams_manually(input_dir, output_path)

                # Notify user
                messagebox.showinfo("Success", f"Calibration set saved to:\n{output_path}")

            def optimize_kde_bandwidth():
                """Runs the bandwidth optimization and handles saving."""
                calibration_folder = "bimodality_calibration"
                sgr_folder = "sgr"
                plot = plot_var.get()  # Get checkbox state (True/False)

                # Get the list of .csv files that start with "bimodality_calibration_set"
                matching_files = [
                    f for f in os.listdir(calibration_folder)
                    if f.startswith("bimodality_calibration_set") and f.endswith(".csv")
                ]

                if not matching_files:
                    messagebox.showerror("Error", "No bimodality calibration sets found in the folder.")
                    return

                optimal_bandwidth = optimize_bandwidth(calibration_folder, sgr_folder, plot)

                # Ask user if they want to save the result
                save_choice = messagebox.askyesno("Save value?", f"Optimal bandwidth: {optimal_bandwidth}\nDo you want to save this value?")
                if not save_choice:
                    return

                # File path to save the result
                file_path = os.path.join(calibration_folder, "optimal_bandwidth.csv")
                today_date = datetime.today().strftime("%Y-%m-%d")

                # Load existing data
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.DataFrame(columns=["Date", "Type", "Optimal bandwidth"])  # Create empty dataframe if file doesn't exist

                # Check if value already exists
                if optimal_bandwidth in df["Optimal bandwidth"].values:
                    df.loc[df["Optimal bandwidth"] == optimal_bandwidth, "Date"] = today_date
                else:
                    new_row = pd.DataFrame({"Date": [today_date], "Type": ["user-defined"], "Optimal bandwidth": [optimal_bandwidth]})
                    df = pd.concat([df, new_row], ignore_index=True)

                # Save updated file
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Saved", f"Optimal bandwidth saved to {file_path}")


            # Buttons for options
            tk.Button(cal_win, text="Make a Calibration Set", command=make_calibration_set).pack(pady=5)

            tk.Button(cal_win, text="Optimize KDE Bandwidth", command=optimize_kde_bandwidth).pack(pady=5)
            # Checkbox for plot option
            plot_var = tk.BooleanVar(value=False)  # Default is False
            plot_checkbox = tk.Checkbutton(cal_win, text="Plot bandwidth results", variable=plot_var)
            plot_checkbox.pack()

        
        def open_make_new_control_set_window():
            """Opens a GUI for user input and starts the control set creation process."""

            def load_calibrated_bandwidths():
                """Loads 'Optimal bandwidth' values from CSV into the dropdown menu."""
                try:
                    df = pd.read_csv("bimodality_calibration/optimal_bandwidth.csv")
                    return df["Optimal bandwidth"].dropna().unique().tolist()
                except (FileNotFoundError, KeyError):
                    messagebox.showerror("Error", "Could not load 'Optimal bandwidth' values.")
                    return []

            def get_selected_bandwidth():
                """Retrieves and validates the selected or entered bandwidth."""
                if use_custom_var.get():  # Custom input selected
                    bw = custom_bw_entry.get()
                    try:
                        return int(bw)
                    except ValueError:
                        status_label.config(text="Bandwidth must be an integer.")
                        return None
                else:  # Dropdown selection used
                    bw = float(dropdown_var.get())
                    try:
                        return int(bw)
                    except ValueError:
                        status_label.config(text="Invalid selection from dropdown.")
                        return None
            
            def run_generate_replicates(input_dir, output_dir, num_replicates=100):
                """Generates replicates for all .csv files in input_dir and saves them to output_dir."""
                os.makedirs(output_dir, exist_ok=True)

                for file in os.listdir(input_dir):
                    if file.endswith(".csv"):
                        file_path = os.path.join(input_dir, file)
                        output_subdir = os.path.join(output_dir, os.path.splitext(file)[0])
                        os.makedirs(output_subdir, exist_ok=True)
                        
                        generate_replicates([file_path, output_subdir, num_replicates])

            def make_new_control_set():
                """Generates a new control set and checks bimodality."""
                bw = get_selected_bandwidth()

                if bw is None:
                    return  # Stop execution if bandwidth is invalid
        
                # Confirm operation
                warning = messagebox.askokcancel("Warning", "This may take a long time.")
                if not warning:
                    return

                input_dir = "my_controls/Points"
                output_dir = "my_bimodality_tests/Controls"

                csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]

                # Check if input_dir is empty
                if not csv_files:  # If the directory is empty
                    messagebox.showerror("Error", "my_controls/Points is empty. Upload control images and generate sample points.")
                    return  # Stop execution


                # Run the generate replicates function
                run_generate_replicates(input_dir, output_dir)

                # Check bimodality across replicates using user-defined bandwidth
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    if os.path.isdir(file_path):  
                        result_file = os.path.join(file_path, f"{os.path.basename(file)}_bimodality_results.csv")
                        check_bimodality_across_replicates([file_path, bw, result_file])

                # Collect and merge all bimodality_results.csv files
                today_date = datetime.now().strftime("%m%d%y")
                output_file_name = f"user_controls_{today_date}.csv"
                output_dir = "control_files"
                os.makedirs(output_dir, exist_ok=True)

                all_results = []
                for root, _, files in os.walk("my_bimodality_tests/Controls"):
                    for file in files:
                        if file.endswith("bimodality_results.csv"):
                            df = pd.read_csv(os.path.join(root, file))
                            all_results.append(df)

                if all_results:
                    combined_df = pd.concat(all_results, ignore_index=True)
                    combined_df.to_csv(os.path.join(output_dir, output_file_name), index=False)
                    messagebox.showinfo("Success", "New control set has been created and saved.")
                else:
                    messagebox.showerror("Error", "Control set could not be saved.")

            # Create GUI for user input
            make_new_control_set_window = tk.Toplevel(bimodality_window)
            make_new_control_set_window.title("Make New Control Set")

            tk.Label(make_new_control_set_window, text="Select bandwidth for bimodality test:").pack(pady=5)

            # Option 1: Custom input field
            use_custom_var = tk.BooleanVar(value=True)  # Default to custom input
            custom_radio = tk.Radiobutton(make_new_control_set_window, text="Enter Custom Bandwidth:", variable=use_custom_var, value=True)
            custom_radio.pack()

            custom_bw_entry = tk.Entry(make_new_control_set_window)
            custom_bw_entry.insert(0, "8")  # Default value
            custom_bw_entry.pack()

            # Option 2: Dropdown menu
            dropdown_radio = tk.Radiobutton(make_new_control_set_window, text="Select Bandwidth from Calibrations:", variable=use_custom_var, value=False)
            dropdown_radio.pack()

            dropdown_var = tk.StringVar(value="")
            dropdown_menu = tk.OptionMenu(make_new_control_set_window, dropdown_var, *load_calibrated_bandwidths())
            dropdown_menu.pack()

            # Status label
            status_label = tk.Label(make_new_control_set_window, text="", fg="red")
            status_label.pack()

            tk.Button(make_new_control_set_window, text="Run", command=make_new_control_set).pack(pady=10)

            make_new_control_set_window.mainloop()




        # Create main bimodality test window
        bimodality_window = tk.Toplevel()
        bimodality_window.title("Bimodality Test")

        # Menu options
        generate_button = tk.Button(bimodality_window, text="Generate Replicates", command=open_generate_replicates_window)
        generate_button.pack()

        apply_button = tk.Button(bimodality_window, text="Apply Bimodality Test", command=open_apply_bimodality_test_window)  # Functionality to be added
        apply_button.pack()

        significance_button = tk.Button(bimodality_window, text="Statistical Significance", command=open_statistical_significance_window)  # Functionality to be added
        significance_button.pack()

        calibrate_button = tk.Button(bimodality_window, text="Calibrate Bimodality Test", command=open_calibrate_bimodality_window)  # Functionality to be added
        calibrate_button.pack()

        control_set_button = tk.Button(bimodality_window, text="Make New Control Set", command=open_make_new_control_set_window)
        control_set_button.pack()




    # --- Main Menu Buttons ---
    tk.Button(root, text="Upload Image", command=show_upload_window, width=20).pack(pady=5)
    tk.Button(root, text="Generate Points", command=show_generate_points_window, width=20).pack(pady=5)
    tk.Button(root, text="Bimodality Test", command=show_bimodality_test_window, width=20).pack(pady=5)

    root.mainloop()
