import param

class ForecastStore(param.Parameterized):
    models = param.Dict(default={})  # dictionary to hold ECMWF, MEPS, etc.

    def update(self, ecmwf=None, meps=None):
        """
        Update the models dictionary with new datasets.
        """
        if ecmwf is not None:
            self.models["ECMWF"] = ecmwf
        if meps is not None:
            self.models["MEPS"] = meps
            