from django.shortcuts import render, redirect
from django.http import HttpResponse
import _thread
import socket
from threading import Thread
import time
import json
import ast
# Create your views here.

trds = {}
active_users = []
show_to_user = {}
get_command_from_user = {}
wait = False
# any_notify = [False,{}]
any_notify = {}


def client_thread(request):
    global show_to_user, get_command_from_user, wait, any_notify
    # Create a TCP/IP socket
    uname = request.session['username']
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 9595)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)

    def clientthread():
        global show_to_user, get_command_from_user, wait, any_notify
        while 1:
            lengt = sock.recv(10)
            if not lengt.strip():
                continue
            wait = True
            length = int(lengt.decode())
            data = sock.recv(length).decode()
            if 'command' in data:
                parsed_data = json.loads(data)
                print(parsed_data)
                for au in active_users:
                    any_notify[au] = [True, parsed_data]
            if get_command_from_user[uname] == '{"command" : "get_cells"}' and type(ast.literal_eval(data)[0]) == list:
                wait = False
            show_to_user[uname]['response'] = data
            wait = False
    _thread.start_new_thread(clientthread, ())
    while 1:
        time.sleep(0.05)
        if get_command_from_user[uname] == 'kill':
            break
        if get_command_from_user[uname] is not False:
            lengt = '{:10d}'.format(len(get_command_from_user[uname]))
            sock.send(lengt.encode())
            sock.send(get_command_from_user[uname].encode())
            get_command_from_user[uname] = False


def notifychecker(request):
    global any_notify
    uname = request.session['username']
    extras = ''
    checker = True
    try:
        any_notify[uname][0]
    except:
        checker = False
    if checker is False or any_notify[uname][0] is False:
        return HttpResponse('{"result":"nothing"}')
    elif checker:
        any_notify[uname][0] = False
        if "set" in any_notify[uname][1]['command']:
            get_command_from_user[
                uname] = '{"command" : "get_cells", "parameter" : "ALL"}'
            time.sleep(0.2)
            try:
                result = ast.literal_eval(show_to_user[uname]['response'])
            except:
                time.sleep(0.2)
                result = ast.literal_eval(show_to_user[uname]['response'])
            extras = '<table class="table table-striped"><tbody>'
            for r in result:
                extras += '<tr>'
                for c in r:
                    extras += '<td style="border:solid black 1px;">'
                    if c != ',':
                        extras += str(c)
                    extras += '</td>'
                extras += '</tr>'
            extras += '</tbody></table>'
            extras = str.replace(extras, '"', "'")
            return HttpResponse('{"result":"table", "extras":" ' + extras + '"}')
        elif "name" in any_notify[uname][1]['command']:
            return HttpResponse('{"result":"get_name", "extras":" ' + extras + '"}')
        elif 'newss' in any_notify[uname][1]['command']:
            get_command_from_user[
                uname] = '{"command" : "get_cells", "parameter" : "ALL"}'
            time.sleep(0.2)
            try:
                result = ast.literal_eval(show_to_user[uname]['response'])
            except:
                time.sleep(0.2)
                result = ast.literal_eval(show_to_user[uname]['response'])
            extras = '<table class="table table-striped"><tbody>'
            for r in result:
                extras += '<tr>'
                for c in r:
                    extras += '<td style="border:solid black 1px;">'
                    if c != ',':
                        extras += str(c)
                    extras += '</td>'
                extras += '</tr>'
            extras += '</tbody></table>'
            extras = str.replace(extras, '"', "'")
            return HttpResponse('{"result":"table", "extras":" ' + extras + '"}')
        else:
            return HttpResponse('{"result":"", "extras":" ' + extras + '"}')


def index(request):
    uname = False
    if 'username' in request.session:
        uname = request.session['username']
    context = {'uname': uname}
    return render(request, 'index.html', context)


def login(request):
    global active_users, show_to_user
    uname = ""
    if request.method == 'POST':
        uname = request.POST['your_name']
        request.session['username'] = uname
    show_to_user[uname] = {'init': '[]', 'type': 'none'}
    if request.method == 'POST':
        return redirect('new')
    return render(request, 'login.html')


def logout(request):
    global trds, get_command_from_user, active_users
    # active_users.remove(request.session['username'])
    get_command_from_user[request.session['username']] = 'kill'
    request.session['username'] = False
    return redirect('index')


def listmem(request):
    global get_command_from_user, show_to_user, wait
    uname = request.session['username']
    get_command_from_user[uname] = '{"command" : "listmem"}'
    show_to_user[uname]['type'] = 'listmem'
    extra = ''
    resp_type = 'listmem'
    command = 'listmem'
    time.sleep(0.2)
    if resp_type == 'nestedlist' or resp_type == 'listmem' or resp_type == 'listdb':
        show_to_user[uname]['response'] = ast.literal_eval(
            show_to_user[uname]['response'])
    if command == 'listmem' or command == 'listdb':
        show_to_user[uname]['response'] = [
            i.split(' ') for i in show_to_user[uname]['response']]
    context = {'uname': uname, 'result': show_to_user[uname], 'extra': extra}
    return render(request, 'listmem.html', context)


def listdb(request):
    global get_command_from_user, show_to_user, wait
    uname = request.session['username']
    show_to_user[uname]['type'] = 'listdb'
    get_command_from_user[uname] = '{"command" : "list"}'
    extra = ''
    resp_type = 'listmem'
    command = 'listmem'
    time.sleep(0.2)
    if resp_type == 'nestedlist' or resp_type == 'listmem' or resp_type == 'listdb':
        show_to_user[uname]['response'] = ast.literal_eval(
            show_to_user[uname]['response'])
    if command == 'listmem' or command == 'listdb':
        show_to_user[uname]['response'] = [
            i.split(' ') for i in show_to_user[uname]['response']]
    context = {'uname': uname, 'result': show_to_user[uname], 'extra': extra}
    return render(request, 'listdb.html', context)


def get_command_ajax(request, command):
    global get_command_from_user, show_to_user, wait
    uname = request.session['username']
    if command == "get_cells":
        show_to_user[uname]['type'] = 'nestedlist'
        get_command_from_user[
            uname] = '{"command" : "get_cells", "parameter" : "ALL"}'
    if command == "delete_single_db":
        sid = request.POST['sid'].strip()
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "clearsingledb", "parameter" :" ' + str(sid) + '"}'
    if command == "get_id":
        show_to_user[uname]['type'] = 'string'
        get_command_from_user[uname] = '{"command" : "getId"}'
    if command == "get_name":
        show_to_user[uname]['type'] = 'string'
        get_command_from_user[uname] = '{"command" : "get_name"}'
    if command == 'evaluate':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '''{"command" : "evaluate"}'''
    if command == 'upload_ankara':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '''{"command" : "upload", "parameter": "Ankara,,,,\\n,,Increase,,\\nYear,People,Number,Percentage,If increase greater than 2%\\n2000,3889199,,,\\n2001,3971642,=B5-B4,=C5/B4*100,=IF(D5>2; 'High'; 'Low')\\n2002,4050309,=B6-B5,=C6/B5*100,=IF(D6>2; 'High'; 'Low')\\n2003,4128889,=B7-B6,=C7/B6*100,=IF(D7>2; 'High'; 'Low')\\n2004,4210596,=B8-B7,=C8/B7*100,=IF(D8>2; 'High'; 'Low')\\n2005,4294678,=B9-B8,=C9/B8*100,=IF(D9>2; 'High'; 'Low')\\n2006,4380736,=B10-B9,=C10/B9*100,=IF(D10>2; 'High'; 'Low')\\n2007,4466756,=B11-B10,=C11/B10*100,=IF(D11>2; 'High'; 'Low')\\n2008,4548939,=B12-B11,=C12/B11*100,=IF(D12>2; 'High'; 'Low')\\n2009,4650802,=B13-B12,=C13/B12*100,=IF(D13>2; 'High'; 'Low')\\n2010,4771716,=B14-B13,=C14/B13*100,=IF(D14>2; 'High'; 'Low')\\n2011,4890893,=B15-B14,=C15/B14*100,=IF(D15>2; 'High'; 'Low')\\n2012,4965542,=B16-B15,=C16/B15*100,=IF(D16>2; 'High'; 'Low')\\n2013,5045083,=B17-B16,=C17/B16*100,=IF(D17>2; 'High';'Low')\\n2014,5150072,=B18-B17,=C18/B17*100,=IF(D18>2; 'High'; 'Low')\\n2015,5270575,=B19-B18,=C19/B18*100,=IF(D19>2; 'High'; 'Low')\\n2016,5346518,=B20-B19,=C20/B19*100,=IF(D20>2; 'High'; 'Low')\\n,,,,\\nAverage,=AVERAGE(B4:B20),,,\\n# of Hi years,=COUNTIF(E5:E20;'High'),,,\\n,,,,\\n,sum,diff,check,\\nfrom 00 to 16,=SUM(C5:C20),=B20-B4,=IF(B26=C26;1;0),"}'''
    if command == 'load_mem':
        sid = request.POST['sid'].strip()
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "load_mem","parameter" : " ' + str(sid) + '"}'
    if command == 'load_db':
        sid = request.POST['sid'].strip()
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "load","parameter" : " ' + str(sid) + '"}'
    if command == 'listmem':
        get_command_from_user[uname] = '{"command" : "listmem"}'
        show_to_user[uname]['type'] = 'listmem'
    if command == 'set_name':
        show_to_user[uname]['type'] = 'none'
        sname = request.POST['sname']
        get_command_from_user[
            uname] = '{"command" : "set_name","parameter" : "' + sname + '"}'
    if command == 'get_cells_range':
        show_to_user[uname]['type'] = 'nestedlist'
        range = request.POST['range']
        get_command_from_user[
            uname] = '{"command" : "get_cells", "parameter" : "' + range + '"}'
    if command == 'set_cell':
        show_to_user[uname]['type'] = 'none'
        type_of_cell = request.POST['type']
        value_of_cell = request.POST['value']
        addr_of_cell = request.POST['cell']
        if type_of_cell == 'formula':
            get_command_from_user[
                uname] = '{"command": "set_cell_formula", "parameter": ["' + addr_of_cell + '", "' + value_of_cell + '"]}'
        else:
            get_command_from_user[
                uname] = '{"command": "set_cell_value", "parameter": ["' + addr_of_cell + '", "' + value_of_cell + '"]}'
    if command == 'listdb':
        show_to_user[uname]['type'] = 'listdb'
        get_command_from_user[uname] = '{"command" : "list"}'
    if command == 'cleardb':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '{"command" : "cleardb"}'
    if command == 'save':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '{"command" : "save"}'
    if command == 'cut':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "cut_range", "parameter":"' + request.POST['rangecell'] + '"}'
    if command == 'copy':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "copy_range", "parameter":"' + request.POST['rangecell'] + '"}'
    if command == 'paste':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "paste_range", "parameter":"' + request.POST['rangecell'] + '"}'
    if command == 'file_upload':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '{"command" : "upload"}'
        myfile = request.FILES['myfile']
        contentstring = ''
        for chunk in myfile.chunks():
            contentstring += chunk.decode()
        tosend = str.replace(contentstring, '"', "'")
        tosend = repr(tosend)
        tosend = str.replace(tosend, r"\r\n", r"\n")
        tosend = tosend[1:-1]
        get_command_from_user[
            uname] = '{"command" : "upload", "parameter": "' + tosend + '"}'
    # print(get_command_from_user[uname])
    resp_type = show_to_user[uname]['type']
    time.sleep(0.2)
    while wait:
        time.sleep(0.1)
    if resp_type == 'nestedlist' or resp_type == 'listmem' or resp_type == 'listdb':
        show_to_user[uname]['response'] = ast.literal_eval(
            show_to_user[uname]['response'])
    if command == 'listmem' or command == 'listdb':
        show_to_user[uname]['response'] = [
            i.split(' ') for i in show_to_user[uname]['response']]
    if command == 'get_cells_range':
        context = {'uname': uname, 'result': show_to_user[uname], 'extra': ''}
        return render(request, 'getrange.html', context)
    else:
        return HttpResponse(show_to_user[uname]['response'])


def get_command(request, command):
    global get_command_from_user, show_to_user, wait
    uname = request.session['username']
    if command == "get_cells":
        show_to_user[uname]['type'] = 'nestedlist'
        get_command_from_user[
            uname] = '{"command" : "get_cells", "parameter" : "ALL"}'
    if command == "get_id":
        show_to_user[uname]['type'] = 'string'
        get_command_from_user[uname] = '{"command" : "getId"}'
    if command == 'evaluate':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '''{"command" : "evaluate"}'''
    if command == 'upload_ankara':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '''{"command" : "upload", "parameter": "Ankara,,,,\\n,,Increase,,\\nYear,People,Number,Percentage,If increase greater than 2%\\n2000,3889199,,,\\n2001,3971642,=B
        5-B4,=C5/B4*100,=IF(D5>2; 'High'; 'Low')\\n2002,4050309,=B6-B5,=C6/B5*100,=IF(D6>2; 'High'; 'Low')\\n2003,4128889,=B7-B6,=C7/B6*100,=IF(D7>2; 'High'; 'Low')\\n2004,4210596,=B8-B7,=C8/B7*100,=I
        F(D8>2; 'High'; 'Low')\\n2005,4294678,=B9-B8,=C9/B8*100,=IF(D9>2; 'High'; 'Low')\\n2006,4380736,=B10-B9,=C10/B9*100,=IF(D10>2; 'High'; 'Low')\\n2007,4466756,=B11-B10,=C11/B10*100,=IF(D11>2; 'H
        igh'; 'Low')\\n2008,4548939,=B12-B11,=C12/B11*100,=IF(D12>2; 'High'; 'Low')\\n2009,4650802,=B13-B12,=C13/B12*100,=IF(D13>2; 'High'; 'Low')\\n2010,4771716,=B14-B13,=C14/B13*100,=IF(D14>2; 'High
        '; 'Low')\\n2011,4890893,=B15-B14,=C15/B14*100,=IF(D15>2; 'High'; 'Low')\\n2012,4965542,=B16-B15,=C16/B15*100,=IF(D16>2; 'High'; 'Low')\\n2013,5045083,=B17-B16,=C17/B16*100,=IF(D17>2; 'High';
        'Low')\\n2014,5150072,=B18-B17,=C18/B17*100,=IF(D18>2; 'High'; 'Low')\\n2015,5270575,=B19-B18,=C19/B18*100,=IF(D19>2; 'High'; 'Low')\\n2016,5346518,=B20-B19,=C20/B19*100,=IF(D20>2; 'High'; 'Lo
        w')\\n,,,,\\nAverage,=AVERAGE(B4:B20),,,\\n# of Hi years,=COUNTIF(E5:E20;'High'),,,\\n,,,,\\n,sum,diff,check,\\nfrom 00 to 16,=SUM(C5:C20),=B20-B4,=IF(B26=C26;1;0),"}'''
    if command == 'load_mem':
        sid = request.POST['sid'].strip()
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "load_mem","parameter" : " ' + str(sid) + '"}'
    if command == 'load_db':
        sid = request.POST['sid'].strip()
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "load","parameter" : " ' + str(sid) + '"}'
    if command == 'listmem':
        get_command_from_user[uname] = '{"command" : "listmem"}'
        show_to_user[uname]['type'] = 'listmem'
    if command == 'set_name':
        show_to_user[uname]['type'] = 'none'
        sname = request.POST['sname']
        get_command_from_user[
            uname] = '{"command" : "set_name","parameter" : "' + sname + '"}'
    if command == 'get_cells_range':
        show_to_user[uname]['type'] = 'nestedlist'
        range = request.POST['range']
        get_command_from_user[
            uname] = '{"command" : "get_cells", "parameter" : "' + range + '"}'
    if command == 'set_cell':
        show_to_user[uname]['type'] = 'none'
        type_of_cell = request.POST['type']
        value_of_cell = request.POST['value']
        addr_of_cell = request.POST['cell']
        if type_of_cell == 'formula':
            get_command_from_user[
                uname] = '{"command": "set_cell_formula", "parameter": ["' + addr_of_cell + '", "' + value_of_cell + '"]}'
        else:
            get_command_from_user[
                uname] = '{"command": "set_cell_value", "parameter": ["' + addr_of_cell + '", "' + value_of_cell + '"]}'
    if command == 'listdb':
        show_to_user[uname]['type'] = 'listdb'
        get_command_from_user[uname] = '{"command" : "list"}'
    if command == 'cleardb':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '{"command" : "cleardb"}'
    if command == 'save':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '{"command" : "save"}'
    if command == 'cut':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "cut_range", "parameter":"' + request.POST['rangecell'] + '"}'
    if command == 'copy':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "copy_range", "parameter":"' + request.POST['rangecell'] + '"}'
    if command == 'paste':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[
            uname] = '{"command" : "paste_range", "parameter":"' + request.POST['rangecell'] + '"}'
    if command == 'file_upload':
        show_to_user[uname]['type'] = 'none'
        get_command_from_user[uname] = '{"command" : "upload"}'
        myfile = request.FILES['myfile']
        contentstring = ''
        for chunk in myfile.chunks():
            contentstring += chunk.decode()
        tosend = str.replace(contentstring, '"', "'")
        tosend = repr(tosend)
        tosend = str.replace(tosend, r"\r\n", r"\n")
        tosend = tosend[1:-1]
        get_command_from_user[
            uname] = '{"command" : "upload", "parameter": "' + tosend + '"}'
    # print(get_command_from_user[uname])
    resp_type = show_to_user[uname]['type']
    time.sleep(0.2)
    while wait:
        time.sleep(0.1)
    if resp_type == 'nestedlist' or resp_type == 'listmem' or resp_type == 'listdb':
        show_to_user[uname]['response'] = ast.literal_eval(
            show_to_user[uname]['response'])
    if command == 'listmem' or command == 'listdb':
        show_to_user[uname]['response'] = [
            i.split(' ') for i in show_to_user[uname]['response']]
    if command in ['evaluate', 'cleardb', 'upload_ankara', 'load_db', 'load_mem', 'set_name', 'set_cell']:
        return redirect('/get_command/get_cells')
    else:
        return redirect('new')
# sudo fuser  -k 9595/tcp


def new(request, extra=None):
    global active_users, get_command_from_user, show_to_user, trds
    uname = request.session['username']
    if not uname:
        return redirect('login')
    if uname in active_users:
        pass
    else:
        active_users.append(uname)
        t = Thread(target=client_thread, args=(request,))
        t.start()
        trds[uname] = t
        get_command_from_user[uname] = False
        return redirect('/get_command/get_cells/')
    if extra == 'set_name' or extra == 'get_cells_range' or extra == 'file_upload' \
            or extra == 'cut' or extra == 'copy' or extra == 'paste':
        show_to_user[uname]['type'] = None
    get_command_from_user[uname] = False
    context = {'uname': uname, 'result': show_to_user[uname], 'extra': extra}
    return render(request, 'new.html', context)
