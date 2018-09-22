"""6.009 Lab 8B: carlae Interpreter"""

import sys


class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass



def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    lines = source.split('\n')
    counter = 0
    for each in lines:
        if ';' in each:
            each = each[:each.index(';')] #will truncate off comment
            lines[counter] = each
        lines[counter] += '\n'
        counter += 1
    stringer= ''
    for line in lines:
        stringer += line
    return stringer.replace("(", " ( ").replace(")", " ) ").split() #create spacing that can be split at spaces

def isValid(tokens):

    net_parantheses = 0
    for token in tokens:
        if token == "(":
            net_parantheses+=1
        elif token == ")":
            net_parantheses-=1
        if net_parantheses<0: #there should never be more ) than ( at any point
            return False
    if net_parantheses != 0: #at the end there should be an equal number of parantheses
        return False
    if "(" not in tokens and ")" not in tokens:
        if len(tokens) > 1:
            return False
    return True

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-rests are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def streamline(tokens):
        answer = []
        for index, token in enumerate(tokens):
            try:
                if "." in token:
                    tokens[index] = float(token)
                else:
                    tokens[index] = int(token)
            except:
                tokens[index] = token
    def parsehelper(tokens):

        if ")" not in tokens: #everything was parsed
            return tokens[0] #this is the parsed expression
        for i in range(len(tokens)):
            if tokens[i] == ")": #find first instance of )
                end_index = i
                for j in range(end_index, -1, -1):
                    start_index = j
                    if tokens[j] == "(": #find matching (
                        parsed = tokens[start_index+1:end_index]
                        break
                break
            else:
                end_index = i

        beginning = tokens[:start_index] #tokens up until the parsed expression
        if len(beginning) == 0: #parsed through all the tokens
            return parsed
        beginning.append(parsed)
        return parsehelper(beginning + tokens[end_index+1:]) #parse the tokens with the old expression replaced by the parsed one

    if tokens[0] == "(" and tokens[-1] != ")":
        raise SyntaxError
    if len(tokens) >1 and tokens[-1] != ")":
        raise SyntaxError

    if len(tokens) > 1 and tokens[0] != "(": #anything beyond a single number of varialbe needs proper parentheses
        raise SyntaxError

    if not isValid(tokens):
        raise SyntaxError

    streamline(tokens)
    return parsehelper(tokens)

def multiply(input):
    temp = 1
    for each in input:
        temp *= each
    return temp

def divide(input):
    temp = input[0]
    rest = input[1:]
    for each in rest:
        temp /= each
    return temp

def equal_to(input):
    for i in input:
        for x in input[1:]:
            if i != x:
                return False
    return True

def greater_than(input):
    input2 = sorted(set(input), reverse = True) #remove duplicates, sort into list with greatest first
    if input2 == input and len(input2) == len(input): #check that it was already ordered
        return True
    return False

def greater_than_or_equal(input):
    #same as above, but can have repeats
    input2 = sorted(set(input), reverse = True)
    if input2 == input:
        return True
    return False

def less_than(input): #same as greater than, except don't reveserse sorted list
    input2 = sorted(set(input)) #remove duplicates, sort into list with greatest first
    if input2 == input and len(input2) == len(input): #check that it was already ordered
        return True
    return False

def less_than_equal(input):
    input2 = sorted(input)
    if input2 == input:
        return True
    return False


def NOT(input):
    return not input[0] #inverse of first argument passed in

def LIST(input):
    if len(input) == 0:
        return 'nil'
    car = input[0]
    cdr = LIST(input[1:])
    return Pair(car, cdr)

def car(input):
    if input[0] == "nil":
        raise EvaluationError
    else:
        return input[0]["car"]

def cdr(input):
    return input[0]['cdr']

def cons(input):
    return Pair(input[0], input[1])#make new Pair object with car and cdr as the two elements direclty behind beginning

def length(input):
    if input[0] == "nil": #empty list always has length of 0
        return 0
    if isinstance(input[0], Pair): #checks to make sure its proper type
        if input[0]['cdr'] == 'nil':
            return 1 #now go to surface, incrementing for each recursive call
        return 1 + length([input[0]['cdr']])

    else:
        raise EvaluationError
def index(input, i = None, counter = 0):
    if len(input) > 1:
        i = input[1]
    if isinstance(input[0], Pair): #checks to make sure its proper type
        if counter ==i:
            return (input[0]['car'])
        else:
            return index([input[0]['cdr']], i, counter+1)
    else:
        raise EvaluationError

def concat(input):
    def helper (first, second):
        if first['cdr'] != 'nil':
            return Pair(first['car'], helper(first['cdr'], second)) #go deeper
        return Pair(first['car'], second)

    for each in input:
        if not isinstance(each, Pair) and not isinstance(each, str):
            raise EvaluationError
        if isinstance(each, Pair) and type(each['cdr']) == int: #(concat (cons 1 2) (cons 3 4))
            raise EvaluationError
    if len(input) ==0:
        return 'nil'
    input = [arg for arg in input if arg != 'nil']
    if len(input) == 1:
        return Pair(input[0]['car'], input[0]['cdr']) #make new Pair object that is exactly the sme as input

    try:
        result = input[0]
        for i in range(len(input)): #concat first two, and then that sum with the third, and so on
            result = helper(result, input[i+1])
            if i == len(input) - 2:
                    return result
    except:
        EvaluationError



carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': multiply,
    '/': divide,
    "#t": True,
    "#f": False,
    "=?": equal_to,
    ">": greater_than,
    ">=": greater_than_or_equal,
    "<": less_than,
    "<=": less_than_equal,
    "not": NOT,
    'nil': 'nil',
    'list': LIST,
    'car': car,
    'cdr': cdr,
    'cons': cons,
    'length': length,
    'elt-at-index': index,
    'concat': concat,

}


class Environment():
    def __init__ (self, parent = carlae_builtins): #optional input so that the first enviorment has a parent class
        self.enviro = {} #env is a dictionary with highest parent class already input
        self.parent = parent
    def __setitem__(self, variable, value):
        self.enviro[variable]= value
    def __getitem__(self, variable): #when you want to create a new environment
        if variable in self.enviro: #you have it on hand
            return self.enviro[variable]
        elif variable not in self.enviro and variable in carlae_builtins: #you dont have it, but its in builtins
            return carlae_builtins[variable]
        elif self.parent == carlae_builtins and variable not in carlae_builtins:
            raise EvaluationError
        return self.parent[variable] #recurse on parent environment
    def __str__(self):
        return str(self.enviro)
    def set(self,key,input):
        if key not in self.enviro.keys():
            self.parent.set(key,input) #try setting
        else:
            self[key]=input #use __setitem__ function

class Lamb():
    def __init__(self, env, parms, func):
        self.env = env #pointer to Environment object in which the functino was defined
        self.parms = parms #list of function's parameters
        self.func = func #code representing body of function as list
    def __call__(self, arguments): #how to get arguements here
        new = Environment(self.env) #old environment becomes parent
        if len(self.parms) > len(arguments) or len(self.parms) < len(arguments): #mismatched number of arguments
            raise EvaluationError
        for i, each in enumerate(self.parms): #input local vars into  parameters
            new[each] = arguments[i]
        return result_and_env(self.func, new)[0] # by calling the user-defined function, you return its evaluation with a new enviroment that consists of the defined parameters, the arguemtns, and a parent class??

class Pair:
    def __init__(self, car, cdr):
        self.car = car #env[car] #evaluate elements in the enviornment in which cons is called
        self.cdr = cdr #same as above
    def __str__(self):
        return "(cons "+ str(self.car) + " " + str(self.cdr) + ")"
    def setCDR(self, cdr):
        self.cdr = cdr

    def append(self, obj):
        if obj != 'nil':
            if not isinstance(obj,Pair):
                obj=Pair(obj,'nil')
            if self != 'nil':
                if self.cdr != 'nil':
                    self.cdr.append(obj)
                else:
                    self.cdr=obj
            else:
                self.car=obj.car
                self.cdr=obj.cdr

    def __getitem__(self, input):
        if input == 'car':
            return self.car
        elif input == 'cdr':
            return self.cdr
        else:
            raise EvaluationError

    def __iter__(self):
        while self != 'nil':
            yield self.car #pop off the car element
            self = self.cdr #go deeper through linked list

def result_and_env(tree, env= None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if env is None:
        env = Environment()

    if tree == []:
        raise EvaluationError

    if type(tree) == list and (type(tree[0]) == int or type(tree[0]) == float): #eg [1 2]
        raise EvaluationError
    if type(tree) == int or type(tree) == float: #just a number
        return tree, env
    if len(tree) == 1 and type(tree[0]) == int or type(tree[0]) == float: #
        return tree[0], env
    if type(tree) == str: #either an operator or a custom variable name
        if tree in carlae_builtins.keys():  #simple operator
            return tree, env
        return env[tree], env

    beginning = tree[0]

    if beginning =='reduce':
        update = result_and_env(tree[3],env)[0]
        if result_and_env(tree[2],env)[0] == 'nil':
            return update, env
        for each in result_and_env(tree[2],env)[0]:
            if update == 'nil':
                udpate = 'nil'
            update = result_and_env([tree[1], update, each],env)[0]
        return update, env


    if beginning=='map':
        outcome='nil'
        update=result_and_env(tree[2],env)[0]
        if update == 'nil':
            return outcome, env
        if not isinstance(update,Pair):
            raise EvaluationError
        for each in update:
            expression = [tree[1], each]
            if outcome == 'nil':
                outcome = Pair(result_and_env(expression, env)[0],'nil') #how to evaluate elem??
            else:
                outcome.append(Pair(result_and_env(expression,env)[0],'nil'))
        return outcome, env

    if beginning=='filter':
        result= 'nil'
        if result_and_env(tree[2],env)[0] == 'nil':
            return result, env
        for each in result_and_env(tree[2],env)[0]:
            if result_and_env([tree[1],each],env)[0]:
                if result != 'nil':
                    result.append(Pair(each,'nil'))
                else:
                    result = Pair(each, 'nil')
        return result, env

    if beginning=='set!':
        if not env[tree[1]]:
            raise EvaluationError
        else:
            outcome = result_and_env(tree[2],env)[0]
            env.set(tree[1], outcome) #update binding
            return outcome, env

    if beginning=='let':
        local = Environment(env)
        for each in tree[1]:
            local[each[0]] = result_and_env(each[1], env)[0]
        return result_and_env(tree[2], local)[0], env

    if type(beginning) is list:
        env['temp'] = result_and_env(beginning, env)[0]
        beginning = 'temp'

    if beginning == 'define':
        if isinstance(tree[1], list): #"easier function"
            tree = ["define", tree[1][0], ["lambda", tree[1][1:], tree[2]]]
            return result_and_env(tree, env)
        var = tree[1] #first non-operator element
        val = result_and_env(tree[2], env)[0]
        env[var] = val #call to setter
        return val, env

    if beginning == "lambda":
        return Lamb(env, tree[1], tree[2]), env

    if beginning =='begin':
        storage = []
        for each in tree[1:]:
            storage.append(result_and_env(each, env)) #evaluate each of the subfunctions
        return storage[-1] #return the last one first

    if beginning == 'if':
        conditional = tree[1] #first thing after 'if'
        true_expression = tree[2] #true expression
        false_expression = tree[3] #false expression
        if result_and_env(conditional, env)[0] is True or result_and_env(conditional, env)[0] == "#t": #if there is a valid return expression
            return result_and_env(true_expression, env)
        else: #otherwise return the flase outcome
            return result_and_env(false_expression, env)

    if beginning == "and":
        for each in tree[1:]: #loop through each conditional literal, if one is false, the whole thing is fails
            status = result_and_env(each, env)[0]
            if status ==False:
                return False, env
        return True, env

    if beginning == "or":
        for each in tree[1:]: #loop thorugh every conditional literal, if one is true, then the expressin evaluates to true
            status = result_and_env(each, env)[0]
            if status == True:
                return True, env
        return False, env

    operation = env[beginning]
    arguments = []
    for each in tree[1:]:
        add = result_and_env(each, env)[0]
        arguments.append(add)
    if operation in carlae_builtins.keys(): #if we made a function of a built-in function
        return carlae_builtins[operation](arguments), env
    else:
        return operation(arguments), env


def evaluate(tree, env = None):
    return result_and_env(tree, env)[0]

def evaluate_file(string, env = None):
    with open (string, "r") as myfile:
        myfile = myfile.read()
        return result_and_env(parse(tokenize(myfile)), env)[0]

if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    env = Environment()
    for filename in sys.argv[1:]:
        evaluate_file(filename, env)
        print("Successfully imported:", filename)
    while True: #infinite loop
        try:
            expression = input('IN: ')
            if expression == 'quit':
                break
            #print(parse(tokenize(expression)))
            print('\n        OUT: ', result_and_env(parse(tokenize(expression)), env)[0])
        except:
            print("Invalid input. Please try again.")
            continue
