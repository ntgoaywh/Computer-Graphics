import tkinter as tk
import numpy as np
import math

class Scene3DRenderer:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Scene Renderer")
        
        # Canvas setup
        self.width = 800
        self.height = 600
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='black')
        self.canvas.pack()
        
        # Create image buffer
        self.buffer = np.zeros((self.height, self.width, 3), dtype=np.float64)
        self.z_buffer = np.full((self.height, self.width), float('inf'))
        
        # Scene parameters
        self.camera = np.array([0, 2, -6])
        self.light_pos = np.array([5, 5, -5])
        self.light_color = np.array([1, 1, 1])
        self.ambient = 0.1
        
        # Initialize scene objects
        self.init_scene()
        
        # Render button
        tk.Button(root, text="Render Scene", command=self.render_scene).pack()
        
    def init_scene(self):
        # Define scene objects
        self.sphere = {
            'center': np.array([0, 0, 0]),
            'radius': 1.0,
            'color': np.array([0.7, 0.3, 0.3]),
            'specular': 50,
            'reflectivity': 0.3
        }
        
        self.floor = {
            'y': -1,
            'color': np.array([0.5, 0.5, 0.5]),
            'specular': 10,
            'reflectivity': 0.1
        }
        
        # Checkerboard texture for floor
        self.checker_size = 1.0
        
    def normalize(self, vector):
        return vector / np.linalg.norm(vector)
    
    def reflect(self, vector, normal):
        return vector - 2 * np.dot(vector, normal) * normal
    
    def sphere_intersect(self, origin, direction):
        b = 2 * np.dot(direction, origin - self.sphere['center'])
        c = np.linalg.norm(origin - self.sphere['center'])**2 - self.sphere['radius']**2
        delta = b**2 - 4*c
        
        if delta < 0:
            return None
            
        t1 = (-b - np.sqrt(delta)) / 2
        t2 = (-b + np.sqrt(delta)) / 2
        
        if t1 < 0 and t2 < 0:
            return None
            
        return min(t for t in [t1, t2] if t > 0)
    
    def floor_intersect(self, origin, direction):
        if abs(direction[1]) < 1e-6:
            return None
            
        t = -(origin[1] - self.floor['y']) / direction[1]
        return t if t > 0 else None
    
    def get_floor_color(self, point):
        # Checkerboard pattern
        x = math.floor(point[0] / self.checker_size)
        z = math.floor(point[2] / self.checker_size)
        if (x + z) % 2 == 0:
            return self.floor['color']
        return self.floor['color'] * 0.5
    
    def compute_lighting(self, point, normal, view_dir, specular, color):
        # Ambient light
        intensity = self.ambient
        
        # Direction to light
        light_dir = self.normalize(self.light_pos - point)
        
        # Diffuse lighting
        diffuse = max(np.dot(normal, light_dir), 0)
        intensity += diffuse
        
        # Specular lighting
        if specular > 0:
            reflect_dir = self.reflect(-light_dir, normal)
            spec = max(np.dot(reflect_dir, view_dir), 0) ** specular
            intensity += 0.5 * spec
        
        return np.clip(color * intensity, 0, 1)
    
    def trace_ray(self, origin, direction, depth=3):
        if depth <= 0:
            return np.zeros(3)
            
        # Check sphere intersection
        t_sphere = self.sphere_intersect(origin, direction)
        
        # Check floor intersection
        t_floor = self.floor_intersect(origin, direction)
        
        # Find closest intersection
        if t_sphere is None and t_floor is None:
            return np.zeros(3)
            
        if t_sphere is None:
            t = t_floor
            hit_point = origin + direction * t
            normal = np.array([0, 1, 0])
            color = self.get_floor_color(hit_point)
            specular = self.floor['specular']
            reflectivity = self.floor['reflectivity']
        elif t_floor is None:
            t = t_sphere
            hit_point = origin + direction * t
            normal = self.normalize(hit_point - self.sphere['center'])
            color = self.sphere['color']
            specular = self.sphere['specular']
            reflectivity = self.sphere['reflectivity']
        else:
            t = min(t_sphere, t_floor)
            if t == t_sphere:
                hit_point = origin + direction * t
                normal = self.normalize(hit_point - self.sphere['center'])
                color = self.sphere['color']
                specular = self.sphere['specular']
                reflectivity = self.sphere['reflectivity']
            else:
                hit_point = origin + direction * t
                normal = np.array([0, 1, 0])
                color = self.get_floor_color(hit_point)
                specular = self.floor['specular']
                reflectivity = self.floor['reflectivity']
        
        # Compute lighting
        view_dir = self.normalize(-direction)
        color = self.compute_lighting(hit_point, normal, view_dir, specular, color)
        
        # Compute reflection
        if reflectivity > 0:
            reflect_dir = self.reflect(direction, normal)
            reflect_origin = hit_point + normal * 1e-4  # Offset to avoid self-intersection
            reflect_color = self.trace_ray(reflect_origin, reflect_dir, depth-1)
            color = color * (1 - reflectivity) + reflect_color * reflectivity
        
        return color
    
    def render_scene(self):
        aspect_ratio = self.width / self.height
        fov = math.pi / 3  # 60 degrees
        
        for y in range(self.height):
            for x in range(self.width):
                # Calculate ray direction
                screen_x = (2 * (x + 0.5) / self.width - 1) * math.tan(fov/2) * aspect_ratio
                screen_y = (1 - 2 * (y + 0.5) / self.height) * math.tan(fov/2)
                direction = self.normalize(np.array([screen_x, screen_y, 1]))
                
                # Trace ray and store color in buffer
                color = self.trace_ray(self.camera, direction)
                self.buffer[y, x] = np.clip(color * 255, 0, 255)
        
        # Display the rendered image
        self.display_buffer()
    
    def display_buffer(self):
        # Convert buffer to hex colors and display on canvas
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = self.buffer[y, x].astype(np.int32)
                color = f'#{r:02x}{g:02x}{b:02x}'
                self.canvas.create_rectangle(x, y, x+1, y+1, fill=color, outline=color)

def main():
    root = tk.Tk()
    app = Scene3DRenderer(root)
    root.mainloop()

if __name__ == "__main__":
    main()