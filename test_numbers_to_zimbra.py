#!/usr/bin/python                                                                                                     
import unittest
from zimbra_number_sync import ZimbraNumberSync
import os

"""
    We want file_content to be a perfect storm of all possible
    combinations.
    
    We'll have leading and trailing blank whitespace.

    Leading and trailing entries with no mobile: or telephoneNumber:
    attributes.
"""

file_content = """


# name asdf0@mozilla.com
# name foo@mozilla.com
mobile: 2161231234
telephoneNumber: 2165551234x204
# name bar@mozilla.com
mobile: 1231231234
# name baz@mozilla.com
mobile: 1231231234, 5678901234
telephoneNumber: 5671231234x123
# name asdf@mozilla.com
# name blah@mozilla.com

"""

class testZimbraNumberSync(unittest.TestCase):
    filename = '/tmp/zimbra_number_sync_test'

    def delete_test_file(self):
        try:
            os.remove(self.filename)
        except OSError:
            pass
    def setUp(self):
        fh = open(self.filename, 'w')
        fh.write(file_content)
        fh.close()

    def tearDown(self):
        self.delete_test_file()


    def test1_constructor_with_file_content(self):
        zn = ZimbraNumberSync(debug=True, file_content=file_content)
        self.assertNotEqual(zn, None)
        self.assertEqual(file_content, zn.file_content)

    def test2_constructor_with_filename(self):
        zn = ZimbraNumberSync(debug=True, filename=self.filename)
        self.assertEqual(zn.filename, self.filename)

    def test3_constructor_raises_exception(self):
        self.assertRaises(Exception, zn = ZimbraNumberSync, debug=True)

    def test4_get_list_object(self):
        zn = ZimbraNumberSync(debug=True, file_content=file_content)
        self.assertEqual(len(zn.get_list_object()), 11)
        zn = ZimbraNumberSync(debug=True, filename=self.filename)
        self.assertEqual(len(zn.get_list_object()), 11)

    def test5_create_object_from_file_content(self):
        zn = ZimbraNumberSync(debug=True, file_content=file_content)
        zn_object = zn.create_object()
        self.confirm_zn_object(zn_object)

    def test6_create_object_from_filename(self):
        zn = ZimbraNumberSync(debug=True, filename=self.filename)
        zn_object = zn.create_object()
        self.confirm_zn_object(zn_object)

    def confirm_zn_object(self, zn_object):
        """
            Main integration test here
        """
        self.assertEqual(len(zn_object), 6)
        self.assertEqual(zn_object['blah@mozilla.com'], {})
        self.assertEqual(zn_object['asdf@mozilla.com'], {})
        self.assertEqual(zn_object['asdf0@mozilla.com'], {})
        self.assertEqual(zn_object['bar@mozilla.com'], {
            'mobile': '1231231234',
            })
        self.assertEqual(zn_object['foo@mozilla.com'], {
            'mobile': '2161231234',
            'telephoneNumber': '2165551234x204',
            })
        self.assertEqual(zn_object['baz@mozilla.com'], {
            'mobile': '1231231234, 5678901234',
            'telephoneNumber': '5671231234x123',
            })

if __name__ == '__main__':
    unittest.main()

