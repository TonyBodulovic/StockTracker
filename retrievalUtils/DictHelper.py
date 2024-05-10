def tryDictPath(dictionary: dict, path: list):

    currentLevel = dictionary

    for pathItem in path:
        if pathItem not in currentLevel:
            return None
        currentLevel = currentLevel[pathItem]

    return currentLevel

