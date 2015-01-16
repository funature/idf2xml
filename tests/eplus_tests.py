import unittest
import idf2xml.eplus
import idf2xml.idf
import csv
import copy
import random

class TestEplus(unittest.TestCase):
    def setUp(self):
        self.runner = idf2xml.eplus.EnergyPlus()
    
    def test_energy_plus_creation(self):
        self.assertIsNotNone(self.runner)
        self.assertEqual(self.runner.runner, 'C:\\EnergyPlusV7-0-0\\EnergyPlus.exe')
        self.assertEqual(self.runner.postprocessor, 'C:\\EnergyPlusV7-0-0\\PostProcess\\ReadVarsESO.exe')
        self.assertEqual(self.runner.iddfile, 'C:\\EnergyPlusV7-0-0\\Energy+.idd')
    
    def test_energy_plus_run(self):
        results = self.runner.run('test.idf', 'weather.epw')
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 8760)
        self.assertAlmostEqual(results[-1]['Heating:Gas [J](Hourly)'], 228687321.927993)
    
    def test_energy_plus_fatal(self):
        results = self.runner.run('fatal_error.idf', 'weather.epw')
        self.assertIsNone(results)
    
    def test_energy_plus_run_with_schedule(self):
        results = self.runner.run('testwithschedule.idf', 'weather.epw',
                                  supplemental_files=[('schedule.csv', 'House1 Sch 2010.csv')])
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2688)
        self.assertAlmostEqual(results[-1]['Whole Building:Total Building Electric Demand [W](TimeStep)'], 397.5300001)
    
    def test_eplus_variable_set(self):
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            varset = idf2xml.eplus.EPlusVariableSet(reader)
            self.assertEqual(varset[16].idffield, 'Fan Efficiency')
            self.assertEqual(varset[33].maximum, 24.7)
        params = []
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            for row in reader:
                p = {}
                for key in row:
                    p[key] = row[key]
                params.append(p)
        varset = idf2xml.eplus.EPlusVariableSet(params)
        self.assertEqual(varset[16].idffield, 'Fan Efficiency')
        self.assertEqual(varset[33].maximum, 24.7)
        with open('params_write_test.csv', 'wb') as pfile:
            pfile.write(str(varset))
        with open('params_write_test.csv') as pfile:
            reader = csv.DictReader(pfile)
            varset = idf2xml.eplus.EPlusVariableSet(reader)
            self.assertEqual(varset[16].idffield, 'Fan Efficiency')
            self.assertEqual(varset[33].maximum, 24.7)
        
    def test_eplus_deepcopy(self):
        v = idf2xml.eplus.EPlusVariable('test')
        v.constraint = idf2xml.eplus.EPlusConstraint('A + B < C')
        c = copy.deepcopy(v)
        c.idfclass = 'copy'
        self.assertEqual(v.idfclass, 'test')
        self.assertEqual(c.idfclass, 'copy')
        self.assertEqual(v.constraint.variables, ['A', 'B', 'C'])
        self.assertEqual(c.constraint.variables, ['A', 'B', 'C'])
        c.constraint.variables = ['A', 'B']
        self.assertEqual(v.constraint.variables, ['A', 'B', 'C'])
        self.assertEqual(c.constraint.variables, ['A', 'B'])
        varset = None
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            varset = idf2xml.eplus.EPlusVariableSet(reader)
        candidate = idf2xml.eplus.EPlusCandidate(varset.variables)
        candcopy = copy.deepcopy(candidate)
        self.assertEqual(candidate.get_value('G003'), 30)
        self.assertEqual(candcopy.get_value('G003'), 30)
        candcopy.set_value('G003', 20)
        self.assertEqual(candidate.get_value('G003'), 30)
        self.assertEqual(candcopy.get_value('G003'), 20)
        
    def test_eplus_candidate(self):
        varset = None
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            varset = idf2xml.eplus.EPlusVariableSet(reader)
        candidate = idf2xml.eplus.EPlusCandidate(varset.variables)
        self.assertTrue(candidate.evaluate_constraint('G001'))
        self.assertTrue(candidate.evaluate_constraint('G002'))
        self.assertTrue(candidate.evaluate_constraint('G003'))
        self.assertTrue(candidate.evaluate_constraint('G004'))
        candidate.set_value('G003', 3)
        self.assertTrue(candidate.get_value('G003'), 3)
        self.assertFalse(candidate.evaluate_constraint('G003'))
        with open('params.idf') as ifile:
            idffile = idf2xml.idf.IDFFile(ifile)
            idffile = candidate.values_to_idf(idffile)
            self.assertEqual(idffile.find('Schedule:Compact', 'CLGSETP_KITCHEN_SCH', 'Field 4'), '3')
            self.assertEqual(idffile.find('Schedule:Compact', 'CLGSETP_KITCHEN_SCH', 'Field 9'), '3')
    
    def test_eplus_candidate_constraints(self):
        varset = None
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            varset = idf2xml.eplus.EPlusVariableSet(reader)
        c = idf2xml.eplus.EPlusCandidate(varset.variables)
        constraint_count = {g: 0 for g in sorted(c.variables)}
        for group in sorted(c.variables):
            v = c.get_variable(group)
            if v.constraint is not None:
                for cvar in v.constraint.variables:
                    if cvar in constraint_count:
                        constraint_count[cvar] += 1
        
        varorder = [(g, c.get_variable(g).maximum - c.get_variable(g).minimum, constraint_count[g]) for g in c]
        varorder.sort(key=lambda x: x[1])
        varorder.sort(key=lambda x: x[2], reverse=True)
        sort_order = [x[0] for x in varorder]
        order = c.get_constraint_order()
        self.assertListEqual(sort_order, order)
        b = c.get_constrained_bounds('G002')
        self.assertAlmostEqual(b[0], 9.03)
        self.assertAlmostEqual(b[1], 13.39999999)
        b = c.get_constrained_bounds('G003')
        self.assertAlmostEqual(b[0], 21.0)
        self.assertAlmostEqual(b[1], 39.0)
        b = c.get_constrained_bounds('G004')
        self.assertAlmostEqual(b[0], 21.0)
        self.assertAlmostEqual(b[1], 33.8)
        
    def test_eplus_candidate_permutation(self):
        rand = random.Random()
        rand.seed(12345)
        varset = None
        with open('params.csv') as pfile:
            reader = csv.DictReader(pfile)
            varset = idf2xml.eplus.EPlusVariableSet(reader)
        c = idf2xml.eplus.EPlusCandidate(varset.variables)
        p = c.permutation(rand)
        for group in p:
            v = p.get_variable(group)
            self.assertLessEqual(v.minimum, v.value)
            self.assertGreaterEqual(v.maximum, v.value)
            self.assertNotEqual(v.value, c.get_variable(group).value)
    
    def test_eplus_results(self):
        results = None
        with open('params_eplusoutput.csv') as resultsfile:
            results = idf2xml.eplus.EPlusResults(resultsfile)
        self.assertEqual(results[-1]['Date/Time'], '12/31  24:00:00')
        self.assertAlmostEqual(results[0]['PSZ-AC_2:2:Air Loop Fan Electric Consumption[J](Hourly)'], 2921620.03001228)
        self.assertIsNone(results[28]['Electricity:Facility [J](Monthly)'])
        with open('params_testoutput.csv', 'wb') as testresfile:
            testresfile.write(str(results))
        with open('params_testoutput.csv') as testresfile:
            testresults = idf2xml.eplus.EPlusResults(testresfile)
        for trow in range(len(results)):
            x = results.results[trow]
            y = testresults.results[trow]
            for key in x:
                if x[key] == y[key]:
                    self.assertEqual(x[key], y[key])
                else:
                    try:
                        diff = abs(x[key] - y[key]) / max(abs(x[key]), abs(y[key]))
                        self.assertLess(diff, 0.00000000001)
                    except:
                        # In case the denominator is 0 in diff, we just fall
                        # back to the AlmostEqual measure with "high" delta.
                        self.assertAlmostEqual(x[key], y[key], delta=1)
    
if __name__ == '__main__':
    import logging
    logger = logging.getLogger('eplus')
    logger.setLevel(logging.DEBUG)
    logging_filehandler = logging.FileHandler('eplus.log')
    logging_filehandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger('eplus').addHandler(logging_filehandler)
    unittest.main()
    
    
    
    