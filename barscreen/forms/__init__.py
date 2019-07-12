"""

Some notes regarding forms.


__fnattr__:

Use __fnattr__ if you want to set a custom filename field instead of using form.file.data.filename() when saving the file locally.
This is primarily used when uploading channels, clips, and promos. As we don't want to upload the file to google storage under whatever
the user uploaded it, instead usually setting __fnattr__ to the name of the uploaded channel/clip/promo.

e.g:
class TestForm():
    __fnattr__ = "channel_name"



__fileattr__:

Since many forms have 1 file upload by many many different attribute names, use this to specify what it is.
e.g:
class TestForm():
    __fileattr__ = "promo_file"

"""
import logging
import os
import traceback
from werkzeug.utils import secure_filename

from flask import current_app
from flask_wtf import FlaskForm



class BSFileForm(FlaskForm):
    """
    Custom Barscreen file form.

    Only difference is a better way to save files locally/name
    them correctly using both __attrs.
    """

    __fnattr__   = None
    __fileattr__ = None

    def get_original_filename(self):
        """
        Used to get the original filename of the uploaded file in the __fileattr__.
        """
        assert self.__fileattr__, "No __fileattr__ set, unable to determine file name."
        # Get file obj.
        f = getattr(self, self.__fileattr__)
        return f.data.filename
    
    def get_file_extension(self):
        """
        Returns the file extension of uploaded file using __fileattr__.
        """
        assert self.__fileattr__, "No __fileattr__ set, unable to determine file extension."
        # Get file obj.
        f = getattr(self, self.__fileattr__)
        # Return file extension of filename.
        return f.data.filename.split(".")[-1]

    def save_uploaded_file(self, upload_dir=None):
        """
        Saves the forms uploaded file, uses __fileattr__ to determine what
        that is from form to form.
        """
        try:
            # Get path, defaulting to app config upload_dir.
            if not upload_dir:
                upload_dir = current_app.config["UPLOAD_DIR"]
            
            filename = None
            # Check for __fnattr__ for custom filenaming.
            if self.__fnattr__:

                # Create new filename from __fnattr__ and the original file extension.
                filename = secure_filename(".".join([getattr(self, self.__fnattr__).data, self.get_file_extension()]))

            # No __fnattr__, use original filename.
            else:
                filename = secure_filename(self.get_original_filename())
            
            # Determine the full path of the to-be-saved file.
            full_path = os.path.join(upload_dir, filename)

            # Save file and return the full path.
            getattr(self, self.__fileattr__).data.save(full_path)
            return full_path
        
        # If any error arises, log it and return False status.
        except Exception as err:
            logging.error("Unable to upload file: {}: {}\n{}".format(type(err), err, traceback.format_exc()))
            return False

        

            