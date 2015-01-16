@ECHO OFF
setlocal
set PYTHONPATH=..
echo Running eplus_tests.py...
python eplus_tests.py
echo Running idf_tests.py...
python idf_tests.py
echo Running idfxml_tests.py...
python idfxml_tests.py
endlocal