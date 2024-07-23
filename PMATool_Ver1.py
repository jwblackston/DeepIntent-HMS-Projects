# PMA Training Automation & Tool for AE/HMS
#Code from Walker in ticket: https://deepintent.atlassian.net/browse/DIA-7013
#Using VAXXED Audience Statistics File
#Ignacio Edits Ver 1, May 7th 2024
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re
# Assuming threshold_3x is a constant value defined elsewhere in your code
threshold_3x = 100  # Replace with the actual value
class App:
    def __init__(self, master):
        self.master = master
        master.title("Audience Stats Analyzer")
        self.label1 = tk.Label(master, text="Drop Audience Stats File Here:")
        self.label1.pack()
        self.drop_area = tk.Label(master, text="Drag and drop file here", relief="groove", width=50, height=5)
        self.drop_area.pack()
        self.drop_area.bind("<Button-1>", self.load_file)
        self.label2 = tk.Label(master, text="Enter Cohort Seed Size (40,000 - 30,000,000):")
        self.label2.pack()
        self.cohort_seed_size_entry = tk.Entry(master)
        self.cohort_seed_size_entry.pack()
        self.analyze_button = tk.Button(master, text="Analyze", command=self.analyze, height=2)
        self.analyze_button.pack()
    def load_file(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
        if file_path:
            self.drop_area.config(text=file_path)
            self.data = pd.read_csv(file_path)  # Assuming CSV file
            print("Column names:", self.data.columns)  # Print column names for debugging
    def validate_number(self, number_str):
        # Remove commas from the string
        number_str = number_str.replace(",", "")
        # Check if the string is a valid number and falls within the specified range
        if re.match(r"^\d+$", number_str):
            number = int(number_str)
            if 40000 <= number <= 30000000:
                return True
        return False
    def analyze(self):
        cohort_seed_size_str = self.cohort_seed_size_entry.get()
        if self.validate_number(cohort_seed_size_str):
            try:
                cohort_seed_size = int(cohort_seed_size_str.replace(",", ""))
                cohort_seed_size_result = cohort_seed_size * 5 / 2
                print(f"Calculated target audience stat size: {cohort_seed_size_result}")  # Debugging output
                closest_index = (self.data['AUDIENCE_SIZE'] - cohort_seed_size_result).abs().idxmin() # changed AUDIENCE_STAT_SIZE to AUDIENCE_SIZE (Ignacio)
                closest_row = self.data.loc[closest_index]
                print(f"Closest row data: {closest_row}")  # Debugging output
                score_threshold = closest_row['SCORE_THRESHOLD']
                audience_stat_size = closest_row['AUDIENCE_SIZE']# changed AUDIENCE_STAT_SIZE to AUDIENCE_SIZE (Ignacio)
                aq_score = closest_row['AQ_SCORE']
                model_power_index = closest_row['MODEL_POWER_INDEX']
                messagebox.showinfo("Results",
                                f"SCORE_THRESHOLD: {score_threshold}\nAUDIENCE_STAT_SIZE: {audience_stat_size}\nAQ_SCORE: {aq_score}\nTHRESHOLD_3X: {threshold_3x}\nMODEL_POWER_INDEX: {model_power_index}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process data: {str(e)}")
        else:
            messagebox.showerror("Error", "Invalid cohort seed size. Please enter a number between 40,000 and 30,000,000.")

root = tk.Tk()
app = App(root)
root.mainloop()
