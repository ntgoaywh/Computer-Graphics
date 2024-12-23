import tkinter as tk
import numpy as np

class CurveGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("曲线生成器")
        
        # 创建控制面板
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP)
        
        # 创建按钮
        tk.Button(self.control_frame, text="B样条曲线", command=lambda: self.set_mode("bspline")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="Bezier曲线", command=lambda: self.set_mode("bezier")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="清除", command=self.clear_canvas).pack(side=tk.LEFT)
        
        # 状态标签
        self.status_label = tk.Label(self.control_frame, text="当前模式：B样条曲线")
        self.status_label.pack(side=tk.LEFT)
        
        # 创建画布
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()
        
        # 初始化变量
        self.mode = "bspline"  # 默认模式
        self.control_points = []
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Double-Button-1>", self.generate_curve)
        
    def set_mode(self, mode):
        self.mode = mode
        self.status_label.config(text=f"当前模式：{'B样条曲线' if mode=='bspline' else 'Bezier曲线'}")
        
    def clear_canvas(self):
        self.canvas.delete("all")
        self.control_points = []
        
    def add_point(self, event):
        # 添加控制点
        x, y = event.x, event.y
        self.control_points.append((x, y))
        
        # 绘制控制点
        self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="red")
        
        # 绘制控制多边形
        if len(self.control_points) > 1:
            p1 = self.control_points[-2]
            p2 = self.control_points[-1]
            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], dash=(4,4))
            
    def generate_curve(self, event):
        if len(self.control_points) < 3:
            return
            
        if self.mode == "bspline":
            self.draw_bspline()
        else:
            self.draw_bezier()
            
    def draw_bspline(self):
        points = np.array(self.control_points)
        n = len(points) - 1
        
        # 生成均匀二次B样条的节点
        t = np.linspace(0, 1, 100)
        
        # 绘制曲线
        curve_points = []
        for i in range(n-1):
            if i + 2 <= n:
                # 计算二次B样条基函数
                for tj in t:
                    x = (1-tj)**2/2 * points[i][0] + \
                        (1/2 + tj - tj**2) * points[i+1][0] + \
                        tj**2/2 * points[i+2][0]
                    
                    y = (1-tj)**2/2 * points[i][1] + \
                        (1/2 + tj - tj**2) * points[i+1][1] + \
                        tj**2/2 * points[i+2][1]
                    
                    curve_points.append((x, y))
        
        # 绘制曲线段
        for i in range(len(curve_points)-1):
            self.canvas.create_line(curve_points[i][0], curve_points[i][1],
                                  curve_points[i+1][0], curve_points[i+1][1],
                                  fill="blue", width=2)
            
    def draw_bezier(self):
        points = np.array(self.control_points)
        n = len(points) - 1
        
        # 生成Bezier曲线点
        curve_points = []
        for t in np.linspace(0, 1, 100):
            x = 0
            y = 0
            for i in range(n + 1):
                # 计算伯恩斯坦基函数
                coef = self.bernstein(i, n, t)
                x += coef * points[i][0]
                y += coef * points[i][1]
            curve_points.append((x, y))
        
        # 绘制曲线段
        for i in range(len(curve_points)-1):
            self.canvas.create_line(curve_points[i][0], curve_points[i][1],
                                  curve_points[i+1][0], curve_points[i+1][1],
                                  fill="green", width=2)
    
    def bernstein(self, i, n, t):
        # 计算组合数
        def comb(n, k):
            if k < 0 or k > n:
                return 0
            if k == 0 or k == n:
                return 1
            k = min(k, n-k)
            c = 1
            for j in range(k):
                c = c * (n - j) // (j + 1)
            return c
            
        return comb(n, i) * (t**i) * ((1-t)**(n-i))

def main():
    root = tk.Tk()
    app = CurveGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()