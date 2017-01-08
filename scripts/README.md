This is a directory to keep all the scripts which lever the functionality of the `roboplot` package.

In order to be able to run the scripts in this folder directly, they should be executable and contain the shebang 
`#!/usr/bin/env python3`. Otherwise the python interpreter will need to be invoked manually and the script file 
passed as an argument.

Note when writing scripts, the developer should include the line

    import context

before any imports from the `roboplot` package. This is because the python interpreter will (by default) not be able 
to locate the `roboplot` module.
