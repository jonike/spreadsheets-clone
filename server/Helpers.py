import re

# return cell addresses in formula by parsing


def parseFormula(formula):
    cells = []
    cells = re.findall("[A-Z]+[0-9]+", formula)
    return cells

# parse A1:B9 like ranges to array of cell addresses -> [A,1,B,9]


def parseRange(range):
    cells = parseFormula(range)
    startCell = cells[0]
    endCell = cells[1]
    startCellRow, endCellRow = re.findall(
        "[A-Z]+", startCell), re.findall("[A-Z]+", endCell)
    startCellColumn, endCellColumn = re.findall(
        "[0-9]+", startCell), re.findall("[0-9]+", endCell)
    return [startCellRow[0], startCellColumn[0], endCellRow[0], endCellColumn[0]]

# check if given address in required range


def checkIfInRange(range, address):
    parsedRange = parseRange(range)  # A 1: J 7
    addRow, addCol = re.findall(
        "[A-Z]+", address), re.findall("[0-9]+", address)
    if parsedRange[0] <= addRow <= parsedRange[2] and parsedRange[1] <= addCol <= parsedRange[3]:
        return True
    else:
        return False

# check if string is numeric


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

# check if given word in between A,B,C -> True


def inBetween(begin, word, end):
    rw, rb, re = 0, 0, 0
    for i in word:
        rw += ord(i)
    for i in begin:
        rb += ord(i)
    for i in end:
        re += ord(i)
    lw, lb, le = len(word), len(begin), len(end)
    if (lw > lb or rw > rb) and (lw <= le or rw <= re):
        print(True)
    else:
        print(False)

# given letter return nex letter A -> B, Z-> AA


def nextLetter(nowLetter, oneLetter=0):
    if(len(nowLetter) == 1):
        if(ord(nowLetter) + 1 != 91):
            return chr(ord(nowLetter) + 1)
        else:
            if oneLetter:
                return "AA"
            else:
                return False
    else:
        result = ""
        reversel = nowLetter[::-1]
        for i in reversel:
            if(nextLetter(i)):
                result += nextLetter(i)
                break
            else:
                result += "A"
        i = 0
        realresult = ""
        for k in result:
            realresult += k
            i += 1
        for l in range(i, len(reversel)):
            realresult += reversel[l]
        return realresult[::-1]

# given range return all cells between that range
# row by row
# A1:C1 -> [[A1,B1,C1]]


def rangeToCells(rangeAddr):
    parsed = parseRange(rangeAddr)  # [A,1,B,9]
    b = int(parsed[1])
    e = int(parsed[3])
    rows = []
    for i in range(b, e + 1):
        curRow = []
        curLetter = parsed[0]
        while curLetter != parsed[2]:
            curRow += [curLetter + str(i)]
            if len(curLetter) == 1:
                curLetter = nextLetter(curLetter, 1)
            else:
                curLetter = nextLetter(curLetter)
        curRow += [curLetter + str(i)]
        rows += [curRow]
    return rows

# given column num turn to letter 26 -> Z, 27 -> AA


def columnToLetter(num):
    letter = 'A'
    for i in range(1, num):
        if len(letter) == 1:
            letter = nextLetter(letter, 1)
        else:
            letter = nextLetter(letter)
    return letter
