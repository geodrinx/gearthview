# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
#

"""
Tests for L{twisted.trial.util}
"""

from __future__ import division, absolute_import

import os, sys

from zope.interface import implementer

from twisted.python.compat import _PY3, NativeStringIO
from twisted.python import filepath
from twisted.internet.interfaces import IProcessTransport
from twisted.internet import defer
from twisted.internet.base import DelayedCall
from twisted.python.failure import Failure

from twisted.trial.unittest import SynchronousTestCase
from twisted.trial import util
from twisted.trial.util import (
    DirtyReactorAggregateError, _Janitor, excInfoOrFailureToExcInfo,
    acquireAttribute)
from twisted.trial.test import suppression



class TestMktemp(SynchronousTestCase):
    """
    Tests for L{TestCase.mktemp}, a helper function for creating temporary file
    or directory names.
    """
    def test_name(self):
        """
        The path name returned by C{mktemp} is directly beneath a directory
        which identifies the test method which created the name.
        """
        name = self.mktemp()
        dirs = os.path.dirname(name).split(os.sep)[:-1]
        self.assertEqual(
            dirs, ['twisted.trial.test.test_util', 'TestMktemp', 'test_name'])


    def test_unique(self):
        """
        Repeated calls to C{mktemp} return different values.
        """
        name = self.mktemp()
        self.assertNotEqual(name, self.mktemp())


    def test_created(self):
        """
        The directory part of the path name returned by C{mktemp} exists.
        """
        name = self.mktemp()
        dirname = os.path.dirname(name)
        self.assertTrue(os.path.exists(dirname))
        self.assertFalse(os.path.exists(name))


    def test_location(self):
        """
        The path returned by C{mktemp} is beneath the current working directory.
        """
        path = os.path.abspath(self.mktemp())
        self.assertTrue(path.startswith(os.getcwd()))



class TestIntrospection(SynchronousTestCase):
    def test_containers(self):
        """
        When pased a test case, L{util.getPythonContainers} returns a list
        including the test case and the module the test case is defined in.
        """
        parents = util.getPythonContainers(
            suppression.SynchronousTestSuppression2.testSuppressModule)
        expected = [suppression.SynchronousTestSuppression2, suppression]
        for a, b in zip(parents, expected):
            self.assertEqual(a, b)
        # Also, the function is deprecated.
        warnings = self.flushWarnings([self.test_containers])
        self.assertEqual(DeprecationWarning, warnings[0]['category'])
        self.assertEqual(
            "twisted.trial.util.getPythonContainers was deprecated in "
            "Twisted 12.3.0: This function never worked correctly.  "
            "Implement lookup on your own.",
            warnings[0]['message'])
        self.assertEqual(1, len(warnings))
    if _PY3:
        test_containers.skip = "getPythonContainers is unsupported on Python 3."



class TestRunSequentially(SynchronousTestCase):
    """
    Sometimes it is useful to be able to run an arbitrary list of callables,
    one after the other.

    When some of those callables can return Deferreds, things become complex.
    """

    def assertDeferredResult(self, deferred, assertFunction, *args, **kwargs):
        """
        Call the given assertion function against the current result of a
        Deferred.
        """
        result = []
        deferred.addCallback(result.append)
        assertFunction(result[0], *args, **kwargs)

    def test_emptyList(self):
        """
        When asked to run an empty list of callables, runSequentially returns a
        successful Deferred that fires an empty list.
        """
        d = util._runSequentially([])
        self.assertDeferredResult(d, self.assertEqual, [])


    def test_singleSynchronousSuccess(self):
        """
        When given a callable that succeeds without returning a Deferred,
        include the return value in the results list, tagged with a SUCCESS
        flag.
        """
        d = util._runSequentially([lambda: None])
        self.assertDeferredResult(d, self.assertEqual, [(defer.SUCCESS, None)])


    def test_singleSynchronousFailure(self):
        """
        When given a callable that raises an exception, include a Failure for
        that exception in the results list, tagged with a FAILURE flag.
        """
        d = util._runSequentially([lambda: self.fail('foo')])
        def check(results):
            [(flag, fail)] = results
            fail.trap(self.failureException)
            self.assertEqual(fail.getErrorMessage(), 'foo')
            self.assertEqual(flag, defer.FAILURE)
        self.assertDeferredResult(d, check)


    def test_singleAsynchronousSuccess(self):
        """
        When given a callable that returns a successful Deferred, include the
        result of the Deferred in the results list, tagged with a SUCCESS flag.
        """
        d = util._runSequentially([lambda: defer.succeed(None)])
        self.assertDeferredResult(d, self.assertEqual, [(defer.SUCCESS, None)])


    def test_singleAsynchronousFailure(self):
        """
        When given a callable that returns a failing Deferred, include the
        failure the results list, tagged with a FAILURE flag.
        """
        d = util._runSequentially([lambda: defer.fail(ValueError('foo'))])
        def check(results):
            [(flag, fail)] = results
            fail.trap(ValueError)
            self.assertEqual(fail.getErrorMessage(), 'foo')
            self.assertEqual(flag, defer.FAILURE)
        self.assertDeferredResult(d, check)


    def test_callablesCalledInOrder(self):
        """
        Check that the callables are called in the given order, one after the
        other.
        """
        log = []
        deferreds = []

        def append(value):
            d = defer.Deferred()
            log.append(value)
            deferreds.append(d)
            return d

        util._runSequentially([lambda: append('foo'),
                               lambda: append('bar')])

        # runSequentially should wait until the Deferred has fired before
        # running the second callable.
        self.assertEqual(log, ['foo'])
        deferreds[-1].callback(None)
        self.assertEqual(log, ['foo', 'bar'])


    def test_continuesAfterError(self):
        """
        If one of the callables raises an error, then runSequentially continues
        to run the remaining callables.
        """
        d = util._runSequentially([lambda: self.fail('foo'), lambda: 'bar'])
        def check(results):
            [(flag1, fail), (flag2, result)] = results
            fail.trap(self.failureException)
            self.assertEqual(flag1, defer.FAILURE)
            self.assertEqual(fail.getErrorMessage(), 'foo')
            self.assertEqual(flag2, defer.SUCCESS)
            self.assertEqual(result, 'bar')
        self.assertDeferredResult(d, check)


    def test_stopOnFirstError(self):
        """
        If the C{stopOnFirstError} option is passed to C{runSequentially}, then
        no further callables are called after the first exception is raised.
        """
        d = util._runSequentially([lambda: self.fail('foo'), lambda: 'bar'],
                                  stopOnFirstError=True)
        def check(results):
            [(flag1, fail)] = results
            fail.trap(self.failureException)
            self.assertEqual(flag1, defer.FAILURE)
            self.assertEqual(fail.getErrorMessage(), 'foo')
        self.assertDeferredResult(d, check)



class DirtyReactorAggregateErrorTest(SynchronousTestCase):
    """
    Tests for the L{DirtyReactorAggregateError}.
    """

    def test_formatDelayedCall(self):
        """
        Delayed calls are formatted nicely.
        """
        error = DirtyReactorAggregateError(["Foo", "bar"])
        self.assertEqual(str(error),
                          """\
Reactor was unclean.
DelayedCalls: (set twisted.internet.base.DelayedCall.debug = True to debug)
Foo
bar""")


    def test_formatSelectables(self):
        """
        Selectables are formatted nicely.
        """
        error = DirtyReactorAggregateError([], ["selectable 1", "selectable 2"])
        self.assertEqual(str(error),
                          """\
Reactor was unclean.
Selectables:
selectable 1
selectable 2""")


    def test_formatDelayedCallsAndSelectables(self):
        """
        Both delayed calls and selectables can appear in the same error.
        """
        error = DirtyReactorAggregateError(["bleck", "Boozo"],
                                           ["Sel1", "Sel2"])
        self.assertEqual(str(error),
                          """\
Reactor was unclean.
DelayedCalls: (set twisted.internet.base.DelayedCall.debug = True to debug)
bleck
Boozo
Selectables:
Sel1
Sel2""")



class StubReactor(object):
    """
    A reactor stub which contains enough functionality to be used with the
    L{_Janitor}.

    @ivar iterations: A list of the arguments passed to L{iterate}.
    @ivar removeAllCalled: Number of times that L{removeAll} was called.
    @ivar selectables: The value that will be returned from L{removeAll}.
    @ivar delayedCalls: The value to return from L{getDelayedCalls}.
    """

    def __init__(self, delayedCalls, selectables=None):
        """
        @param delayedCalls: See L{StubReactor.delayedCalls}.
        @param selectables: See L{StubReactor.selectables}.
        """
        self.delayedCalls = delayedCalls
        self.iterations = []
        self.removeAllCalled = 0
        if not selectables:
            selectables = []
        self.selectables = selectables


    def iterate(self, timeout=None):
        """
        Increment C{self.iterations}.
        """
        self.iterations.append(timeout)


    def getDelayedCalls(self):
        """
        Return C{self.delayedCalls}.
        """
        return self.delayedCalls


    def removeAll(self):
        """
        Increment C{self.removeAllCalled} and return C{self.selectables}.
        """
        self.removeAllCalled += 1
        return self.selectables



class StubErrorReporter(object):
    """
    A subset of L{twisted.trial.itrial.IReporter} which records L{addError}
    calls.

    @ivar errors: List of two-tuples of (test, error) which were passed to
        L{addError}.
    """

    def __init__(self):
        self.errors = []


    def addError(self, test, error):
        """
        Record parameters in C{self.errors}.
        """
        self.errors.append((test, error))



class JanitorTests(SynchronousTestCase):
    """
    Tests for L{_Janitor}!
    """

    def test_cleanPendingSpinsReactor(self):
        """
        During pending-call cleanup, the reactor will be spun twice with an
        instant timeout. This is not a requirement, it is only a test for
        current behavior. Hopefully Trial will eventually not do this kind of
        reactor stuff.
        """
        reactor = StubReactor([])
        jan = _Janitor(None, None, reactor=reactor)
        jan._cleanPending()
        self.assertEqual(reactor.iterations, [0, 0])


    def test_cleanPendingCancelsCalls(self):
        """
        During pending-call cleanup, the janitor cancels pending timed calls.
        """
        def func():
            return "Lulz"
        cancelled = []
        delayedCall = DelayedCall(300, func, (), {},
                                  cancelled.append, lambda x: None)
        reactor = StubReactor([delayedCall])
        jan = _Janitor(None, None, reactor=reactor)
        jan._cleanPending()
        self.assertEqual(cancelled, [delayedCall])


    def test_cleanPendingReturnsDelayedCallStrings(self):
        """
        The Janitor produces string representations of delayed calls from the
        delayed call cleanup method. It gets the string representations
        *before* cancelling the calls; this is important because cancelling the
        call removes critical debugging information from the string
        representation.
        """
        delayedCall = DelayedCall(300, lambda: None, (), {},
                                  lambda x: None, lambda x: None,
                                  seconds=lambda: 0)
        delayedCallString = str(delayedCall)
        reactor = StubReactor([delayedCall])
        jan = _Janitor(None, None, reactor=reactor)
        strings = jan._cleanPending()
        self.assertEqual(strings, [delayedCallString])


    def test_cleanReactorRemovesSelectables(self):
        """
        The Janitor will remove selectables during reactor cleanup.
        """
        reactor = StubReactor([])
        jan = _Janitor(None, None, reactor=reactor)
        jan._cleanReactor()
        self.assertEqual(reactor.removeAllCalled, 1)


    def test_cleanReactorKillsProcesses(self):
        """
        The Janitor will kill processes during reactor cleanup.
        """
        @implementer(IProcessTransport)
        class StubProcessTransport(object):
            """
            A stub L{IProcessTransport} provider which records signals.
            @ivar signals: The signals passed to L{signalProcess}.
            """

            def __init__(self):
                self.signals = []

            def signalProcess(self, signal):
                """
                Append C{signal} to C{self.signals}.
                """
                self.signals.append(signal)

        pt = StubProcessTransport()
        reactor = StubReactor([], [pt])
        jan = _Janitor(None, None, reactor=reactor)
        jan._cleanReactor()
        self.assertEqual(pt.signals, ["KILL"])


    def test_cleanReactorReturnsSelectableStrings(self):
        """
        The Janitor returns string representations of the selectables that it
        cleaned up from the reactor cleanup method.
        """
        class Selectable(object):
            """
            A stub Selectable which only has an interesting string
            representation.
            """
            def __repr__(self):
                return "(SELECTABLE!)"

        reactor = StubReactor([], [Selectable()])
        jan = _Janitor(None, None, reactor=reactor)
        self.assertEqual(jan._cleanReactor(), ["(SELECTABLE!)"])


    def test_postCaseCleanupNoErrors(self):
        """
        The post-case cleanup method will return True and not call C{addError}
        on the result if there are no pending calls.
        """
        reactor = StubReactor([])
        test = object()
        reporter = StubErrorReporter()
        jan = _Janitor(test, reporter, reactor=reactor)
        self.assertTrue(jan.postCaseCleanup())
        self.assertEqual(reporter.errors, [])


    def test_postCaseCleanupWithErrors(self):
        """
        The post-case cleanup method will return False and call C{addError} on
        the result with a L{DirtyReactorAggregateError} Failure if there are
        pending calls.
        """
        delayedCall = DelayedCall(300, lambda: None, (), {},
                                  lambda x: None, lambda x: None,
                                  seconds=lambda: 0)
        delayedCallString = str(delayedCall)
        reactor = StubReactor([delayedCall], [])
        test = object()
        reporter = StubErrorReporter()
        jan = _Janitor(test, reporter, reactor=reactor)
        self.assertFalse(jan.postCaseCleanup())
        self.assertEqual(len(reporter.errors), 1)
        self.assertEqual(reporter.errors[0][1].value.delayedCalls,
                          [delayedCallString])


    def test_postClassCleanupNoErrors(self):
        """
        The post-class cleanup method will not call C{addError} on the result
        if there are no pending calls or selectables.
        """
        reactor = StubReactor([])
        test = object()
        reporter = StubErrorReporter()
        jan = _Janitor(test, reporter, reactor=reactor)
        jan.postClassCleanup()
        self.assertEqual(reporter.errors, [])


    def test_postClassCleanupWithPendingCallErrors(self):
        """
        The post-class cleanup method call C{addError} on the result with a
        L{DirtyReactorAggregateError} Failure if there are pending calls.
        """
        delayedCall = DelayedCall(300, lambda: None, (), {},
                                  lambda x: None, lambda x: None,
                                  seconds=lambda: 0)
        delayedCallString = str(delayedCall)
        reactor = StubReactor([delayedCall], [])
        test = object()
        reporter = StubErrorReporter()
        jan = _Janitor(test, reporter, reactor=reactor)
        jan.postClassCleanup()
        self.assertEqual(len(reporter.errors), 1)
        self.assertEqual(reporter.errors[0][1].value.delayedCalls,
                          [delayedCallString])


    def test_postClassCleanupWithSelectableErrors(self):
        """
        The post-class cleanup method call C{addError} on the result with a
        L{DirtyReactorAggregateError} Failure if there are selectables.
        """
        selectable = "SELECTABLE HERE"
        reactor = StubReactor([], [selectable])
        test = object()
        reporter = StubErrorReporter()
        jan = _Janitor(test, reporter, reactor=reactor)
        jan.postClassCleanup()
        self.assertEqual(len(reporter.errors), 1)
        self.assertEqual(reporter.errors[0][1].value.selectables,
                          [repr(selectable)])



class RemoveSafelyTests(SynchronousTestCase):
    """
    Tests for L{util._removeSafely}.
    """
    def test_removeSafelyNoTrialMarker(self):
        """
        If a path doesn't contain a node named C{"_trial_marker"}, that path is
        not removed by L{util._removeSafely} and a L{util._NoTrialMarker}
        exception is raised instead.
        """
        directory = self.mktemp().encode("utf-8")
        os.mkdir(directory)
        dirPath = filepath.FilePath(directory)
        self.assertRaises(util._NoTrialMarker, util._removeSafely, dirPath)


    def test_removeSafelyRemoveFailsMoveSucceeds(self):
        """
        If an L{OSError} is raised while removing a path in
        L{util._removeSafely}, an attempt is made to move the path to a new
        name.
        """
        def dummyRemove():
            """
            Raise an C{OSError} to emulate the branch of L{util._removeSafely}
            in which path removal fails.
            """
            raise OSError()

        # Patch stdout so we can check the print statements in _removeSafely
        out = NativeStringIO()
        self.patch(sys, 'stdout', out)

        # Set up a trial directory with a _trial_marker
        directory = self.mktemp().encode("utf-8")
        os.mkdir(directory)
        dirPath = filepath.FilePath(directory)
        dirPath.child(b'_trial_marker').touch()
        # Ensure that path.remove() raises an OSError
        dirPath.remove = dummyRemove

        util._removeSafely(dirPath)
        self.assertIn("could not remove FilePath", out.getvalue())


    def test_removeSafelyRemoveFailsMoveFails(self):
        """
        If an L{OSError} is raised while removing a path in
        L{util._removeSafely}, an attempt is made to move the path to a new
        name. If that attempt fails, the L{OSError} is re-raised.
        """
        def dummyRemove():
            """
            Raise an C{OSError} to emulate the branch of L{util._removeSafely}
            in which path removal fails.
            """
            raise OSError("path removal failed")

        def dummyMoveTo(path):
            """
            Raise an C{OSError} to emulate the branch of L{util._removeSafely}
            in which path movement fails.
            """
            raise OSError("path movement failed")

        # Patch stdout so we can check the print statements in _removeSafely
        out = NativeStringIO()
        self.patch(sys, 'stdout', out)

        # Set up a trial directory with a _trial_marker
        directory = self.mktemp().encode("utf-8")
        os.mkdir(directory)
        dirPath = filepath.FilePath(directory)
        dirPath.child(b'_trial_marker').touch()

        # Ensure that path.remove() and path.moveTo() both raise OSErrors
        dirPath.remove = dummyRemove
        dirPath.moveTo = dummyMoveTo

        error = self.assertRaises(OSError, util._removeSafely, dirPath)
        self.assertEqual(str(error), "path movement failed")
        self.assertIn("could not remove FilePath", out.getvalue())



class ExcInfoTests(SynchronousTestCase):
    """
    Tests for L{excInfoOrFailureToExcInfo}.
    """
    def test_excInfo(self):
        """
        L{excInfoOrFailureToExcInfo} returns exactly what it is passed, if it is
        passed a tuple like the one returned by L{sys.exc_info}.
        """
        info = (ValueError, ValueError("foo"), None)
        self.assertTrue(info is excInfoOrFailureToExcInfo(info))


    def test_failure(self):
        """
        When called with a L{Failure} instance, L{excInfoOrFailureToExcInfo}
        returns a tuple like the one returned by L{sys.exc_info}, with the
        elements taken from the type, value, and traceback of the failure.
        """
        try:
            1 / 0
        except:
            f = Failure()
        self.assertEqual((f.type, f.value, f.tb), excInfoOrFailureToExcInfo(f))



class AcquireAttributeTests(SynchronousTestCase):
    """
    Tests for L{acquireAttribute}.
    """
    def test_foundOnEarlierObject(self):
        """
        The value returned by L{acquireAttribute} is the value of the requested
        attribute on the first object in the list passed in which has that
        attribute.
        """
        self.value = value = object()
        self.assertTrue(value is acquireAttribute([self, object()], "value"))


    def test_foundOnLaterObject(self):
        """
        The same as L{test_foundOnEarlierObject}, but for the case where the 2nd
        element in the object list has the attribute and the first does not.
        """
        self.value = value = object()
        self.assertTrue(value is acquireAttribute([object(), self], "value"))


    def test_notFoundException(self):
        """
        If none of the objects passed in the list to L{acquireAttribute} have
        the requested attribute, L{AttributeError} is raised.
        """
        self.assertRaises(AttributeError, acquireAttribute, [object()], "foo")


    def test_notFoundDefault(self):
        """
        If none of the objects passed in the list to L{acquireAttribute} have
        the requested attribute and a default value is given, the default value
        is returned.
        """
        default = object()
        self.assertTrue(default is acquireAttribute([object()], "foo", default))
