import unittest
import idf2xml.idfxml
import idf2xml.idf
import idf2xml.eplus
import xml.etree.ElementTree
import csv
import inspect
import os
import subprocess

class TestIdfXml(unittest.TestCase):
    
    def test_idf_to_xml(self):
        xmlstr = None
        with open('params.idf') as ifile:
            idffile = idf2xml.idf.IDFFile(ifile)
            xmlstr = idf2xml.idfxml.idf_to_xml(idffile)
        root1 = xml.etree.ElementTree.fromstring(xmlstr)
        root2 = xml.etree.ElementTree.parse('params.xml').getroot()
        set1 = [i.strip() for i in root1.itertext() if i.strip()]
        set2 = [i.strip() for i in root2.itertext() if i.strip()]
        self.assertListEqual(set1, set2)
    
    def test_xml_to_idf(self):
        xmlstr = None
        with open('params.xml') as xfile:
            xmlstr = xfile.read()
        xidf = idf2xml.idfxml.xml_to_idf(xmlstr)
        with open('params.idf') as ifile:
            iidf = idf2xml.idf.IDFFile(ifile)
        self.assertListEqual(xidf.idf, iidf.idf)

    def test_xml_to_variables(self):
        xmlstr = None
        with open('params.xml') as xfile:
            xmlstr = xfile.read()
        xpar = idf2xml.idfxml.xml_to_variables(xmlstr)
        ppar = None
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            ppar = idf2xml.eplus.EPlusVariableSet(reader)
        self.assertEqual(len(xpar), len(ppar))
        for xp, pp in zip(xpar, ppar):
            self.assertEqual(xp.idffield, pp.idffield)
            self.assertEqual(xp.idfclass, pp.idfclass)
            self.assertEqual(xp.idfobject, pp.idfobject)
            self.assertEqual(xp.group, pp.group)
            self.assertAlmostEqual(xp.value, pp.value)
    
    def test_variables_to_xml(self):
        xmlstr = None
        vars = None
        with open('noparams.xml') as xfile:
            xmlstr = xfile.read()
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            vars = idf2xml.eplus.EPlusVariableSet(reader)
        vxmlstr = idf2xml.idfxml.variables_to_xml(vars, xmlstr)
        newvars = idf2xml.idfxml.xml_to_variables(vxmlstr)
        for v, n in zip(vars.variables, newvars.variables):
            self.assertEqual(v.type, n.type)
            self.assertAlmostEqual(v.minimum, n.minimum)
            self.assertAlmostEqual(v.maximum, n.maximum)
            self.assertEqual(v.distribution, n.distribution)
            self.assertEqual(v.group, n.group)
            self.assertEqual(v.constraint.constraint, n.constraint.constraint)
    
    def test_command_line(self):
        test_script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        main_script = os.path.join(os.path.dirname(test_script_dir), 'idf2xml', 'idfxml.py')
        
        subprocess.call(['python', main_script, 
                         os.path.join(test_script_dir, 'params.idf'), 'idf2xml'])
        subprocess.call(['python', main_script, 
                         os.path.join(test_script_dir, 'params.idf.xml'), 'xml2idf'])
        
        with open(os.path.join(test_script_dir, 'params.idf')) as ofile, open(os.path.join(test_script_dir, 'params.idf.xml.idf')) as nfile:
            olines = ofile.readlines()
            nlines = nfile.readlines()
            self.assertListEqual(olines, nlines)
          
        subprocess.call(['python', main_script, 
                         os.path.join(test_script_dir, 'params.idf'), 'idf2xml',
                         '--varfile', os.path.join(test_script_dir, 'params.csv')])
        with open(os.path.join(test_script_dir, 'params.xml')) as ofile, open(os.path.join(test_script_dir, 'params.idf.xml')) as nfile:
            olines = ofile.readlines()
            nlines = nfile.readlines()
            self.assertListEqual(olines, nlines)
        
        
        
        
if __name__ == '__main__':
    unittest.main()
    
    
    
    