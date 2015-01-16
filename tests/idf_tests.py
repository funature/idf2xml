import unittest
import idf2xml.idf
import copy

class TestIdf(unittest.TestCase):
    def setUp(self):
        with open('test.idd') as iddfile:
            self.idd = idf2xml.idf.IDDFile(iddfile)
        with open('test.idd') as iddfile, open('test.idf') as idffile:
            self.idf_with_custom_idd = idf2xml.idf.IDFFile(idffile, iddfile)
        with open('test.idf') as idffile:
            self.idf = idf2xml.idf.IDFFile(idffile)
        
    def test_idd_load(self):
        self.assertIsNotNone(self.idd)
        self.assertEqual(len(self.idd.groups), 54)
        fields = self.idd.get_fields('Material')
        self.assertEqual(fields[0].name, 'Name')
        self.assertTrue(fields[0].required)
        self.assertEqual(fields[3].name, 'Conductivity')
        self.assertEqual(fields[3].minimum, 0)
        self.assertFalse(fields[3].include_minimum)
        
    def test_idf_load(self):
        self.assertIsNotNone(self.idf)
        self.assertEqual(len(self.idf.idf), 286)
        self.assertEqual(self.idf._find('Material')[0][1], 'Metal Building Semi-Cond Wall Insulation')
        self.assertEqual(self.idf._find('Material')[2][6], '1210')
        
    def test_idf_deepcopy(self):
        iddcopy = copy.deepcopy(self.idd)
        idfcopy = copy.deepcopy(self.idf)
        origval = self.idf.find('Material', 
                                'Metal Building Semi-Cond Wall Insulation', 
                                'Conductivity')
        idfcopy.update('Material', 
                       'Metal Building Semi-Cond Wall Insulation', 
                       'Conductivity', 'TEST')
        self.assertEqual(idfcopy.find('Material', 
                                      'Metal Building Semi-Cond Wall Insulation', 
                                      'Conductivity'), 'TEST')
        self.assertEqual(self.idf.find('Material', 
                                       'Metal Building Semi-Cond Wall Insulation', 
                                       'Conductivity'), origval)
    
    def test_idf_find(self):
        self.assertEqual(self.idf.find('Material', 
                                       'Metal Building Semi-Cond Wall Insulation', 
                                       'Conductivity'), '0.049')
                                       
    def test_idf_find_with_custom_idd(self):
        self.assertEqual(self.idf_with_custom_idd.find('Material', 
                                       'Metal Building Semi-Cond Wall Insulation', 
                                       'Conductivity'), '0.049')
                                       
    def test_idf_update(self):
        self.assertEqual(self.idf.update('Material', 
                                         'Metal Building Semi-Cond Wall Insulation', 
                                         'Conductivity', 'TEST'), 1)
        self.assertEqual(self.idf.find('Material', 
                                       'Metal Building Semi-Cond Wall Insulation', 
                                       'Conductivity'), 'TEST')

    def test_idf_update_with_custom_idd(self):
        self.assertEqual(self.idf_with_custom_idd.update('Material', 
                                         'Metal Building Semi-Cond Wall Insulation', 
                                         'Conductivity', 'TEST'), 1)
        self.assertEqual(self.idf_with_custom_idd.find('Material', 
                                       'Metal Building Semi-Cond Wall Insulation', 
                                       'Conductivity'), 'TEST')


if __name__ == '__main__':
    unittest.main()