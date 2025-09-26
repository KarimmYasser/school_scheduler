"""
Quick test for the algorithm selection dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox

def test_dialog():
    root = tk.Tk()
    root.title("Dialog Test")
    root.geometry("400x200")
    
    def show_algorithm_dialog():
        # Create algorithm selection dialog
        dialog = tk.Toplevel(root)
        dialog.title("Select Scheduling Algorithm")
        dialog.geometry("600x650")  # Increased size
        dialog.resizable(False, False)
        dialog.grab_set()  # Make dialog modal
        
        # Center dialog on parent
        dialog.transient(root)
        root.update_idletasks()
        x = (root.winfo_x() + (root.winfo_width() // 2)) - 300
        y = (root.winfo_y() + (root.winfo_height() // 2)) - 325
        dialog.geometry(f"600x650+{x}+{y}")
        
        ttk.Label(dialog, text="Choose Scheduling Algorithm", 
                 font=('Helvetica', 14, 'bold')).pack(pady=20)
        
        # Algorithm selection
        algorithm_var = tk.StringVar(value="ultra_fast")
        
        algorithms = [
            ("ultra_fast", "⚡ Ultra-Fast (Recommended)", "Optimized ultra-fast algorithm\n• Typical time: < 0.5 seconds\n• Quality: Very Good\n• Best for: Instant scheduling"),
            ("smart_greedy", "🚀 Smart Greedy", "Intelligent greedy with heuristics\n• Typical time: < 1 second\n• Quality: Excellent\n• Best for: Fast + high quality"),
            ("ml_inspired", "🧠 ML-Inspired Scheduler", "Pattern-learning algorithm\n• Typical time: 1-3 seconds\n• Quality: Excellent\n• Best for: Learning from data")
        ]
        
        # Create scrollable frame for algorithms
        canvas_frame = ttk.Frame(dialog)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(canvas_frame, height=350, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create radio buttons with descriptions
        for i, (value, title, description) in enumerate(algorithms):
            algo_frame = ttk.LabelFrame(scrollable_frame, text="", padding=10)
            algo_frame.pack(fill=tk.X, padx=5, pady=8)
            
            # Radio button with larger font
            radio_btn = ttk.Radiobutton(algo_frame, text=title, variable=algorithm_var, 
                                       value=value)
            radio_btn.pack(anchor=tk.W)
            
            # Description with better formatting  
            desc_lines = description.split('\n')
            for line in desc_lines:
                if line.strip():
                    desc_label = ttk.Label(algo_frame, text=line, font=('Helvetica', 9), 
                                         foreground='#666666')
                    desc_label.pack(anchor=tk.W, padx=20, pady=1)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Separator line
        separator = ttk.Separator(dialog, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=15)
        
        # Buttons frame - make it more prominent
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def run_selected_algorithm():
            algorithm = algorithm_var.get()
            dialog.destroy()
            messagebox.showinfo("Selected", f"You selected: {algorithm}")
        
        # Larger, More prominent buttons
        generate_btn = ttk.Button(btn_frame, text="🚀 Generate Schedule", 
                                 command=run_selected_algorithm)
        generate_btn.pack(side=tk.LEFT, padx=15, pady=10)
        generate_btn.configure(width=20)  # Make button wider
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Cancel", 
                               command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=15, pady=10)
        cancel_btn.configure(width=15)  # Make button wider
        
        # Add keyboard shortcuts
        dialog.bind('<Return>', lambda e: run_selected_algorithm())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Focus on the dialog
        dialog.focus_set()
    
    # Main window
    ttk.Label(root, text="Algorithm Dialog Test", font=('Helvetica', 16, 'bold')).pack(pady=50)
    
    test_btn = ttk.Button(root, text="Show Algorithm Selection Dialog", 
                         command=show_algorithm_dialog)
    test_btn.pack(pady=20)
    test_btn.configure(width=30)
    
    root.mainloop()

if __name__ == "__main__":
    test_dialog()