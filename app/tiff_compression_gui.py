import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from tiff_compression import TiffCompressorManager
from compression_check import check_compression


class TiffCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TIFF Compressor")
        self.root.geometry("600x500")

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # File/Folder Selection
        ttk.Label(main_frame, text="Select File or Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Select File", command=self.select_file).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Select Folder", command=self.select_folder).grid(row=0, column=1, padx=5)

        # Compression options
        ttk.Label(main_frame, text="Compression Method:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.compression_var = tk.StringVar(value="zip")
        compression_frame = ttk.Frame(main_frame)
        compression_frame.grid(row=4, column=0, sticky=tk.W, pady=5)

        ttk.Radiobutton(compression_frame, text="ZIP", value="zip",
                        variable=self.compression_var).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(compression_frame, text="LZW", value="lzw",
                        variable=self.compression_var).grid(row=0, column=1, padx=5)

        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=5, column=0,
                                                                   columnspan=2, sticky=tk.W, pady=10)
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Compress button
        ttk.Button(main_frame, text="Compress", command=self.compress).grid(row=7, column=0,
                                                                            columnspan=2, pady=10)

        # Results text area
        self.results_text = tk.Text(main_frame, height=10, width=50)
        self.results_text.grid(row=8, column=0, columnspan=2, pady=5)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("TIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if filename:
            self.path_var.set(filename)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def compress(self):
        path = self.path_var.get()
        if not path:
            messagebox.showerror("Error", "Please select a file or folder first")
            return

        self.results_text.delete(1.0, tk.END)
        self.progress_var.set("Processing...")
        self.progress_bar['value'] = 0
        self.root.update()

        try:
            if os.path.isfile(path):
                self.compress_single_file(path)
            else:
                self.compress_folder(path)

            self.progress_var.set("Compression completed!")
            self.progress_bar['value'] = 100
            messagebox.showinfo("Success", "Compression completed successfully!")

        except Exception as e:
            self.progress_var.set("Error occurred!")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        self.root.update()

    def manage_files(self, original_path: str, compressed_path: str, compression_successful: bool):
        """Manage files after compression based on success status."""
        try:
            if compression_successful:
                # If compression was successful, delete the original
                os.remove(original_path)
                self.add_result(f"Original file deleted: {os.path.basename(original_path)}\n")
                return compressed_path
            else:
                # If compression failed, delete the compressed version and keep original
                os.remove(compressed_path)
                self.add_result(f"Compressed file deleted: {os.path.basename(compressed_path)}\n")
                return original_path
        except Exception as e:
            self.add_result(f"Error managing files: {str(e)}\n")
            return original_path

    def compress_single_file(self, file_path):
        self.progress_bar['value'] = 33
        self.root.update()

        compressed_path = TiffCompressorManager.compress_file(
            file_path,
            compression_type=self.compression_var.get()
        )

        self.progress_bar['value'] = 66
        self.root.update()

        success = check_compression(file_path, compressed_path)

        self.add_result(f"File: {os.path.basename(file_path)}\n")
        self.add_result(f"Compressed to: {os.path.basename(compressed_path)}\n")
        self.add_result(f"Verification: {'Success' if success else 'Failed'}\n")

        # Manage files based on compression success
        kept_file = self.manage_files(file_path, compressed_path, success)
        self.add_result(f"Kept file: {os.path.basename(kept_file)}\n")
        self.add_result("-" * 50 + "\n")

    def compress_folder(self, folder_path):
        tiff_files = [f for f in Path(folder_path).glob("**/*.tif*")]
        total_files = len(tiff_files)

        if total_files == 0:
            self.add_result("No TIFF files found in the selected folder.\n")
            return

        for i, file_path in enumerate(tiff_files, 1):
            self.progress_bar['value'] = (i / total_files) * 100
            self.progress_var.set(f"Processing file {i} of {total_files}")
            self.root.update()

            self.compress_single_file(str(file_path))

    def add_result(self, text):
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = TiffCompressorGUI(root)
    root.mainloop()
