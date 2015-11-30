import unittest

from .utils import adjust, cleanse_java, cleanse_python


class AdjustTests(unittest.TestCase):
    def assertEqualOutput(self, actual, expected):
        self.assertEqual(adjust(actual), adjust(expected))

    def test_adjust(self):
        "Test input can be stripped of leading spaces."
        self.assertEqual("""for i in range(0, 10):
    print('hello, world')
print('Done.')
""", adjust("""
            for i in range(0, 10):
                print('hello, world')
            print('Done.')
        """))

    def test_adjust_no_leading_space(self):
        self.assertEqual("""for i in range(0, 10):
    print('hello, world')
print('Done.')
""", adjust("""for i in range(0, 10):
    print('hello, world')
print('Done.')
"""))


class JavaNormalizationTests(unittest.TestCase):
    def assertNormalized(self, actual, expected):
        self.assertEqual(cleanse_java(adjust(actual)), adjust(expected))

    def test_no_exception(self):
        self.assertNormalized(
            """
            Hello, world.
            """,
            """
            Hello, world.
            """
        )

    def test_exception_in_clinit(self):
        self.assertNormalized(
            """
            Exception in thread "main" java.lang.ExceptionInInitializerError
            Caused by: org.python.exceptions.IndexError: list index out of range
                at org.python.types.List.__getitem__(List.java:100)
                at org.python.types.List.__getitem__(List.java:85)
                at python.test.<clinit>(test.py:2)
            """,
            """
            ### EXCEPTION ###
            IndexError: list index out of range
                test.py:2
            """
        )

    def test_exception_in_clinit_after_output(self):
        self.assertNormalized(
            """
            Hello, world.
            Exception in thread "main" java.lang.ExceptionInInitializerError
            Caused by: org.python.exceptions.IndexError: list index out of range
                at org.python.types.List.__getitem__(List.java:100)
                at org.python.types.List.__getitem__(List.java:85)
                at python.test.<clinit>(test.py:2)
            """,
            """
            Hello, world.
            ### EXCEPTION ###
            IndexError: list index out of range
                test.py:2
            """
        )

    def test_exception_in_method(self):
        self.assertNormalized(
            """
            Exception in thread "main" org.python.exceptions.IndexError: list index out of range
                at org.python.types.List.__getitem__(List.java:100)
                at org.python.types.List.__getitem__(List.java:85)
                at python.test.main(test.py:3)
            """,
            """
            ### EXCEPTION ###
            IndexError: list index out of range
                test.py:3
            """
        )

    def test_exception_in_method_after_output(self):
        self.assertNormalized(
            """
            Hello, world.
            Exception in thread "main" org.python.exceptions.IndexError: list index out of range
                at org.python.types.List.__getitem__(List.java:100)
                at org.python.types.List.__getitem__(List.java:85)
                at python.test.main(test.py:3)
            """,
            """
            Hello, world.
            ### EXCEPTION ###
            IndexError: list index out of range
                test.py:3
            """
        )

    def test_exception_in_constructor(self):
        self.assertNormalized(
            """
            Exception in thread "main" java.lang.ExceptionInInitializerError
            Caused by: org.python.exceptions.UnboundLocalError: local variable 'x' referenced before assignment
              at python.example.Foo.__init__(example.py:44)
              at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
              at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:57)
              at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
              at java.lang.reflect.Method.invoke(Method.java:606)
              at org.python.types.Method.invoke(Method.java:66)
              at python.example.Foo.<init>(example.py)
              at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
              at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:57)
              at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
              at java.lang.reflect.Constructor.newInstance(Constructor.java:526)
              at org.python.types.Constructor.invoke(Constructor.java:25)
              at python.example.<clinit>(example.py:51)
            """,
            """
            ### EXCEPTION ###
            UnboundLocalError: local variable 'x' referenced before assignment
                example.py:51
                example.py:44
            """
        )

    def test_float(self):
        self.assertNormalized('7.950899459780156E-6', '7.950899459780156e-6')


class PythonNormalizationTests(unittest.TestCase):
    def assertNormalized(self, actual, expected):
        self.assertEqual(cleanse_python(adjust(actual)), adjust(expected))

    def test_no_exception(self):
        self.assertNormalized(
            """
            Hello, world.
            """,
            """
            Hello, world.
            """
        )

    def test_exception(self):
        self.assertNormalized(
            """
            Traceback (most recent call last):
              File "test.py", line 3, in <module>
                print(x & y)
            TypeError: unsupported operand type(s) for &: 'float' and 'bool'
            """,
            """
            ### EXCEPTION ###
            TypeError: unsupported operand type(s) for &: 'float' and 'bool'
                test.py:3
            """
        )

    def test_exception_with_other_text(self):
        self.assertNormalized(
            """
            Hello, world.
            Traceback (most recent call last):
              File "test.py", line 3, in <module>
                print(x & y)
            TypeError: unsupported operand type(s) for &: 'float' and 'bool'
            """,
            """
            Hello, world.
            ### EXCEPTION ###
            TypeError: unsupported operand type(s) for &: 'float' and 'bool'
                test.py:3
            """
        )

    def test_float(self):
        self.assertNormalized('7.950899459780156e-06', '7.950899459780156e-6')