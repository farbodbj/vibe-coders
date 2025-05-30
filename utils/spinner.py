from yaspin import yaspin


class Spinner:
    text = "Loading..."

    def __init__(self, text):
        self.text = text
        self.spinner = yaspin(text=self.text)
        self.spinner.start()

    def done(self):
        self.spinner.ok("Done!")

    def __str__(self):
        return self.text
