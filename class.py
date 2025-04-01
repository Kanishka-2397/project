class paris:
    name=""
    drink=""
    def party(self):

        print("let the party .....")
    def beach(self):
        print("enjoying the beach...")
kanishka = paris() 
lathika = paris()
kanishka.drink="yes"
lathika.drink="no"
kanishka.name="kanishka"
lathika.name="lathika "
print(kanishka.name)
print("drink:",kanishka.drink)
kanishka.party()
print(lathika.name)
print("drink:",lathika.drink)
lathika.beach()


class laptop:
    price=0
    processor=""
    Ram=""

HP=laptop()
DELL=laptop()
LENOVO=laptop()

HP.price=60000
HP.processor="i5"
HP.Ram="8gp"

DELL.price=65000
DELL.processor="i5"
DELL.Ram="9gb"

LENOVO.price=70000
LENOVO.Ram="10gb"
LENOVO.processor="i7"

print("Details for HP laptop:")
print(HP.price,HP.Ram,HP.processor)
print()
print("Details for DELL laptop:")
print(DELL.price,DELL.processor,DELL.Ram)
print()
print("Details for LENOVO laptop:")
print(LENOVO.price,LENOVO.price,LENOVO.Ram)
