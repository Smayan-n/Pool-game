#using pymunk (for physics) and pygame for display

import math
import pygame, sys
from pymunk.pygame_util import DrawOptions
import pymunk
pygame.init()


#to create a border around the pool table
#uses 4 pymunk segments to do so
class Border():
    def __init__(self, p1, p2, d):

        self.p1 = p1
        self.p2 = p2
        self.depth = d
        
        #creates new segment based on start, end pos, and depth passed in
        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, self.depth)
        self.shape.elasticity = 0.8
        self.shape.friction = 1
        self.shape.collision_type = 16
        space.add(self.body, self.shape)
    
    #draws segments using pygame(for illustration only)
    def draw(self):

        newDepth = int(self.depth * (12/5))

        pygame.draw.line(screen, (255, 255, 0) , self.p1, self.p2, newDepth)

    def getValues(self):
        return self.p1, self.p2, self.depth


#class for all pool balls and pockets
class Ball():

    def __init__(self, pos, color, ballNum, vel = (0, 0), radius = 11):

        self.color = color
        self.radius = radius
        self.friction = 0.1

        #stores ball num(cue ball(0), 8 ball(8), etc)
        self.ballNum = ballNum
        self.cueBall_move = False

        #list of all pockets' coordinates
        #self.pockets = [(30, 25), (400, 25), (775, 25), (30, 425), (400, 425), (775, 425)]

        #-----------------creating the pymunk object-------------------------------------
        #                       mass, inertia,      body type: static, dynamic, or kinetic
        self.body = pymunk.Body(1, 100, body_type = pymunk.Body.DYNAMIC)
        self.body.position = pos  
        self.body.velocity = vel      
        
        #putting the body in a shape
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.8
        self.shape.collision_type = ballNum

        #adding shape to pymunk space
        space.add(self.body, self.shape)

    #makes pymunk shape visible. Draws balls as circles
    def draw(self, isOverride = False, pos_x = 0, pos_y = 0, radius = 11):
        #override and other parammeters used to display the balls remaining below the table
        #getting x and y position of the balls
        if not isOverride:
            pos_x, pos_y = self.body.position 

        #drawing a circle with position     
        pygame.draw.circle(screen, self.color, (pos_x, pos_y), radius)
        
        #displaying the ball numbers on each ball
        text_color = (0, 0, 0)
        if(self.ballNum == 8 or self.ballNum == 0):
            text_color = (255, 255, 255)

        ballNum = font1.render(str(self.ballNum), 5, text_color)
        screen.blit(ballNum, (pos_x - ballNum.get_width() / 2, pos_y - ballNum.get_height() / 2))

    #applys friction to all moving balls so that they do not infinitely move
    def applyFriction(self):

        vel_x, vel_y = self.body.velocity
        
        #keeping the signs of the x and y velocities so they can be re-applied afterwards
        if vel_x  == 0: vel_x = 0.1
        if vel_y == 0: vel_y = 0.1

        x_sign = vel_x/abs(vel_x)
        y_sign = vel_y/abs(vel_y)

        #calculating angle of trinagle
        angle = 0
        if vel_x != 0:
            angle = math.atan(vel_y/vel_x)

        #the hypotenuse of the triangle(total velocity) 
        vel = math.sqrt(vel_x**2 + vel_y**2)

        #applying friction on the total velocity
        if vel != 0:
            vel -= self.friction

        #setting vel to 0 when its close to 0: so that it does not go on infinitely
        if -self.friction <= vel <= self.friction:
            vel = 0

        #calculating the new x and y components of the velocity
        vel_x = abs(vel * math.cos(angle)) * x_sign
        vel_y = abs(vel * math.sin(angle)) * y_sign

        #setting the new velocity
        self.body.velocity = (vel_x, vel_y)     

    #checks if any balls go in the pockets
    def checkPut(self):
        global balls_remaining

        #only uses the y pos of ball and pocket to determine score
        pos_y = self.body.position.y
        
        if (pos_y < 23 or pos_y > 427):
            #if ball potted is cue ball then it should not be deleted
            if self.ballNum == 0:
                #if cue ball is potted then the other balls should stop moving
                for ball in balls:
                    ball.body.velocity = (0, 0)

                #resetting cue ball pos and vel
                self.body.position = (table_width / 4, table_height / 2)
                self.body.velocity = (0, 0)
                
                #displaying a message after cue balls stop moving
                msg = font3.render("You potted the cue ball!", 5, (255, 200, 0))
                screen.blit(msg, (table_width / 2 - (msg.get_width() / 2), table_height / 2 - (msg.get_height() / 2)))
                pygame.display.update()

                #to play message for longer
                pygame.time.delay(800)

                
            else:
                #deleting ball 
                pymunk.Space.remove(space, self.body)
                pymunk.Space.remove(space, self.shape)
                balls.remove(self)
                balls_remaining -= 1
                #exiting func so no errors are produced
                return

    def moveCueBall(self, event):
        mouse_pos = pygame.mouse.get_pos()
        #cue ball position and radius
        ball_pos = (self.body.position.x, self.body.position.y)
        radius = self.shape.radius

        #checks if player is clicking on the cue ball, then allowing him to move it
        if mouse_pos[0] > ball_pos[0] - radius and mouse_pos[0] < ball_pos[0] + radius:
            if mouse_pos[1] > ball_pos[1] - radius and mouse_pos[1] < ball_pos[1] + radius:
                if pygame.mouse.get_pressed()[2]:
                    self.cueBall_move = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                     self.cueBall_move = False

        #moving ball
        if self.cueBall_move:
            self.body.position = mouse_pos
        
        #keeping ball on the left side of white line
        if self.body.position.x + self.shape.radius> table_width / 4 + 20:
            self.body.position = (table_width / 4 + 20 - self.shape.radius, self.body.position.y)

    #NOT USED
    #ball and border collision
    def collide(self, arbiter, space, body):
        print("collide:", self.ballNum)  

    #static method that returns true if all any balls are moving
    @staticmethod
    def areMoving():
        
        for ball in balls:  
            vel_x, vel_y = ball.body.velocity
            #there is some head room (vel does not have to be exactly 0)
            if vel_x < -0.2 or vel_x > 0.2 or vel_y < -0.2 or vel_y > 0.2:
                return True         
        return False


#cue class
class Cue():
    def __init__(self):
        #max force
        self.maxForce = 18000

        self.force = 0 
        self.rise = 0
        self.run = 0

    #drawing the cue and the calculations
    def draw(self):
        #cue ball position
        cueBall_x, cueBall_y  = balls[0].body.position 
	
	    #mouse position
        end_x, end_y = pygame.mouse.get_pos()

        #drawing the cue stick from center of cue ball to cursr position
        pygame.draw.line(screen, (204, 102, 0), (cueBall_x, cueBall_y), (end_x, end_y), 5)

        #-----------------------------------------------------------------------------------------
        #drawing the guide line of a costant length. METHOD:
        #using ratios and proportion to calculate each x and y value opposite to cue
        #ex: run = 3, rise = 4, THEN hyp = 5 we know that the x,y coord is (3,4)
        #now we find x,y coord when hyp is gl_length (lets say 100):
        #   5 : 3 (run)  |  5 : 4 (rise)
        # 100 : x (run)  |  100 : y (run) ----> solve for x and y
        # (x,y) will be new relative point - subtract from cue_ball pos to get accurate plottable point

        #distance of cue
        dist = int(math.sqrt((end_y - cueBall_y)**2 + (end_x - cueBall_x)**2))

        #partial slope (the signs are opposite)
        self.rise = (end_y - cueBall_y)
        self.run = (end_x - cueBall_x)
        
        #calculating the hypotenuese of the triangle fromed by cue
        hyp = math.sqrt(self.run**2 + self.rise**2)
        if hyp == 0: hyp = 1
        
        #guide line length
        gl_length = 250

        end_x_gl = cueBall_x - (gl_length * self.run) / hyp
        end_y_gl = cueBall_y - (gl_length * self.rise) / hyp

        self.guideLine(cueBall_x, cueBall_y)
        
        pygame.draw.line(screen, (255, 255, 255), (cueBall_x, cueBall_y), (end_x_gl, end_y_gl), 2)
        

        #using distance of cue to determine the force
        #doing it here because the power bar needs force to be constantly updated
        self.force = int(dist) * 60   

    def guideLine(self, cueBall_x, cueBall_y):

        rise, run = -self.rise, -self.run

        l_slope = 0
        if run != 0: l_slope = rise / run

        # y = mx + b
        #l_y = l_slope*l_x + cueBall_y

    #for calculating the power and direction cue ball will go after release
    def release(self):
        global moves

        moves += 1
        
        #inverting rise and run
        rise, run = -self.rise, -self.run
        rise_run_sum = abs(rise) + abs(run)

        #limiting max force
        if self.force > self.maxForce:
            self.force = self.maxForce

        force_x = 0
        force_y = 0

        if rise_run_sum != 0:
            #using ratios to divide up the force to the x and y components

            force_x = (run / rise_run_sum) * self.force
            force_y = (rise / rise_run_sum) * self.force

        #applying force to cue ball
        balls[0].body.apply_force_at_local_point((force_x, force_y), (0, 0))


#creates objects like the borders and balls and acts as reset func
def initGameObjects():
    global balls, borders, cue, ball_border_handlers, balls_remaining, moves

    balls_remaining = 15
    moves = 0
    borders = []
    balls = []

    #creating borders around pool table so the balls can bounce 
    #top 2
    borders.append(Border((60, 0), (table_width / 2 - 35, 0), 25))
    borders.append(Border((table_width / 2 + 37, 0), (table_width - 60, 0), 25))

    #bottom 2
    borders.append(Border((60, table_height), (table_width / 2 - 35, table_height), 25))
    borders.append(Border((table_width / 2 + 37, table_height), (table_width - 60, table_height), 25))

    #left and right
    borders.append(Border((0, 60), (0, table_height - 60), 28))
    borders.append(Border((table_width, 60), (table_width, table_height - 60), 28))

    #creating the pool balls    
    #cue ball
    balls.append(Ball((table_width / 4, table_height / 2), (255, 255, 255), 0, (0, 0)))

    #other balls
    #temp width
    tw = table_width / 1.5
    #temp height
    th = table_height / 2

    spacer_x = 14
    spacer_y = 12

    #front most ball
    balls.append(Ball((tw, th), yellow, 1))
    #balls.append(Ball((table_width - 50, table_height - 50), (230, 230, 0), 1))

    #top diagonal
    balls.append(Ball((tw + spacer_x, th - spacer_y), blue, 2))
    balls.append(Ball((tw + spacer_x*2, th - spacer_y*2), green, 3))
    balls.append(Ball((tw + spacer_x*3, th - spacer_y*3), orange, 4))
    balls.append(Ball((tw + spacer_x*4, th - spacer_y*4), red, 5))

    #bottom diagonal
    balls.append(Ball((tw + spacer_x, th + spacer_y), purple, 6))
    balls.append(Ball((tw + spacer_x*2, th + spacer_y*2), brown, 7))
    balls.append(Ball((tw + spacer_x*3, th + spacer_y*3), (0, 0, 0), 8))
    balls.append(Ball((tw + spacer_x*4, th + spacer_y*4), yellow, 9))

    #middle
    spacer_x2 = 14
    spacer_y2 = 6
    balls.append(Ball((tw + spacer_x*2, th), blue, 10))

    balls.append(Ball((tw + spacer_x2*3, th - spacer_y2*2), red, 11))
    balls.append(Ball((tw + spacer_x2*4, th - spacer_y2*4), green, 12))

    balls.append(Ball((tw + spacer_x2*3, th + spacer_y2*2), orange, 13))
    balls.append(Ball((tw + spacer_x2*4, th + spacer_y2*4), purple, 14))

    balls.append(Ball((tw + spacer_x*4.3, th), brown, 15))

    #collision ball_border_handlers
    #for balls and borders
    ball_border_handlers = [space.add_collision_handler(16, i) for i in range(16)]

    #Cue object
    cue = Cue()

#for displaying thigns like score, cue, force bar
def displayGraphics():

    #fill background
    screen.fill(bg_color)
    screen.blit(bg, (0, 0))
        
    #white start line
    pygame.draw.line(screen, (255, 255, 255), (table_width / 4 + 20, 27), (table_width / 4 + 20, table_height - 27),  2)

    #text
    score_text = font2.render("Balls remaining: " + str(balls_remaining), 5, (0, 138, 230))
    screen.blit(score_text, (width - 280, height - 75))

    moves_txt = font2.render("Moves: " + str(moves), 5, (0, 138, 230))
    screen.blit(moves_txt, (width - 280, height - 40))

    #displaying the balls remaining at the bottom
    i = 1
    for ball in balls:
        if ball.ballNum != 0:
            ball.draw(True, 20 + i, height - 40, 15)
            i += 35

            pass

    #drawing balls, appying friction, and checking for a score
    #applying friction to balls so they dont infinitely move
    for ball in balls:
            ball.draw()#drawing balls
            ball.applyFriction() 
            ball.checkPut()

    #power bar

    #label
    pwr_lbl = font1.render("POWER" , 5, orange)
    screen.blit(pwr_lbl, (width - 48, 5))

    #background rect
    pygame.draw.rect(screen, (0, 230, 0), (table_width + 10, 30, 35, table_height - 40))

    #grey top rect
    #dist of cue used as height of bar
    max_bar_height = (table_height - 40) + 30

    const =  cue.maxForce / max_bar_height
    h = cue.force / const

    pygame.draw.rect(screen, bg_color, (table_width + 10, 30, 35, table_height - 40 - h))

    #outline rect
    pygame.draw.rect(screen, (255, 0, 0), (table_width + 10, 30, 35, table_height - 40), 1)
      
    #draw que only when drawCue is true
    if drawCue:
        cue.draw()

def main():
    global space, screen, width, height, balls, borders, table_width, table_height, drawCue, bg

    width = 855
    height = 530

    #seperate table h and w
    table_width = width - 55
    table_height = height - 80

    #loading background image and changing its dimentions accordingly
    bg = pygame.image.load("assets/pool_table.jpg")
    bg = pygame.transform.scale(bg, (table_width, table_height))

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pool")
    clock = pygame.time.Clock()

    space = pymunk.Space()#creating main pymunk physics space
    
    #var for cue
    drawCue = False

    #calling initGameObjects method
    initGameObjects()

    #main gameloop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #func for moving cue ball at the start of the game
            if moves == 0:
                balls[0].moveCueBall(event)

            #only if balls are not in motion, will it check for user input
            if not Ball.areMoving():

                #drawing cue only if user presses left mouse button
                   #returns tuple of boolean for each mosue button press
                if pygame.mouse.get_pressed()[0]:
                    drawCue = True
                    
                #user releasing ball
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    drawCue = False
                    #calling release function
                    cue.release()

            #resets pool table when 'r' is clicked on keyboard
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                #first clearing pymunk space
                for ball in balls:
                    pymunk.Space.remove(space, ball.body)
                    pymunk.Space.remove(space, ball.shape)
                for border in borders:
                    pymunk.Space.remove(space, border.body)
                    pymunk.Space.remove(space, border.shape)

                initGameObjects()                    

        #calling graphics methods
        displayGraphics()      

        #space.debug_draw(DrawOptions(screen))

        space.step(1/40)
        clock.tick(120)

        pygame.display.update()


#static varibles meant to be accesed by all classes and funcs

#initializing fonts
font1 = pygame.font.SysFont('comicsansms', 12, True)
font2 = pygame.font.SysFont('comicsansms', 25, False, True)
font3 = pygame.font.SysFont('comicsansms', 50, False, True)

#colors
yellow = (244, 208, 63)
brown = (100, 31, 22)
purple = (136, 78, 160)
blue = (53, 152, 219)
red = (204, 67, 54)
green = (28, 125, 70)
orange = (230, 126, 33)
bg_color = (200, 200, 200)

#bounce_sound = pygame.mixer.Sound('assets/bounce_sound.wav')

if __name__ == '__main__':
   main()
