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



