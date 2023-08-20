import sys, pygame
from time import time,sleep
from math import cos,sin,pi,log,tan,sqrt
from random import random
from PIL import Image
tau=2*pi
hp=pi/2
red=(255,0,0)
yellow=(200,200,0)
white=(255,255,255)

Weapon_Sprites={"pistol":pygame.image.load("Gun1.png")}
#Grass=Image.open("Grass.jpg")

def BlendCols(col1,col2,r):
    red=int(col1[0]*(1-r)+col2[0]*r)
    green=int(col1[1]*(1-r)+col2[1]*r)
    blue=int(col1[2]*(1-r)+col2[2]*r)
    return (red,green,blue)
def fade(col,inc):
    if abs(inc-pi/2)<.01:
        return col
    elif abs(inc)<.01:
        return (128,128,128)
    else:
        dist=sqrt((2/tan(inc))**2+4)
        return BlendCols(col,(128,128,128),min(1,dist**.6/10))
    return col[0],col[1],col[2]


black = 0, 0, 0
def ini_pygame(size=(800,600)):
    pygame.init()
    clock=pygame.time.Clock()
    screen = pygame.display.set_mode(size)
    mixer=pygame.mixer.pre_init(frequency=44100, size=-16, channels=8, buffer=512)
    return screen,mixer,clock



    
class  camera:##CLASS START####
    #origin is the location
    #target is where it looks
    #follows is an object whos position will constantly become the new target, and the origin ofthe camera will approach itwhen it trails too far
    def __init__(self,origin,azimuth,inclination,follows=None):
        self.origin=origin
        self.azimuth=azimuth
        self.inclination=inclination
        self.follows=follows
        self.viewWidth=.6
        self.viewHeight=.6
        self.maxinc=pi/2-self.viewHeight-.01
        self.mininc=-(pi/2-self.viewHeight)+.01
    def facing_vector(self,az,inc):
        x=cos(az)*sin(inc)
        y=sin(az)*sin(inc)
        z=cos(inc)
        return x,y,z
    def move(self,orientation=(0,0),displacement=(0,0,0)):
        self.azimuth+=orientation[0]
        self.inclination+=orientation[1]
        if self.inclination>self.maxinc:
            self.inclination=self.maxinc
        if self.inclination<self.mininc:
            self.inclination=self.mininc
        if self.azimuth<pi:
            self.azimuth+=tau
        if self.azimuth>pi:
            self.azimuth-=tau
        if displacement!=(0,0,0):
            self.origin=sum_tuples(self.origin,displacement)
        
    def draw(self,game,time):
        screen=game.screen
        planecol=game.planecol
        #draw plane
        for vert in range(0,game.size[1],4):
            for hor in range(0,game.size[0],10):
                left=hor-5
                right=hor+5
                az=self.azimuth+self.viewWidth*.5-(hor/game.size[0]*self.viewWidth)
                inc=self.inclination+self.viewHeight*.5-(vert/game.size[1]*self.viewHeight)
                
                if inc==0:
                    dist="infinity"
                    col=(128,128,128)
                elif inc<0:
                    dist=sqrt((self.origin[1]/tan(inc))**2+self.origin[1]**2)
                    x,y=self.origin[0]+cos(az)*dist,self.origin[2]+sin(az)*dist
                    #col=fade(BlendCols(Grass.getpixel(((x*200)%Grass.size[0],(y*200)%Grass.size[1])),planecol(x,y,inc),.5),inc)
                    col=(40,180,60)
                else:
                    col=game.skybox.bgcol(az,inc,time)
                pygame.draw.line(screen, col, (left,vert), (right,vert), 4)
        
            

class player:##CLASS START####
    def __init__(self,base,height=2,radius=.2,azimuth=1,inclination=-.2):
        self.base=base
        self.height=height
        self.radius=radius
        self.azimuth=azimuth
        self.inclination=inclination
        self.jumping=False
        self.crouching=False
        self.Health=95
    def facing_vector(self,az,inc):
        x=cos(az)*sin(inc)
        y=sin(az)*sin(inc)
        z=cos(inc)
        return x,y,z
    def draw(self):
        pass
    
######CLASS END####3

class skybox:##CLASS START####
    def __init__(self,bgcol=black,image="Sky.jpg"):
        
        self.texture=Image.open(image)
#       self.bgcol=lambda azimuth,inc:fade(BlendCols(bgcol,(255,255,255),abs(sin(azimuth*10)*(pi/2-inc)/5)),inc)
        #self.bgcol=lambda azimuth,inc:fade(BlendCols(bgcol,(69,90,30),abs(sin((azimuth)%pi*4)**8*(pi/2-inc)/3)),inc)
        def colorfunc(azimuth,inc,time=0):
            tex_x=((azimuth+pi+(time/10)%tau)/(pi*2)*self.texture.size[0])%self.texture.size[0]
            tex_y=((inc+pi)/(pi*2)*self.texture.size[1])%self.texture.size[1]
            try:
                out=fade(self.texture.getpixel((tex_x,tex_y)),inc)
            except:
                print(azimuth)
                print(tex_x)
                print(tex_y)
                out=self.texture.getpixel((0,0))
                input()
            return out 
        self.bgcol=colorfunc
    def render():
        pass

Movement_Lookup={pygame.K_a:(1,0),pygame.K_w:(0,1),pygame.K_s:(0,-1),pygame.K_d:(-1,0)}
Walking_Lookup={pygame.K_j:(1,0),pygame.K_i:(0,1),pygame.K_k:(0,-1),pygame.K_l:(-1,0)}
######CLASS END####
def sum_tuples(a,b):
    o=[]
    for i in range(len(a)):
        o.append(a[i]+b[i])
    return tuple(o)
class gameloop:##CLASS START####
    def __init__(self,displaysize,objects={"trees":[],"signs":[],"chests":[],"stairs":[],"buildings":[],"rooms":[]}):
        self.screen,self.mixer,self.clock=ini_pygame(displaysize)
        self.size=displaysize
        #ini screen
        self.skybox=skybox((0,0,200))
        self.cam=camera((20,2,40),pi/2,0)
        self.player=player((0,0,0))
        self.planecol=lambda x,y,inc:(80+sin(x*pi)*16-abs(sin(y*pi)*15),max(170,160+sin(x/3*pi)*16-sin(y/4*pi)*15-x-(y*25)%7),30+((abs(x**2-y**2)*25)%7)*5)
        self.objects=objects
    def HUD(self,shooting=False):
        #healthbar
        pygame.draw.line(self.screen,(0,0,0), (19,self.size[1]-40), (221,self.size[1]-40), 42)
        pygame.draw.line(self.screen,(255,0,0), (20,self.size[1]-40), (20+self.player.Health*2,self.size[1]-40), 40)
        #weapon
        #DRAW GUN
        #---#Shooting
        if shooting>0:
            if shooting == 2:
                cols=white,yellow
            elif shooting==1:
                cols=yellow,red
            pygame.draw.circle(self.screen,cols[0],(745,self.size[1]-290+int(random()*20)),16)
            pygame.draw.circle(self.screen,cols[1],(735+int(random()*20),self.size[1]-300+int(random()*20)),18)
            shooting-=1
        self.screen.blit(Weapon_Sprites["pistol"],(700,400))
        pygame.display.flip()
        #draw crosshair
        pygame.draw.line(self.screen,(0,0,0), (self.size[0]*.49,self.size[1]*.5-1), (self.size[0]*.51,self.size[1]*.5-1), 2)
        pygame.draw.line(self.screen,(0,0,0), (self.size[0]*.5-1,self.size[1]*.485), (self.size[0]*.5-1,self.size[1]*.515), 2)
        
        
        
    def play(self):
        t=0
        mousepos=pygame.mouse.get_pos()
        shooting=0
        while 1:

            ##look for keys held down
            keys=pygame.key.get_pressed()
            
            
            #get user inputs
            for key in Walking_Lookup:
                if keys[key]:
                    step=Walking_Lookup[key]
                    forward=(cos(self.cam.azimuth),0,sin(self.cam.azimuth))
                    left=(cos(self.cam.azimuth+hp),0,sin(self.cam.azimuth+hp))
                    displacement=[i*step[0] for i in left]
                    displacement=sum_tuples(displacement,[i*step[1] for i in forward])
                    
                    self.cam.move((0,0),displacement)
                    
            #move character
            for key in Movement_Lookup:
                if keys[key]:
                    looking=Movement_Lookup[key]
                    self.cam.move((looking[0]*.1,looking[1]*.05),(0,0,0))

            #look for keys just pressed this moment
            # set shooting to False,it will be changed to True if space isn't pressed
            events=pygame.event.get()
            for event in events:
                events=pygame.event.get()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        shooting=2
                        
            #move camera
            #iterate objects
            
            ##calculate which objects fall into the azimuth arc of the camera and their depth
            visible=[]
            for i in self.objects["trees"]:
                if inarc(i.pos):
                    pass
            #draw world
                        
            self.cam.draw(self,t)
            
            #draw character
            #Draw HUD LAST
            #HealthBar
            
            self.HUD(shooting)
            shooting-=1
            pygame.display.flip()
            pygame.event.pump()
            self.clock.tick(20)
            t+=1/20
            
######CLASS END####
Game=gameloop((1260,720))
Game.play()
