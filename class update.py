class laptop:
    def __init__(self):
        self.price=()
        self.processor=""
        self.Ram=""

    def display(self):
        print("hp price:",self.price)
        print("hp processor:",self.processor)
        print("hp Ram",self.Ram)
        print("dell price:",self.price)
        print("dell processor:",self.processor)
        print("dell Ram:",self.Ram)
hp=laptop()

hp.price=60000
hp.processor="i5"
hp.Ram="8gb"

hp.dellprice=64000
hp.dellprocessor="i5"
hp.dellRam="8gp"

print("This is hp laptop details:")
print(hp.price,hp.processor,hp.Ram)
print()
print("This is dell laptop details:")
print(hp.dellprice,hp.dellprocessor,hp.dellRam)
print()

hp.display()



class student:
    def __init__(self):
        self.name=""
        self.reg=()
    def display(self):
        print("name:",self.name)
        print("reg:",self.reg)
        print("name:",self.name2)
        print("reg:",self.reg2)

detail=student()

detail.name="kanishka"
detail.reg="2397"
detail.name2="lathika"
detail.reg2="0723"

detail.display()


class Teacher:
    def __init__(self,name,reg):
        self.name=name
        self.reg=reg

    def display(self):
        print("name:",self.name)
        print("reg:",self.reg)
        
t1=Teacher("kanishka","9723")
t2=Teacher("lathika","0723")

t1.display()
t2.display()


class calculate:
    def add(self,a,b):
        print("add:",a+b)
    def sub(self,a,b):
        print("sub:",a-b)
    def mul(self,a,b):
        print("mul:",a*b)
    def div(self,a,b):
        print("div",a%b)

obj=calculate()
obj.add(10,5)
obj.sub(45,60)
obj.mul(67,98)
obj.div(47,23)

