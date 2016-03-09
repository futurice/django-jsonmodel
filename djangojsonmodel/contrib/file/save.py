from djangojsonmodel.convert import logger
from djangojsonmodel.presentation.json import to_json

def json_file(c, filename):
    formjs = to_json(c);
    f = open(filename, 'w+')
    f.write("jsform = %s;" % (formjs))
    logger.debug("jsmodels(): {}".format(filename))
