# lets start with a simple empty function 

def say_hi(): # definition 
    print("Hi!") # what it does 
say_hi() # call the function, run the script, you'll get Hi! 

# now, we use 1 input 

def say_howdy(name):
    print("Howdy", name) # name is the input 
say_howdy("John!") # Python sets name her = John, 

# now let's do some math
def double_number(number):
    return number * 2 
answer = double_number(5)
print(answer)

# now we make the script responde to our commands in the terminal 
import sys # for Python to read the terminal commands 

def square_number(number): # function that takes one number as an input 
    print(number * number) # squaring that number 

# sys,argv[1]: get the 2nd thing after I type the script name 
# if nothing was type, command becomes none 
command = sys.argv[1] if len(sys.argv) > 1 else None  # this will be a one time thing you need to write

if command == "square": # when I type script_name.py square
    number = int(sys.argv[2]) # sys.argv[2] get the 3rd thing we type in the terminal, int turns it into a number 
    square_number(number) # run the function 
else:
    print("For squaring a number, use: square <number>")