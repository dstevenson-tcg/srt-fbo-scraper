import logging
import os
from zipfile import ZipFile, BadZipfile

import textract

logger = logging.getLogger(__name__)

def get_doc_text(file_name, rm = True):
    """Textract a doc given its path
    
    Arguments:
        file_name {str} -- path to a doc
    """
    try:
        b_text = textract.process(file_name, encoding = 'utf-8', errors = 'ignore')
    #ShellError with antiword occurs when an rtf is saved with a doc extension
    except textract.exceptions.ShellError as e:
        err_message = str(e)
        if 'antiword' in err_message and file_name.endswith('.doc'):
            new_name = file_name.replace('.doc','.rtf')
            os.rename(file_name, new_name)
            b_text = textract.process(new_name, 
                                      encoding = 'utf-8', 
                                      errors = 'ignore')
    except textract.exceptions.MissingFileError as e:
        b_text = None
        logger.error(f"Couldn't textract {file_name} since the file couldn't be found: \
                     {e}", exc_info=True)
    #This can be raised when a pdf is incorrectly saved as a .docx (GH183)
    except BadZipfile as e:
        if file_name.endswith('.docx'):
            new_name = file_name.replace('.docx','.pdf')
            os.rename(file_name, new_name)
            b_text = textract.process(new_name, 
                                      encoding = 'utf-8', 
                                      method = 'pdftotext', 
                                      errors = 'ignore')
        else:
            b_text = None
            logger.error(f"Exception occurred textracting {file_name}:  \
                         {e}", exc_info=True)
    #TypeError is raised when None is passed to str.decode()
    #This happens when textract can't extract text from scanned documents
    except TypeError:
        b_text = None
    except Exception as e:
        logger.error(f"Exception occurred textracting {file_name}:  \
                     {e}", exc_info=True)
        b_text = None
    text = b_text.decode('utf8', errors = 'ignore').strip() if b_text else ''
    if rm:
        try:
            os.remove(file_name)
        except:
            logger.error(f"{e}Unable to remove {file_name}", exc_info = True)
        finally:
            return text
    
    return text