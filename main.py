import pygame
from scene import Scene
from lightSource import LightSource
from blender import load_obj_file
from BaseModel import DrawModelFromMesh
from shaders import *
from ShadowMapping import *
from sphereModel import Sphere
from skyBox import *
from environmentMapping import *

class CityScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        self.light = LightSource(self, position=[-4, 4, 4])

        self.shaders='phong'

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        # Load the scene model to be drawn.
        meshes = load_obj_file('models/scene.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,0,0]),scaleMatrix([0.1,0.1,0.1])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]
        )
        
        # Load the dinosaur model to be drawn.
        rex = load_obj_file('models/final_rex.obj')
        self.rex = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,0.7,0]), scaleMatrix([0.05,0.05,0.05])), mesh=mesh, shader=self.shaders, name='rex') for mesh in rex]

        self.skybox = SkyBox(scene=self)

        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.2), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())

        self.environment = EnvironmentMappingTexture(width=400, height=400)

        self.sphere = DrawModelFromMesh(scene=self, M=poseMatrix(), mesh=Sphere(), shader=EnvironmentShader(map=self.environment))

        # Load the helipcopter model to be drawn.
        chopper = load_obj_file('models/chopper.obj')
        self.chopper = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,3,1]), scaleMatrix([1,1,1])), mesh=mesh, shader=EnvironmentShader(map=self.environment)) for mesh in chopper]

    def draw_shadow_map(self):
        '''
        Draw the shadows in the scene.
        '''
        # Clear the scene and the depth buffer to handle occlusions.
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for model in self.models:
            model.draw()
 
        for model in self.rex:
            model.draw()
            
        for model in self.chopper:
            model.draw()

    def draw_reflections(self):
        '''
        Draw the reflections in the scene.
        '''
        self.skybox.draw()

        for model in self.models:
            model.draw()

        for model in self.rex:
            model.draw()


    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene.
        return: None
        '''

        # Clear the scene and the depth buffer to handle occlusions.
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # When using a framebuffer, do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()

        # Draw the skybox.
        self.skybox.draw()

        # Render the shadows.
        self.shadows.render(self)

        # When rendering the framebuffer we ignore the reflective object.
        if not framebuffer:

            self.environment.update(self)

            for model in self.chopper:
                model.draw()

            self.show_shadow_map.draw()

        # Draw the scene models.
        for model in self.models:
            model.draw()
        
        # Draw the dinosaur models.
        for model in self.rex:
            model.draw()

        self.show_light.draw()

        # Flip the buffers as we draw on a different buffer.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Processes keyboard events.
        '''
        Scene.keyboard(self, event)

        # If the 1 key is pressed.
        if event.key == pygame.K_1:
            for model in self.chopper:
                # Move the helicopter along the x axis by 0.5.
                model.M[:, -1][2] += 0.5

        # If the 2 key is pressed.
        if event.key == pygame.K_2:
            for model in self.chopper:
                # Move the helicopter along the x axis by 0.5.
                model.M[:, -1][2] -= 0.5

if __name__ == '__main__':

    scene = CityScene()
    # starts drawing the scene
    scene.run()
