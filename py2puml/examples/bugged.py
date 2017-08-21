#This is a simple program that reads 10 numbers and prints the highest one.
#
i=0 #This is the initial amount of numbers
m=0 #This is the initial highest number
x=0 #This one of the user-defined numbers
while i<10 #Begin loop, repeat until there's ten numbers
    x=input("Enter a number:") #Number input
    i=i+1 #i is increased by 1 each loop, so the loop is repeated 10 times
    if x>m: #If a new number is higher than the one entered before, it becomes the biggest one
        m=x
print("The highest number is", m) #The result is printed
