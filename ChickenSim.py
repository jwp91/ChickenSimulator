#!/usr/bin/env python
# coding: utf-8

# In[14]:


import tkinter as tk
import random
from PIL import Image, ImageTk
import math

class Chicken:
    def __init__(self, canvas, image_file, max_x, max_y, initial_scale=1.0):
        self.canvas = canvas
        self.max_x = max_x
        self.max_y = max_y

        self.initialize_position()

        self.original_image = Image.open(image_file)
        self.image = None  # Placeholder for the ImageTk.PhotoImage reference

        self.create_image(initial_scale)
        self.speech_bubble = None

    def initialize_position(self):
        self.x = random.randint(50, self.max_x)
        self.y = random.randint(50, self.max_y)

    def create_image(self, scale):
        image_width, image_height = self.original_image.size
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)
        resized_image = self.original_image.resize((new_width, new_height))
        self.image = ImageTk.PhotoImage(resized_image)

        self.shape = self.canvas.create_image(self.x, self.y, image=self.image)

    def move_towards_food(self, food_piles):
        if not food_piles:
            return  # No food available, so stay in place

        nearest_food = min(food_piles, key=lambda food: math.sqrt((self.x - food.x)**2 + (self.y - food.y)**2))

        # Calculate the distance to the nearest food
        distance_to_food = math.sqrt((self.x - nearest_food.x)**2 + (self.y - nearest_food.y)**2)

        # Set max chicken speed
        max_speed = 5 #Adjust as needed

        #Calculate speed based on distance
        critical_radius = 75 #distance away (pixels) at which chickens reach max speed
        speed = min(max_speed, max_speed*(critical_radius**2)/(distance_to_food+0.001)**2)
        
        # If the distance is less than or equal to 3 pixels, remove the food
        if distance_to_food <= 5:
            food_piles.remove(nearest_food)
            self.canvas.delete(nearest_food.shape)
        else:
            # Calculate the direction vector towards the nearest food
            direction_x = nearest_food.x - self.x
            direction_y = nearest_food.y - self.y
    
            # Normalize the direction vector
            magnitude = math.sqrt(direction_x**2 + direction_y**2)
            if magnitude != 0:
                direction_x /= magnitude
                direction_y /= magnitude
    
            # Update the chicken's position towards the food
            self.x += direction_x * speed
            self.y += direction_y * speed
    
            # Update the canvas coordinates
            self.canvas.coords(self.shape, self.x, self.y)
        
    def move(self, food_piles):
        delta_x, delta_y = random.randint(-5, 5), random.randint(-5, 5)
        self.x += delta_x
        self.y += delta_y

        #Set bounds for chickens
        if self.x > self.max_x:
            self.x = self.max_x
        if self.y > self.max_y:
            self.y = self.max_y
        
        self.canvas.coords(self.shape, self.x, self.y)

        if random.random() < 0.05:
            self.display_speech_bubble("Cluck")

        self.move_towards_food(food_piles)  # Move towards the nearest food
        self.canvas.after(100, self.move, food_piles)

    def display_speech_bubble(self, text):
        if self.speech_bubble:
            self.canvas.delete(self.speech_bubble)
        x1, y1, x2, y2 = self.canvas.bbox(self.shape)
        x, y = (x1 + x2) / 2, y1 - 20
        self.speech_bubble = self.canvas.create_text(x, y, text=text, anchor='center', fill='black', font=("Arial", 12))
        self.canvas.after(2000, self.clear_speech_bubble)

    def clear_speech_bubble(self):
        if self.speech_bubble:
            self.canvas.delete(self.speech_bubble)
            self.speech_bubble = None

class ChickenFarmSimulator:
    def __init__(self, root):
        self.root = root
        root.title("Chicken Farm Simulator")

         # Ask the user for the initial number of chickens
        try:
            num_chickens = int(input("Enter the initial number of chickens: "))
        except ValueError:
            print("Please enter a valid integer for the number of chickens.")
            exit()

        self.canvas = tk.Canvas(root, width=600, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resized)

        self.food_piles = [] # Initialize the list of food piles

        self.initialize_chickens(num_chickens)  # Pass the user-input number of chickens)
        self.center_canvas_on_screen()
        
        self.canvas.bind("<Button-1>", self.create_food_pile)
        self.canvas.bind("<ButtonPress-1>", self.start_placing_food)
        self.canvas.bind("<ButtonRelease-1>", self.stop_placing_food)

        self.placing_food = False  # Flag to track whether the user is placing food
        self.food_placement_delay = 200 #Set delay


    def create_food_pile(self, event):
        # Get the clicked position
        x, y = event.x, event.y

        # Create a food pile at the clicked position
        initial_scale = 0.1
        image_file = 'wheat.png'
        
        food_pile = FoodPile(self.canvas, x, y, image_file, initial_scale)
        self.food_piles.append(food_pile)

    def start_placing_food(self, event):
        self.placing_food = True
        self.place_food_continuously()

    def stop_placing_food(self, event):
        self.placing_food = False

    def place_food_continuously(self):
        if self.placing_food:
            # Get the current pointer coordinates
            x, y = self.canvas.winfo_pointerxy()
            x -= self.canvas.winfo_rootx()
            y -= self.canvas.winfo_rooty()
            
            # Create a food pile at the clicked position
            initial_scale = 0.1
            image_file = 'wheat.png'

            food_pile = FoodPile(self.canvas, x, y, image_file, initial_scale)
            self.food_piles.append(food_pile)

            # Schedule the next placement with the specified delay
            self.canvas.after(self.food_placement_delay, self.place_food_continuously)
    
    def on_canvas_resized(self, event):
        self.update_chicken_bounds(event.width, event.height)

    def center_canvas_on_screen(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x = (screen_width - canvas_width) // 2
        y = (screen_height - canvas_height) // 2

        self.root.geometry(f"{canvas_width}x{canvas_height}+{x}+{y}")

    def initialize_chickens(self, num_chickens):
        image_file = "chicken.png"
        initial_scale = 0.1
        self.chickens = [Chicken(self.canvas, image_file, 600, 600, initial_scale) for _ in range(num_chickens)]

        for chicken in self.chickens:
            chicken.move(self.food_piles)

    def update_chicken_bounds(self, max_x, max_y):
        for chicken in self.chickens:
            chicken.max_x = max_x
            chicken.max_y = max_y

class FoodPile:
    def __init__(self, canvas, x, y, image_file, initial_scale):
        self.canvas = canvas
        self.x = x
        self.y = y

        original_image = Image.open(image_file)
        image_width, image_height = original_image.size
        new_width = int(image_width * initial_scale)
        new_height = int(image_height * initial_scale)
        resized_image = original_image.resize((new_width, new_height))
        self.image = ImageTk.PhotoImage(resized_image)

        self.shape = canvas.create_image(self.x, self.y, image=self.image)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChickenFarmSimulator(root)
    root.mainloop()


# In[ ]:




