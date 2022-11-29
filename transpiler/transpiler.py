from transpiler.old import Translator


class Transpiler:
    def transpile(self, code):
        return Translator().translate(code)
