import tkinter as tk
import numpy as np
from scipy.special import comb  # 确保正确导入 comb

class CurveDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("B-spline & Bezier Curve Generator")
        
        # 创建画布
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(side=tk.BOTTOM)
        
        # 控制按钮
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP)
        
        tk.Button(self.control_frame, text="B样条", command=lambda: self.set_mode("bspline")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="Bezier (Bernstein)", command=lambda: self.set_mode("bezier")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="Bezier (Casteljau)", command=lambda: self.set_mode("casteljau")).pack(side=tk.LEFT)  # 新按钮
        tk.Button(self.control_frame, text="Clear",command=self.clear_canvas).pack(side=tk.LEFT)
        
        # 初始化变量
        self.mode = "bspline"
        self.control_points = []
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
    def set_mode(self, mode):
        self.mode = mode
        self.clear_canvas()
        
    def clear_canvas(self):
        self.canvas.delete("all")
        self.control_points = []
        
    def draw_point(self, x, y, color="black"):
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill=color)
        
    def draw_control_polygon(self):
        if len(self.control_points) > 1:
            for i in range(len(self.control_points)-1):
                x1, y1 = self.control_points[i]
                x2, y2 = self.control_points[i+1]
                self.canvas.create_line(x1, y1, x2, y2, dash=(2,2))
                
    def uniform_bspline(self):
        if len(self.control_points) < 3:
            return
            
        def N(t, i):
            if t[i] <= t_param < t[i+1]:
                return 1
            return 0
            
        def N2(t, i):
            d1 = t[i+2] - t[i]
            d2 = t[i+1] - t[i]
            
            n1 = 0 if d2 == 0 else ((t_param - t[i]) / d2) * N1(t, i)
            n2 = 0 if d1 == 0 else ((t[i+2] - t_param) / (t[i+2] - t[i+1])) * N1(t, i+1)
            
            return n1 + n2
            
        def N1(t, i):
            d1 = t[i+1] - t[i]
            d2 = t[i+2] - t[i+1]
            
            n1 = 0 if d1 == 0 else ((t_param - t[i]) / d1) * N(t, i)
            n2 = 0 if d2 == 0 else ((t[i+2] - t_param) / d2) * N(t, i+1)
            
            return n1 + n2
            
        n = len(self.control_points)
        knots = list(range(n+3))
        points = []
        
        for t_param in np.arange(2, n+1, 0.01):
            x = y = 0
            for i in range(n):
                basis = N2(knots, i)
                x += basis * self.control_points[i][0]
                y += basis * self.control_points[i][1]
            points.append((x, y))
            
        for i in range(len(points)-1):
            self.canvas.create_line(points[i][0], points[i][1], 
                                  points[i+1][0], points[i+1][1],
                                  fill='blue', width=2)
                
    def bezier_curve(self):
        if len(self.control_points) < 2:
            return
            
        def bernstein(i, n, t):
            return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
            
        points = []
        n = len(self.control_points) - 1
        
        for t in np.arange(0, 1.01, 0.01):
            x = y = 0
            for i in range(n + 1):
                basis = bernstein(i, n, t)
                x += basis * self.control_points[i][0]
                y += basis * self.control_points[i][1]
            points.append((x, y))
            
        for i in range(len(points)-1):
            self.canvas.create_line(points[i][0], points[i][1],
                                  points[i+1][0], points[i+1][1],
                                  fill='red', width=2)
    
    def casteljau_curve(self):
        if len(self.control_points) < 2:
            return
        
        def de_casteljau(points, t):
            """
            递归实现 de Casteljau 算法，并返回每一层的插值点。
            """
            layers = [points]
            while len(points) > 1:
                new_points = []
                for i in range(len(points)-1):
                    x = (1 - t) * points[i][0] + t * points[i+1][0]
                    y = (1 - t) * points[i][1] + t * points[i+1][1]
                    new_points.append((x, y))
                layers.append(new_points)
                points = new_points
            return layers
        
        points_on_curve = []
        for t in np.arange(0, 1.01, 0.01):
            layers = de_casteljau(self.control_points, t)
            final_point = layers[-1][0]
            points_on_curve.append(final_point)
            
            # 可视化每一层的插值点和线条
            for layer in layers[:-1]:  # 不绘制最后一层的单个点
                for i in range(len(layer)-1):
                    x1, y1 = layer[i]
                    x2, y2 = layer[i+1]
                    self.canvas.create_line(x1, y1, x2, y2, fill='lightgray', dash=(1,1))
                for point in layer:
                    self.canvas.create_oval(point[0]-2, point[1]-2, point[0]+2, point[1]+2, fill='orange', outline='')

        # 绘制贝塞尔曲线
        for i in range(len(points_on_curve)-1):
            self.canvas.create_line(points_on_curve[i][0], points_on_curve[i][1],
                                  points_on_curve[i+1][0], points_on_curve[i+1][1],
                                  fill='green', width=2)
        
    def on_click(self, event):
        self.control_points.append((event.x, event.y))
        self.draw_point(event.x, event.y)
        self.draw_control_polygon()
        
    def on_double_click(self, event):
        if self.mode == "bspline":
            self.uniform_bspline()
        elif self.mode == "bezier":
            self.bezier_curve()
        elif self.mode == "casteljau":
            self.casteljau_curve()

def main():
    root = tk.Tk()
    app = CurveDrawer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
