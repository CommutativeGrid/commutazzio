class CLInvariants:
    def __init__(self, invs):
        self.invs = invs

    def __call__(self, *args, **kwargs):
        return self.invs