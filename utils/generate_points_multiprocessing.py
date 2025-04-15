from utils.generate_points import generate_points
import multiprocessing as mp
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from utils.plot_line_segment import *
import os

def generate_points_multiprocessing(args):
    # This function generates randomly sampled points from an image,
    # approximates the flow direction, and saves the sampled points.
    
    # Unpack arguments
    image_path, file_path, K, plot = args
    num_workers = 8

    # Split the total points K across available workers
    K_per_worker = K // num_workers
    remainder = K % num_workers  # Handle cases where K is not evenly divisible

    # Create argument list for multiprocessing
    args_list = [[image_path, file_path, K_per_worker + (1 if i < remainder else 0), plot] for i in range(num_workers)]

    with mp.Pool(num_workers) as pool:
        results = pool.map(generate_points, args_list)  # Use map with lists

    # Combine results into one DataFrame
    final_df = pd.concat(results, ignore_index=True)

    # Save final DataFrame once
    final_df.to_csv(file_path, index=False)

    # Plotting
    if plot:
        image_name = os.path.basename(image_path)

        tg = Image.open(image_path)

        w, h = tg.size

        # Convert image to binary
        tg_binary = tg.convert('L')
        tg_binary = np.array(tg_binary)
        tg_binary[tg_binary < 128] = 0
        tg_binary[tg_binary >= 128] = 1

        slopes = final_df['average slope']
        pixels = final_df['pixel']
    
        colors = plt.cm.rainbow(np.linspace(0, 1, len(pixels)))
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(tg_binary, cmap=plt.cm.gray)
        ax.set_xlabel("y")
        ax.set_ylabel("x")

        for i, pix in enumerate(pixels):
            if np.abs(slopes[i]) < 1e5:
                x_line, y_line = plot_line_segment(pix, slopes[i], 5)
                ax.plot(x_line, y_line, color='b', linewidth=1.0)
        plt.tight_layout()
        plt.title(f"{image_name}")
        plt.show()


    
