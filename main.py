import uuid
from Equation import Expression
import re
import sqlite3
import pickle
import time
from Observer import Observable, Observer
from Helpers import *

createdSpreadsheets = {}


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

''' cell types: formula, string, number '''


class SpreadSheet(Observable):

    class Cell:

        def __init__(self, cellType, content):
            self.type = cellType
            if cellType == 'formula':
                self.formula = content
                self.value = content  # !!! ATTENTION !!!
            else:
                self.formula = False
                self.value = content

        def getType(self):
            return self.type

        def getValue(self):
            return self.value

        def getFormula(self):
            return self.formula

        def setCellValue(self, content):
            self.value = content

        def setCellFormula(self, formulastr):
            self.formula = formulastr

    def __init__(self, rows, cols):
        super().__init__()
        self.name = 'Unnamed'
        self.id = uuid.uuid1()
        self.rows = rows
        self.cols = cols
        self.cells = {}

    def getId(self):
        with self.mutex:
            return self.id

    def setName(self, name):
        with self.mutex:
            self.name = name
            self.update_observers("changenamed", name, id=self.getId())

    def getName(self):
        with self.mutex:
            return self.name

    def getCell(self, addr):
        with self.mutex:
            cell = self.cells[addr]
            if cell.getType() != 'formula':
                return (cell.getValue(), cell.getType())
            else:
                return (cell.getValue(), cell.getType(), cell.getFormula())

    # return all addresses of filled cells
    def allAddress(self):
        with self.mutex:
            addr = []
            for key, cellObject in self.cells.items():
                addr += [key]
            return addr

    # return cells in given range in csv format
    def getCells(self, rangeAddr='ALL'):
        with self.mutex:
            resultCols = []
            realResult = []
            if rangeAddr == 'ALL':
                rows = rangeToCells(
                    "A1:" + columnToLetter(self.cols) + str(self.rows))
            else:
                rows = rangeToCells(rangeAddr)
            for row in rows:
                resultCols = []
                for col in row:
                    if col in self.cells:
                        if self.cells[col].getType() == 'formula':
                            if self.cells[col].getValue() == self.cells[col].getFormula():
                                resultCols += ['=' +
                                               str(self.cells[col].getValue())]
                            else:
                                resultCols += [str(self.cells[col].getValue())]
                        else:
                            resultCols += [self.cells[col].getValue()]
                    else:
                        resultCols += [',']
                realResult += [resultCols]
            return realResult

    # delete cells in given range and return them
    def cutCells(self, rangeAddr='ALL'):
        with self.mutex:
            self.update_observers("setcutted", id=self.getId())
            resultCols = []
            realResult = []
            if rangeAddr == 'ALL':
                rows = rangeToCells(
                    "A1:" + columnToLetter(self.cols) + str(self.rows))
            else:
                rows = rangeToCells(rangeAddr)
            for row in rows:
                resultCols = []
                for col in row:
                    if col in self.cells:
                        if self.cells[col].getType() == 'formula':
                            if self.cells[col].getValue() == self.cells[col].getFormula():
                                resultCols += ['=' +
                                               str(self.cells[col].getValue())]
                            else:
                                resultCols += [str(self.cells[col].getValue())]
                        else:
                            resultCols += [self.cells[col].getValue()]
                        del self.cells[col]
                    else:
                        resultCols += [',']
                realResult += [resultCols]
            return realResult

    # read from csv, update row & col
    def csvToCells(self, csvContent):
        with self.mutex:
            self.cells.clear()
            self.update_observers("setuploaded", id=self.getId())
            i = 1
            letter = 'A'
            maxCol = 0
            colnumber = 0
            for row in csvContent:
                letter = 'A'
                colnumber = 0
                for col in row:
                    colnumber += 1
                    if col:
                        if (not is_number(col)) and col[0] == "=":
                            col = col.replace("=", "", 1)
                            NewCell = self.Cell('formula', str(col))
                        elif is_number(col):
                            NewCell = self.Cell('number', str(col))
                        else:
                            NewCell = self.Cell('string', str(col))
                        self.cells[letter + str(i)] = NewCell
                    if len(letter) == 1:
                        letter = nextLetter(letter, 1)
                    else:
                        letter = nextLetter(letter)
                if colnumber > maxCol:
                    maxCol = colnumber
                i += 1
            self.rows = i - 1
            self.cols = maxCol

    # read from cut, paste it
    def cutToPaste(self, csvContent, topLeft):
        with self.mutex:
            self.update_observers("setpasted", id=self.getId())
            topLeftCol = parseRange(topLeft + ':' + topLeft)[0]  # A
            topLeftRow = parseRange(topLeft + ':' + topLeft)[1]  # 1
            letter = topLeftCol
            i = int(topLeftRow)
            for row in csvContent:
                letter = topLeftCol
                for col in row:
                    if col:
                        if (not is_number(col)) and col[0] == "=" and ("IF" not in col):
                            col = col.replace("=", "")
                            NewCell = self.Cell('formula', str(col))
                        elif is_number(col):
                            NewCell = self.Cell('number', str(col))
                        else:
                            NewCell = self.Cell('string', str(col))
                        if letter + str(i) in self.cells:
                            del self.cells[letter + str(i)]
                        self.cells[letter + str(i)] = NewCell
                    if len(letter) == 1:
                        letter = nextLetter(letter, 1)
                    else:
                        letter = nextLetter(letter)
                i += 1

    def setCellValue(self, addr, content):  # BE CAREFUL !!!
        with self.mutex:
            self.update_observers("setcellvalue", addr, id=self.getId())
            if is_number(content):
                NewCell = self.Cell('number', float(content))
            else:
                NewCell = self.Cell('string', str(content))
            self.cells[addr] = NewCell

    def setCellFormula(self, celladdr, formulastr):
        with self.mutex:
            self.update_observers("setcellformula", celladdr, id=self.getId())
            NewCell = self.Cell('formula', formulastr)
            self.cells[celladdr] = NewCell

    def avg_function(self, cell, iter):
        with self.mutex:
            formula = cell.getFormula()
            sumx = re.findall(
                "AVERAGE\([A-Z]+[0-9]+[:][A-Z]+[0-9]+\)", formula)[0]  # SUM(A5:B7)
            justrange = re.findall(
                "AVERAGE\([A-Z]+[0-9]+[:][A-Z]+[0-9]+\)", formula)[0]  # A5:B7
            sum_cells = rangeToCells(justrange)
            sum_cells = [k for sub in sum_cells for k in sub]
            numofcells = len(sum_cells)
            return_sum = 0
            for cellcik in sum_cells:
                return_sum += self.evaluateHelper(cellcik, iter - 1)
            return str.replace(formula, sumx, str("{:.3f}".format(return_sum / numofcells)))

    def sum_function(self, cell, iter):
        with self.mutex:
            formula = cell.getFormula()
            sumx = re.findall(
                "SUM\([A-Z]+[0-9]+[:][A-Z]+[0-9]+\)", formula)[0]  # SUM(A5:B7)
            justrange = re.findall(
                "SUM\([A-Z]+[0-9]+[:][A-Z]+[0-9]+\)", formula)[0]  # A5:B7
            sum_cells = rangeToCells(justrange)
            sum_cells = [k for sub in sum_cells for k in sub]
            return_sum = 0
            for cellcik in sum_cells:
                return_sum += self.evaluateHelper(cellcik, iter - 1)
            return str.replace(formula, sumx, str(return_sum))

    def if_function(self, cell, iter):
        with self.mutex:
            formula = cell.getFormula()
            formula = str.replace(formula, "=", "==")
            cellsofformula = parseFormula(formula)
            for cof in cellsofformula:
                formula = str.replace(formula, cof, str(
                    self.evaluateHelper(cof, iter - 1)))
            comps = formula.split(";")
            comps[0] = str.replace(comps[0], "IF(", "")
            if '"' in comps[1]:
                comps[1] = re.findall('\"(.*)\"', comps[1])[0]
            if '"' in comps[2]:
                comps[2] = re.findall('\"(.*)\"', comps[2])[0]
            comps[2] = str.replace(comps[2], ")", "")
            if eval(comps[0]):
                return comps[1]
            else:
                return comps[2]

    def count_if(self, cell, iter):  # =COUNTIF(E5:E20;"High")
        with self.mutex:
            formula = cell.getFormula()
            justrange = re.findall(
                "[A-Z]+[0-9]+[:][A-Z]+[0-9]+", formula)[0]  # E5:E20
            sum_cells = rangeToCells(justrange)
            sum_cells = [k for sub in sum_cells for k in sub]
            return_sum = 0
            comps = formula.split(";")
            if '"' in comps[1]:
                comps[1] = re.findall('\"(.*)\"', comps[1])[0]
            for cellcik in sum_cells:
                if self.evaluateHelper(cellcik, iter - 1) == comps[1]:
                    return_sum += 1
            return return_sum

    # if given address is a formula evaluates and return evaluated value
    # else return cell value
    def evaluateHelper(self, addr, iter):
        with self.mutex:
            if addr not in self.cells:
                return 0
            cell = self.cells[addr]
            if cell.getType() == 'formula' and iter >= 0:
                new_formula = cell.getFormula()
                if 'AVERAGE' in new_formula:
                    new_formula = self.avg_function(cell, iter - 1)
                if 'SUM' in new_formula:
                    new_formula = self.sum_function(cell, iter - 1)
                if 'COUNTIF' in new_formula:
                    new_formula = self.count_if(cell, iter - 1)
                    cell.setCellValue(new_formula)
                    if is_number(cell.getValue()):
                        return float(cell.getValue())
                    else:
                        return str(cell.getValue())
                if 'IF' in new_formula:
                    new_formula = self.if_function(cell, iter - 1)
                    cell.setCellValue(new_formula)
                    if is_number(cell.getValue()):
                        return float(cell.getValue())
                    else:
                        return str(cell.getValue())
                expCells = parseFormula(new_formula)  # [A1,B2] a1:b2 x
                expCellsForFormula = expCells[:]  # duplicate
                if len(expCells) != 0:
                    formulFunction = Expression(
                        new_formula, expCellsForFormula)
                else:
                    formulFunction = Expression(new_formula)
                evaluatedCells = []
                for i in range(0, len(expCells)):
                    evaluatedCells += [
                        self.evaluateHelper(expCells[i], iter - 1)]
                cell.setCellValue(formulFunction(*evaluatedCells))
                if is_number(cell.getValue()):
                    return float(cell.getValue())
                else:
                    return str(cell.getValue())
            elif iter < 0:
                return 0
            else:
                if is_number(cell.getValue()):
                    return float(cell.getValue())
                else:
                    return str(cell.getValue())

    # use evaluateHelper to recursively evalute cells
    def evaluate(self, iterations=10):
        with self.mutex:
            self.update_observers("setevaluate", id=self.getId())
            for key, cellObject in self.cells.items():
                if cellObject.getType() == 'formula':
                    self.evaluateHelper(key, iterations - 1)


class SSController(Observer):

    def __init__(self, id='NEW', rows=0, cols=0):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.isnotchanged = [True, '']
        if id == 'NEW' and rows != 0 and cols != 0:
            self.spread = SpreadSheet(rows, cols)
            self.id = self.spread.getId()
            self.spread.register(self)
            createdSpreadsheets[self.id] = [self.spread, False]
        else:
            self.spread = createdSpreadsheets[id][0]
            self.rows = self.spread.rows
            self.cols = self.spread.cols
            self.spread.register(self)

    def update(self, *args, **kwargs):
        print("SSController notified:\n"
              "SpreadSheet has changed.: {0}\n{1}".format(args, kwargs))
        ekstras = ''
        if len(args) == 2:
            ekstras = ',"ekstras":"' + args[1] + '"'
        tmp = '{"command":"' + args[0] + '", "id":"' + \
            str(kwargs['id']) + '" ' + ekstras + ' }'
        self.isnotchanged[1] = tmp
        self.isnotchanged[0] = False
        createdSpreadsheets[kwargs['id']][1] = False

    def upload(self, csvcontent):
        self.spread.csvToCells(csvcontent)

    def cutRange(self, rangeaddr):
        self.copied = self.spread.cutCells(rangeaddr)

    def copyRange(self, rangeaddr):
        self.copied = self.spread.getCells(rangeaddr)

    def pasteRange(self, topleftcelladdr):
        self.spread.cutToPaste(self.copied, topleftcelladdr)

    def getName(self):
        return self.spread.getName()

    def getId(self):
        return self.spread.getId()

    def setName(self, name):
        self.spread.setName(name)

    def getCell(self, addr):
        return self.spread.getCell(addr)

    def allAddress(self):
        return self.spread.allAddress()

    def getCells(self, rangeAddr='ALL'):
        return self.spread.getCells(rangeAddr)

    def cutCells(self, rangeAddr='ALL'):
        self.copied = self.spread.cutCells(rangeAddr)

    def setCellValue(self, addr, content):
        self.spread.setCellValue(addr, content)

    def setCellFormula(self, celladdr, formulastr):
        self.spread.setCellFormula(celladdr, formulastr)

    def evaluate(self, iterations=10):
        self.spread.evaluate(iterations)


# When notify change true to false in createdspreadsheets
@singleton
class SSPersistency(Observer):

    def __init__(self):
        self.conn = sqlite3.connect('SpreadSheets.db', check_same_thread=False)
        self.c = self.conn.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS `Spreadsheets` (`id` int(11) NOT NULL,`name` text NOT NULL,`content` text' \
              '  NOT NULL,`date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`id`,`date`));'
        self.c.execute(sql)

    def update(self, *args, **kwargs):
        print("SSPersistency notified:\n"
              "SpreadSheet has changed.: {0}\n{1}".format(args, kwargs))
        createdSpreadsheets[kwargs['id']][1] = False

    # save to database given spreadsheet via pickle
    def save(self, id):
        time.sleep(1)
        createdSpreadsheets[id][1] = True
        sp = createdSpreadsheets[id][0]
        spname = sp.getName()
        sp = sp.getCells()
        pick = pickle.dumps(sp)
        sql = "INSERT INTO `Spreadsheets` (`id`,`name`, `content`, `date`) VALUES ('" + str(
            id) + "','" + str(spname) + "', :pick, CURRENT_TIMESTAMP)"
        self.c.execute(sql, [sqlite3.Binary(pick)])
        self.conn.commit()

    # retrieve from database given id spreadsheet
    def load(self, id):
        sql = "select * from Spreadsheets where id='" + \
            str(id) + "'  order by date desc limit 1"
        self.c.execute(sql)
        object = self.c.fetchone()
        try:
            sps = pickle.loads(object[2])  # csv content
            idofsps = object[0]
            nameofsps = object[1]
            return [sps, idofsps, nameofsps]
        except:
            print("No spreadsheet.")
    # 0-> id 1-> name 2-> csvcontent 3-> date
    # list all spreadsheets from database

    def list(self):
        toReturn = []
        sql = 'select * from Spreadsheets'
        i = 0
        for row in self.c.execute(sql):
            print(row[0], row[1])
            toReturn += [str(row[0]) + ' ' + str(row[1])]
            i += 1
        if i == 0:
            print("There is no spreadsheet in database.")
            toReturn += ["There is no spreadsheet in memory."]
        return toReturn

    # take care !!!
    def listmem(self, dirty=False):
        i = 0
        toReturn = []
        for id, arr in createdSpreadsheets.items():
            i += 1
            if arr[1] is False and dirty:
                print(id, arr[0].getName())
                toReturn += [str(id) + ' ' + str(arr[0].getName())]
            elif dirty is False:
                print(id, arr[0].getName())
                toReturn += [str(id) + ' ' + str(arr[0].getName())]
        if i == 0:
            print("There is no spreadsheet in memory.")
            toReturn += ["There is no spreadsheet in memory."]
        return toReturn

    # delete given id from database
    # can not delete from memory !!!
    def delete(self, id):
        sql = "delete from Spreadsheets where id='" + str(id) + "'"
        self.c.execute(sql)
        self.conn.commit()

    # delete all spreadsheets in database
    def deleteAll(self):
        sql = "delete from Spreadsheets"
        self.c.execute(sql)
        self.conn.commit()

    # save to database changes
    def __del__(self):
        self.conn.commit()
