#!/usr/bin/python
import subprocess
import re

class ZimbraNumberSync(object):
    DEBUG = True
    filename = None
    file_content = None

    def __init__(self, debug=False, filename=None, file_content=None):
        self.debug = debug
        if self.debug:
            if not filename and not file_content:
                raise Exception("When running in debug mode, filename is required")
            elif filename:
                self.filename = filename
            elif file_content:
                self.file_content = file_content

    
    def get_output_from_zimbra(self):
        zmprov_out = subprocess.Popen(['/opt/zimbra/bin/zmprov', '-l', 'gaa', '-v'], stdout=subprocess.PIPE)
        grepped = subprocess.Popen(['/bin/grep', '-E', '^\# name |mobile:|telephoneNumber:'],
                        stdin=zmprov_out.stdout,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        out,err = grepped.communicate()
        return out

    def get_output_from_file(self, filename=None):
        return open(filename, 'rb').read()

    def parse_name_to_email(self, input_line):
        found = False
        m = re.search('# name (.*)', input_line)
        if m:
            found = m.group(1)
        return found

    def format_output(self, file_content):
        ret_list = []
        the_lines = file_content.split("\n")
        for line in the_lines:
            if line != '':
                ret_list.append(line)
        return ret_list

    def get_zimbra_output(self, filename):
        if self.DEBUG == True:
            return self.format_output(self.get_output_from_file(filename))
        else:
            return self.format_output(self.get_output_from_zimbra())

    def get_starting_index(self, email, file_list):
        counter = 0
        for line in file_list:
            if line.strip() == "# name %s" % email:
                return counter
            counter += 1
        return None

    def is_name_line(self, line):
        return True if re.match('# name', line) else False



    def get_list_by_indexes(self, starting_index, ending_index, file_list):
        return file_list[starting_index:ending_index]

    def get_list_object(self):
        list_object = []
        if self.file_content:
            list_object = self.format_output(self.file_content)
        elif self.filename:
            list_object = self.format_output(
                    self.get_output_from_file(self.filename)
                    )
        return list_object

    def extract_destination_email_from_list(self, incoming_list):
        for line in incoming_list:
            m = re.search('# name (.*)', line)
            if m:
                return m.group(1)

    def convert_list_to_dict(self, incoming_list):
        return_dict = {}
        email_dest = self.extract_destination_email_from_list(incoming_list)
        return_dict[email_dest] = {}
        for line in incoming_list:
                mobile_re = re.search('mobile: (.*)', line)
                if mobile_re:
                    return_dict[email_dest]['mobile'] = mobile_re.group(1)
                telephoneNumber_re = re.search('telephoneNumber: (.*)', line)
                if telephoneNumber_re:
                    return_dict[email_dest]['telephoneNumber'] = telephoneNumber_re.group(1)
        return return_dict

    def get_ending_index(self, starting_index, file_list):
        counter = starting_index
        for line in file_list[starting_index + 1:]:
            if re.match('^# name ', line):
                return counter
            counter += 1
        return counter

    def create_object(self, list_object = None):
        if not list_object:
            list_object = self.get_list_object()
        """
            Iterate over all of the lines
            everytime that we find a new # name line
            we want to get the start and end index of it
            we then want to take the ensuing list, and convert
            it to a dictionary object
            once we have iterated over everything, we want to
            return the entire dictionary
        """
        full_return_dict = {}

        for line in list_object:
            if self.is_name_line(line):
                email = self.parse_name_to_email(line)
                start_index = self.get_starting_index(email, list_object)
                end_index = self.get_ending_index(start_index,
                        list_object) + 1
                user_list = self.get_list_by_indexes(start_index,
                        end_index,
                        list_object)
                user_dict = self.convert_list_to_dict(user_list)
                full_return_dict = dict(full_return_dict.items() + user_dict.items())

        return full_return_dict
