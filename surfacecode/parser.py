class parser:
    def __init__(self):
        pass
        
    # parse by the end of each string(end not included)
    # with names a dictionary will be provided
    # without there will be a list of lists
    def parse(number, breakpoints, names = None):
        list = [int(d) for d in str(bin(number))[2:]]
        print(list)
        if names is None:
            output = []
            pointer = 0
            for i in breakpoints:
                temp = []
                while pointer < i:
                    temp.append(list.pop(0))
                    pointer = pointer + 1
                output.append(temp)
            return output
        else:
            output = {}
            pointer = 0
            for i in range(len(breakpoints)):
                temp = []
                while pointer < breakpoints[i]:
                    temp.append(list.pop(0))
                    pointer = pointer + 1
                output[names[i]] = temp 
            return output
        
    o = parse(31,[1,3])
    print(o)
            