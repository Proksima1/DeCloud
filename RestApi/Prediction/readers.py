
def readS3Keys(fileName: str) -> map:
    """
        This function reades the key for an s3 client and returns a map with keys "key_id", "key", "region", "bucket_name".\n
        If the file does not exist or if it is in the wrong format this function returns None.\n
        The file must exist in resources folder of the project and must consist of:\n
        1) ACCESS_KEY_ID;\n
        2) SECRET_ACCESS_KEY;\n
        3) YOUR_AWS_REGION;\n
        4) BUCKET_NAME;\n 
    """
    fileName = "../../../resources/" + fileName
    retMap = map()
    with open(fileName) as out:
        try:
            retMap["key_id"] = out.readline(0)
            retMap["key"] = out.readline(1)
            retMap["region"] = out.readline(2)
            retMap["bucket_name"] = out.readline(3)
        except:
            return None
    return retMap