input_code = []
binary_code = []
file_name = "inputfile"
LC = 0
max_LC = 255
errors = []
no_error = True
error_dict={-1 : "Provided with less than required operands",
            -2 : "Label has already been initialised",
            -3 : "Label provided as variable",
            -4 : "Provided with more than required operands",
            -5 : "More operands present than required",
            -6 : "Undefined symbol",
            -7 : "Missing symbol",
            -8 : "Symbol missing in symbol table",
            -9 : "Variable provided as label",
            -10 : "Opcode missing",
            -11 : "Provided opcode as label",
            -12 : "Program longer than 255 words",
            -13 : "Provided opcode as variable",
            -14 : "Label not initialised"}

def newFile(file_name):
    try:
        f = open(file_name, 'r+')
        f.truncate(0)
    except Exception:
        f = open(file_name, 'w+')
        f.close()

def readInputFile(filename):
    inp_line = []
    fhand = open(filename + ".txt", "r")
    for line in fhand:
        line = line[0:-1]
        a = line.split(' ')
        inp_line.append(a)
        if line == 'STP':
            break
    fhand.close()
    return(inp_line)


def addError(err, problem, line_number, file_name="inputfile_error.txt"):
    error = problem + " " + error_dict[err] + "\n  "
    if line_number!=-1:
        error += "Error at line number:" + str(line_number+1)
    print(error)
    file = open(file_name, "a+")
    file.write(error + "\r\n")
    file.close()

######OPCODE TABLE########
#mneumonic:opcode,number of operands, takes variable as input or not,defines variable or not
Opcode_Table={'CLA': ('0000',0,False,False) ,'LAC':('0001',1,True,False) ,'SAC':('0010',1,True,True),
         'ADD':('0011',1,True,False),'SUB':('0100',1,True,False),'BRZ':('0101',1,False,False),
         'BRN':('0110',1,False,False),'BRP':('0111',1,False,False),'INP':('1000',1,True,True),
         'DSP':('1001',1,True,False),'MUL':('1010',1,True,False),'DIV':('1011',1,True,False),
         'STP':('1100',0,False,False)}

#if there is an error in code, negative number is returned

def getOpcodeInfo(opcode):
    if opcode not in Opcode_Table:
        return((),-1) #error
    else:
        return(Opcode_Table[opcode],0)

#####SYMBOL TABLE######

class Symbol:
    def __init__(self,name,type):
        self.Name=name
        self.Type=type

Symbol_Table={} # basically how we build the symbol table is that it is a dictionary again! It is a key value pair where the
# key is the name of the symbol and the value is the tuple of two arguments having location and type respectively.
# for example the symbol table consists of the following, where there is the symbol, the location and the type is a variable
# we add all types of things like variables, functions etc.

# labels are variables, if we provide a label as an opcode, it will obviously give an error

def addLabelAndLocation(label,location): #

    if getOpcodeInfo(label)[1]!=-1: #if we give opcode is a label which is an error , it return -11 as error
        return -11

    sym=Symbol(label,"Label")

    if sym.Name not in Symbol_Table: # if symbol table is not in the symbol table, we basically add the synbol to the symbol table
        Symbol_Table[sym.Name]=[location,sym.Type]
        return 0
    else:
        Type=Symbol_Table[sym.Name][1] #  if it is in the symbol, we cross check again with respect to the above error dictionary
        # type is basically the second argument, which is why it is 1

        if Type == ("Variable"):
            return -9 # we get an error if "Variable provided as label",

        if Type == ("Label"):
            address = Symbol_Table[sym.Name][0]
            if (address == -1):
                Symbol_Table[sym.Name][0] = location
                return 0

            return -2

def addLabel(label): #the symbol table has labels and variables basically

    if getOpcodeInfo(label)[1]!=-1:
        return -11

    sym=Symbol(label,"Label")

    if sym.Name not in Symbol_Table:
        Symbol_Table[sym.Name] = [-1, sym.Type]
        return 0

    else:
        Type = Symbol_Table[sym.Name][1]
        if Type == ("Variable"):
            return -9
        return 0

def addVariable(var): # this function basically cross checks that it is not an opcode and it is not a label, if it is not either of those things it adds the variable
    if getOpcodeInfo(var)[1]!=-1:
        return -13

    sym=Symbol(var,"Variable")

    if sym.Name in Symbol_Table:
        if sym.Type == ("Label"):
            return -3
    else:
        Symbol_Table[sym.Name] = [-1, "Variable"]
    return 0

def findSymbol(sym,type): #checks if the symbol is symbol or not
    if sym in Symbol_Table:
        if Symbol_Table[sym][1]==type:
            return True
        return False

def getLocation(sym): #
    if sym in Symbol_Table:
        return Symbol_Table[sym][0]


def removeCommentsAndColons(line): #inorder to completely remove all the comments and colons, most assembly language code have comments and colons
    colon = False # before going through the first pass, we go through this function in order to filter out all the comments and the colons, and just have the code we need for the compilation of the first pass

    for i in range(len(line)):
        if ("//" in line[i]):
            index = line[i].find("//")
            if (index == 0):
                line = line[:i]
            else:
                line = line[:i + 1]
                line[i] = line[i][:index]
            break

    for j in range(len(line)):
        if (":" in line[j]):
            colon = True
            index = line[j].find(":")
            line = line[:j] + [line[j][:index]] + [line[j][index + 1:]] + line[j + 1:]
            break

    while ('' in line):
        line.remove('')

    return line, colon


def firstPass():
    global LC
    global no_error

    for i in range(len(input_code)):
        input_code[i], has_label = removeCommentsAndColons(input_code[i]) # first function the first pass calls is the remove comments and colons.

        # input_code has > max_LC lines
        if (LC > max_LC):
            addError(-12, "CRITICAL", -1)
            no_error = False
            break

        # found a label
        if (has_label):
            error_num = addLabelAndLocation(input_code[i][0], LC) #
            if (error_num < 0):
                addError(error_num, input_code[i][0], LC)
                no_error = False

            # remove label
            input_code[i].pop(0) #when there

        # line too long
        if (len(input_code[i]) > 2):
            no_error = False

        opcode = input_code[i][0]
        opcode_info, error_num = getOpcodeInfo(opcode)

        if (error_num < 0):
            addError(error_num, input_code[i][0], LC)
            no_error = False
            LC += 1
            continue

        opcode, operands, input_var, output_var = opcode_info

        if (operands != 0):
            if (len(input_code[i][1:]) == operands):
                if (not input_var):
                    error_num = addLabel(input_code[i][1])
                else:
                    if (output_var or findSymbol(input_code[i][1], "Variable")):
                        error_num = addVariable(input_code[i][1])
                    else:
                        # symbol  not defined
                        error_num = -6

                if (error_num < 0):
                    addError(error_num, input_code[i][1], LC)
                    no_error = False
                    LC += 1
                    continue
            else:
                if (len(input_code[i][1:]) > operands):
                    # extra operands present
                    err = ""
                    for i in input_code[i][1:]:
                        err += i + " "

                    error_num = -5
                    addError(error_num, err, LC)
                else:
                    # Needs more operands
                    error_num = -1
                    addError(error_num, input_code[i][0], LC)

                if (error_num < 0):
                    no_error = False
                    LC += 1
                    continue
                    
        else:
            # can not stop in the middle
            if (opcode == "1100" and LC != len(input_code) - 1): # if
                break
            elif len(input_code[i][1:]) != 0:
                # does not need operand
                error_num = -4

            if (error_num< 0):
                addError(error_num, input_code[i][0], LC)
                no_error = False
                LC += 1
                continue
        LC += 1

    # stop not found
    if ("STP" not in input_code[-1]):
        addError(-7, "STP", LC)

    error_num = 0

    for i in Symbol_Table: # whenever we make the symbol table, we basically must go through the first pass so as to ensure that we get rid of all the errors and necessary wrong code.

        if (Symbol_Table[i][1] == "Variable"): # we go through another error check to see if the there are any errors..
            Symbol_Table[i][0] = LC
            LC += 1
            
        # label not initialized anywhere
        if (Symbol_Table[i][1] == "Label"):
            if (Symbol_Table[i][0] == -1):
                error_num = -14
        # Cannot fit in given space
        if (LC > max_LC):
            error_num = -12

        if (error_num < 0):
            addError(error_num, "CRITICAL", -1)
            no_error = False
            if (error_num == -12):
                break
    print("Instruction Table: ")
    print("Opcode   Operand")
    for i in (input_code):
        if len(i)==1:
            print(str(i[0]))
        elif (len(i))==2:
            print(str(i[0])+"        "+str(i[1]))
        elif (len(i))==3:
            print(str(i[1])+"       "+str(i[2]))
        elif (len(i)==4):
            print(str(i[2]) + "       " + str(i[3]))
    print("")
    print("Symbol Table: ")
    print("Name    Location    Type")
    for x in (Symbol_Table):
        print (str(x)+"         "+ str(Symbol_Table[x][0])+"       "+str(Symbol_Table[x][1]))
    print("")

# from the first pass we get two outputs, the symbol table and the

def secondPass():
    global input_code
    global binary_code

    for i in input_code:
        opcode_info,error_num=getOpcodeInfo(i[0])
        opcode, operands, input_var, output_var = opcode_info
        if (operands==0):
            instruction=opcode+"00000000"
        else:
            symbol_address=getLocation(i[1])
            symbol_address=bin(symbol_address)[2:]
            symbol_address="0"*(len(symbol_address))+symbol_address
            instruction=opcode+symbol_address
        binary_code.append(instruction)

def writeOutput():
    global file_name
    global binary_code
    f = open(file_name + "_Output.txt", 'a+')
    for i in binary_code:
        f.write(i)
        f.write("\r\n")
    f.close()

def main():
    global input_code
    global no_error
    global LC

    LC = 0

    newFile(file_name + "_error.txt")
    newFile(file_name + "_Output.txt")
    input_code=readInputFile(file_name)

    firstPass()
    if (no_error):
        secondPass()
    if (no_error):
        writeOutput()
        print("Output stored in inputfile_Output.txt")
    else:
        print("Error stored in inputfile_error.txt")

if __name__=="__main__":
    main()
