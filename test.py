vel_x = self.body.velocity[0]
        vel_y = self.body.velocity[1]

        friction_x = self.friction
        friction_y = self.friction


        #reducing or increasing each ball's speed to slow it down (friction)
        if(vel_x > 0):
            vel_x -= friction_x
        elif(vel_x < 0):
            vel_x += friction_x
        
        #to make sure balls come to rest
        if(vel_x < self.friction and vel_x > self.friction*-1):
            vel_x = 0


        if(vel_y > 0):
            vel_y -= friction_y
        elif(vel_y < 0):
            vel_y += friction_y

        #to make sure balls come to rest
        if(vel_y < self.friction and vel_y > self.friction*-1):
            vel_y = 0

        #setting vel to balls after calculation
        self.body.velocity = (vel_x, vel_y)



    #checks if any balls go in the pockets
    def checkPut(self):
        global balls_remaining

        #only uses the y pos of ball and pocket to determine score
        pos_y = self.body.position.y
