from qmlease import Model


class ModelProxy(Model):
    def setData(self, index, value, role) -> bool:
        super().setData(index, value, role)
        return True
