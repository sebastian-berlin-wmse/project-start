from collections import OrderedDict


class Template:
    """Representation of Mediawiki templates.

    Attributes
    ----------
    _name : str
        The name of the template.
    _subst : bool
        Whether the template should be substituted or not. If True,
        add "subst:" after the initial "{{" in the template string.
    _parameters : OrderedDict
        The parameters to pass to the template.

    """
    def __init__(self, name, subst=False):
        self._name = name
        self._subst = subst
        self._parameters = OrderedDict()

    def __str__(self):
        output = "{{{{{}{}".format("subst:" * self._subst, self._name)
        if self._parameters:
            for name, value in self._parameters.items():
                output += "\n| {} = {}".format(name, value)
            output += "\n}}"
        else:
            output += "}}"
        return output

    def add_parameter(self, name, value):
        """Add a template parameter.

        Parameters
        ----------
        name : str
            Name of the parameter.
        value : str
            Value of the parameter.

        """
        self._parameters[name] = value
