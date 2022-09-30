import moderngl_window as mglw
from moderngl_window import geometry
import moderngl
import numpy as np

import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer


class App(mglw.WindowConfig):
    window_size = (1600, 900)
    resource_dir = "DiffusionReaction"
    gl_version = (4, 3)
    vsync = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()

        self.f = 0.05
        self.k = 0.06

        self.imgui = ModernglWindowRenderer(self.wnd)

        self.updateSpeed = 1/2000
        self.last_time = 0.0

        self.width, self.height = 1600, 900

        R = np.ones((self.height, self.width))
        #G = np.eye(self.width, self.height, 4)
        G = np.zeros((self.height, self.width))


        """ G[200:300, 1200:1300] = 1
        G[200:300, 300:400] = 1
        G[600:700, 300:400] = 1 """
        G[100:800:15, 100:1500] = 1

        """ G[200:300, 300:1300] = 1
        G[200:700, 300:400] = 1
        G[600:700, 300:1300] = 1
        G[200:700, 1200:1300] = 1 """
        


        pixels = np.stack([R, G, np.zeros((self.height, self.width))], axis=2).astype('f4')

        self.display_program = self.load_program(vertex_shader='vertex_shader.glsl', fragment_shader='fragment_shader.glsl')

        self.transformer_program = self.load_program(vertex_shader='diffusion.glsl', varyings=['outVert'])
        self.texture_transformer = self.ctx.vertex_array(self.transformer_program, [])


        



        self.display_buffer = self.ctx.buffer(np.array([
            # x    y     u  v
            -1.0, -1.0,  0.0, 0.0,  # lower left
            -1.0,  1.0,  0.0, 1.0,  # upper left
            1.0,   1.0,  1.0, 1.0, # upper right
            1.0,  -1.0,  1.0, 0.0,  # lower right
              
        ], dtype="f4"))


        self.render_array = self.ctx.vertex_array(self.display_program, [(self.display_buffer, '2f 2f', 'in_vert', 'in_texcoord')])
        
        
        self.texture = self.ctx.texture((self.width, self.height), components=3, data=pixels.tobytes(), dtype='f4')
        self.texture.filter = moderngl.NEAREST, moderngl.NEAREST
        self.texture_buffer = self.ctx.buffer(reserve=pixels.nbytes)

    def restart_sim(self):
        R = np.ones((self.height, self.width))
        G = np.zeros((self.height, self.width))
        G[100:800:15, 100:1500] = 1
        pixels = np.stack([R, G, np.zeros((self.height, self.width))], axis=2).astype('f4')

        self.texture_buffer = self.ctx.buffer(data=pixels)
        self.texture = self.ctx.texture((self.width, self.height), components=3, data=pixels.tobytes(), dtype='f4')


    def update_uniforms(self):
        self.set_uniform('k', self.k)
        self.set_uniform('f', self.f)

    def set_uniform(self, u_name, u_value):
        try:
            self.transformer_program[u_name] = u_value
        except:
            print(f'uniform: {u_name} - not used in shader')

    def render(self, time: float, frame_time: float):
        self.ctx.clear()
        self.texture.use(location=0)
        if time - self.last_time > self.updateSpeed:
            self.texture_transformer.transform(self.texture_buffer, vertices=self.width * self.height)
            self.texture.write(self.texture_buffer)

            self.last_time = time


        self.render_array.render(moderngl.TRIANGLE_FAN)
        self.render_ui()

    
    def render_ui(self):
        imgui.new_frame()

        if imgui.begin("Settings"):
            imgui.push_item_width(imgui.get_window_width()*0.25)

            changed = False
            c, self.f = imgui.slider_float(
                "Feeding Rate", self.f, 0.01, 0.1
            )
            changed = changed or c
            c, self.k = imgui.slider_float(
                "Kill Rate", self.k, 0.01, 0.1
            )
            changed = changed or c
            if changed:
                self.update_uniforms()
            
            if imgui.button("Restart Simulation"):
                self.restart_sim()
            
            imgui.pop_item_width()



        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    
    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)


if __name__=='__main__':
    mglw.run_window_config(App)