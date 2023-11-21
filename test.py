import pygame, sys
import pandas as pd
import sqlite3
import numpy as np


BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,100,255)
GREEN = (50,150,50)
RED = (255,0,0)
PURPLE=(130,0,130)
ORANGE = (255,160,122)
GREY =  (230,230,230)
HORRIBLE_YELLOW =(190,175,50)

BACKGROUND = WHITE 
pruebaInfectados = []
pruebaTiempo=[]
pruebaRecuperados = []

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
        self.quarentined= True

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
                x = 160
            if y < 90:
                if x<165:
                    self.pos[1] = 200
                    y = 200
                    self.pos[0] = 600
                    x = 600
            if y > self.HEIGHT:
                self.pos[1] = 90
                y = 90

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


        
    def respawn(self,w,h,color,radius=5):
        return Dot(
            self.rect.x,
            self.rect.y,
            width=w,
            height=h,
            color = color,
            velocity = self.vel

    )

    def killswitch(self,cycles_to_fate=20,mortality_rate=0.2):
        self.killswitch_on = True
        self.cycles_to_fate=cycles_to_fate
        self.mortality_rate=mortality_rate

    def quarentinedF(self,w,h,color,radius=2):
        return Dot(
            self.rect.x,
            self.rect.y,
            width=w,
            height=h,
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
        self.n_quarentined=0
        #self.n_recovered = 1
        self.T = 700
        self.cicles_to_fate=200
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

        for i in range(self.n_quarentined): #Numero de individuos infectados
            x= np.random.randint(0,150)
            y= np.random.randint(0,79)

            vel = np.random.rand(2) * 2 - 1
            guy2 = Dot(x, y,160,80,color=ORANGE, velocity=vel,randomize=randomize)
            self.infected_container.add(guy2)
            self.all_container.add(guy2)


        stats = pygame.Surface(
            (self.WIDTH // 4 , self.HEIGHT//4)
        )
        stats.fill(GREY)
        stats.set_alpha(230)
        stats_pos = (440,12)

        



        clock = pygame.time.Clock()

        for i in range(self.T):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            pruebaTiempo.append(i)
            self.all_container.update()


            screen.fill(BACKGROUND)

            #Grafica

            stats_height = stats.get_height()
            stats_width = stats.get_width()
            numero_infectados_now = len(self.quarentined_container)
            numero_recuperados_now = len(self.recovered_container)
            pruebaRecuperados.append(numero_recuperados_now)
            pruebaInfectados.append(numero_infectados_now)
            numero_pop_now = len(self.all_container)
            n_rec_now = len(self.recovered_container)
            t=int((i/self.T) * stats_width)
            y_infected = int(
                stats_height
                - (numero_infectados_now/numero_pop_now)*stats_height
            )
            y_dead = int(
                ((self.N - numero_pop_now)/self.N)*stats_height
            )
            y_recoverd = int(
                (n_rec_now / numero_pop_now) * stats_height
           )
            
            stats_graph = pygame.PixelArray(stats)
            stats_graph[t,y_infected:] = pygame.Color(*ORANGE)

            stats_graph[t,:y_dead] = pygame.Color(*HORRIBLE_YELLOW)
            stats_graph[t,y_dead:y_dead + y_recoverd] = pygame.Color(*PURPLE)

                
            collision_group = pygame.sprite.groupcollide(
                self.susceptible_container,
                self.infected_container,
                True, 
                False,
            )
            for guy in collision_group:
                #new_guy = guy.respawn(BLUE)   
                                         
            #Quarentined
                quarentined = []
                if guy.quarentined:
                    new_guy2 = guy.quarentinedF(160,80,ORANGE)   
                    new_guy2.vel *=-1#Va a la dirección contraria a la que estaba
                    #new_guy2.vel *=-1#Va a la dirección contraria a la que estaba
                    self.quarentined_container.add(new_guy2)
                    #self.recovered_container.remove(5)
                    self.all_container.add(new_guy2)
                    quarentined.append(guy)
                
                
                new_guy2.killswitch( 
                    self.cicles_to_fate, self.mortality_rate
                )


            # #Recuperados
            recovered = []
            for guy in self.quarentined_container:
                if guy.recovered:
                    new_guy = guy.respawn(600,480,PURPLE)
                    self.recovered_container.add(new_guy)
                    self.all_container.add(new_guy)
                    recovered.append(guy)
                if len(recovered) > 0:
                    self.quarentined_container.remove(*recovered)
                    self.all_container.remove(*recovered)
            #        print(self.infected_container , "In")
                    #print(recovered)
#

            self.all_container.draw(screen)

            del stats_graph
            stats.unlock()
            screen.blit(stats,stats_pos)
            #print(stats_pos)

            pygame.display.flip()

            clock.tick(30)

        pygame.quit()

        # Creación DataFrame Pandas

        df = pd.DataFrame(list(zip(pruebaTiempo,pruebaInfectados,pruebaRecuperados)),columns=["Tiempo","Infectados","Recuperados"])

        #Conexión BD Datos

        con = sqlite3.connect("covid.db")

        #try:
        #    con.execute("""create table individuos (
        #                      tiempo,
        #                      infectados,
        #                      recuperados  
        #                )""")
        #    print("se creo la tabla articulos")                        
        #except sqlite3.OperationalError:
        #    print("La tabla articulos ya existe")                    
        #con.close()

        df.to_sql('individuos',con,if_exists='replace',index=False)
        cursor=con.execute("Select * from individuos")
        for fila in cursor:
            print(fila)
        con.close()

        
        
        #cur = con.cursor()
        #cur.execute("CREATE TABLE individuos(Time, Infectados, Recuperados)")




        #print(df)
        #print(pruebaInfectados)
        #print("---------------------------")
        #print(pruebaTiempo)
        #print("---------------------------")
        #print(pruebaRecuperados)
        #print("---------------------------")
        #print(len(pruebaInfectados))
        #print(len(pruebaTiempo))
        #print(len(pruebaRecuperados))
    
        
        #for row in range (filas):
        #        for columns in range (columnas):
        #            print(matrix[row][columns],end = " ")
        #        print()



        #print(matrix)
        #df.to_csv('fichero.csv',sep=';')

if __name__ == "__main__":
     covid = Simulation()
     covid.n_subceptible = 100
     covid.n_infected = 5
     covid.cycles_to_fate = 2000
     covid.start(randomize=True)