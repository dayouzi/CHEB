def getArgMap(args):
    argMap = dict()
    for i in xrange(0, len(args), 2):
        argMap[args[i]] = args[i + 1]
    return argMap

