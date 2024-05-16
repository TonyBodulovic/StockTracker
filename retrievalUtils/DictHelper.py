def tryDictPath(dictionary: dict, path: list):

    if not isinstance(path,tuple) and not isinstance(path,list):
        if path not in dictionary:
            return None
        else:
            return dictionary[path]

    currentLevel = dictionary
    for pathItem in path:
        if pathItem not in currentLevel:
            return None
        currentLevel = currentLevel[pathItem]

    return currentLevel

