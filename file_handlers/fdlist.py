
class FDlist():
    def __init__(self, paths=()):
        r'''pass in any number of paths to fdlists as arguments
        '''
        self.__contents = []
        if not(paths == () or paths == []) and paths[0]:
            for path in paths:
                with open(path, "rt") as fp:
                    self.__contents += fp.readlines()
            self.__contents = list(set(self.__contents))


    def get_list(self):
        r'''returns the contents of an FDlist as a list
        '''
        output = []
        for item in self.__contents:
            output.append(item.strip("\n"))
            
        return output
