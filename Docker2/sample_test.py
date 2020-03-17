from adt import Manager, Runner


class Sample(Runner):
    def __init__(self, logger, manager: Manager):
        super().__init__(manager)

        logger.info('Sim Running')

        self.reset()
        while not self.is_done():
            try:
                self.step()
            except KeyboardInterrupt:
                break

        logger.info('Sim Shutdown')
