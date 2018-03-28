from main import *


def prettify(content):
    for row in content:
        print(row)

print("***Creating SSController: ssc1 with 20 cols, rows\n")
ssc1 = SSController("NEW", 20, 20)
ssc1.setName("ssc1")

print("*** Name of ssc1")
print(ssc1.getName())

print("\n*** Printing getCells() of ssc1\n")
print(ssc1.getCells())

print("\n*** Uploading ankara.csv to ssc1, and resizing spreadsheet according to it...\n")
with open('ankara.csv', newline='') as csvfile:
    csvcontent = csv.reader(csvfile, delimiter=',')
    ssc1.upload(csvcontent)

print("*** Printing getCells() of ssc1\n")
rows = ssc1.getCells()
prettify(rows)

print("\n*** Printing getCell('A5') of ssc1")
print(ssc1.getCell("A5"))

print("\n*** Printing getCell('C5') of ssc1")
print(ssc1.getCell("C5"))

print("\n*** Changing cell A5 to 2023 then, printing")
ssc1.setCellValue("A5", "2023")
print(ssc1.getCell("A5"))

print("\n*** Changing cell C5 to A4+A5 formula then, printing")
ssc1.setCellFormula("C5", "A4+A5")
print(ssc1.getCell("C5"))

print("\n*** Evaluating formulas in ssc1")
ssc1.evaluate()

print("\n*** Printing getCells() of ssc1 after evaluation")
prettify(ssc1.getCells())

print("\n*** Printing range A1:B3")
prettify(ssc1.getCells("A1:B3"))

print("\n*** Cutting range A1:B3 of ssc1 then, print range A1:B3")
ssc1.cutRange("A1:B3")
prettify(ssc1.getCells("A1:B3"))

print("\n*** Pasting cutted content to B4, then print B4:C6")
ssc1.pasteRange("B4")
prettify(ssc1.getCells("B4:C6"))

print("\n*** In our code, if spreadsheet evaluated, "
      "\n*** It always return its value, if it is not evaluated, returns with = and formula")

print("\n*** Copying range C5:D7 of ssc1 then, print range C5:D7")
ssc1.copyRange("C5:D7")
prettify(ssc1.getCells("C5:D7"))

print("\n*** Pasting cutted content to B4, then print B4:C6")
ssc1.pasteRange("B4")
prettify(ssc1.getCells("B4:C6"))

print("\n*** Creating SSPersistency named ssp, if database and table not created, create it.")
ssp = SSPersistency()

print("\n*** Listing database via ssp")
ssp.list()

print("\n*** Listing spreadsheets in memory via ssp")
ssp.listmem()

print("\n*** Listing spreadsheets in memory but not saved via ssp")
ssp.listmem(True)
print("\n*** Saving ssc1 to database")
ssp.save(ssc1.getId())

print("\n*** Listing database via ssp")
ssp.list()

print("\n*** Listing spreadsheets in memory but not saved via ssp")
ssp.listmem(True)

print("\n*** Loading ssc1 from database")
ssp.load(ssc1.getId())

print("\n*** Printing getCells() of ssc1 after loading")
prettify(ssc1.getCells())

print("\n*** OBSERVER TESTS ****")

print("\n*** Registering ssp to observers of ssc1")
ssc1.register(ssp)

print("\n *** Changing name of ssc1")
ssc1.setName("New Name")

print("\n*** Deleting ssc1 from memory and database")
ssp.delete(ssc1.getId())

print("\n*** Listing spreadsheets in memory")
ssp.listmem()

print("\n*** Listing database via ssp")
ssp.list()

print("\n*** Deleting every spreadsheet from database and memory")
ssp.deleteAll()
