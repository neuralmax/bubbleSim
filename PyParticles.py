import math, random

def addVectors(v1,v2):
	""" Returns the sum of two vectors """
	angle1, length1=v1
	angle2, length2=v2

	x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
	y  = math.cos(angle1) * length1 + math.cos(angle2) * length2

	angle  = 0.5 * math.pi - math.atan2(y, x)
	length = math.hypot(x, y)

	return (angle, length)

def combine(p1, p2):
	if math.hypot(p1.x - p2.x, p1.y - p2.y) < p1.size + p2.size:
		total_mass = p1.mass + p2.mass
		p1.x = (p1.x*p1.mass + p2.x*p2.mass)/total_mass
		p1.y = (p1.y*p1.mass + p2.y*p2.mass)/total_mass
		(p1.angle, p1.speed) = addVectors((p1.angle, p1.speed*p1.mass/total_mass), (p2.angle, p2.speed*p2.mass/total_mass))
		p1.speed *= (p1.elasticity*p2.elasticity)
		p1.mass += p2.mass
		p1.collide_with = p2

def collide(p1, p2):
	""" Tests whether two particles overlap
		If they do, make them bounce, i.e. update their angle, speed and position """

	dx = p1.x - p2.x
	dy = p1.y - p2.y

	dist = math.hypot(dx, dy)
	if dist < p1.size + p2.size:
		if p1.type=='brick' or p2.type=='brick':
			p2.colidedType=p1.type
			p2.colidedId=p1.id
			p1.colidedType=p2.type
			p1.colidedId=p2.id
		angle = math.atan2(dy, dx) + 0.5 * math.pi
		total_mass = p1.mass + p2.mass

		(p1.angle, p1.speed) = addVectors((p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass), (angle, 2*p2.speed*p2.mass/total_mass))
		(p2.angle, p2.speed) = addVectors((p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass), (angle+math.pi, 2*p1.speed*p1.mass/total_mass))
		elasticity = p1.elasticity * p2.elasticity
		p1.speed *= elasticity
		p2.speed *= elasticity

		overlap = 0.5*(p1.size + p2.size - dist+1)
		p1.x += math.sin(angle)*overlap
		p1.y -= math.cos(angle)*overlap
		p2.x -= math.sin(angle)*overlap
		p2.y += math.cos(angle)*overlap

class Particle:
	""" A circular object with a velocity, size and mass """

	def __init__(self, p, size, mass=1,type='',id=0):
		x, y=p
		self.x = x
		self.y = y
		self.size = size
		self.colour = (0, 0, 255)
		self.thickness = 0
		self.speed = 0
		self.angle = 0
		self.mass = mass
		self.drag = 1
		self.elasticity = 0.9
		self.type=type
		self.centerX=0
		self.centerY=0
		self.deleteMe=False
		self.initAge=500
		self.age=self.initAge
		self.colidedType=''
		self.colidedId=0
		self.links=[]
		self.id=id
		self.frame=0
	def resetAge(self):
		self.age=random.randint(self.initAge,self.initAge*2)
	def move(self):
		""" Update position based on speed, angle """

		self.x += math.sin(self.angle) * self.speed
		self.y -= math.cos(self.angle) * self.speed

	def experienceDrag(self):
		self.speed *= self.drag

	def mouseMove(self, p):
		""" Change angle and speed to move towards a given point """
		x, y=p
		dx = x - self.x
		dy = y - self.y
		self.angle = 0.5*math.pi + math.atan2(dy, dx)
		self.speed = math.hypot(dx, dy) * 0.1

	def accelerate(self, vector):
		""" Change angle and speed by a given vector """
		#print('particle.accelerate.test',self.centerX)
		#print('particle.accelerate.test.gas')
		if self.type=='':
			(self.angle, self.speed) = addVectors((self.angle, self.speed), vector)
		elif self.type=='gas':#move from center
			#print('particle.accelerate.test.gas')
			self.age-=1
			x=self.x-self.centerX
			y=self.y-self.centerY
			angle=math.atan2(y, x)
			(self.angle, self.speed) = addVectors((self.angle, self.speed),(angle,0.01))
		elif self.type=='wall':#move towards center
			(self.angle, self.speed) = addVectors((self.angle, self.speed), vector)

	def attract(self, other):
		"""" Change velocity based on gravatational attraction between two particle"""

		dx = (self.x - other.x)
		dy = (self.y - other.y)
		dist  = math.hypot(dx, dy)

		if dist < self.size + other.size:
			return True

		theta = math.atan2(dy, dx)
		force = 0.1 * self.mass * other.mass / dist**2
		self.accelerate((theta - 0.5 * math.pi, force/self.mass))
		other.accelerate((theta + 0.5 * math.pi, force/other.mass))

class Spring:
	def __init__(self, p1, p2, length=50, strength=0.5,id=0):
		self.id=id
		p1.links.append(id)
		p2.links.append(id)
		self.p1 = p1
		self.p2 = p2
		self.length = length
		self.strength = strength

	def update(self):
		dx = self.p1.x - self.p2.x
		dy = self.p1.y - self.p2.y
		dist = math.hypot(dx, dy)
		theta = math.atan2(dy, dx)
		force = (self.length - dist) * self.strength

		self.p1.accelerate((theta + 0.5 * math.pi, force/self.p1.mass))
		self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))

class Environment:
	""" Defines the boundary of a simulation and its properties """

	def __init__(self,sz):
		width, height=sz
		self.width = width
		self.height = height
		self.particles = []
		self.springs = []

		self.colour = (255,255,255)
		self.mass_of_air = 0.2
		self.elasticity = 0.75
		self.acceleration = (0,0)

		self.particle_functions1 = []
		self.particle_functions2 = []
		self.function_dict = {
		'move': (1, lambda p: p.move()),
		'drag': (1, lambda p: p.experienceDrag()),
		'bounce': (1, lambda p: self.bounce(p)),
		'accelerate': (1, lambda p: p.accelerate(self.acceleration)),
		'collide': (2, lambda p1, p2: collide(p1, p2)),
		'combine': (2, lambda p1, p2: combine(p1, p2)),
		'attract': (2, lambda p1, p2: p1.attract(p2))}

		self.lostParticles=0
		self.unselect=False

	def addFunctions(self, function_list):
		for func in function_list:
			(n, f) = self.function_dict.get(func, (-1, None))
			#print(func)
			if n == 1:
				self.particle_functions1.append(f)
			elif n == 2:
				self.particle_functions2.append(f)
			else:
				print("No such function: %s" % f)

	def addParticles(self, n=1, **kargs):
		""" Add n particles with properties given by keyword arguments """

		for i in range(n):
			size = kargs.get('size', random.randint(10, 20))
			mass = kargs.get('mass', random.randint(100, 10000))
			x = kargs.get('x', random.uniform(size, self.width - size))
			y = kargs.get('y', random.uniform(size, self.height - size))

			particle = Particle((x, y), size, mass)
			particle.speed = kargs.get('speed', random.random())
			particle.angle = kargs.get('angle', random.uniform(0, math.pi*2))
			particle.colour = kargs.get('colour', (0, 0, 255))
			particle.elasticity = kargs.get('elasticity', self.elasticity)
			particle.drag = (particle.mass/(particle.mass + self.mass_of_air)) ** particle.size
			particle.type=kargs.get('type')
			particle.centerX=self.width//2
			particle.centerY=self.height//2
			particle.id=len(self.particles)

			self.particles.append(particle)

	def addSpring(self, p1, p2, length=50, strength=0.5):
		""" Add a spring between particles p1 and p2 """
		self.springs.append(Spring(self.particles[p1], self.particles[p2], length, strength,id=len(self.springs)))

	def update(self):
		"""  Moves particles and tests for collisions with the walls and each other """
		resetIndexes=False
		for i, particle in enumerate(self.particles):
			if particle.age==0:
				particle.resetAge()
				self.addParticles(x=particle.x,y=particle.y,mass=100, size=10, speed=0, elasticity=1, colour=(20,200,40),type='gas',id=len(self.particles))
			if particle.type=='wall' and particle.colidedType=='brick':
				#newParticleId=len(self.particles)
				self.particles[particle.colidedId].type='wall'
				self.particles[particle.colidedId].colour=(20,100,200)
				#self.addParticles(x=particle.x,y=particle.y,mass=100, size=10, speed=0, elasticity=0.1, colour=(20,100,200),type='wall',id=newParticleId)
				linkId=particle.links[0]
				if self.springs[linkId].p1.id==particle.id:
					self.springs[linkId].p1=self.particles[particle.colidedId]
					self.springs[linkId].p1.id=particle.colidedId
				else:
					self.springs[linkId].p2=self.particles[particle.colidedId]
					self.springs[linkId].p2.id=particle.colidedId
				self.addSpring(particle.id,particle.colidedId, length=10, strength=0.1)
				print('update particle.colidedId',particle.colidedId)
				#self.particles.pop(particle.colidedId)
				self.unselect=True
				particle.colidedType=''
				particle.colidedId=0
				break
			#if particle.type=='brick' and particle.colidedType=='wall':

			#	self.lostParticles+=1
			#	break
			if particle.deleteMe:
				self.particles.pop(i)
				self.lostParticles+=1
				break
		if resetIndexes:
			for i, particle in enumerate(self.particles):
				particle.id=i

		for i, particle in enumerate(self.particles, 1):
			for f in self.particle_functions1:
				f(particle)
			for particle2 in self.particles[i:]:
				for f in self.particle_functions2:
					f(particle, particle2)

		for spring in self.springs:
			spring.update()

	def bounce(self, particle):
		""" Tests whether a particle has hit the boundary of the environment """
		if particle.type=='gas':
			if particle.x > self.width + particle.size or particle.x < -particle.size or particle.y > self.height + particle.size or particle.y < -particle.size:
				particle.deleteMe=True
		else:
			if particle.x > self.width - particle.size:
				particle.x = 2*(self.width - particle.size) - particle.x
				particle.angle = - particle.angle
				particle.speed *= self.elasticity
			elif particle.x < particle.size:
				particle.x = 2*particle.size - particle.x
				particle.angle = - particle.angle
				particle.speed *= self.elasticity
			if particle.y > self.height - particle.size:
				particle.y = 2*(self.height - particle.size) - particle.y
				particle.angle = math.pi - particle.angle
				particle.speed *= self.elasticity
			elif particle.y < particle.size:
				particle.y = 2*particle.size - particle.y
				particle.angle = math.pi - particle.angle
				particle.speed *= self.elasticity

	def findParticle(self, p):
		""" Returns any particle that occupies position x, y """
		x, y=p
		for particle in self.particles:
			if math.hypot(particle.x - x, particle.y - y) <= particle.size:
				return particle
		return None
