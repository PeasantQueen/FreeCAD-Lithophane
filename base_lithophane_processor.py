import FreeCAD
from FreeCAD import Base
from utils.timer import Timer, computeOverallTime
from utils.qtutils import processEvents, QThread

CANCEL_TASK = False

class WorkerThread(QThread):
    def __init__(self, processor, fp, startParameter):
        super(WorkerThread, self).__init__()

        self.processor = processor
        self.fp = fp
        self.startParameter = startParameter
        self.running = True

    def executeStep(self, step, lastReturnValue):
        if self.fp is not None:
            if lastReturnValue is not None:
                lastReturnValue = step(self.fp, lastReturnValue)
            else:
                lastReturnValue = step(self.fp)
        else:
            if lastReturnValue is not None:
                lastReturnValue = step(lastReturnValue)
            else:
                lastReturnValue = step()

        return lastReturnValue

    def run(self):
        global CANCEL_TASK
        CANCEL_TASK = False

        progress_bar = Base.ProgressIndicator()

        try:
            timers = []
            processor = self.processor
            fp = self.fp

            processingSteps = processor.getProcessingSteps(fp)

            numberOfSteps = len(processingSteps) + 1
            progress_bar.start(processor.description, numberOfSteps)
            actualStep = 1
            lastReturnValue = None

            if self.startParameter != '<ignore>':
                lastReturnValue = self.startParameter

            for stepDescription, step in processingSteps:
                if CANCEL_TASK:
                    print('Cancelling step %s' % (stepDescription))
                    break
                
                timers.append(Timer('%s (%s/%s)' % (stepDescription, actualStep, numberOfSteps)))

                lastReturnValue = self.executeStep(step, lastReturnValue)

                progress_bar.next()
                timers[-1].stop()

                actualStep += 1

            if not CANCEL_TASK:
                timers.append(Timer('%s (%s/%s)' % ('Post Processing', actualStep, numberOfSteps)))

                processor.processingDone(fp, lastReturnValue)
                
                progress_bar.next()
                timers[-1].stop()
            
            FreeCAD.Console.PrintMessage('%s took %.3f s' % (processor.description, computeOverallTime(timers)))
        except:
            raise
        finally:
            CANCEL_TASK = False
            self.running = False
            progress_bar.stop()

class BaseLithophaneProcessor(object):
    def __init__(self, description):
        self.description = description

    def getProcessingSteps(self, fp):
        raise NotImplementedError('Subclasses must override this to provide a list of steps')

    def execute(self, fp):
        startParameter = self.checkExecution()

        if startParameter is None:
            return

        worker = WorkerThread(self, fp, startParameter)
        worker.start()

        while worker.running:
            processEvents()

    def Activated(self):
        startParameter = self.checkExecution()

        if startParameter is None:
            return

        worker = WorkerThread(self, None, startParameter)
        worker.start()

        while worker.running:
            processEvents()

    def checkExecution(self):
        return '<ignore>'

    def processingDone(self, fp, params):
        # subclasses might override this
        pass
