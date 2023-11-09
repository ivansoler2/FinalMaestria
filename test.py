import pygame, sys
import numpy as np


BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,100,255)
GREEN = (50,150,50)
RED = (255,0,0)
PURPLE=(130,0,130)
ORANGE = (255,160,122)

BACKGROUND = WHITE 

class Dot(pygame.sprite.Sprite): #Se crea la clase para la visalización de Objetos
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color=BLACK,
        radius=5,
        velocity=[0, 0],
        randomize=False
    ):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2]) #Imagen Principal
        self.image.fill(BACKGROUND) #Fondo del tablero
        pygame.draw.circle(#Se agregan los circulos
            self.image, color, (radius, radius), radius #4 Parametros para los circulos
        )

        self.rect = self.image.get_rect()#Trae el área de la ventana
        self.pos = np.array([x, y], dtype=np.float64)#Crear una variable con un arreglo float de X y Y
        self.vel = np.asarray(velocity, dtype=np.float64)#Convierte la velocidad en un array y lo deja en vel

        self.killswitch_on=False
        self.recovered = False
        self.randomize = randomize

        self.WIDTH = width
        self.HEIGHT = height

    def update(self):
            self.pos+= self.vel

            x, y = self.pos

            if x < 0: #Manejo de limites de la pantalla 
                self.pos[0] = self.WIDTH
                x = self.WIDTH
            if x > self.WIDTH:
                self.pos[0] = 0
                x = 0
            if y < 0:
                self.pos[1] = self.HEIGHT
                y = self.HEIGHT
            if y > self.HEIGHT:
                self.pos[1] = 0
                y = 0

            self.rect.x = x 
            self.rect.y = y

            vel_norm = np.linalg.norm(self.vel)

            if vel_norm > 3:
                self.vel/=vel_norm

            if self.randomize:
                self.vel += np.random.rand(2) * 2 - 1

            if self.killswitch_on:
                self.cycles_to_fate -=1

                if self.cycles_to_fate<=0:
                    self.killswitch_on=False
                    some_number = np.random.rand()
                    if self.mortality_rate > some_number:
                        self.kill()
                    
                    else:
                        self.recovered = True


        
    def respawn(self,color,radius=5):
        return Dot(
            self.rect.x,
            self.rect.y,
            self.WIDTH,
            self.HEIGHT,
            color = color,
            velocity = self.vel

    )

    def killswitch(self,cycles_to_fate=20,mortality_rate=0.2):
        self.killswitch_on = True
        self.cycles_to_fate=cycles_to_fate
        self.mortality_rate=mortality_rate
    def quarentined(self,color,radius=5):
        return Dot(
            self.rect.x,
            self.rect.y,
            self.WIDTH,
            self.HEIGHT,
            color = color,
            velocity = self.vel

    )




class Simulation:
    def __init__(self,width=600,height = 480):

        self.WIDTH = width
        self.HEIGHT = height

        self.susceptible_container = pygame.sprite.Group()
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.quarentined_container = pygame.sprite.Group()
        self.all_container = pygame.sprite.Group()

        self.n_subceptible = 50
        self.n_infected = 5 # Numero de infectados 
        self.n_quarentined=1
        #self.n_recovered = 1
        self.T = 1000
        self.cicles_to_fate=20
        self.mortality_rate = 0.2
        
    def start(self,randomize=False):
        self.N = self.n_subceptible + self.n_infected + self.n_quarentined #Totales
        pygame.init()
        screen = pygame.display.set_mode(
            [self.WIDTH, self.HEIGHT]
        )


        for i in range(self.n_subceptible): #Numero de individuos
            x= np.random.randint(0,self.WIDTH+1)
            y= np.random.randint(0,self.HEIGHT+1)

            vel = np.random.rand(2) * 2 - 1
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=GREEN, 
                velocity=vel,
                randomize=randomize)
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        for i in range(self.n_infected): #Numero de individuos infectados
            x= np.random.randint(0,self.WIDTH+1)
            y= np.random.randint(0,self.HEIGHT+1)

            vel = np.random.rand(2) * 2 - 1
            guy = Dot(x, y,self.WIDTH,self.HEIGHT,color=RED, velocity=vel,randomize=randomize)
            self.infected_container.add(guy)
            self.all_container.add(guy)


        clock = pygame.time.Clock()

        for i in range(self.T):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.all_container.update()


            screen.fill(BACKGROUND)

            #New Infections

            collision_group = pygame.sprite.groupcollide(
                self.susceptible_container,
                self.infected_container,
                True, 
                False,
            )

            for guy in collision_group:
                new_guy = guy.respawn(BLUE)   
                new_guy.vel *=-1#Va a la dirección contraria a la que estaba
                new_guy.killswitch(
                    self.cicles_to_fate, self.mortality_rate
                )
                self.infected_container.add(new_guy)
                self.all_container.add(new_guy)

            
            for guy in collision_group:
                new_guy2 = guy.respawn(ORANGE)   
                #new_guy2.vel *=-1#Va a la dirección contraria a la que estaba
                self.quarentined_container.add(new_guy2)
                self.all_container.add(new_guy2)

            # Recuperados

            recovered = []

            for guy in self.infected_container:
                if guy.recovered:
                    new_guy = guy.respawn(PURPLE)
                    self.recovered_container.add(new_guy)
                    self.all_container.add(new_guy)
                    recovered.append(guy)

            if len(recovered) > 0:
                self.infected_container.remove(*recovered)
                self.all_container.remove(*recovered)

            self.all_container.draw(screen)

            pygame.display.flip()

            clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
     covid = Simulation()
     covid.cycles_to_fate = 800
     covid.start(randomize=True)

