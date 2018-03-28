import socket,sys
from main import *
from threading import *
import _thread,csv
import json,uuid

HOST = 'localhost'  # Symbolic name, meaning all available interfaces
PORT = 9595  # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')


def notify_handler(conn, SSController):
    while 1:
        with SSController.spread.c:
            while SSController.isnotchanged[0]:
                SSController.spread.c.wait()
            reply = str.encode(SSController.isnotchanged[1])
            lengt = '{:10d}'.format(len(reply))
            conn.sendall(lengt.encode())
            conn.sendall(reply)
            SSController.isnotchanged[0] = True

# Function for handling connections. This will be used to create threads


def clientthread(conn, SSController, ssp):
    # infinite loop so that function do not terminate and thread do not end.
    while True:
        # Receiving from client
        lengt = conn.recv(10)
        if not lengt.strip():
            continue
        length = int(lengt.decode())
        data = conn.recv(length)
        reply = b''
        try:
            parseData = json.loads(data.decode())
            current_command = parseData['command']
            if current_command == "load":
                parameter = parseData['parameter']
                SSId = parameter.strip()
                csvandid = ssp.load(SSId)
                todeleteid = SSController.getId()
                updatethis = createdSpreadsheets[todeleteid][0]
                updatethis.csvToCells(csvandid[0])
                createdSpreadsheets[uuid.UUID(csvandid[1])] = [
                    SSController, False]
                SSController.id = uuid.UUID(csvandid[1])
                SSController.spread.id = uuid.UUID(csvandid[1])
                SSController.setName(csvandid[2])
                del createdSpreadsheets[todeleteid]
                SSController.spread.register(SSController)
            if current_command == 'getId':
                SSId = SSController.getId()
                reply += str.encode(str(SSId))
            if current_command == 'save':
                ssp.save(SSController.getId())
            if current_command == 'listmem':
                listofmem = ssp.listmem()
                reply += json.dumps(listofmem).encode()
            if current_command == 'list':
                reply += json.dumps(ssp.list()).encode()
            if current_command == 'set_name':
                parameter = parseData['parameter']
                SSController.setName(parameter)
            if current_command == 'get_name':
                print(SSController.getName())
                reply += str.encode(SSController.getName())
            if current_command == 'cut_range':
                parameter = parseData['parameter']
                SSController.cutRange(parameter)
            if current_command == 'copy_range':
                parameter = parseData['parameter']
                SSController.copyRange(parameter)
            if current_command == 'paste_range':
                parameter = parseData['parameter']
                SSController.pasteRange(parameter)
            if current_command == 'get_cell':
                parameter = parseData['parameter']
                tuple23 = SSController.getCell(parameter)
                reply += str.encode(str(tuple23[1]) + ', ')
                reply += str.encode(str(tuple23[2]) + ',')
                if len(tuple23) == 3:
                    reply += str.encode(str(tuple23[3]) + ',')
            if current_command == 'get_cells':
                parameter = parseData['parameter']
                csvcontent = SSController.getCells(parameter)
                tmp = json.dumps(csvcontent)
                reply += str.encode(tmp)
            if current_command == 'set_cell_value':
                parameter = parseData['parameter']
                SSController.setCellValue(parameter[0], parameter[1])
            if current_command == 'set_cell_formula':
                parameter = parseData['parameter']
                SSController.setCellFormula(parameter[0], parameter[1])
            if current_command == 'evaluate':
                SSController.evaluate()
            if current_command == 'load_mem':
                parameter = parseData['parameter']
                SSId = parameter.strip()
                print(SSId, 'x')
                tmp = SSController.getId()
                tmp2 = SSController.spread
                SSController.spread = createdSpreadsheets[uuid.UUID(SSId)][0]
                createdSpreadsheets[tmp][0].update_observers(
                    "newssloaded", id=tmp)
                tmp2.unregister(SSController)
                SSController.spread.register(SSController)
            if current_command == 'upload':
                parameter = parseData['parameter']
                csv_content = parameter
                csvcontent = csv.reader(csv_content.splitlines(), delimiter=',')
                SSController.upload(csvcontent)
            if current_command == 'cleardb':
                ssp.deleteAll()
            if current_command == 'clearsingledb':
                parameter = parseData['parameter']
                SSId = parameter.strip()
                ssp.delete(SSId)
        except TypeError as e:
            print("No command")
            print(e)
        if not data:
            break
        if reply == b'':
            continue
        lengt = '{:10d}'.format(len(reply))
        conn.sendall(lengt.encode())
        conn.sendall(reply)
    conn.close()


trds = []
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    # start new thread takes 1st argument as a function name to be run, second
    # is the tuple of arguments to the function.
    New_Controller = SSController('NEW', 20, 20)
    ssp = SSPersistency()
    t = _thread.start_new_thread(clientthread, (conn, New_Controller, ssp))
    n = _thread.start_new_thread(notify_handler, (conn, New_Controller))
    trds.append(t)
    trds.append(n)

for t in trds:
    t.join()

s.close()
