import tkinter as tk
import numpy as np
import math

class FractalGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal Generator")
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(side=tk.BOTTOM)
        
        # Control panel
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP)
        
        # Koch curve controls
        tk.Button(self.control_frame, text="Koch Curve", command=self.draw_koch).pack(side=tk.LEFT)
        self.koch_depth = tk.Scale(self.control_frame, from_=1, to=6, orient=tk.HORIZONTAL, label="Koch Depth")
        self.koch_depth.pack(side=tk.LEFT)
        self.koch_depth.set(4)
        
        # Fern controls
        tk.Button(self.control_frame, text="Fern", command=self.draw_fern).pack(side=tk.LEFT)
        self.fern_iterations = tk.Scale(self.control_frame, from_=10000, to=100000, 
                                      orient=tk.HORIZONTAL, label="Fern Points")
        self.fern_iterations.pack(side=tk.LEFT)
        self.fern_iterations.set(50000)
        
        # Clear button
        tk.Button(self.control_frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT)
        
    def clear_canvas(self):
        self.canvas.delete("all")
        
    def draw_line(self, x1, y1, x2, y2, color="black"):
        self.canvas.create_line(x1, y1, x2, y2, fill=color)
        
    def koch_curve_points(self, start, end, depth):
        if depth == 0:
            return [start, end]
            
        # Calculate required points
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        p1 = start
        p2 = (start[0] + dx/3, start[1] + dy/3)
        
        # Calculate the position of the peak point
        angle = math.pi/3  # 60 degrees
        p3x = p2[0] + (dx/3)*math.cos(angle) - (dy/3)*math.sin(angle)
        p3y = p2[1] + (dx/3)*math.sin(angle) + (dy/3)*math.cos(angle)
        p3 = (p3x, p3y)
        
        p4 = (start[0] + 2*dx/3, start[1] + 2*dy/3)
        p5 = end
        
        # Recursive calls
        curve1 = self.koch_curve_points(p1, p2, depth-1)
        curve2 = self.koch_curve_points(p2, p3, depth-1)
        curve3 = self.koch_curve_points(p3, p4, depth-1)
        curve4 = self.koch_curve_points(p4, p5, depth-1)
        
        # Combine all points (removing duplicates at joints)
        return curve1[:-1] + curve2[:-1] + curve3[:-1] + curve4
        
    def draw_koch(self):
        self.clear_canvas()
        depth = self.koch_depth.get()
        
        # Set up initial line (centered horizontally, in lower third of canvas)
        start_x = 100
        end_x = 700
        y = 400
        
        points = self.koch_curve_points((start_x, y), (end_x, y), depth)
        
        # Draw the curve
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            self.draw_line(x1, y1, x2, y2, "blue")
            
    def draw_fern(self):
        self.clear_canvas()
        iterations = self.fern_iterations.get()
        
        # Transformation matrices and probabilities
        p = np.array([0.85, 0.07, 0.07, 0.01])  # Probabilities
        
        # Starting point
        x, y = 0, 0
        
        # Scale and translate coordinates to fit canvas
        def transform_coords(x, y):
            return (400 + x*70, 550 - y*70)
        
        # Draw points
        for _ in range(iterations):
            r = np.random.random()
            if r < p[0]:
                # Stem
                x_new = 0.85*x + 0.04*y
                y_new = -0.04*x + 0.85*y + 1.6
            elif r < p[0] + p[1]:
                # Left leaflet
                x_new = 0.2*x - 0.26*y
                y_new = 0.23*x + 0.22*y + 1.6
            elif r < p[0] + p[1] + p[2]:
                # Right leaflet
                x_new = -0.15*x + 0.28*y
                y_new = 0.26*x + 0.24*y + 0.44
            else:
                # Successive stems
                x_new = 0
                y_new = 0.16*y
                
            x, y = x_new, y_new
            
            # Transform and plot point
            plot_x, plot_y = transform_coords(x, y)
            self.canvas.create_rectangle(plot_x, plot_y, plot_x+1, plot_y+1, 
                                       fill="dark green", outline="dark green")

def main():
    root = tk.Tk()
    app = FractalGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()