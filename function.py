def add():
    print("This is add cal")
    a=int(input("enter your number1:"))
    b=int(input("enter your number2:"))
    print(a+b)
def sub():
    print("This is sub cal")
    d=int(input("enter your num1:"))
    f=int(input("enter your num2:"))
    print(d-f)
def mul():
    print("This is mul cal")
    a=int(input("enter your num1:"))
    b=int(input("enter your num2:"))
    print(a*b)
def dev():
    print("This is dev cal")
    a=int(input("enter your num1:"))
    b=int(input("enter your num2:"))
    print(a%b)


num1 = int(input("enter the first value:"))
num2 = int(input("enter the second value:"))
calu = input(f"choose the operators[add, sub, mul, div, modul, power, floor]:")
if (calu == "add"):
    print(f"{num1} and {num2} add value {num1+num2}")
elif (calu == "sub"):
    print(f" {num1} and {num2} sub value {num1-num2}")
elif (calu == "mul"):
    print(f" {num1} and {num2} mulvalue {num1*num2}")
elif (calu == "div"):
    try:
        print(f"The {num1} and{num2} div value {num1/num2}")
    except ZeroDivisionError:
        print ("ERROR: division by zero is not allowed.")
elif (calu == "modul"):
    print(f" The {num1} and{num2}modul value {num1%num2}")
elif (calu == "power"):
    print(f" The {num1} and {num2}power value {num1**num2}")
elif (calu == "floor"):
    print(f" The {num1} and {num2} floor value {num1//num2}")
elif input():
    while True:
        try:
           print (input())
        except ValueError:
           print("invalid input.please enter a numeric value")
else:
    print("choose correct operators")




























def findpassorfail(num):
    if(num>35):
        print("pass or even")
    elif(num<35):
        print("fail or odd")
    else:
        print("invoid num")

findpassorfail(24)



s_username="kanishka"
s_password="123"
uname=input("enter your uname:")
passwd=input("enter your password:")
def validate():
    if(s_username==uname and s_password==passwd):
        return ("true")
    else:
        return ("false")
a=validate()
print(a)



def add(a,b):
    return(a+b)
a=int(input("enter the number a :"))
b=int(input("enter the number b :"))
c=int(input("enter the number c :"))

added=add(a,b)
output=added*c
print(output)



