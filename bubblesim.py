#[V] control spawn place
#[V] gas gravity to the outside
#[V] split gas
#[V] split border
#[X] border gravity to the center
#[V] aestetic
#[ ] endgame screen

from math import pi,radians,sqrt,hypot
from math import sin as rsin
from math import cos as rcos
from random import randint
import pygame
import PyParticles
import time
#--- parameters
newParticleTimeInit=200
newParticleTime=0
sizeX,sizeY = (1280,720)
#--- functions
def sin(a):
	return rsin(radians(a))
def cos(a):
	return rcos(radians(a))
def vecLen(ax,ay,bx,by):
	#print(ax,ay,bx,by,(ax-bx)+(ay-by))
	#return sqrt((ax-bx)**2+(ay-by)**2)
	return hypot(ax-bx,ay-by)
def uVec(ax,ay,bx,by):
	x=ax-bx
	y=ay-by
	l=vecLen(ax,ay,bx,by)
	return [x/l,y/l]
'''
uvecTestX=randint(0,10)
uvecTestY=randint(0,10)
uvecTest=uVec(uvecTestX,uvecTestY,0,0)
print('uvec test',uvecTestX,uvecTestY,'l',vecLen(uvecTestX,uvecTestY,0,0),'u',uvecTest,'ul',vecLen(uvecTest[0],uvecTest[1],0,0))
'''


screen = pygame.display.set_mode((sizeX,sizeY))
pygame.display.set_caption('Springs')
#-- load animations
brickAnim=[]
wallAnim=[]
gasAnim=[]
for i in range(1,31):
	brickAnim.append(pygame.image.load('brick'+str(i).zfill(4)+'.png').convert_alpha())
	wallAnim.append(pygame.image.load('wall'+str(i).zfill(4)+'.png').convert_alpha())
	gasAnim.append(pygame.image.load('gas'+str(i).zfill(4)+'.png').convert_alpha())
background=pygame.image.load('bubbleBlurred.png').convert_alpha()
pygame.font.init()
font = pygame.font.Font('DarkPoint.otf', 48)
clock=pygame.time.Clock()


universe = PyParticles.Environment((sizeX,sizeY))
universe.colour = (0,0,0)
universe.addFunctions(['move', 'bounce', 'collide', 'drag', 'accelerate'])
universe.acceleration = (0,0)
universe.mass_of_air = 0.02

count=20
for i in range(count):
	x=sin((360/count)*i)*4*count+sizeX//2
	y=cos((360/count)*i)*4*count+sizeY//2
	universe.addParticles(x=x,y=y,mass=100, size=10, speed=1, elasticity=0.1, colour=(20,100,200),type='wall')
	if i>0:
		universe.addSpring(i-1, i, length=10, strength=0.1)
universe.addSpring(i, 0, length=10, strength=0.1)
#for i in range(100):
universe.addParticles(x=sizeX//2,y=sizeY//2,mass=100, size=10, speed=1, elasticity=0.1, colour=(20,200,40),type='gas')
endGame=False
scoreRecorded=False
lostParticles=0
selected_particle = None
paused = False
running = True
clock.tick(30)
startTime=time.time()
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				paused = (True, False)[paused]
			if event.key == pygame.K_ESCAPE:
				running=False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			selected_particle = universe.findParticle(pygame.mouse.get_pos())
		elif event.type == pygame.MOUSEBUTTONUP:
			selected_particle = None
			universe.unselect=False
	#--counters
	newParticleTime-=1
	if endGame:
		#print('endGame',)
		l=len(universe.springs)
		if l>10:
			universe.springs.pop(randint(0,l-1))
	if newParticleTime<=0:
		newParticleTime=newParticleTimeInit
		plc=randint(0,3)# vertical or horizontal
		off=20
		if plc==0:
			universe.addParticles(x=randint(off,sizeX-off),y=off,mass=100, size=10, speed=0, elasticity=0.1, colour=(200,200,40),type='brick')
		elif plc==1:
			universe.addParticles(x=randint(off,sizeX-off),y=sizeY-off,mass=100, size=10, speed=0, elasticity=0.1, colour=(200,200,40),type='brick')
		elif plc==2:
			universe.addParticles(x=off,y=randint(off,sizeY-off),mass=100, size=10, speed=0, elasticity=0.1, colour=(200,200,40),type='brick')
		else:
			universe.addParticles(x=sizeX-off,y=randint(off,sizeY-off),mass=100, size=10, speed=0, elasticity=0.1, colour=(200,200,40),type='brick')
	#-- user move particle
	if universe.unselect:
		selected_particle = None
	if selected_particle:
		selected_particle.mouseMove(pygame.mouse.get_pos())
	if not paused:
		universe.update()
	screen.fill(universe.colour)
	screen.blit(background,pygame.rect.Rect(0,0,1000,1000))
	for s in universe.springs:
		pygame.draw.line(screen, (50,0,0), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)),width=20)
	for p in universe.particles:
		p.frame+=1
		if p.frame>28:
			p.frame=1
		if p.type=='brick':
			screen.blit(brickAnim[p.frame],pygame.rect.Rect(int(p.x)-15,int(p.y)-15,30,30))
		elif p.type=='wall':
			screen.blit(wallAnim[p.frame],pygame.rect.Rect(int(p.x)-15,int(p.y)-15,30,30))
		elif p.type=='gas':
			screen.blit(gasAnim[p.frame],pygame.rect.Rect(int(p.x)-15,int(p.y)-15,30,30))
		else:
			pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, 0)
	lostParticles=universe.lostParticles
	pygame.display.set_caption('bubbleSim totalParticles '+str(len(universe.particles))+'lostParticles: '+str(lostParticles))
	if lostParticles>0:
		endGame=True
	if endGame and not scoreRecorded:
		scoreRecorded=True
		endTime = time.time()
		elapsedTime=endTime-startTime
		minutes, seconds = divmod(elapsedTime, 60)
		text1 = font.render('T: '+str(int(minutes))+'m '+str(int(seconds))+'s Scr: '+str(len(universe.particles)), True, (20,200,100))
		text1Rect = text1.get_rect()
		text1Rect.centerx = screen.get_rect().centerx
		text1Rect.centery = screen.get_rect().centery
	if endGame and scoreRecorded:
		screen.blit(text1, text1Rect)
	#print('clock.tick',)
	clock.tick(60)
	pygame.display.flip()
